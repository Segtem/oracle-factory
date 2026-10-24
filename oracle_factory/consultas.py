"""Consultas tipadas de sólo lectura al registro. Nunca interpreta código ni comandos del modelo."""
import json
import hashlib
import re
import unicodedata

from . import kb

ESTADOS = ('todos', 'abiertos', 'cerrados', 'abandonados')
OPERACIONES = ('contar', 'listar', 'agrupar', 'detalle')


def plano(texto):
    return ' '.join(re.findall(r'[a-z0-9]+', ''.join(c for c in unicodedata.normalize('NFKD', texto.casefold())
                                                   if not unicodedata.combining(c))))


def interpretar(texto):
    """Camino directo acotado. Un filtro desconocido se rechaza en vez de perderlo silenciosamente."""
    p = plano(texto)
    if not re.search(r'\b(?:tareas?|cambios?)\b', p):
        return None
    contar = bool(re.search(r'\b(?:cuantos|cuantas|cantidad|numero)\b', p))
    listar = bool(re.search(r'^(?:lista|listar|listame|lista me|mostra|mostrame|muestra|muestrame|cuales|que)\b', p))
    if not contar and not listar:
        return None
    clausula = p.split(' y ', 1)[0]
    if re.search(r'\b(?:no|excepto|sin|desde|hasta|ayer|hoy|semana|mes|ano|fecha|periodo)\b', clausula):
        return {'tipo': 'consulta_no_admitida', 'respuesta': 'Ese filtro no está admitido en la consulta directa. '
                'Podés consultar todos, abiertos, cerrados o abandonados; para otros datos usá estado o tablero.'}
    # Las consultas compuestas y variantes fuera del camino directo pasan al modelo, nunca se rechazan por su vocabulario.
    if ' y ' in p:
        return None
    permitidas = set('cuantos cuantas cantidad numero de el la los las tareas tarea cambios cambio hay tenemos tiene '
                     'son en total todos todas abiertos abiertas abierto abierta cerrados cerradas cerrado cerrada '
                     'abandonados abandonadas abandonado abandonada lista listar listame me mostra mostrame muestra '
                     'muestrame cuales que proyecto este factory estan existe existen quedan actualmente nos ya se cuantos'.split())
    if set(p.split()) - permitidas:
        return None
    filtros = [e for e in ESTADOS[1:] if any(palabra.startswith(e[:-2]) for palabra in p.split())]
    if len(filtros) > 1:
        return {'tipo': 'requiere_aclaracion', 'respuesta': '¿Querés consultar abiertos, cerrados o abandonados? Indicá un filtro.'}
    return {'operacion': 'contar' if contar else 'listar', 'estado': filtros[0] if filtros else 'todos'}


