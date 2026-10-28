"""Elegir, proponer y confirmar las medidas de cada requisito (sacado de cli.py).

Lo que necesita de cli.py lo lee de `cli` en el momento de usarlo (`cli.NOMBRE`), no lo copia: así un valor
cambiado en `cli` (la raíz del proyecto en las pruebas, por ejemplo) vale también acá."""
from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path
import contextlib
import json
import os

from . import cli
from . import estructura
from . import modos


def catalogo_del_proyecto():
    """El catálogo efectivo del proyecto Oracle, como lo arma `oracle cobertura`: con sus macros y, si el proyecto lo
    declaró (confiar_escalares), con sus escalares, que Oracle ejecuta aislados."""
    from oracle_metalenguaje.nucleo.proyecto import (EscalaresInvalidas, EscalaresNoConfiables, catalogo_efectivo,
                                                     escalares_del_proyecto, macros_del_proyecto, resolver)
    proyecto = resolver(["--proyecto", str(cli.proyecto_oracle())])
    try:
        with escalares_del_proyecto(proyecto, confiar=cli.config_proyecto()["confiar_escalares"]):
            return catalogo_efectivo(proyecto, macros=macros_del_proyecto(proyecto))
    except EscalaresNoConfiables as e:
        raise cli.FactoryError(f'{e}. En Factory, eso lo declara el proyecto con "confiar_escalares": true en '
                           ".factory/config.json") from e
    except EscalaresInvalidas as e:
        raise cli.FactoryError(f"los escalares del proyecto no se pudieron cargar: {e}") from e


def archivos_de_medidas(contenido: bytes, catalogo=None) -> dict[str, Path | None]:
    """{medida: su archivo en el catálogo efectivo} para las medidas que nombra el requisito; None si no está."""
    from oracle_metalenguaje.nucleo import requisito
    medidas = requisito.Requisito.de_datos(requisito.leer(contenido.decode("utf-8"))).medido_por
    catalogo = cli.catalogo_del_proyecto() if catalogo is None else catalogo
    return {m: Path(catalogo.entradas[m].ruta) if m in catalogo else None for m in medidas}


def nombre_de_archivo(ruta: Path) -> str:
    """La ruta relativa al proyecto, o el nombre del archivo en el catálogo base de Oracle: nunca una ruta de esta máquina."""
    return ruta.relative_to(cli.ROOT).as_posix() if ruta.is_relative_to(cli.ROOT) else f"catálogo base de Oracle, {ruta.name}"


def huellas_de_catalogo(contenido: bytes, catalogo=None) -> tuple[dict[str, str | None], dict[str, str | None]]:
    """Las huellas y los archivos de las medidas que nombra el requisito, como se guardan en una decisión o propuesta."""
    archivos = cli.archivos_de_medidas(contenido, catalogo)
    return ({m: cli.sha256(r.read_bytes()) if r else None for m, r in archivos.items()},
            {m: cli.nombre_de_archivo(r) if r else None for m, r in archivos.items()})


def con_huellas(registro: dict, contenido: bytes) -> dict:
    huellas, archivos = cli.huellas_de_catalogo(contenido)
    return {**registro, "catalogos": huellas, "archivos_catalogo": archivos}


def catalogos_cambiados(registro: dict, contenido: bytes, catalogo=None) -> list[tuple[str, str, str]]:
    """(medida, archivo, qué pasó: «cambió», «falta», «no_carga» o «ilegible») de cada medida cuyo archivo cambió o ya no está desde
    el registro; vacía si el registro no guardó huellas, porque no se puede comparar."""
    viejas = registro.get("catalogos")
    if viejas is None:
        return []
    archivos_viejos = registro.get("archivos_catalogo") or {}
    try:
        archivos = cli.archivos_de_medidas(contenido, catalogo)
        actuales = {m: cli.sha256(r.read_bytes()) if r else None for m, r in archivos.items()}
    except (OSError, ValueError, cli.FactoryError):  # sin leer el catálogo (o sin poder cargar sus escalares) no se da por igual
        return sorted((m, archivos_viejos.get(m) or "sin archivo", "ilegible") for m in viejas)
    def que_paso(m):
        if actuales.get(m):
            return "cambió"
        viejo = archivos_viejos.get(m)  # el archivo sigue en el proyecto pero Oracle no carga la medida: ilegible, no falta
        return "no_carga" if viejo and (cli.ROOT / viejo).is_file() else "falta"
    return sorted((m, cli.nombre_de_archivo(archivos[m]) if archivos.get(m) else archivos_viejos.get(m) or "sin archivo", que_paso(m))
                  for m in set(viejas) | set(actuales) if actuales.get(m) is None or actuales.get(m) != viejas.get(m))


