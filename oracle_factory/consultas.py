"""Consultas tipadas de sólo lectura al registro. Nunca interpreta código ni comandos del modelo."""
import json
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
    listar = bool(re.search(r'^(?:lista|listar|listame|lista me|mostra|mostrame|muestra|muestrame|cuales)\b', p))
    if not contar and not listar:
        return None
    permitidas = set('cuantos cuantas cantidad numero de el la los las tareas tarea cambios cambio hay tenemos tiene '
                     'son en total todos todas abiertos abiertas abierto abierta cerrados cerradas cerrado cerrada '
                     'abandonados abandonadas abandonado abandonada lista listar listame me mostra mostrame muestra '
                     'muestrame cuales proyecto este factory'.split())
    if set(p.split()) - permitidas:
        return {'tipo': 'consulta_no_admitida', 'respuesta': 'Ese filtro no está admitido en la consulta directa. '
                'Podés consultar todos, abiertos, cerrados o abandonados; para otros datos usá estado o tablero.'}
    filtros = [e for e in ESTADOS[1:] if any(palabra.startswith(e[:-2]) for palabra in p.split())]
    if len(filtros) > 1:
        return {'tipo': 'requiere_aclaracion', 'respuesta': '¿Querés consultar abiertos, cerrados o abandonados? Indicá un filtro.'}
    return {'operacion': 'contar' if contar else 'listar', 'estado': filtros[0] if filtros else 'todos'}


def registro(cli, argumentos):
    if not isinstance(argumentos, dict) or set(argumentos) - {'operacion', 'estado', 'id'}:
        raise ValueError('Argumentos no admitidos para registro.')
    op, estado, ident = argumentos.get('operacion'), argumentos.get('estado', 'todos'), argumentos.get('id')
    if op not in OPERACIONES or estado not in ESTADOS or (ident is not None and
            (not isinstance(ident, str) or cli.ID_RE.fullmatch(ident) is None)):
        raise ValueError('Operación, estado o ID inválido para registro.')
    if (op == 'detalle') != (ident is not None):
        raise ValueError('detalle requiere un ID; las otras operaciones no admiten ID.')
    cli.ruta_segura(cli.CHANGES)
    cambios = kb.cambios_del_proyecto(cli)
    def coincide(e):
        fase = e.get('fase')
        return (estado == 'todos' or (estado == 'abiertos' and fase not in ('cerrada', 'abandonada'))
                or (estado == 'cerrados' and fase == 'cerrada') or (estado == 'abandonados' and fase == 'abandonada'))
    elegidos = [(i, e) for i, e in cambios if coincide(e) and (ident is None or i == ident)]
    filas, archivos = [], []
    for i, e in elegidos:
        carpeta, _ = cli.leer(i)
        ruta = cli.ruta_segura(cli.ruta_registro(carpeta)).relative_to(cli.ROOT).as_posix()
        archivos.append(ruta)
        filas.append({'id': i, 'titulo': e.get('titulo', ''), 'fase': e.get('fase'), 'archivo': ruta,
                      'revision': e.get('revision'), 'requisitos': e.get('requisitos', []),
                      'spec_aprobada': e.get('spec_aprobada'), 'cierre': e.get('cierre'),
                      'responsable': e.get('responsable'), 'aceptados': e.get('aceptados', [])})
    datos = {'cantidad': len(filas), 'ids': [r['id'] for r in filas]}
    if op in ('listar', 'detalle'):
        datos.update(cambios=filas[:50], omitidos=max(0, len(filas) - 50))
    if op == 'agrupar':
        datos['por_fase'] = {fase: sum(r['fase'] == fase for r in filas) for fase in sorted({r['fase'] for r in filas})}
    criterio = {'operacion': op, 'estado': estado, **({'id': ident} if ident else {})}
    # Una fuente de consulta existe también con cero registros. Identifica el criterio y todos los registros leídos.
    fuente = {'ruta': 'registro', 'cita': f'registro:{json.dumps(criterio, ensure_ascii=False, sort_keys=True)}',
              'texto': json.dumps({'criterio': criterio, **datos}, ensure_ascii=False), 'archivos': archivos}
    return {'datos': datos, 'criterio': criterio, 'fuentes': [fuente]}


def directa(cli, pregunta):
    intencion = interpretar(pregunta)
    if intencion is None or 'tipo' in intencion:
        return intencion
    consulta = registro(cli, intencion)
    datos, filtro = consulta['datos'], intencion['estado']
    respuesta = f'Hay {datos["cantidad"]} cambios {filtro}.' if filtro != 'todos' else f'Hay {datos["cantidad"]} cambios en total.'
    if intencion['operacion'] == 'listar':
        respuesta += '\n' + '\n'.join(f'- {r["id"]}: {r["titulo"]} ({r["fase"]})' for r in datos['cambios'])
        if datos['omitidos']:
            respuesta += f'\nSe muestran 50; quedan {datos["omitidos"]} sin mostrar.'
    return {'tipo': 'registro', 'respuesta': respuesta, 'valor': datos['cantidad'], 'ids': datos['ids'],
            'filtro': filtro, 'fuentes': consulta['fuentes'], 'criterio': consulta['criterio']}