def registro(cli, argumentos):
    if not isinstance(argumentos, dict) or set(argumentos) - {'operacion', 'estado', 'id', 'limite', 'desplazamiento'}:
        raise ValueError('Argumentos no admitidos para registro.')
    op, estado, ident = argumentos.get('operacion'), argumentos.get('estado', 'todos'), argumentos.get('id')
    if op not in OPERACIONES or estado not in ESTADOS or (ident is not None and
            (not isinstance(ident, str) or cli.ID_RE.fullmatch(ident) is None)):
        raise ValueError('Operación, estado o ID inválido para registro.')
    if (op == 'detalle') != (ident is not None):
        raise ValueError('detalle requiere un ID; las otras operaciones no admiten ID.')
    limite, desplazamiento = argumentos.get('limite', 5), argumentos.get('desplazamiento', 0)
    if (type(limite) is not int or not 1 <= limite <= 10 or type(desplazamiento) is not int or desplazamiento < 0
            or (op != 'listar' and ('limite' in argumentos or 'desplazamiento' in argumentos))):
        raise ValueError('Sólo listar admite limite entero entre 1 y 10 y desplazamiento entero no negativo.')
    cli.ruta_segura(cli.CHANGES)
    cambios = kb.cambios_del_proyecto(cli)
    def coincide(e):
        fase = e.get('fase')
        return (estado == 'todos' or (estado == 'abiertos' and fase not in ('cerrada', 'abandonada'))
                or (estado == 'cerrados' and fase == 'cerrada') or (estado == 'abandonados' and fase == 'abandonada'))
    elegidos = [(i, e) for i, e in cambios if coincide(e) and (ident is None or i == ident)]
    archivos = [cli.ruta_segura(cli.ruta_registro(cli.CHANGES / i)).relative_to(cli.ROOT).as_posix() for i, _ in cambios]
    huella = hashlib.sha256(json.dumps([(i, e.get('fase')) for i, e in cambios], ensure_ascii=False).encode()).hexdigest()
    filas = []
    pagina = elegidos[desplazamiento:desplazamiento + limite] if op == 'listar' else elegidos if op == 'detalle' else []
    for i, e in pagina:
        carpeta, _ = cli.leer(i)
        ruta = cli.ruta_segura(cli.ruta_registro(carpeta)).relative_to(cli.ROOT).as_posix()
        fila = {'id': i, 'titulo': e.get('titulo', ''), 'fase': e.get('fase'), 'archivo': ruta,
                'quien': cli.quien_del_cambio(e), 'archivado': bool(e.get('archivo'))}
        if op == 'detalle':
            actual = cli.datos_estado(i)
            fila['estado_actual'] = {k: actual[k] for k in ('fase', 'modo', 'pendientes', 'proximo_paso', 'requisitos',
                'decisiones', 'revision', 'oracle', 'avisos', 'quien')}
        else:
            fila['detalle_requerido_para_pendientes'] = True
        filas.append(fila)
    datos = {'cantidad': len(elegidos), 'ids': [i for i, _ in (pagina if op == 'listar' else elegidos)]}
    if op in ('listar', 'detalle'):
        restantes = max(0, len(elegidos) - desplazamiento - len(filas))
        datos.update(cambios=filas, omitidos=restantes, desplazamiento=desplazamiento,
                     siguiente=({'operacion': op, 'estado': estado, 'limite': limite,
                                 'desplazamiento': desplazamiento + len(filas)} if restantes else None))
    if op == 'agrupar':
        datos['por_fase'] = {fase: sum(e.get('fase') == fase for _, e in elegidos)
                            for fase in sorted({e.get('fase') for _, e in elegidos})}
    criterio = {'operacion': op, 'estado': estado, **({'id': ident} if ident else {})}
    if op == 'listar':
        criterio.update(limite=limite, desplazamiento=desplazamiento)
    # Una fuente de consulta existe también con cero registros. Identifica el criterio y todos los registros leídos.
    lineas = [f'Cantidad de cambios {estado}: {datos["cantidad"]}.', json.dumps({'criterio': criterio, 'cantidad': datos['cantidad']}, ensure_ascii=False)]
    if op == 'agrupar':
        lineas.append('Por fase: ' + json.dumps(datos['por_fase'], ensure_ascii=False))
    for fila in filas:
        lineas.append(f"{fila['id']}: {fila['titulo']}; fase {fila['fase']}" + (' (archivado).' if fila['archivado'] else '.'))
        actual = fila.get('estado_actual')
        if actual:
            lineas.append('Pendientes: ' + '; '.join(actual['pendientes']))
            lineas.append('Próximo paso: ' + str(actual['proximo_paso']))
            lineas.append('Avisos: ' + '; '.join(actual['avisos']))
            lineas.append('Decisiones registradas: ' + json.dumps(actual['decisiones'], ensure_ascii=False))
            for gate in ('revision', 'oracle'):
                lineas.append(f'{gate}: ' + json.dumps(actual[gate], ensure_ascii=False))
    fuente = {'ruta': 'registro', 'cita': f'registro:{json.dumps(criterio, ensure_ascii=False, sort_keys=True)}',
              'texto': '\n'.join(lineas), 'archivos': archivos,
              'inventario_sha256': huella, 'directorio': cli.CHANGES.relative_to(cli.ROOT).as_posix(),
              'directorio_existe': cli.CHANGES.is_dir(),
              'criterio': criterio, 'valor': datos['cantidad'], 'agregados': datos.get('por_fase', {})}
    return {'datos': datos, 'criterio': criterio, 'fuentes': [fuente]}


def directa(cli, pregunta):
    intencion = interpretar(pregunta)
    if intencion is None or 'tipo' in intencion:
        return intencion
    consulta = registro(cli, intencion)
    datos, filtro = consulta['datos'], intencion['estado']
    respuesta = f'Hay {datos["cantidad"]} cambios {filtro}.' if filtro != 'todos' else f'Hay {datos["cantidad"]} cambios en total.'
    if intencion['operacion'] == 'listar':
        respuesta += '\n' + '\n'.join(f'- {r["id"]}: {r["titulo"]} ({r["fase"]}' +
                                        ('; archivado)' if r['archivado'] else ')') for r in datos['cambios'])
        if datos['omitidos']:
            respuesta += f'\nSe muestran {len(datos["cambios"])}; quedan {datos["omitidos"]} sin mostrar. Usá listar para verlos todos.'
    return {'tipo': 'registro', 'respuesta': respuesta, 'valor': datos['cantidad'], 'ids': datos['ids'],
            'filtro': filtro, 'fuentes': consulta['fuentes'], 'criterio': consulta['criterio'],
            **({'pagina': {'limite': intencion.get('limite', 5), 'desplazamiento': datos['desplazamiento'],
                           'omitidos': datos['omitidos'], 'siguiente': datos['siguiente']}} if intencion['operacion'] == 'listar' else {})}