def describir_cambios(cambiadas: list[tuple[str, str, str]]) -> str:
    nota = {"cambió": "", "falta": ", ya no está en el catálogo", "ilegible": ", no pude leer el catálogo",
            "no_carga": ", el archivo está pero Oracle no carga la medida"}
    texto = "el catálogo de " + ", ".join(f"{m} ({a}{nota[que]})" for m, a, que in cambiadas)
    texto += " cambió después de la decisión registrada; " if any(q != "ilegible" for _, _, q in cambiadas) else \
        " no se pudo comparar con la decisión registrada; "
    return texto + ("volvé a decidirla con medir y las mismas medidas" if all(q == "cambió" for _, _, q in cambiadas)
                    else "revisá el catálogo y volvé a decidirla con medir")


def registrar_medidas(estado: dict, rid: str, forma: str, motivo: str | None, contenido: bytes) -> dict:
    registro = cli.con_huellas({**cli.registro_decision(estado, forma, motivo), "sha256": cli.sha256(contenido)}, contenido)
    estado.setdefault("medidas", {})[rid] = registro
    return registro


def medidas_sin_decision(estado: dict) -> list[tuple[str, str]]:
    """Requisitos con medidas en su archivo y sin decisión registrada (cambios con modo)."""
    if "modo" not in estado and "medidas" not in estado:
        return []  # cambio anterior a los modos
    medidas, pendientes = estado.get("medidas") or {}, estado.get("medidas_pendientes") or {}
    faltan, catalogo = [], None
    for rid in estado.get("requisitos", []):
        ruta = cli.requisitos_dir() / f"{rid}.requisito"
        if not ruta.is_file() or rid in pendientes:
            continue
        contenido = ruta.read_bytes()
        if not any(linea.startswith("    medido_por ") for linea in contenido.decode("utf-8").splitlines()):
            continue
        if rid not in medidas:
            faltan.append((rid, "sin decisión registrada; registrala con medir y las mismas medidas"))
        elif medidas[rid].get("sha256") not in (None, cli.sha256(contenido)):
            # None: decisión anterior a que se guardara el hash; no se puede comparar.
            faltan.append((rid, "cambió después de la decisión registrada; volvé a decidirla con medir"))
        elif medidas[rid].get("catalogos") is not None:
            if catalogo is None:  # uno solo para todos los requisitos; si no se lee, catalogos_cambiados lo dice
                with contextlib.suppress(OSError, ValueError, cli.FactoryError):
                    catalogo = cli.catalogo_del_proyecto()
            if cambiadas := cli.catalogos_cambiados(medidas[rid], contenido, catalogo):
                faltan.append((rid, cli.describir_cambios(cambiadas)))
    return faltan


@contextmanager
def bloqueo_medidas(identificador: str):
    ruta = cli.ruta_segura(cli.ROOT / estructura.DIR / 'local' / 'locks' / (identificador + '.medir.lock'))
    ruta.parent.mkdir(parents=True, exist_ok=True)
    try:
        descriptor = os.open(ruta, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError as e:
        raise cli.FactoryError(f'otra operación medir está en curso: {ruta}; si fue interrumpida, comprobá que terminó antes de retirar ese bloqueo') from e
    try:
        os.close(descriptor)
        yield
    finally:
        ruta.unlink()


def medidas_en_uso(excepto: str) -> tuple[set[str], list[str]]:
    """Las medidas que nombra algún requisito del proyecto, salvo `excepto`, y los requisitos que no se pudieron leer."""
    from oracle_metalenguaje.nucleo import requisito
    usadas, ilegibles = set(), []
    propio = cli.requisitos_dir() / f'{excepto}.requisito'
    base = cli.requisitos_dir()
    rutas = []  # también en subcarpetas, como los carga Oracle; una carpeta que no se puede abrir cuenta como ilegible
    for carpeta, _, archivos in os.walk(base, onerror=lambda e: ilegibles.append(Path(e.filename).relative_to(base).as_posix() + '/')):
        rutas += [Path(carpeta) / a for a in archivos if a.endswith('.requisito')]
    for ruta in sorted(rutas):
        if ruta != propio:
            try:
                usadas.update(requisito.cargar(ruta).medido_por)
            except (OSError, ValueError):
                ilegibles.append(ruta.relative_to(base).as_posix())
    return usadas, ilegibles


def inventario_medidas(estado: dict):
    # Oracle es quien valida la sintaxis, forma única, ids y catálogo efectivo.
    from oracle_metalenguaje.nucleo import requisito
    cli.ruta_segura(cli.requisitos_dir())
    requisitos = {}
    for rid in estado.get('requisitos', []):
        if not requisito.ID_RE.fullmatch(rid):
            raise cli.FactoryError(f'id de requisito inválido en el registro: {rid}')
        ruta = cli.ruta_segura(cli.requisitos_dir() / f'{rid}.requisito')
        requisitos[rid] = requisito.cargar(ruta)
    catalogo = cli.catalogo_del_proyecto()
    huella = cli.sha256(json.dumps([
        [mid, str(catalogo.entradas[mid].ruta), cli.sha256(catalogo.entradas[mid].ruta.read_bytes()), repr(m)]
        for mid, m in sorted(catalogo.items())
    ], ensure_ascii=False).encode())
    return requisitos, catalogo, huella


def medir(identificador: str, *, requisito_id: str | None = None,
          medidas: list[str] | None = None, listar_opciones: bool = False,
          sin_medir: str | None = None, quitar_sin_medir: bool = False) -> None:
    carpeta, estado = cli.abierto(identificador)
    cli.ruta_segura(cli.ruta_registro(carpeta))
    cli.ruta_segura(cli.ROOT / estado['spec'])
    cli.ruta_segura(carpeta / 'proposal.md')
    cli.exigir_spec(carpeta, estado)
    if not estado.get('requisitos'):
        raise cli.FactoryError(f'primero importá los requisitos: oracle-factory importar {identificador}')
    try:
        requisitos, catalogo, catalogo_sha = cli.inventario_medidas(estado)
    except ValueError as e:
        raise cli.FactoryError(f'Oracle rechazó requisito o catálogo: {e}') from e
    if listar_opciones:
        if requisito_id is not None or medidas or sin_medir is not None or quitar_sin_medir:
            raise cli.FactoryError('--listar no acepta opciones de edición')
        print('Requisitos de este cambio (sin evaluar cumplimiento):')
        for rid, r in requisitos.items():
            print(f"{rid}\n  Archivo: {cli.requisitos_dir() / (rid + '.requisito')}\n  Texto: {r.texto}\n  Fuente: {r.fuente}")
            print('  Medidas: ' + (', '.join(r.medido_por) or 'ninguna'))
            print('  SIN MEDIR: ' + (r.sin_medir or 'sin límite adicional declarado; no prueba cobertura semántica'))
        base = {mid for mid in catalogo if catalogo.entradas[mid].origen.clase == 'catalogo_base'}
        print('Medidas del proyecto:')
        for mid, m in sorted(catalogo.items()):
            if mid not in base:
                print(f'{mid}\n  Archivo: {catalogo.entradas[mid].ruta}\n  Umbral: {m.op} {m.limite} · según {m.segun}\n  Ámbito: {m.ambito}\n  Alcance: {m.alcance}')
        if base:
            print(f'Del catálogo base de Oracle ({len(base)}; se aplican a todo proyecto):')
            for mid in sorted(base):
                print(f'  {mid} · {catalogo[mid].alcance}')
        print('La persona elige y justifica la pertinencia. No se ejecutaron pruebas ni un juicio.')
        return
    if requisito_id not in requisitos:
        raise cli.FactoryError('usá el id completo de un requisito importado por este cambio; recuperalo con medir ID --listar')
    if not medidas:
        raise cli.FactoryError('indicá al menos una --medida con su id completo')
    if len(set(medidas)) != len(medidas):
        raise cli.FactoryError('no repitas una medida')
    desconocidas = sorted(set(medidas) - set(catalogo))
    if desconocidas:
        raise cli.FactoryError('medidas inexistentes o no efectivas en este proyecto: ' + ', '.join(desconocidas))
    if sin_medir is not None and (not sin_medir.strip() or quitar_sin_medir):
        raise cli.FactoryError('--sin-medir necesita un límite no vacío y no se combina con --quitar-sin-medir')
    tipo = (estado.get('tipos') or {}).get(requisito_id, 'funcional')
    via = modos.via_agente(cli.modo_de(estado), 'medidas', [tipo]) if cli.AGENTE else 'persona'
    if via == 'rechaza':
        raise cli.FactoryError(f'en modo {cli.modo_de(estado)}, las medidas de un requisito {tipo} las elige una persona desde una terminal interactiva, sin --agente')
    if via == 'persona' and not cli.terminal_interactiva():
        raise cli.FactoryError('elegir medidas es una decisión de persona y se toma desde una terminal interactiva; un agente usa --agente')
    motivo = cli.pedir_motivo(estado, 'medidas', [tipo], f'Medidas de {requisito_id}') if via == 'persona' else None
    from dataclasses import replace
    from oracle_metalenguaje.nucleo import requisito
    from oracle_metalenguaje.nucleo.forma import error_forma
    ruta = cli.requisitos_dir() / f'{requisito_id}.requisito'
    original = ruta.read_bytes()
    registro_original = (cli.ruta_registro(carpeta)).read_bytes()
    doc_original = cli.documentos(carpeta, estado)
    r = requisitos[requisito_id]
    if (requisito.Requisito.de_datos(requisito.leer(original.decode('utf-8'))) != r
            or json.loads(registro_original) != estado
            or doc_original != estado['spec_aprobada']['documentos']):
        raise cli.FactoryError('las entradas cambiaron durante la lectura; volvé a listar')
    limite = '' if quitar_sin_medir else (sin_medir if sin_medir is not None else r.sin_medir)
    nuevo_r = replace(r, medido_por=tuple(medidas), sin_medir=limite)
    if nuevo_r == r:
        # El archivo ya tiene estas medidas: lo que falta, si algo, es el registro de quién las decidió.
        pendiente = (estado.get('medidas_pendientes') or {}).get(requisito_id)
        registro = (estado.get('medidas') or {}).get(requisito_id)
        huella = cli.sha256(original)
        if registro and registro.get('sha256') in (None, huella) and not pendiente and not cli.catalogos_cambiados(registro, original):
            print('Sin cambios en la asociación; conservé la revisión y el juicio existentes.')
            return
        if via == 'propone':
            if (pendiente and pendiente['sha256'] == huella and not pendiente.get('descartada')
                    and pendiente.get('catalogos') is not None and not cli.catalogos_cambiados(pendiente, original)):
                print('Sin cambios: la propuesta ya está registrada, a la espera de una persona.')
                return
            estado.setdefault('medidas_pendientes', {})[requisito_id] = cli.con_huellas({'sha256': huella, **cli.actor(), 'cuando': cli.ahora()},
                                                                                    original)
            (estado.get('medidas') or {}).pop(requisito_id, None)
            cli.evento(estado, 'medidas_propuestas', forma='propuso', requisito=requisito_id, medidas=medidas)
            cli.escribir_atomico(cli.ruta_registro(carpeta), cli.bytes_json(estado), esperado=registro_original)
            cli.nota_tarea(identificador, f'Medidas de {requisito_id} propuestas por {cli.AGENTE} (agente, modo {cli.modo_de(estado)}); '
                       'no cuentan hasta que una persona las confirme.')
            print(f'Propuesta de {cli.AGENTE} (modo {cli.modo_de(estado)}): las medidas que el archivo ya tiene no cuentan hasta que '
                  f'una persona las confirme desde una terminal interactiva: oracle-factory medir {identificador} --confirmar')
            return
        # La persona confirma tal cual lo propuesto (mismos bytes) o decide; el agente que ahora decide
        # reemplaza su propia propuesta.
        forma = 'confirmo' if (via == 'persona' and pendiente and pendiente['sha256'] == huella
                               and not pendiente.get('descartada') and pendiente.get('catalogos') is not None
                               and not cli.catalogos_cambiados(pendiente, original)) else 'decidio'
        (estado.get('medidas_pendientes') or {}).pop(requisito_id, None)
        cli.registrar_medidas(estado, requisito_id, forma, motivo, original)
        cli.evento(estado, 'medidas_confirmadas' if forma == 'confirmo' else 'medidas_elegidas', forma=forma,
               requisito=requisito_id, medidas=medidas)
        cli.escribir_atomico(cli.ruta_registro(carpeta), cli.bytes_json(estado), esperado=registro_original)
        cli.nota_tarea(identificador, f'Medidas de {requisito_id}: {cli.quien(estado["medidas"][requisito_id])}.')
        print(f'Medidas de {requisito_id} confirmadas tal como las propuso {pendiente["actor"]}.' if forma == 'confirmo'
              else f'Medidas de {requisito_id} registradas como decisión de {cli.quien(estado["medidas"][requisito_id])}.')
        return
    # Sólo modificar cláusulas de asociación/límite; conservar prosa, fuente y comentarios.
    lineas = original.decode('utf-8').splitlines(keepends=True)
    destino = []
    insertada = False
    for linea in lineas:
        if linea.startswith('    medido_por '):
            if not insertada:
                destino.append('    medido_por ' + ', '.join(medidas) + '\n')
                insertada = True
        elif linea.startswith('    sin_medir '):
            if not insertada:
                destino.append('    medido_por ' + ', '.join(medidas) + '\n')
                insertada = True
            if limite:
                destino.append('    sin_medir ' + json.dumps(limite, ensure_ascii=False) + '\n')
        else:
            destino.append(linea)
    if not insertada:
        destino.append('    medido_por ' + ', '.join(medidas) + '\n')
    if limite and not r.sin_medir:
        destino.append('    sin_medir ' + json.dumps(limite, ensure_ascii=False) + '\n')
    datos = ''.join(destino).encode('utf-8')
    try:
        arbol = requisito.leer(datos.decode('utf-8'))
        error = error_forma(ruta, datos.decode('utf-8'), requisito.imprimir(arbol))
        if error:
            raise cli.FactoryError(error)
    except ValueError as e:
        raise cli.FactoryError(f'Oracle rechazó la asociación propuesta: {e}') from e
    with cli.bloqueo_medidas(identificador):
        cli.ruta_segura(ruta)
        cli.ruta_segura(cli.ruta_registro(carpeta))
        if (ruta.read_bytes() != original or (cli.ruta_registro(carpeta)).read_bytes() != registro_original
                or cli.documentos(carpeta, estado) != doc_original):
            raise cli.FactoryError('requisito, registro o spec cambió durante la operación; volvé a listar')
        try:
            _, _, actual_sha = cli.inventario_medidas(estado)
        except (ValueError, OSError) as e:
            raise cli.FactoryError(f'el catálogo cambió durante la operación: {e}') from e
        if actual_sha != catalogo_sha:
            raise cli.FactoryError('el catálogo cambió durante la operación; volvé a listar')
        # Invalidar primero: si falla después la escritura, nunca queda un verde anterior vigente.
        estado.update(revision=None, oracle=None, fase='requisitos_importados')
        if via == 'propone':
            estado.setdefault('medidas_pendientes', {})[requisito_id] = cli.con_huellas({'sha256': cli.sha256(datos), **cli.actor(), 'cuando': cli.ahora()},
                                                                                    datos)
            (estado.get('medidas') or {}).pop(requisito_id, None)
        else:
            (estado.get('medidas_pendientes') or {}).pop(requisito_id, None)
            cli.registrar_medidas(estado, requisito_id, 'decidio', motivo, datos)
        cli.evento(estado, 'medidas_propuestas' if via == 'propone' else 'medidas_elegidas',
               forma='propuso' if via == 'propone' else 'decidio', requisito=requisito_id, medidas=medidas, sin_medir=limite)
        cli.escribir_atomico(cli.ruta_registro(carpeta), (json.dumps(estado, ensure_ascii=False, indent=2) + '\n').encode(), esperado=registro_original)
        cli.escribir_atomico(ruta, datos, esperado=original)
    cli.nota_tarea(identificador, f'Medidas de {requisito_id}: {", ".join(medidas)}; {"propuestas" if via == "propone" else "elegidas"} por {cli.quien(cli.registro_decision(estado, "propuso" if via == "propone" else "decidio", motivo))}. SIN MEDIR: {limite or "sin límite adicional declarado"}. Revisión y juicio anteriores invalidados; no se declara cumplimiento ni aprobación de pertinencia.')
    print(f'Asociación guardada: {ruta}')
    if r.medido_por and set(r.medido_por) != set(medidas):
        print(f'Reemplaza las medidas que tenía ({", ".join(r.medido_por)}) por: {", ".join(medidas)}')
        usadas, ilegibles = cli.medidas_en_uso(excepto=requisito_id)
        sueltas = [m for m in r.medido_por if m not in medidas and m not in usadas]
        if sueltas and ilegibles:  # alguno de esos podría usarlas: no se afirma que quedaron sueltas
            print(f'No pude leer {len(ilegibles)} requisito(s) del proyecto ({", ".join(ilegibles)}); no sé si '
                  + ', '.join(sueltas) + ' queda(n) sin requisito que las use')
        elif sueltas:
            print('Quedan sin ningún requisito del proyecto que las use: ' + ', '.join(sueltas))
    print('SIN MEDIR: ' + (limite or 'sin límite adicional declarado; revisá la pertinencia y el alcance de las medidas'))
    print('Revisión y juicio anteriores invalidados. Ejecutá pruebas/sensor, registrá la versión y renová la revisión antes de juzgar.')
    if via == 'propone':
        print(f'Propuesta de {cli.AGENTE} (modo {cli.modo_de(estado)}): no cuenta hasta que una persona la confirme desde una '
              f'terminal interactiva: oracle-factory medir {identificador} --confirmar')


def propuestas_confirmables(estado: dict) -> list[str]:
    """Requisitos con medidas propuestas por el agente que siguen tal como las propuso (si el archivo cambió, ya no lo son)."""
    def actual(r):
        ruta = cli.requisitos_dir() / f"{r}.requisito"
        return cli.sha256(ruta.read_bytes()) if ruta.is_file() else None  # un requisito que falta no se puede confirmar
    propuestas = {r: p for r, p in (estado.get("medidas_pendientes") or {}).items()
                  if not p.get("descartada") and actual(r) == p["sha256"]}
    # Una propuesta sin huellas de catálogo (anterior a guardarlas) no se puede confirmar tal cual: no se sabe qué vio el agente.
    catalogo = None
    if any(p.get("catalogos") is not None for p in propuestas.values()):
        with contextlib.suppress(OSError, ValueError, cli.FactoryError):
            catalogo = cli.catalogo_del_proyecto()
    return sorted(r for r, p in propuestas.items() if p.get("catalogos") is not None
                  and not cli.catalogos_cambiados(p, (cli.requisitos_dir() / f"{r}.requisito").read_bytes(), catalogo))


def confirmar_medidas(identificador: str) -> None:
    """Las medidas que propuso el agente, por requisito, confirmadas de una vez o de a una."""
    _, estado = cli.abierto(identificador)
    cli.exigir_terminal("confirmar medidas")
    propuestas = {r: p for r, p in (estado.get("medidas_pendientes") or {}).items() if not p.get("descartada")}
    pendientes = cli.propuestas_confirmables(estado)
    cambiadas = sorted(set(propuestas) - set(pendientes))
    for rid in cambiadas:
        print(f"Aviso: {rid} o el catálogo de sus medidas cambió después de la propuesta; no se confirma acá. Revisalo con oracle-factory medir "
              f"{identificador} --listar y decidilo con medir --requisito.")
    if not pendientes:
        print("No hay medidas propuestas pendientes de confirmar.")
        return
    try:
        requisitos, _, _ = cli.inventario_medidas(estado)
    except ValueError as e:
        raise cli.FactoryError(f"Oracle rechazó requisito o catálogo: {e}") from e
    print(f"Medidas propuestas en {identificador}:")
    for rid in pendientes:
        r = requisitos[rid]
        print(f"  {rid}\n    Medidas: {', '.join(r.medido_por) or 'ninguna'}\n    "
              + (f"SIN MEDIR: {r.sin_medir} (queda a medio cubrir: juzgar no lo dará cubierto)" if r.sin_medir
                 else "Sin límite sin medir: queda cubierto"))
    i = cli.elegir(f"¿Qué hacés con las {len(pendientes)} propuestas?",
               [("Confirmar todas", "quedan como decisión tuya, tal como las propuso el agente"),
                ("Decidir de a una", "te pregunto por cada requisito"), ("Cancelar", "no registra nada")])
    if i not in (0, 1):
        raise cli.FactoryError("confirmación cancelada; no registré nada")
    elegidos = pendientes
    if i == 1:  # primero todas las respuestas: una que no es opción cancela sin haber registrado ninguna
        elegidos = []
        for rid in pendientes:
            j = cli.elegir(f"¿Confirmás las medidas de {rid}?", [("Confirmar", "queda como decisión tuya"),
                                                            ("Saltear", "sigue pendiente")])
            if j is None:
                raise cli.FactoryError("confirmación cancelada; no registré nada")
            if j == 0:
                elegidos.append(rid)
    for rid in elegidos:
        cli.medir(identificador, requisito_id=rid, medidas=list(requisitos[rid].medido_por))
