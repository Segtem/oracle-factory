#!/usr/bin/env python3
"""Orquestación mínima con aprobaciones humanas explícitas."""
from __future__ import annotations

import argparse
import contextlib
import io
import datetime as dt
import fcntl
import getpass
import hashlib
import json
import os
import shutil
import tempfile
import time
from contextlib import contextmanager
import random
import re
import shlex
import subprocess
import sys
from importlib import metadata, resources

from . import __version__
from . import archivo
from . import resumen
from . import revisores as revisores_mod
from . import estructura
from . import migracion
from . import preparacion
from . import trazabilidad as trazabilidad_mod
from . import modos
from . import plantillas
from . import osv as osv_mod
from . import procedencia as procedencia_mod
from . import revision as documentos_revision
from . import tablero as tablero_mod
from . import kb as kb_mod
from . import agentes as agentes_mod
from . import mcp as mcp_mod
from . import rag as rag_mod
from . import unir as unir_mod
from pathlib import Path, PurePosixPath, PureWindowsPath

ROOT = Path.cwd().resolve()
AGENTE: str | None = None  # --agente o FACTORY_AGENTE: la vía de agente nunca se registra como persona
CHANGES = ROOT / "openspec" / "changes"
ID_RE = re.compile(r"^\d{8}-\d{6}-[a-z0-9_-]+$")
SLUG_RE = re.compile(r"^[a-z][a-z0-9-]*$")


class FactoryError(Exception):
    pass


class ArchivoCambiado(FactoryError):
    """Otro proceso escribió el archivo entre que se leyó y se guardó."""


def reintentar_si_cambia(funcion):
    """Para comandos que sólo agregan al registro: si otro proceso lo escribió mientras tanto, se vuelve a leer y a
    comprobar todo desde el principio (la función entera), hasta 20 veces, con una espera corta al azar."""
    def envuelta(*args, **kwargs):
        for intento in range(20):
            try:
                return funcion(*args, **kwargs)
            except ArchivoCambiado:
                time.sleep(random.uniform(0.01, 0.05) * (intento + 1))
        raise FactoryError("el registro del cambio cambió 20 veces mientras escribía (otros procesos escriben a la vez); "
                           "no guardé nada: volvé a intentarlo")
    envuelta.__name__, envuelta.__doc__ = funcion.__name__, funcion.__doc__
    return envuelta


_ULTIMA_HORA = dt.datetime.min.replace(tzinfo=dt.timezone.utc)


def ahora() -> str:
    # Con microsegundos: dos escrituras del mismo segundo (en dos ramas, por ejemplo) quedan en orden al unirlas. Las horas
    # se ordenan como horas, no como texto (unir.hora); una vieja, en segundos, cuenta desde el principio de su segundo.
    # Dentro de un proceso nunca se repite ni retrocede: si el reloj da el mismo microsegundo, se suma uno.
    # Dos procesos pueden dar la misma: evento() la corre después del último evento del registro.
    global _ULTIMA_HORA
    _ULTIMA_HORA = max(dt.datetime.now(dt.timezone.utc), _ULTIMA_HORA + dt.timedelta(microseconds=1))
    return _ULTIMA_HORA.isoformat(timespec="microseconds")


def sha256(datos: bytes) -> str:
    return hashlib.sha256(datos).hexdigest()


def ruta_cambio(identificador: str) -> Path:
    if not ID_RE.fullmatch(identificador):
        raise FactoryError("id inválido; usá el id completo que imprimió oracle-task")
    ruta = (CHANGES / identificador).resolve()
    if not ruta.is_relative_to(CHANGES.resolve()):
        raise FactoryError("ruta de cambio fuera de openspec/changes")
    return ruta_segura(CHANGES / identificador)


def ruta_registro(carpeta: Path) -> Path:
    """El registro del cambio cuyo acuerdo está en `carpeta`: en .factory/cambios/<ID>/ o, si el proyecto no se migró, en el lugar anterior."""
    return estructura.registro_de(ROOT, carpeta.name)


def dir_estado(carpeta: Path) -> Path:
    return ruta_registro(carpeta).parent


AVISADOS: set[str] = set()
LEIDOS: dict[Path, bytes] = {}  # lo último que este proceso leyó o escribió de cada registro


def leer(identificador: str) -> tuple[Path, dict]:
    carpeta = ruta_cambio(identificador)
    archivo = ruta_segura(ruta_registro(carpeta))
    if not archivo.is_file():
        raise FactoryError(f"no encuentro el registro de factory: {archivo}")
    if estructura.es_anterior(ROOT, identificador) and identificador not in AVISADOS:
        AVISADOS.add(identificador)
        print(f"Aviso: el estado de {identificador} está en el lugar anterior a la fase 2 (openspec/changes/); "
              "oracle-factory migrar lo pasa a .factory/cambios/.", file=sys.stderr)
    LEIDOS[archivo] = datos = archivo.read_bytes()
    return carpeta, json.loads(datos.decode("utf-8"))


def guardar(carpeta: Path, estado: dict, esperado: bytes | None = None) -> None:
    destino = ruta_registro(carpeta)
    destino.parent.mkdir(parents=True, exist_ok=True)
    if destino.exists() and not os.access(destino, os.W_OK):  # el reemplazo atómico saltearía la protección del archivo
        raise FactoryError(f"{destino.relative_to(ROOT)} es de sólo lectura; no lo modifico")
    datos = (json.dumps(estado, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    escribir_atomico(destino, datos, esperado=LEIDOS.get(destino) if esperado is None else esperado)  # un corte no lo trunca
    LEIDOS[destino] = datos  # también si no se había leído: es la base de la próxima escritura
    if (ROOT / kb_mod.DIR).is_dir() and estado.get("id"):
        actualizar_kb(estado["id"])


def carpeta_relativa(carpeta: str) -> PurePosixPath | None:
    """La carpeta como ruta relativa al proyecto, o None si es absoluta (en POSIX o Windows), tiene .. o barras invertidas."""
    relativa = PurePosixPath(carpeta)
    if (relativa.is_absolute() or PureWindowsPath(carpeta).is_absolute() or PureWindowsPath(carpeta).drive
            or "\\" in carpeta or ".." in relativa.parts):
        return None
    return relativa


def proyecto_oracle() -> Path:
    """La carpeta del proyecto Oracle: la raíz, o la que dice "oracle" en .factory/config.json."""
    carpeta = config_proyecto()["oracle"]
    if carpeta in (".", ""):
        return ROOT
    relativa = carpeta_relativa(carpeta)
    if relativa is None:
        raise FactoryError(f'.factory/config.json: "oracle" es una carpeta relativa al proyecto, sin ..; dice «{carpeta}»')
    ruta = ROOT / relativa
    if ruta.resolve() != ROOT / relativa or not (ruta / "oracle.json").is_file():  # un enlace que sale, o sin proyecto Oracle
        raise FactoryError(f'.factory/config.json: "oracle" dice «{carpeta}», pero ahí no hay un proyecto Oracle '
                           f'({relativa.as_posix()}/oracle.json); creálo con oracle init o corregí la carpeta')
    return ruta


def oracle_rel() -> str:
    """La carpeta del proyecto Oracle relativa a la raíz ('' si es la raíz), para nombrar rutas."""
    o = proyecto_oracle()
    return "" if o == ROOT else o.relative_to(ROOT).as_posix()


def requisitos_dir() -> Path:
    return proyecto_oracle() / "requisitos"


def con_escalares() -> list[str]:
    """--confiar-escalares si el proyecto lo declaró: Oracle ejecuta su escalares.py, aislado."""
    return ["--confiar-escalares"] if config_proyecto()["confiar_escalares"] else []


def terminal_interactiva() -> bool:
    return sys.stdin.isatty()


def actor() -> dict:
    if AGENTE:
        return {"actor": AGENTE, "tipo_actor": "agente"}
    if not terminal_interactiva():
        # Ni --agente ni terminal: no se puede atribuir a una persona.
        return {"actor": "sin identificar", "tipo_actor": "sin_identificar"}
    nombre = subprocess.run(["git", "config", "user.name"], cwd=ROOT, capture_output=True, text=True).stdout.strip()
    return {"actor": nombre or getpass.getuser(), "tipo_actor": "persona"}


def modo_de(estado: dict) -> str:
    return estado.get("modo", modos.POR_DEFECTO)


def config_proyecto() -> dict:
    ruta = ruta_segura(ROOT / estructura.DIR / "config.json")
    if not ruta.is_file():
        ruta = ruta_segura(ROOT / "factory.json")  # proyecto anterior a la fase 2
        if ruta.is_file() and "config" not in AVISADOS:
            AVISADOS.add("config")
            print("Aviso: la configuración está en factory.json de la raíz; oracle-factory migrar la pasa a "
                  ".factory/config.json.", file=sys.stderr)
    datos = json.loads(ruta.read_text(encoding="utf-8")) if ruta.is_file() else {}
    if not isinstance(datos, dict):
        raise FactoryError(f"{ruta}: se requiere un objeto JSON")
    config = {"modo_por_defecto": datos.get("modo_por_defecto", modos.POR_DEFECTO),
              "tipos_obligatorios": datos.get("tipos_obligatorios", False),
              "capacidades": datos.get("capacidades", {}),
              "revisores": datos.get("revisores", {}),
              "oracle": datos.get("oracle", "."),
              "confiar_escalares": datos.get("confiar_escalares", False),
              "rag": datos.get("rag", {}),
              "idioma": datos.get("idioma", plantillas.POR_DEFECTO)}
    try:
        plantillas.validar(config["idioma"])
    except (ValueError, TypeError) as e:
        raise FactoryError(f"{ruta}: idioma no admitido ({config['idioma']!r}): se admiten {' y '.join(plantillas.IDIOMAS)}") from e
    try:
        revisores_mod.validar_config(config["revisores"])
    except revisores_mod.RevisorInvalido as e:
        raise FactoryError(f"{ruta}: {e}; por ejemplo: {revisores_mod.EJEMPLO}") from e
    alias = config["capacidades"]
    if (set(datos) - set(config) or config["modo_por_defecto"] not in modos.MODOS
            or type(config["tipos_obligatorios"]) is not bool or type(config["confiar_escalares"]) is not bool
            or not isinstance(config["oracle"], str) or not isinstance(config["rag"], dict)
            or not isinstance(alias, dict) or not all(isinstance(k, str) and isinstance(v, str) and v not in alias
                                                      for k, v in alias.items())):
        raise FactoryError(f"{ruta}: se admiten modo_por_defecto ({', '.join(modos.MODOS)}), tipos_obligatorios (true/false), "
                           "capacidades (alias → capacidad, sin cadenas de alias), revisores, oracle (la carpeta del proyecto Oracle) "
                           "confiar_escalares (true/false), rag (sus embeddings, ver oracle-factory preguntar) e idioma (es o en, el de las plantillas de un cambio nuevo)")
    return config


def evento(estado: dict, accion: str, forma: str = "decidio", **datos) -> None:
    # Siempre después del último evento del registro, aunque otro proceso lo haya escrito en el mismo microsegundo (las
    # escrituras de un registro están serializadas: la que pierde la carrera vuelve a leer y a pasar por acá).
    cuando = ahora()
    previos = estado.get("eventos") or []
    if previos:
        ultimo = max(unir_mod.hora(e)[0] for e in previos)
        if unir_mod.hora({"cuando": cuando})[0] <= ultimo:
            cuando = (ultimo + dt.timedelta(microseconds=1)).isoformat(timespec="microseconds")
    estado.setdefault("eventos", []).append({
        "accion": accion, **actor(), "modo": modo_de(estado), "forma": forma, "cuando": cuando, **datos})
    # Lo que quedó sin decidir al unir dos ramas lo resuelve la decisión que corresponde.
    resueltos = unir_mod.resueltos_por(accion, datos.get("requisito"))
    if resueltos and estado.get("pendientes_de_union"):
        quedan = [x for x in estado["pendientes_de_union"] if not unir_mod.resuelto(x, resueltos)]
        if quedan:
            estado["pendientes_de_union"] = quedan
        else:
            estado.pop("pendientes_de_union")


def exigir_terminal(que: str = "esta decisión") -> None:
    # Una decisión de persona no la toma un agente, aunque corra en una terminal: con --agente sólo se propone.
    if AGENTE:
        raise FactoryError(f"{que} es de una persona, sin --agente; {AGENTE} puede proponerla, no tomarla")
    if not terminal_interactiva():
        raise FactoryError(f"{que} es de una persona y se toma desde una terminal interactiva; la entrada por pipe no cuenta. "
                           "Un agente deja su propuesta con --agente y queda registrado como agente.")


def elegir(pregunta: str, opciones: list[tuple[str, str]]) -> int | None:
    """Menú numerado: el índice de la opción elegida, o None si la respuesta no es una opción (Enter solo no elige)."""
    print(f"\n{pregunta}")
    for i, (etiqueta, implica) in enumerate(opciones, 1):
        print(f"  {i}) {etiqueta} — {implica}")
    respuesta = input(f"Elegí 1-{len(opciones)}: ").strip()
    # Sólo dígitos ASCII: isdigit() también acepta «²», que int() no convierte.
    return int(respuesta) - 1 if re.fullmatch(r"[0-9]+", respuesta) and 1 <= int(respuesta) <= len(opciones) else None


def confirmar_persona(menu: tuple[str, str, str], cancelado: str) -> None:
    """menu = (qué se decide, etiqueta de la opción que confirma, qué implica confirmar)."""
    pregunta, confirmar, implica = menu
    exigir_terminal(f"«{pregunta}»")
    if elegir(pregunta, [(confirmar, implica), ("Cancelar", "no registra nada")]) != 0:
        raise FactoryError(cancelado)


def elegir_motivo(armado: str, propuesto: str | None = None) -> tuple[str, str]:
    """(motivo, origen): el que propuso el agente, uno armado con los datos del cambio o uno escrito ('persona')."""
    opciones = ([("Propuesto por el agente", propuesto, "agente")] if propuesto else []) + [
        ("Armado con los datos del cambio", armado, "armado"), ("Otro", "escribirlo", "persona")]
    i = elegir("Motivo de la decisión:", [(e, f"«{t}»" if o != "persona" else t) for e, t, o in opciones])
    if i is None:
        raise FactoryError("no se eligió un motivo; no registré nada")
    if opciones[i][2] != "persona":
        return opciones[i][1], opciones[i][2]
    motivo = input("Motivo: ").strip()
    if not motivo:
        raise FactoryError("motivo vacío; no registré nada")
    return motivo, "persona"


DESCRIPCION = {"spec": "la aceptación de la propuesta/spec", "medidas": "la elección de medidas",
               "revision": "la decisión de revisión", "cierre": "el cierre"}


def decidir(estado: dict, decision: str, tipos: list[str], firma, menu: tuple[str, str, str], cancelado: str, publicar,
            confirmado: tuple[str, str] | None = None) -> str | None:
    """Aplica el modo: devuelve la forma registrada, o None si el agente sólo dejó una propuesta.

    confirmado = (motivo, origen) cuando la persona ya decidió en un recorrido guiado (revisar): no se pregunta otra vez.
    """
    modo = modo_de(estado)
    if AGENTE:
        via = modos.via_agente(modo, decision, tipos)
        if via == "rechaza":
            raise FactoryError(f"en modo {modo}, {DESCRIPCION[decision]} la toma una persona desde una terminal interactiva, sin --agente")
        if via == "propone":
            estado.setdefault("propuestas", {})[decision] = {"firma": firma, **actor(), "cuando": ahora()}
            evento(estado, decision + "_propuesta", forma="propuso")
            publicar(estado)
            print(f"Propuesta registrada por {AGENTE} (modo {modo}): {DESCRIPCION[decision]} no cuenta hasta que una persona "
                  "la confirme repitiendo el comando desde una terminal interactiva, sin --agente.")
            return None
        (estado.get("propuestas") or {}).pop(decision, None)  # decidir reemplaza su propuesta anterior
        return "decidio"
    if confirmado is None:
        confirmar_persona(menu, cancelado)
        motivo = pedir_motivo(estado, decision, tipos, menu[0])
    else:
        exigir_terminal()
        motivo = confirmado
    if motivo:
        estado["motivo_pendiente"] = motivo
    propuesta = (estado.get("propuestas") or {}).pop(decision, None)
    return "confirmo" if (propuesta and propuesta["firma"] == firma) or (motivo and motivo[1] == "agente") else "decidio"


def menu_revision(identificador: str, decision: str) -> tuple[str, str, str]:
    return (f"Registrar la revisión de {identificador} con la decisión «{decision}»", "Registrar",
            "queda como decisión tuya, con el informe y las resoluciones indicados")


def pedir_motivo(estado: dict, decision: str, tipos: list[str], que: str) -> tuple[str, str] | None:
    """En modo funcional la persona decide lo funcional: con un motivo, no sólo confirmando."""
    if modo_de(estado) != "funcional" or decision == "cierre" or "funcional" not in tipos:
        return None
    return elegir_motivo(f"{que}: lo leí y lo decido tal como está (modo funcional).")


def registro_decision(estado: dict, forma: str, motivo: tuple[str, str] | None = None) -> dict:
    motivo = motivo or estado.pop("motivo_pendiente", None)
    if isinstance(motivo, str):  # registro anterior a los motivos con origen
        motivo = (motivo, "persona")
    return {**actor(), "forma": forma, "modo": modo_de(estado), "cuando": ahora(),
            **({"motivo": motivo[0], "origen_motivo": motivo[1]} if motivo else {})}


def quien(registro: dict | None) -> str:
    if not registro:
        return "pendiente"
    if "tipo_actor" not in registro:
        return f"{registro.get('por', '?')} (actor no registrado: anterior a los modos)"
    motivo = f"; motivo: {registro['motivo']}" if registro.get("motivo") else ""
    return f"{registro['actor']} ({registro['tipo_actor']}, {registro['forma']}, modo {registro['modo']}{motivo})"


def ejecutar(args: list[str]) -> subprocess.CompletedProcess[str]:
    # uv tool install no expone los ejecutables de dependencias en el PATH global.
    # Usar los entry points del mismo intérprete evita depender de otra instalación.
    paquetes = {"oracle": "oracle-metalenguaje", "tasks": "oracle-task", "oracle-clue": "oracle-clue"}
    if args[0] in paquetes:
        paquete = paquetes[args[0]]
        try:
            metadata.distribution(paquete)
        except metadata.PackageNotFoundError:
            if args[0] == "oracle-clue":  # dependencia fija: se usa la del entorno de Factory, nunca otra del PATH
                raise FactoryError(f"falta oracle-clue en el entorno de Factory ({sys.executable}); reinstalá oracle-factory "
                                   "o, en un clon, uv pip install -e . en su .venv")
            pass  # Compatibilidad con el checkout y herramientas ya instaladas.
        else:
            codigo = ("import sys; from importlib.metadata import distribution; "
                      "d=distribution(sys.argv.pop(1)); nombre=sys.argv.pop(1); "
                      "ep=next(e for e in d.entry_points if e.group=='console_scripts' and e.name==nombre); "
                      "sys.exit(ep.load()())")
            args = [sys.executable, "-c", codigo, paquete, *args]
    return subprocess.run(args, cwd=ROOT, capture_output=True, text=True, encoding="utf-8", check=False)


def nota_tarea(identificador: str, texto: str) -> None:
    p = ejecutar(["tasks", "note", identificador, texto, "--proyecto", str(ROOT)])
    if p.returncode:
        raise FactoryError(f"oracle-task no pudo registrar la nota: {p.stderr.strip()}")


def nuevo(titulo: str, capacidad: str | None = None, con_ejemplo: str | None = None, modo: str | None = None,
          sufijo: str | None = None, idioma: str | None = None) -> str:
    if con_ejemplo and (con_ejemplo != 'notas' or capacidad not in (None, 'notas')):
        raise FactoryError('--con-ejemplo notas requiere capacidad notas, o no indicar --capacidad')
    capacidad = capacidad or ('notas' if con_ejemplo else None)
    if capacidad is None:
        raise FactoryError('indicá --capacidad o --con-ejemplo notas')
    ruta_segura(CHANGES)
    ruta_segura(ROOT / "tareas")
    if not SLUG_RE.fullmatch(capacidad):
        raise FactoryError("capacidad debe ser un slug OpenSpec: minúsculas, números y guiones")
    # El sufijo del ID: por defecto la capacidad, no los primeros 16 caracteres del título (que cortan la frase).
    sufijo = sufijo or capacidad
    if not SLUG_RE.fullmatch(sufijo) or len(sufijo) > 40:
        raise FactoryError("el sufijo debe empezar con una letra y tener sólo minúsculas, números y guiones (hasta 40)")
    if capacidad_destino(capacidad) != capacidad:
        print(f"Aviso: la capacidad {capacidad} es un alias de {capacidad_destino(capacidad)} en la configuración del proyecto; "
              f"al cerrar, la spec se fusiona en openspec/specs/{capacidad_destino(capacidad)}/.", file=sys.stderr)
    modo = modo or config_proyecto()["modo_por_defecto"]
    idioma = config_proyecto()["idioma"] if idioma is None else idioma
    try:
        plantillas.validar(idioma)
    except ValueError as e:
        raise FactoryError(f"{e}; no creé nada") from e
    textos = plantillas.TEXTOS[idioma]
    if modo not in modos.MODOS:
        raise FactoryError("modo desconocido; usá " + ", ".join(modos.MODOS))
    # Contra confirmacion, no contra factory.json: ese archivo también lo puede escribir un agente.
    if modos.baja_intervencion(modos.POR_DEFECTO, modo):
        if AGENTE:
            raise FactoryError(f"el modo {modo} tiene menos intervención humana que {modos.POR_DEFECTO}: lo elige una persona, sin --agente")
        confirmar_persona((f"Crear el cambio en modo {modo}, con menos intervención humana que {modos.POR_DEFECTO}",
                           f"Usar el modo {modo}", "el agente podrá decidir más pasos sin una persona"),
                          "no se creó el cambio: modo no confirmado")
    plan = plan_ejemplo() if con_ejemplo else {}
    if plan:
        preparar_ejemplo(plan)
    # Tres caracteres al azar antes del sufijo: dos clones que crean un cambio en el mismo segundo con el mismo sufijo no
    # generan el mismo ID, y el ID sigue terminando en el sufijo.
    al_azar = "".join(random.choice("abcdefghijklmnopqrstuvwxyz0123456789") for _ in range(3))
    for carpeta_necesaria in (ROOT / "tareas", CHANGES, ROOT / estructura.DIR / "cambios"):  # un clon de un proyecto viejo
        carpeta_necesaria.mkdir(parents=True, exist_ok=True)
    p = ejecutar(["tasks", "new", titulo, "--sufijo", f"{al_azar}-{sufijo}", "--json", "--proyecto", str(ROOT)])
    if p.returncode:
        raise FactoryError(f"oracle-task no pudo crear la tarea: {p.stderr.strip()}. No reintentes con otro título sin revisar los archivos del ejemplo que ya se copiaron; no hubo una tarea confirmada.")
    try:
        identificador = json.loads(p.stdout)["id"]
    except (json.JSONDecodeError, KeyError) as e:
        raise FactoryError("oracle-task no devolvió el id completo de la tarea") from e
    carpeta = ruta_cambio(identificador)
    try:
        spec = carpeta / "specs" / capacidad / "spec.md"
        spec.parent.mkdir(parents=True, exist_ok=False)
        carpeta.mkdir(parents=True, exist_ok=True)
        (carpeta / "proposal.md").write_text(textos["propuesta"].format(titulo=titulo), encoding="utf-8")
        spec.write_text(textos["spec"].format(capacidad=capacidad), encoding="utf-8")
        (carpeta / "design.md").write_text(textos["diseno"], encoding="utf-8")
        (carpeta / "tasks.md").write_text(textos["tareas"], encoding="utf-8")
        estado = {
            "id": identificador, "titulo": titulo, "capacidad": capacidad,
            "fase": "espera_aprobacion_spec",
            "spec": str(spec.relative_to(ROOT)), "spec_sha256": None,
            "spec_aprobada": None, "requisitos": [], "revision": None, "oracle": None,
            "modo": modo, "eventos": [],
        }
        evento(estado, "cambio_creado", capacidad=capacidad)
        if con_ejemplo:
            (carpeta / 'proposal.md').write_bytes((ROOT / 'examples/notas/proposal.md').read_bytes())
            spec.write_bytes((ROOT / 'examples/notas/spec.md').read_bytes())
            estado['ejemplo'] = con_ejemplo
        guardar(carpeta, estado)
    except OSError as e:
        raise FactoryError(f'preparación incompleta de la tarea {identificador}: {e}. '
                           f'No crees otra tarea: recuperá este ID con tasks show {identificador}; '
                           f'revisá y completá los archivos en {carpeta}. Los destinos existentes no se sobrescriben al reintentar nuevo.') from e
    nota_tarea(identificador, f"OpenSpec: {carpeta.relative_to(ROOT)}. Modo de trabajo: {modo}. Estado de factory: espera aceptación de proposal.md y spec.md.")
    print(f"Cambio creado: {identificador}")
    print(f"Modo de trabajo: {modo}")
    print(f"Tarea: {ROOT / 'tareas' / identificador / 'TAREA.md'}")
    print(f"Propuesta/spec/tasks: {carpeta}")
    if con_ejemplo:
        print(f'Ejemplo y catálogos preparados en {ROOT / "examples/notas"} y {proyecto_oracle() / "catalogos"}. No se ejecutó el programa.')
    else:
        print('Completá los TODO antes de pedir aceptación.')
    print(f"Próximo paso humano: revisar {carpeta / 'proposal.md'} y {spec}")
    siguiente(identificador, 'espera_aprobacion_spec')
    return identificador


def abierto(identificador: str) -> tuple[Path, dict]:
    carpeta, estado = leer(identificador)
    if estado.get("fase") == "cerrada":
        raise FactoryError("el cambio ya está cerrado; creá una nueva tarea")
    if estado.get("fase") == "abandonada":
        raise FactoryError(f"el cambio está abandonado ({quien(estado.get('abandono'))}); lo que siga va en un cambio nuevo")
    return carpeta, estado


def documentos(carpeta: Path, estado: dict) -> dict[str, str]:
    return {str(p.relative_to(ROOT)): sha256(p.read_bytes())
            for p in (carpeta / "proposal.md", ROOT / estado["spec"])}


def exigir_spec(carpeta: Path, estado: dict) -> None:
    aprobacion = estado.get("spec_aprobada") or {}
    if not aprobacion:
        raise FactoryError("primero hay que aceptar la propuesta y la spec (aprobar-spec)")
    if aprobacion.get("documentos") != documentos(carpeta, estado):
        raise FactoryError("la propuesta/spec cambió o su aprobación es antigua; renová la aceptación")


def es_producto(nombre: str) -> bool:
    """Si un archivo (ruta relativa) cuenta en la huella del producto."""
    partes = Path(nombre).parts
    # Una spec consolidada que Factory generó (tiene índice) se deriva de specs ya aceptadas: no es producto nuevo, y si
    # contara, archivar los cambios anteriores vencería la revisión del último integrado. Las demás de openspec/specs/ sí cuentan.
    gestionada = (len(partes) == 4 and partes[:2] == ("openspec", "specs") and partes[3] == "spec.md"
                  and (ROOT / estructura.DIR / "specs" / f"{partes[2]}.json").is_file())
    # Las notas generadas de kb/ se derivan del registro y se rehacen con cada decisión: si contaran, cada decisión
    # vencería la revisión y el juicio. Las de personas (kb/notas/) sí son producto.
    generada = partes[:1] == (kb_mod.DIR,) and (partes[1:] == ("README.md",) or (len(partes) == 3 and partes[1] in ("cambios", "requisitos")))
    return not (partes[0] in ("tareas", estructura.DIR) or gestionada or generada
                or (len(partes) == 4 and partes[:2] == ("openspec", "changes")
                    and partes[-1] in {"factory.json", "review.md", "oracle-veredicto.txt"}))


def cambios_locales_de_producto() -> list[str]:
    """Archivos del producto modificados, en el índice o nuevos, sin commit."""
    locales = ejecutar(["git", "diff", "--name-only", "HEAD"]).stdout.splitlines()
    locales += ejecutar(["git", "ls-files", "--others", "--exclude-standard"]).stdout.splitlines()
    return [n for n in locales if es_producto(n)]


def candidatos_anteriores(identificador: str, sha: str | None) -> list[str]:
    """Los candidatos del cambio con informes de revisores, ancestros de HEAD y distintos de `sha`, del más viejo al más nuevo."""
    base = ROOT / estructura.DIR / "cambios" / identificador / "candidatos"
    if base.is_symlink() or not base.is_dir():
        return []
    con_informes = {p.name for p in base.iterdir() if p.is_dir() and not p.is_symlink() and any((p / "revision").glob("*.json"))}
    orden = [c[:7] for c in ejecutar(["git", "rev-list", "HEAD"]).stdout.split()]
    return [c for c in reversed(orden) if c in con_informes and c != sha]


def candidato_vigente(identificador: str) -> str | None:
    """El commit (7 caracteres) del candidato con carpeta propia más cercano a HEAD, si el producto no cambió desde él.

    La evidencia se produce sobre el commit de producto y se guarda en un commit posterior: ese commit no cambia el producto,
    así que el candidato sigue siendo el anterior.
    """
    base = ROOT / estructura.DIR / "cambios" / identificador / "candidatos"
    if base.is_symlink() or not base.is_dir():
        return None
    existentes = {p.name for p in base.iterdir() if p.is_dir() and not p.is_symlink()}
    # Un cambio de producto sin commit (modificado, en el índice o nuevo) también deja viejo a cualquier candidato.
    if cambios_locales_de_producto():
        return None
    for commit in ejecutar(["git", "rev-list", "HEAD"]).stdout.split():
        if commit[:7] in existentes:
            cambiados = ejecutar(["git", "diff", "--name-only", commit, "HEAD"]).stdout.splitlines()
            return None if any(es_producto(n) for n in cambiados) else commit[:7]
    return None


def hechos_del_candidato(identificador: str) -> Path:
    """`hechos.json` de la evidencia del candidato vigente; FactoryError con la ruta esperada si no está."""
    leer(identificador)
    sha = candidato_vigente(identificador) or ejecutar(["git", "rev-parse", "HEAD"]).stdout.strip()[:7]
    hechos = estructura.ruta_canonica(ROOT, identificador, "evidencia", sha) / "hechos.json"
    if not ruta_segura(hechos).is_file():
        raise FactoryError(f"no encuentro los hechos del candidato: {hechos.relative_to(ROOT)}. Generalos ahí "
                           f"(oracle-factory ruta {identificador} evidencia) o indicá --con RUTA")
    return hechos


def contexto_producto() -> dict:
    """Vincula revisión y juicio con HEAD y archivos no ignorados, incluidos los nuevos.

    Los registros generados del flujo no son código del producto; las specs y las
    medidas Oracle sí forman parte de lo revisado. No sigue enlaces simbólicos.
    """
    head = ejecutar(["git", "rev-parse", "--verify", "HEAD"])
    lista = ejecutar(["git", "ls-files", "-z", "--cached", "--others", "--exclude-standard"])
    if head.returncode or lista.returncode:
        raise FactoryError("la revisión necesita un repositorio Git con al menos un commit")
    archivos = []
    for nombre in sorted(set(lista.stdout.split("\0")) - {""}):
        if not es_producto(nombre):
            continue
        p = ROOT / nombre
        if p.is_symlink():
            dato = ["enlace", str(p.readlink())]
        elif p.is_file():
            dato = ["archivo", sha256(p.read_bytes()), bool(p.stat().st_mode & 0o111)]
        elif p.is_dir():
            raise FactoryError("los submódulos/directorios Git requieren revisión externa explícita: " + nombre)
        else:
            dato = ["ausente"]
        archivos.append([nombre, dato])
    return {"head": head.stdout.strip(), "archivos_sha256": sha256(json.dumps(archivos).encode())}


def ruta_del_registro(valor) -> Path | None:
    """Una ruta que guarda el registro (informe, decisiones, hechos), o None si no es texto: el criterio de donde."""
    return ROOT / valor if estructura._texto(valor) else None


NO_VALIDO = " no válido en el registro (no es una ruta de texto)"


def no_es_ruta(valor) -> bool:
    """Un campo presente que no es una ruta de texto, también 0, False, "", [] o {}; null es un campo ausente."""
    return valor is not None and ruta_del_registro(valor) is None


hechos_registrados = estructura.hechos_registrados


def comando_juzgar(ident: str, registrados: list[tuple]) -> str:
    """Repetir el juicio con los mismos archivos; uno que no es una ruta queda por completar (no se ofrece ejecutar)."""
    return f"oracle-factory juzgar {ident} " + " ".join(
        "--con " + (shlex.quote(ruta) if estructura._texto(ruta) else "RUTA_DE_LOS_HECHOS") for ruta, _ in registrados)


def juicio_vigente(oracle: dict, actual: dict | None) -> bool:
    """El juicio vale si sus hechos y su informe son los registrados y el producto es el que se juzgó."""
    def intacto(relativa, huella):
        ruta = ruta_del_registro(relativa)
        return ruta is not None and ruta.is_file() and sha256(ruta.read_bytes()) == huella
    return (actual is not None and all(intacto(ruta, huella) for ruta, huella in hechos_registrados(oracle))
            and intacto(oracle.get("informe"), oracle.get("informe_sha256")) and mismo_producto(oracle.get("contexto"), actual))


def mismo_producto(registrado: dict | None, actual: dict) -> bool:
    """Vigencia por contenido: el HEAD es un dato del registro, no una condición."""
    return bool(registrado) and registrado.get("archivos_sha256") == actual.get("archivos_sha256")


def corto(head) -> str:
    # El registro puede venir de un informe: tolera lo que no sea un commit en vez de romper estado y el cierre.
    return head[:7] if isinstance(head, str) and head else "desconocido"


def commits_registrados(estado: dict) -> list[str]:
    """Commit observado al registrar cada gate, siempre visible; el HEAD es un dato, no una condición."""
    lineas = [f"{etiqueta} sobre el commit {corto((estado[nombre].get('contexto') or {}).get('head'))}"
              for nombre, etiqueta in (("revision", "revisión registrada"), ("oracle", "veredicto Oracle registrado")) if estado.get(nombre)]
    preparado = (estado.get("revision") or {}).get("head_preparacion")
    if preparado:  # lo declara el informe; Factory no lo comprueba contra Git
        lineas[0] += f" (informe preparado en {corto(preparado)}, según el propio informe)"
    return lineas


HOOK_MARCA = "# oracle-factory: une cada commit con su cambio"
# Sin el intérprete (un .venv borrado) la llamada falla y el hook igual sigue: nunca impide un commit, tampoco
# encadenada en un hook ajeno con set -e.
LLAMADA_HOOK = ("{py} -c 'import sys; from oracle_factory.cli import main; sys.exit(main())' "
                'trailer "$1" >/dev/null 2>&1 || true')
# prepare-commit-msg pone el trailer a un mensaje que ya viene escrito (-m, -F, merge, amend); commit-msg, al que se
# escribe en el editor. Los dos llaman a lo mismo, y el trailer no se repite.
HOOKS = ("prepare-commit-msg", "commit-msg")
# Al integrar: el registro de un cambio se une con Factory, y lo generado se rehace después del merge.
ATRIBUTOS_MARCA = "# oracle-factory: une los registros de los cambios y rehace lo generado al integrar"
ATRIBUTOS = (".factory/cambios/*/factory.json merge=oracle-factory-registro",
             ".factory/resumen.md merge=oracle-factory-generado", "kb/README.md merge=oracle-factory-generado",
             "kb/cambios/*.md merge=oracle-factory-generado", "kb/requisitos/*.md merge=oracle-factory-generado")
LLAMADA_POST_MERGE = ("{py} -c 'import sys; from oracle_factory.cli import main; sys.exit(main())' "
                      "rehacer-generado || true")
# Un merge con conflictos termina con git commit, y ahí Git no corre post-merge: post-commit lo hace si fue un merge.
LLAMADA_POST_COMMIT = "git rev-parse -q --verify HEAD^2 >/dev/null && " + LLAMADA_POST_MERGE
# Lo que se rehace (y se commitea) después de integrar: nunca una nota de personas de kb/notas/.
GENERADO_KB = ("kb/README.md", "kb/cambios", "kb/requisitos")


def instalar_union() -> str:
    """Los drivers de merge (en la configuración del clon), sus atributos (en .gitattributes, versionado) y el post-merge
    que rehace lo generado. Un post-merge ajeno no se pisa."""
    py = shlex.quote(sys.executable)
    codigo = "'import sys; from oracle_factory.cli import main; sys.exit(main())'"
    for nombre, orden, que in (("oracle-factory-registro", "unir-registro %O %A %B %P", "une el registro de un cambio"),
                               ("oracle-factory-generado", "unir-generado %O %A %B %P", "deja lo generado para rehacerlo")):
        ejecutar(["git", "config", f"merge.{nombre}.name", f"Factory: {que}"])
        ejecutar(["git", "config", f"merge.{nombre}.driver", f"{py} -c {codigo} {orden}"])
    atributos = ROOT / ".gitattributes"
    actual = atributos.read_text(encoding="utf-8") if atributos.is_file() else ""
    presentes = {" ".join(linea.split()) for linea in actual.splitlines()}  # otro espaciado es la misma línea
    faltan = [linea for linea in ATRIBUTOS if linea not in presentes]
    if faltan:
        bloque = ([ATRIBUTOS_MARCA] if ATRIBUTOS_MARCA not in actual else []) + faltan
        atributos.write_text(actual + ("\n" if actual and not actual.endswith("\n") else "") + "\n".join(bloque) + "\n",
                             encoding="utf-8")
    p = ejecutar(["git", "rev-parse", "--git-path", "hooks"])
    avisos = []
    for nombre, llamada in (("post-merge", LLAMADA_POST_MERGE), ("post-commit", LLAMADA_POST_COMMIT)):
        hook = ROOT / p.stdout.strip() / nombre
        if hook.exists() and HOOK_MARCA not in hook.read_text(encoding="utf-8", errors="replace"):
            avisos.append(f"Aviso: ya hay un hook {hook} que no es de Factory; no lo toqué. Para que lo generado se rehaga al "
                          f"integrar, agregale esta línea antes de su final:\n{llamada.format(py=py)}")
            continue
        hook.parent.mkdir(parents=True, exist_ok=True)
        hook.write_text(f"#!/bin/sh\n{HOOK_MARCA} (rehace lo generado después de integrar). Lo instaló oracle-factory hooks.\n"
                        f"{llamada.format(py=py)}\nexit 0\n", encoding="utf-8")
        hook.chmod(0o755)
    if avisos:
        return "\n".join(avisos)
    return ("Al integrar, el registro de un cambio editado en dos ramas se une con Factory (sin perder eventos) y lo generado "
            "se rehace después del merge (.gitattributes, post-merge y post-commit).")


def unir_registro(base: str, nuestro: str, suyo: str) -> int:
    """El merge driver del registro: Git pasa la versión común (%O), la de la rama actual (%A, donde va el resultado) y
    la de la otra (%B). Un registro que no se puede leer queda como conflicto para una persona."""
    try:
        leidos = [json.loads(Path(x).read_text(encoding="utf-8") or "{}") for x in (base, nuestro, suyo)]
    except (OSError, ValueError):
        return 1
    unido = unir_mod.unir(*leidos)
    Path(nuestro).write_text(json.dumps(unido, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return 0


def rehacer_generado() -> None:
    """Lo llama el post-merge: rehace resumen.md y kb/ y, si cambiaron, los commitea aparte."""
    if not (ROOT / estructura.DIR).is_dir():
        return
    escribir_atomico(ruta_resumen(), texto_resumen().encode("utf-8"))
    if (ROOT / kb_mod.DIR).is_dir():
        notas = kb_mod.armar(sys.modules[__name__])
        escribir_kb(notas)
        for rel in generadas_en_disco() - set(notas):
            (ROOT / rel).unlink()
    rutas = [str(ruta_resumen().relative_to(ROOT))] + [r for r in GENERADO_KB if (ROOT / r).exists()]
    if ejecutar(["git", "status", "--porcelain", "--", *rutas]).stdout.strip():
        # Dentro del post-merge Git todavía tiene MERGE_HEAD y no deja commitear rutas sueltas: el commit se arma a mano,
        # con el índice que dejó el merge más lo rehecho, y con un solo padre.
        ejecutar(["git", "add", "-A", "--", *rutas])
        arbol = ejecutar(["git", "write-tree"]).stdout.strip()
        hecho = ejecutar(["git", "commit-tree", arbol, "-p", "HEAD", "-m", "Rehacer lo generado después de integrar (oracle-factory)"])
        if hecho.returncode or ejecutar(["git", "update-ref", "HEAD", hecho.stdout.strip()]).returncode:
            raise FactoryError(f"no pude commitear lo rehecho después de integrar: {(hecho.stderr or '').strip()}")
        print("Rehice resumen.md y kb/ después de integrar, en un commit aparte.")


def decidir_union(identificador: str, campo: str, cual: str) -> None:
    """Una persona elige cuál de las dos versiones vale de algo que dos ramas decidieron distinto (también en un cambio
    cerrado: dos cierres se eligen acá)."""
    carpeta, estado = leer(identificador)
    pendiente = next((x for x in estado.get("pendientes_de_union") or [] if x.get("campo") == campo), None)
    if pendiente is None:
        raise FactoryError(f"{identificador} no tiene nada pendiente de unir en {campo}; no cambié nada")
    valor = pendiente[cual]
    confirmar_persona((f"¿Vale la versión {cual} de {campo} en {identificador}?",
                       f"Sí, la {cual}: {json.dumps(valor, ensure_ascii=False)[:120]}", "queda esa y se borra el aviso"),
                      "no elegí nada")
    destino, camino = estado, pendiente.get("camino") or campo.split(".")
    for k in camino[:-1]:
        destino = destino.setdefault(k, {})
    if valor is None:
        destino.pop(camino[-1], None)
    else:
        destino[camino[-1]] = valor
    estado["pendientes_de_union"] = [x for x in estado["pendientes_de_union"] if x is not pendiente]
    if not estado["pendientes_de_union"]:
        estado.pop("pendientes_de_union")
    evento(estado, "union_decidida", campo=campo, eligio=cual)
    guardar(carpeta, estado)
    print(f"En {identificador}, {campo} quedó con la versión {cual}.")


def aviso_union(identificador: str, estado: dict) -> list[str]:
    return [f"al unir dos ramas, {x.get('campo')} quedó con dos valores ({json.dumps(x.get('nuestro'), ensure_ascii=False)[:80]} y "
            f"{json.dumps(x.get('suyo'), ensure_ascii=False)[:80]}); Factory no eligió: "
            f"{unir_mod.como_resolver(x.get('campo', ''), identificador)}" for x in estado.get("pendientes_de_union") or []]


def instalar_hook() -> str:
    """Instala los hooks de Factory en la carpeta de hooks de Git (la comparten los worktrees); nunca pisa uno ajeno."""
    p = ejecutar(["git", "rev-parse", "--git-path", "hooks"])
    if p.returncode:
        return ("Hook de commits: este proyecto todavía no usa Git; después de git init, instalalo con "
                "oracle-factory hooks.")
    carpeta = ROOT / p.stdout.strip()
    llamada = LLAMADA_HOOK.format(py=shlex.quote(sys.executable))
    # Con un hook ajeno, en cualquiera de los dos, Factory no pone ninguno (y saca el suyo): la persona decide si
    # encadena la línea en el suyo.
    ajenos = [carpeta / n for n in HOOKS if (carpeta / n).exists()
              and HOOK_MARCA not in (carpeta / n).read_text(encoding="utf-8", errors="replace")]
    if ajenos:
        for nombre in HOOKS:
            if carpeta / nombre not in ajenos and (carpeta / nombre).exists():
                (carpeta / nombre).unlink()
        return "\n".join(f"Aviso: ya hay un hook {hook} que no es de Factory; no lo toqué ni instalé los de Factory. Para "
                         f"que tus commits digan de qué cambio son, agregale esta línea antes de su final:\n{llamada}"
                         for hook in ajenos)
    instalados = []
    for nombre in HOOKS:
        hook = carpeta / nombre
        hook.parent.mkdir(parents=True, exist_ok=True)
        hook.write_text(f"#!/bin/sh\n{HOOK_MARCA} (trailer «Cambio: ID»). Lo instaló oracle-factory hooks; nunca "
                        f"impide un commit.\n{llamada}\nexit 0\n", encoding="utf-8")
        hook.chmod(0o755)
        instalados.append(nombre)
    return (f"Hook de commits en {carpeta} ({', '.join(instalados)}): un commit hecho con un solo cambio abierto lleva "
            "«Cambio: ID».")


@reintentar_si_cambia
def tomar(identificador: str, con: list[str] | None = None, relevo: bool = False) -> None:
    """Una persona se registra como responsable del cambio (con sus agentes); un agente se suma al cambio."""
    carpeta, estado = abierto(identificador)
    quien_actua = actor()
    if quien_actua["tipo_actor"] == "sin_identificar":
        raise FactoryError("tomar un cambio lo hace una persona desde su terminal, o un agente que se suma con "
                           "--agente NOMBRE; la entrada por pipe no identifica a nadie")
    if quien_actua["tipo_actor"] == "agente":
        evento(estado, "agente_sumado", forma="registro", agente=AGENTE)
        guardar(carpeta, estado)
        print(f"{AGENTE} quedó como agente de {identificador}; responsable: "
              f"{(estado.get('responsable') or {}).get('persona') or 'nadie todavía'}.")
        return
    persona, previo = quien_actua["actor"], estado.get("responsable") or {}
    if previo.get("persona") and previo["persona"] != persona and not relevo:
        raise FactoryError(f"{identificador} lo tiene {previo['persona']} desde {previo.get('desde', '')[:16].replace('T', ' ')}; "
                           f"acordalo con esa persona y tomalo con oracle-factory tomar {identificador} --relevo. No cambié nada")
    agentes = sorted(set(con or []))
    estado["responsable"] = {"persona": persona, "desde": ahora(), "con": agentes}
    datos = {"con": agentes, **({"relevo_de": previo["persona"]} if previo.get("persona") and previo["persona"] != persona else {})}
    evento(estado, "tomado", forma="registro", **datos)
    guardar(carpeta, estado)
    print(f"{persona} tiene {identificador}" + (f", con {', '.join(agentes)}" if agentes else "")
          + (f" (relevo de {datos['relevo_de']})" if "relevo_de" in datos else "") + ".")


@reintentar_si_cambia
def soltar(identificador: str) -> None:
    carpeta, estado = abierto(identificador)
    previo = (estado.get("responsable") or {}).get("persona")
    if not previo:
        print(f"{identificador} no tiene responsable; no cambié nada.")
        return
    if actor()["tipo_actor"] != "persona" or actor()["actor"] != previo:
        raise FactoryError(f"{identificador} lo tiene {previo}: lo suelta esa persona desde su terminal, o otra lo toma "
                           f"con --relevo. No cambié nada")
    estado["responsable"] = None
    evento(estado, "soltado", forma="registro")
    guardar(carpeta, estado)
    print(f"{previo} soltó {identificador}; queda sin responsable.")


@reintentar_si_cambia
def mensaje(identificador: str, texto: str, de: str | None = None) -> None:
    """Un mensaje en el registro del cambio. Sin --de, lo firma el actor de siempre (persona con terminal o agente);
    --de lo usa la extensión de VS Code para un mensaje que llegó por Live Share, con el nombre que da Live Share."""
    carpeta, estado = abierto(identificador)
    texto = (texto or "").strip()
    if not texto or len(texto) > 2000:
        raise FactoryError("el mensaje tiene que tener texto y hasta 2000 caracteres; no guardé nada")
    if de is not None:
        de = de.strip()
        if AGENTE or not de or len(de) > 100:
            raise FactoryError("--de es para la extensión de VS Code (un mensaje de Live Share, con un nombre de hasta "
                               "100 caracteres) y no se combina con --agente; no guardé nada")
        # Factory no autentica a nadie: el nombre es el que dio Live Share al anfitrión, y queda quién lo guardó.
        guardado_por = subprocess.run(["git", "config", "user.name"], cwd=ROOT, capture_output=True, text=True).stdout.strip()
        evento(estado, "mensaje", forma="mensaje", texto=texto, actor=de, tipo_actor="persona", via="live-share",
               guardado_por=guardado_por or getpass.getuser())
    else:
        if actor()["tipo_actor"] == "sin_identificar":
            raise FactoryError("un mensaje lo escribe una persona desde su terminal o un agente con --agente NOMBRE; "
                               "la entrada por pipe no identifica a nadie. No guardé nada")
        evento(estado, "mensaje", forma="mensaje", texto=texto)
    guardar(carpeta, estado)
    print(f"Mensaje guardado en {identificador}.")


ACTIVIDAD_RECIENTE = dt.timedelta(hours=24)


def quien_del_cambio(estado: dict) -> dict:
    """Quién trabaja en el cambio, sólo con su registro: la persona responsable, sus agentes (declarados, sumados o
    que actuaron en las últimas 24 horas, con su última acción) y los revisores lanzados sin resultado."""
    responsable = estado.get("responsable") or None
    eventos = estado.get("eventos") or []
    hoy = dt.datetime.now(dt.timezone.utc)
    declarados = set((responsable or {}).get("con") or [])
    declarados |= {e.get("agente") for e in eventos if e.get("accion") == "agente_sumado" and e.get("agente")}
    ultimas: dict[str, dict] = {}
    for e in eventos:  # una migración de registros (limpiar rutas, archivar viejos) no es trabajar en el cambio
        if e.get("tipo_actor") == "agente" and e.get("actor") and e.get("forma") != "migracion":
            ultimas[e["actor"]] = e
    agentes = []
    for nombre in sorted(declarados | set(ultimas)):
        ultima = ultimas.get(nombre)
        try:
            cuando = dt.datetime.fromisoformat(ultima["cuando"]) if ultima else None
        except (KeyError, TypeError, ValueError):
            cuando = None
        if cuando and cuando.tzinfo is None:
            cuando = cuando.replace(tzinfo=dt.timezone.utc)  # un registro viejo sin zona: Factory escribe en UTC
        # Una fecha futura (otro reloj) no es «hace poco»: cuenta hasta cinco minutos de diferencia.
        reciente = bool(cuando) and hoy - ACTIVIDAD_RECIENTE <= cuando <= hoy + dt.timedelta(minutes=5)
        if nombre in declarados or reciente:
            agentes.append({"nombre": nombre, "declarado": nombre in declarados,
                            "ultima_accion": (ultima or {}).get("accion"), "cuando": (ultima or {}).get("cuando")})
    return {"responsable": responsable, "agentes": agentes,
            "revisores_en_curso": [{"revisor": e.get("revisor"), "candidato": e.get("candidato"), "cuando": e.get("cuando")}
                                   for e in lanzamientos_abiertos(estado)],
            "ultima_actividad": ({k: eventos[-1].get(k) for k in ("actor", "tipo_actor", "accion", "cuando")}
                                 if eventos else None)}


def linea_quien(q: dict) -> str:
    r = q["responsable"]
    partes = [f"Responsable: {r['persona']} desde {str(r.get('desde', ''))[:16].replace('T', ' ')}" if r
              else "Responsable: nadie (oracle-factory tomar ID)"]
    if q["agentes"]:
        partes.append("agentes: " + ", ".join(
            a["nombre"] + (f" ({a['ultima_accion']} {str(a['cuando'])[:16].replace('T', ' ')})" if a["ultima_accion"] else "")
            for a in q["agentes"]))
    if q["revisores_en_curso"]:
        partes.append("revisando: " + ", ".join(f"{v['revisor']} sobre {v['candidato']}" for v in q["revisores_en_curso"]))
    return "; ".join(partes)


def cambios_abiertos() -> list[str]:
    if not CHANGES.is_dir():
        return []
    return [c.name for c in sorted(CHANGES.iterdir()) if ID_RE.fullmatch(c.name) and ruta_registro(c).exists()
            and leer(c.name)[1].get("fase") not in ("cerrada", "abandonada")]


def cambio_del_commit(mensaje: str) -> str | None:
    """El cambio de un commit: el que nombra su mensaje (si nombra uno solo del proyecto); si no, el único abierto; con
    varios abiertos, el único que tiene como responsable a quien commitea (su user.name de Git). Si no, ninguno."""
    nombrados = {i for i in re.findall(r"\b\d{8}-\d{6}-[a-z0-9_]+(?:-[a-z0-9_]+)*", mensaje)
                 if (CHANGES / i).is_dir() and ruta_registro(CHANGES / i).exists()}
    if nombrados:
        return nombrados.pop() if len(nombrados) == 1 else None
    abiertos = cambios_abiertos()
    if len(abiertos) == 1:
        return abiertos[0]
    yo = subprocess.run(["git", "config", "user.name"], cwd=ROOT, capture_output=True, text=True).stdout.strip()
    mios = [i for i in abiertos if yo and (leer(i)[1].get("responsable") or {}).get("persona") == yo]
    return mios[0] if len(mios) == 1 else None


def poner_trailer(archivo: str) -> None:
    """Lo llama el hook: agrega «Cambio: ID» al mensaje si no lo tiene, con el cambio que elige cambio_del_commit."""
    # Un mensaje todavía vacío (sólo comentarios, con el carácter de comentario que use este Git): se deja así, para
    # que cerrar el editor sin escribir siga abortando el commit; commit-msg lo completa después.
    vacio = subprocess.run(["git", "stripspace", "--strip-comments"], cwd=ROOT, input=Path(archivo).read_bytes(),
                           capture_output=True, check=False)
    if vacio.returncode or not vacio.stdout.strip():
        return
    # Sólo cuenta un Cambio: del bloque de trailers, no una línea del cuerpo que empiece igual.
    trailers = ejecutar(["git", "interpret-trailers", "--parse", archivo]).stdout
    if re.search(r"^Cambio:", trailers, re.M | re.I):
        return
    cambio = cambio_del_commit(vacio.stdout.decode("utf-8", errors="replace"))
    if cambio:
        ejecutar(["git", "interpret-trailers", "--in-place", "--trailer", f"Cambio: {cambio}", archivo])


def commits_del_cambio(identificador: str, estado: dict) -> list[dict]:
    """Los commits del cambio, del más nuevo al más viejo: los que llevan su trailer y los deducidos de sus candidatos y
    del merge que los integró (para lo de antes del trailer)."""
    formato = "--format=%H%x1f%an%x1f%aI%x1f%cI%x1f%s"  # la fecha de autor y la de cuando se hizo el commit

    def git_log(*args: str) -> list[list[str]]:
        p = ejecutar(["git", "log", formato, *args])
        return [] if p.returncode else [linea.split("\x1f") for linea in p.stdout.splitlines() if linea.count("\x1f") == 4]

    def completo(ref: str) -> str | None:
        p = ejecutar(["git", "rev-parse", "--verify", "--quiet", ref + "^{commit}"])
        return p.stdout.strip() if p.returncode == 0 else None

    base = ROOT / estructura.DIR / "cambios" / identificador / "candidatos"
    carpetas = {c.name: c for c in base.iterdir() if c.is_dir() and not c.is_symlink()} if base.is_dir() else {}
    pedidos = {e.get("candidato") for e in estado.get("eventos") or [] if e.get("candidato")}  # pedidos, no informes
    candidatos = {}  # sha completo -> nombre corto
    for corto_ in sorted(set(carpetas) | pedidos):
        sha = completo(str(corto_))
        if sha:
            candidatos[sha] = str(corto_)
    # --grep encuentra la línea en cualquier parte del mensaje; cuenta sólo si está en el bloque de trailers.
    con_trailer = set(ejecutar(["git", "log", "--all", f"--grep=^Cambio: {identificador}$",
                                "--format=%H %(trailers:key=Cambio,valueonly,separator=%x20)"]).stdout.splitlines())
    propios = {linea.split()[0] for linea in con_trailer if identificador in linea.split()[1:]}
    unidos = {c[0]: (c, "trailer") for c in git_log(*propios, "--no-walk")} if propios else {}
    deducidos = git_log("--no-walk", *candidatos) if candidatos else []
    # El merge que integró la rama, en un cambio cerrado (uno abierto no se integró: no se busca): el primer commit de
    # la línea principal (primeros padres de main, master o HEAD) que contiene un candidato. Si lo trae por su segundo
    # padre, es el merge que integró la rama; si lo trae por el primero, el cambio ya estaba en main sin merge propio
    # (directo, fast-forward, squash) y quedan sólo los candidatos. Un merge de otras ramas nunca está en esa línea.
    principal = next((r for r in ("main", "master") if completo(r)), "HEAD")

    def contiene(ref: str, sha: str) -> bool:
        return ejecutar(["git", "merge-base", "--is-ancestor", sha, ref]).returncode == 0

    for sha in candidatos if estado.get("fase") == "cerrada" else ():
        if not contiene(principal, sha):
            continue  # un candidato de una vuelta descartada: no está en la historia
        merge = next((m for m in ejecutar(["git", "rev-list", "--first-parent", "--merges", "--reverse",
                                           f"{sha}..{principal}"]).stdout.split() if contiene(m, sha)), None)
        if merge and not contiene(merge + "^1", sha):
            deducidos += git_log(f"{merge}^1..{merge}^2")
        break
    for c in deducidos:
        unidos.setdefault(c[0], (c, "deducido"))
    salida = []
    for sha, ((_, autor, fecha, fecha_commit, asunto), union) in unidos.items():
        carpeta = carpetas.get(candidatos.get(sha, ""))
        revisado = bool(carpeta and any((carpeta / "revision").glob("*.json")))  # con un informe, no sólo pedido
        salida.append({"sha": sha, "corto": sha[:7], "autor": autor, "fecha": fecha, "fecha_commit": fecha_commit,
                       "asunto": asunto, "union": union,
                       "candidato": sha in candidatos, "revisado": revisado,
                       "evidencia": bool(carpeta and (carpeta / "evidencia").is_dir())})
    return sorted(salida, key=lambda c: dt.datetime.fromisoformat(c["fecha"]), reverse=True)


def linea_commits(commits: list[dict]) -> str:
    if not commits:
        return "Commits: ninguno unido todavía (los nuevos llevan «Cambio: ID» con el hook de oracle-factory hooks)"
    return f"Commits: {len(commits)}; el último {commits[0]['corto']} «{commits[0]['asunto']}» (oracle-factory log para verlos)"


def comando_log(identificador: str, como_json: bool) -> None:
    _, estado = leer(identificador)
    commits = commits_del_cambio(identificador, estado)
    if como_json:
        imprimir_json({"esquema": "oracle-factory.log/1", "id": identificador, "commits": commits})
        return
    print(f"{identificador} — {estado.get('titulo', '')}")
    for c in commits:
        marcas = [c["union"]] + [m for m in ("candidato", "revisado", "evidencia") if c[m]]
        print(f"{c['corto']}  {c['fecha'][:10]}  {c['autor']}  {c['asunto']}  [{', '.join(marcas)}]")
    if not commits:
        print(linea_commits(commits) + ".")


def avisos_head(estado: dict) -> list[str]:
    """Registros vigentes cuyo HEAD no es el actual: producto idéntico, otra historia."""
    try:
        actual = contexto_producto()
    except (FactoryError, OSError):
        return []
    avisos = []
    for nombre, etiqueta in (("revision", "revisión registrada"), ("oracle", "veredicto Oracle registrado")):
        registro = estado.get(nombre) or {}
        contexto = registro.get("contexto") or {}
        if mismo_producto(contexto, actual) and contexto.get("head") != actual["head"]:
            avisos.append(f"{etiqueta} en {corto(contexto.get('head'))}; HEAD actual {corto(actual['head'])} con el producto idéntico")
    return avisos


def requisitos_verdes(salida: str, requisitos: list[str]) -> bool:
    # Oracle 0.38.1 puede salir con 0 ante «sin juicio» o fallas en sombra.
    # Exigimos la fila exacta de cada requisito con marca ✓; no coincidencias parciales.
    filas = {}
    for linea in salida.splitlines():
        m = re.match(r"^([✓◐·✗?])\s+([a-z][a-z0-9_.]*)\s+", linea)
        if m:
            filas.setdefault(m[2], []).append(m[1])
    return bool(requisitos) and all(filas.get(rid) == ["✓"] for rid in requisitos)


def specs_de_otra_capacidad(carpeta: Path, estado: dict) -> list[str]:
    """Specs del cambio que no son la de su capacidad, a cualquier profundidad de specs/: Factory importa una sola, así
    que las otras se perderían. Se comparan por ruta, no por destino: un enlace a la propia también es otra spec."""
    return sorted(rel for p in (carpeta / "specs").rglob("spec.md") if (rel := p.relative_to(ROOT).as_posix()) != estado["spec"])


def exigir_plantilla_completa(archivos) -> None:
    """Falla, diciendo de cada archivo qué falta, si alguno no existe o todavía tiene la marca de pendiente de la plantilla."""
    pendientes, faltan = [], []
    for archivo in archivos:
        ruta_segura(archivo)  # ni un enlace ni una salida del proyecto: no se lee lo que está afuera
        ruta = archivo.relative_to(ROOT)
        if not archivo.is_file():
            faltan.append(str(ruta))
            continue
        try:
            texto = archivo.read_text(encoding="utf-8")
        except UnicodeDecodeError as e:
            raise FactoryError(f"{ruta} no está en UTF-8 (byte inválido en la posición {e.start}); guardalo en UTF-8 y aprobá de nuevo") from e
        con_marca = [(n, linea.strip()) for n, linea in enumerate(texto.splitlines(), 1) if "TODO:" in linea]
        if con_marca:
            n, linea = con_marca[0]
            linea = linea if len(linea) <= 80 else linea[:80] + "…"
            resto = len(con_marca) - 1
            resto = f"; {'queda' if resto == 1 else 'quedan'} {resto} más" if resto else ""
            pendientes.append(f"{ruta} (línea {n}: «{linea}»{resto})")
    if pendientes or faltan:
        partes = ([f"hay que completar y revisar primero: {'; '.join(pendientes)}"] if pendientes else []) \
            + ([f"{'falta el archivo' if len(faltan) == 1 else 'faltan los archivos'} {', '.join(faltan)}"] if faltan else [])
        raise FactoryError("; ".join(partes))


def aprobar_spec(identificador: str) -> None:
    carpeta, estado = abierto(identificador)
    spec = ROOT / estado["spec"]
    otras = specs_de_otra_capacidad(carpeta, estado)
    if otras:
        raise FactoryError(f"este cambio es de la capacidad {estado['capacidad']} y Factory importa sólo su spec ({estado['spec']}); "
                           f"{', '.join(otras)} no se importaría. Pasá sus requisitos a esa spec o sacala, y aprobá de nuevo")
    exigir_plantilla_completa((carpeta / "proposal.md", spec, carpeta / "tasks.md"))
    contenido = spec.read_text(encoding="utf-8")
    if not re.search(r"(?m)^### Requirement:", contenido) or not re.search(r"(?m)^#### Scenario:", contenido):
        raise FactoryError("la spec debe tener al menos un Requirement y un Scenario de OpenSpec")
    huellas = documentos(carpeta, estado)
    for archivo, huella in huellas.items():
        print(f"{archivo} (SHA-256 {huella})\n{(ROOT / archivo).read_text(encoding='utf-8')}")
    print(f"Modo de trabajo: {modo_de(estado)}. Aceptar reinicia importación, revisión y veredicto de este cambio.")
    try:
        tipos = list(modos.tipos_spec(contenido).values())
    except modos.TipoInvalido as e:
        raise FactoryError(str(e)) from e
    forma = decidir(estado, "spec", tipos, huellas, (f"Aprobar la propuesta y la spec de {identificador}", "Aprobar",
                    "reinicia importación, revisión y veredicto de este cambio"),
                    "aprobación cancelada; no cambié el estado", lambda e: guardar(carpeta, e))
    if forma is None:
        return
    if documentos(carpeta, estado) != huellas:
        raise FactoryError("los documentos cambiaron durante la aprobación; volvé a revisarlos")
    estado["spec_sha256"] = huellas[estado["spec"]]
    estado["spec_aprobada"] = {**registro_decision(estado, forma), "documentos": huellas}
    # importar concilia medidas y propuestas por id: la misma spec conserva sus ids y sus registros.
    estado.update(requisitos=[], tipos={}, revision=None, oracle=None, fase="spec_aprobada")
    (estado.get("propuestas") or {}).pop("revision", None)
    evento(estado, "spec_aprobada", forma=forma, documentos=huellas)
    guardar(carpeta, estado)
    nota_tarea(identificador, f"{quien(estado['spec_aprobada'])} aceptó propuesta y spec {estado['spec']}; se reiniciaron las validaciones dependientes.")
    print("Alcance aprobado; sus requisitos todavía deben importarse y medirse.")
    siguiente(identificador, estado["fase"])

def fuente_relativa(ruta: Path) -> None:
    """Oracle escribe la fuente con la ruta de esta máquina; en el repositorio va relativa al proyecto."""
    if not ruta.is_file():
        return
    texto = ruta.read_text(encoding="utf-8")
    # Oracle escapa las comillas y las barras invertidas de la ruta: se reconocen las dos formas.
    relativa = texto
    for prefijo in {str(ROOT), json.dumps(str(ROOT))[1:-1]}:
        relativa = relativa.replace(f'fuente "{prefijo}/', 'fuente "')
    if relativa != texto:
        ruta.write_text(relativa, encoding="utf-8")
    if re.search(r'(?m)^\s*fuente "/', relativa):
        print(f"Aviso: no pude hacer relativa la fuente de {ruta.name}; conserva una ruta absoluta de esta máquina.", file=sys.stderr)


def importar(identificador: str) -> None:
    carpeta, estado = abierto(identificador)
    exigir_spec(carpeta, estado)
    spec = ROOT / estado["spec"]
    # Oracle preserva requisitos existentes. Aislamos cada tarea y versión de spec
    # para que una promesa nueva no herede medidas de una promesa anterior.
    version = sha256((identificador + ":" + estado["spec_sha256"]).encode())[:16]
    dominio = estado["capacidad"].replace("-", "_") + "_c" + version
    try:
        tipos = modos.tipos_spec(spec.read_text(encoding="utf-8"), obligatorios=config_proyecto()["tipos_obligatorios"])
    except modos.TipoInvalido as e:
        raise FactoryError(f"{e}. No se modificó el registro.") from e
    estado.update(requisitos=[], revision=None, oracle=None, fase="importacion_pendiente")
    guardar(carpeta, estado)
    p = ejecutar(["oracle", "requisito", "importar", str(spec), "--dominio", dominio, "--escribir", "--proyecto", str(proyecto_oracle())])
    sys.stdout.write(p.stdout)
    if p.returncode:
        raise FactoryError(p.stderr.strip() or "Oracle no pudo importar los requisitos")
    ids = sorted(set(re.findall(r"(?m)^[+=]\s+([a-z][a-z0-9_.]*)", p.stdout)))
    if not ids:
        raise FactoryError("Oracle no devolvió ids; no doy la importación por confirmada")
    # El importador de Oracle no distingue las secciones del delta: lo que la spec retira no se importa ni se mide.
    retirados = {modos.slug(nombre) for op, nombre, _ in archivo.bloques(spec.read_text(encoding="utf-8")) if op == "REMOVED"}
    for rid in [i for i in ids if i.split(".", 1)[1] in retirados]:
        (requisitos_dir() / f"{rid}.requisito").unlink(missing_ok=True)  # el dominio es propio de este cambio
        ids.remove(rid)
    exigir_spec(carpeta, estado)
    sin_tipo = [i for i in ids if i.split(".", 1)[1] not in tipos]
    if sin_tipo:
        raise FactoryError("no pude asociar el tipo de estos requisitos a la spec: " + ", ".join(sin_tipo))
    for rid in ids:
        fuente_relativa(requisitos_dir() / f"{rid}.requisito")
    # Una importación anterior de este cambio (otra versión de la spec, con otro dominio): sus requisitos ya no son
    # promesas del cambio. El dominio es propio de este cambio, así que no se toca el de otro.
    anteriores = sorted({i for e in estado.get("eventos") or [] if e.get("accion") == "requisitos_importados"
                         for i in e.get("ids") or []} - set(ids))
    quitados = [rid for rid in anteriores if (requisitos_dir() / f"{rid}.requisito").is_file()]
    for rid in quitados:
        (requisitos_dir() / f"{rid}.requisito").unlink()
    if quitados:
        print("Quité de requisitos/ los de la importación anterior de este cambio: " + ", ".join(quitados))
    estado["requisitos"] = ids
    estado["tipos"] = {i: tipos[i.split(".", 1)[1]] for i in ids}
    for clave in ("medidas", "medidas_pendientes"):
        estado[clave] = {rid: v for rid, v in (estado.get(clave) or {}).items() if rid in ids}
    estado["fase"] = "requisitos_importados"
    evento(estado, "requisitos_importados", ids=ids)
    guardar(carpeta, estado)
    nota_tarea(identificador, "Requisitos importados: " + ", ".join(f"{i} ({estado['tipos'][i]})" for i in ids) + ". Los nuevos nacen SIN MEDIR; verificá cobertura antes del juicio.")
    print("La persona debe revisar medidas y límites de cada requisito.")
    siguiente(identificador, estado["fase"])

def tipos_cambio(estado: dict) -> list[str]:
    if estado.get("tipos"):
        return list(estado["tipos"].values())
    try:
        return list(modos.tipos_spec((ROOT / estado["spec"]).read_text(encoding="utf-8")).values())
    except modos.TipoInvalido as e:
        raise FactoryError(str(e)) from e


def firma_revision(formato, informe_sha, decisiones_sha, revisor, decision, contexto) -> dict:
    # ponytail: la revisión afecta a todo el cambio; si un hallazgo nombrara su requisito, se podría decidir por tipo.
    return {"formato": formato, "informe_sha256": informe_sha, "decisiones_sha256": decisiones_sha,
            "revisor": revisor, "decision": decision, "producto": contexto["archivos_sha256"]}


def juzgar(identificador: str, hechos: Path | list[Path]) -> None:
    """Juzga con los hechos de uno o varios sensores (un archivo por sensor, `--con` repetido)."""
    hechos = [hechos] if isinstance(hechos, Path) else list(hechos)
    carpeta, estado = abierto(identificador)
    try:  # escalares sin declarar o que no cargan: su causa antes que nada; lo demás lo dicen las comprobaciones que siguen
        catalogo_del_proyecto()
    except (OSError, ValueError):
        pass
    if estado.get("medidas_pendientes"):
        raise FactoryError("hay medidas sin confirmar por una persona; no cuentan para el juicio: "
                           + ", ".join(estado["medidas_pendientes"]))
    if medidas_sin_decision(estado):
        raise FactoryError("hay medidas sin una decisión vigente; no cuentan para el juicio: "
                           + "; ".join(f"{rid} ({motivo})" for rid, motivo in medidas_sin_decision(estado)))
    # Una corrida fallida nunca debe dejar disponible el verde de la anterior.
    estado.update(oracle=None, fase="juicio_pendiente")
    guardar(carpeta, estado)
    exigir_spec(carpeta, estado)
    if not estado.get("requisitos"):
        raise FactoryError("importá primero los requisitos de la spec aprobada")
    hechos = [h.resolve() for h in hechos]
    rutas = []
    for archivo in hechos:
        if not archivo.is_file():
            raise FactoryError(f"no encuentro los hechos del sensor: {archivo}")
        # Con ruta relativa al proyecto, el registro vale en cualquier clon; fuera de él, sólo en esta máquina.
        try:
            rutas.append(archivo.relative_to(ROOT).as_posix())
        except ValueError:
            rutas.append(str(archivo))
            print(f"Aviso: los hechos están fuera del proyecto ({archivo}); otra máquina no podrá verificarlos. "
                  "Guardalos dentro de tareas/ para que viajen con el repositorio.", file=sys.stderr)
        else:
            if ejecutar(["git", "check-ignore", "-q", str(archivo)]).returncode == 0:
                print(f"Aviso: los hechos ({rutas[-1]}) están ignorados por Git y no viajan con el repositorio; otra máquina "
                      "no podrá verificarlos. Guardalos fuera de las carpetas ignoradas, por ejemplo en tareas/.", file=sys.stderr)
    contexto = contexto_producto()
    huellas = [sha256(archivo.read_bytes()) for archivo in hechos]
    huella = huellas[0]
    cobertura = ejecutar(["oracle", "cobertura", "--proyecto", str(proyecto_oracle()), *con_escalares()])
    if cobertura.returncode or not requisitos_verdes(cobertura.stdout, estado["requisitos"]):
        detalle = (cobertura.stderr or cobertura.stdout).strip() if cobertura.returncode else ""
        faltan = sin_medir_con_medidas(estado)
        raise FactoryError("Oracle todavía no tiene cobertura completa de cada requisito importado"
                           + (f": {detalle[:500]}" if detalle else "")
                           + (f". Todavía dicen «sin medir»: {', '.join(faltan)} (proponé sus medidas con --quitar-sin-medir)"
                              if faltan else ""))
    p = ejecutar(["oracle", "cobertura", *(a for archivo in hechos for a in ("--con", str(archivo))),
                  "--proyecto", str(proyecto_oracle()), *con_escalares()])
    sys.stdout.write(p.stdout)
    if p.stderr:
        sys.stderr.write(p.stderr)
    # Sin ninguna fila de requisito, Oracle no juzgó (por ejemplo, dos sensores con la misma relación): no hay veredicto.
    if not any(re.search(r"^[✓◐·✗?]\s+" + re.escape(rid) + r"\s", p.stdout, re.M) for rid in estado["requisitos"]):
        raise FactoryError("Oracle no pudo juzgar estos hechos; no registré un veredicto: "
                           + (p.stdout + p.stderr).strip()[:800])
    if not mismo_producto(contexto, contexto_producto()) or [sha256(a.read_bytes()) for a in hechos] != huellas:
        raise FactoryError("el producto o los hechos cambiaron durante el juicio; repetí la corrida")
    exigir_spec(carpeta, estado)
    informe = dir_estado(carpeta) / 'oracle-veredicto.txt'
    informe.write_text(p.stdout + p.stderr, encoding="utf-8")
    ok = p.returncode == 0 and requisitos_verdes(p.stdout, estado["requisitos"])
    estado["oracle"] = {
        "codigo": 0 if ok else 1, "codigo_oracle": p.returncode,
        "hechos": rutas[0], "hechos_sha256": huella,
        # Más de un sensor: los demás archivos, cada uno con su huella. Con uno solo, el registro es el de siempre.
        **({"hechos_mas": [{"ruta": r, "sha256": h} for r, h in zip(rutas[1:], huellas[1:])]} if len(hechos) > 1 else {}),
        "informe": str(informe.relative_to(ROOT)), "informe_sha256": sha256(informe.read_bytes()),
        "cuando": ahora(), "contexto": contexto,
    }
    estado["fase"] = "oracle_verde" if ok else "oracle_rojo"
    evento(estado, "oracle_ejecutado", codigo=estado["oracle"]["codigo"], codigo_oracle=p.returncode, hechos_sha256=huella)
    guardar(carpeta, estado)
    nota_tarea(identificador, f"Juicio Factory: {'verde' if ok else 'incompleto/rojo'}; salida Oracle {p.returncode}; informe {informe.relative_to(ROOT)}.")
    print(f"Informe Oracle: {informe}")
    siguiente(identificador, estado["fase"])
    if not ok:
        raise FactoryError("Oracle no confirmó cada requisito: puede faltar evidencia o haber fallas en sombra")

def pendientes(estado: dict) -> list[str]:
    faltan = []
    humana = modo_de(estado) != "autonomo"
    if not estado.get("spec_aprobada"):
        faltan.append("aprobación humana de spec" if humana else "aceptación de spec")
    if not estado.get("requisitos"):
        faltan.append("importación OpenSpec → requisitos Oracle")
    rev = estado.get("revision") or {}
    if rev.get("decision") != "aprobar" or rev.get("hallazgos_abiertos") != 0:
        faltan.append("revisión humana aprobada y sin hallazgos abiertos" if humana else "revisión aprobada y sin hallazgos abiertos")
    oracle = estado.get("oracle") or {}
    if oracle.get("codigo") != 0:
        faltan.append("veredicto Oracle exitoso con evidencia")
    for decision, propuesta in (estado.get("propuestas") or {}).items():
        faltan.append(f"{DESCRIPCION[decision]} propuesta por {propuesta['actor']}, sin confirmar por una persona")
    for rid, propuesta in (estado.get("medidas_pendientes") or {}).items():
        faltan.append(f"medidas de {rid} elegidas por el agente {propuesta['actor']}; en modo {modo_de(estado)} las decide una persona"
                      if propuesta.get("descartada") else
                      f"medidas de {rid} propuestas por {propuesta['actor']}, sin confirmar por una persona")
    return faltan


def problemas_de_revision(estado: dict) -> list[str]:
    """Lo que invalida la revisión registrada por sus artefactos (informe y decisiones), sin mirar el producto."""
    rev, faltan = estado.get("revision") or {}, []
    for etiqueta, ruta, huella in (("informe de revisión", rev.get("informe"), rev.get("sha256")),
                                   ("decisiones de revisión", rev.get("decisiones"), rev.get("decisiones_sha256"))):
        if no_es_ruta(ruta):
            faltan.append(etiqueta + NO_VALIDO)
            continue
        if not ruta and not huella:
            continue
        try:
            if not ruta or not huella or sha256(ruta_del_registro(ruta).read_bytes()) != huella:
                faltan.append(etiqueta + " cambiado o sin huella")
        except OSError:
            faltan.append(etiqueta + " ausente")
    # Los registros antiguos sólo tenían un código numérico: no son evidencia vigente.
    if rev and not all(rev.get(k) for k in ("informe", "sha256", "contexto")):
        faltan.append("revisión sin evidencia vinculada")
    if rev.get('formato') == 'guiado' and not all(rev.get(k) for k in ('decisiones', 'decisiones_sha256')):
        faltan.append('revisión guiada sin decisiones vinculadas')
    return faltan


def pendientes_actuales(carpeta: Path, estado: dict) -> list[str]:
    faltan = pendientes(estado)
    faltan += [f"medidas de {rid}: {motivo}" for rid, motivo in medidas_sin_decision(estado)]
    try:
        exigir_spec(carpeta, estado)
    except (FactoryError, OSError) as e:
        faltan.append(str(e))
    if estado.get("revision") or estado.get("oracle"):
        try:
            contexto = contexto_producto()
            for nombre in ("revision", "oracle"):
                registro = estado.get(nombre)
                if registro and not mismo_producto(registro.get("contexto"), contexto):
                    faltan.append(nombre + " desactualizado respecto del producto")
        except (FactoryError, OSError) as e:
            faltan.append(str(e))
    faltan += problemas_de_revision(estado)
    oracle = estado.get("oracle") or {}
    registrados = hechos_registrados(oracle)
    for etiqueta, ruta, huella in (
        ("informe Oracle", oracle.get("informe"), oracle.get("informe_sha256")),
        # Con varios sensores, cada uno se nombra: por su ruta, o por su lugar si la ruta no sirve.
        *(("hechos" if len(registrados) == 1 else f"hechos {ruta}" if estructura._texto(ruta)
           else f"hechos del sensor {i} de {len(registrados)}", ruta, huella)
          for i, (ruta, huella) in enumerate(registrados, 1)),
    ):
        if no_es_ruta(ruta) or etiqueta.startswith("hechos del sensor"):  # en la lista, también un null es inválido
            faltan.append(etiqueta + NO_VALIDO)
            continue
        if not ruta and not huella:
            continue
        try:
            if not ruta or not huella or sha256(ruta_del_registro(ruta).read_bytes()) != huella:
                faltan.append(etiqueta + " cambiado o sin huella")
        except OSError:
            if etiqueta.startswith("hechos"):
                repetir = (comando_juzgar(estado['id'], registrados) if len(registrados) > 1
                           else f"oracle-factory juzgar {estado['id']} --con RUTA_DE_LOS_HECHOS")
                faltan.append(f"hechos ausentes ({ruta}); en esta máquina se recuperan juzgando de nuevo con los hechos "
                              f"del clon: {repetir}")
            else:
                faltan.append(etiqueta + " ausente")
    if oracle and not all(oracle.get(k) for k in ("informe", "informe_sha256", "hechos", "hechos_sha256", "contexto")):
        faltan.append("juicio sin evidencia vinculada")
    return faltan


def capacidad_destino(capacidad: str) -> str:
    return config_proyecto()["capacidades"].get(capacidad, capacidad)


def ruta_indice(capacidad: str) -> Path:
    return ROOT / estructura.DIR / "specs" / f"{capacidad}.json"


def ruta_spec_consolidada(capacidad: str) -> Path:
    return ROOT / "openspec" / "specs" / capacidad / "spec.md"


def leer_indice(capacidad: str) -> dict:
    ruta = ruta_segura(ruta_indice(capacidad))
    return json.loads(ruta.read_text(encoding="utf-8")) if ruta.is_file() else archivo.indice_vacio(capacidad)


def plan_archivo(estado: dict) -> tuple[str, dict]:
    """(capacidad, índice nuevo) de fusionar la spec del cambio; FactoryError si hay conflicto. No escribe."""
    capacidad = capacidad_destino(estado["capacidad"])
    dominio = {rid.split(".", 1)[1]: rid for rid in estado.get("requisitos", [])}
    try:
        indice = archivo.fusionar(leer_indice(capacidad), (ROOT / estado["spec"]).read_text(encoding="utf-8"),
                                  estado["id"], dominio)
    except archivo.Conflicto as e:
        raise FactoryError(f"la spec no se puede fusionar en openspec/specs/{capacidad}/: {e}") from e
    exigir_spec_consolidada(capacidad, indice)  # también antes de preguntar: cerrar no debe dejar un cierre sin archivar
    return capacidad, indice


def exigir_spec_consolidada(capacidad: str, indice: dict) -> None:
    """Falla si la spec consolidada en disco no es la que generó Factory (ni la de antes ni la que se va a escribir)."""
    spec = ruta_spec_consolidada(capacidad)
    previo = leer_indice(capacidad)
    esperado = archivo.texto_consolidado(previo) if ruta_indice(capacidad).is_file() else None
    actual = ruta_segura(spec).read_text(encoding="utf-8") if spec.is_file() else None
    # La nueva también vale: una corrida cortada entre la spec y el índice ya la había escrito.
    if actual not in (esperado, archivo.texto_consolidado(indice)):  # editada a mano o por otra herramienta: no se pisa
        raise FactoryError(f"{spec.relative_to(ROOT)} no es la que generó Factory (se editó a mano o no tiene índice en "
                           f"{ruta_indice(capacidad).relative_to(ROOT)}); restaurala con git restore antes de fusionar; "
                           "lo que se quería cambiar entra por la spec de un cambio")


def escribir_archivo(capacidad: str, indice: dict) -> str:
    """Escribe la spec consolidada y su índice; devuelve la ruta relativa de la spec."""
    exigir_spec_consolidada(capacidad, indice)
    spec = ruta_spec_consolidada(capacidad)
    for destino in (spec, ruta_indice(capacidad)):
        ruta_segura(destino).parent.mkdir(parents=True, exist_ok=True)
    escribir_atomico(spec, archivo.texto_consolidado(indice).encode("utf-8"))
    escribir_atomico(ruta_indice(capacidad), bytes_json(indice))
    return spec.relative_to(ROOT).as_posix()


def marcar_archivado(estado: dict, capacidad: str, spec: str, forma: str) -> None:
    estado["archivo"] = {"capacidad": capacidad, "spec": spec, "cuando": ahora()}
    evento(estado, "archivado", forma=forma, capacidad=capacidad, spec=spec)


SOLO_LECTURA = {"estado", "donde", "log", "tablero", "por-que", "kb", "resumen", "listar", "ruta", "buscar", "trazabilidad",
               "trailer", "hooks", "init", "ejemplo", "preguntar", "unir-registro", "unir-generado", "rehacer-generado"}


def archivar() -> None:
    """Archiva los cambios cerrados que todavía no lo están, en el orden en que se cerraron."""
    pendientes = []
    for carpeta in sorted(CHANGES.iterdir()) if CHANGES.is_dir() else []:
        if ID_RE.fullmatch(carpeta.name) and ruta_registro(carpeta).is_file():
            _, estado = leer(carpeta.name)
            if estado.get("fase") == "cerrada" and not estado.get("archivo"):
                cuando = (estado.get("cierre") or {}).get("cuando") or next(
                    (e.get("cuando", "") for e in reversed(estado.get("eventos", [])) if e.get("accion") == "cierre"), "")
                pendientes.append((cuando, carpeta.name))
    if not pendientes:
        print("No hay cambios cerrados sin archivar.")
        actualizar_resumen()
        return
    for _, identificador in sorted(pendientes, key=lambda x: (unir_mod.hora({"cuando": x[0]}), x[1])):
        carpeta, estado = leer(identificador)
        capacidad, indice = plan_archivo(estado)
        spec = escribir_archivo(capacidad, indice)
        marcar_archivado(estado, capacidad, spec, "migracion")
        guardar(carpeta, estado)
        print(f"Archivado {identificador} en {spec}.")
    actualizar_resumen()


def cerrar(identificador: str) -> None:
    carpeta, estado = abierto(identificador)
    if AGENTE and modos.via_agente(modo_de(estado), "cierre", []) == "rechaza":  # antes que lo que falte para cerrar
        raise FactoryError(f"en modo {modo_de(estado)}, {DESCRIPCION['cierre']} la toma una persona desde una terminal "
                           "interactiva, sin --agente")
    falta = pendientes_actuales(carpeta, estado)
    if falta:
        raise FactoryError("no se puede cerrar: " + "; ".join(falta))
    capacidad, indice = plan_archivo(estado)  # un conflicto rechaza el cierre antes de preguntar
    print(f"Al cerrar, la spec se fusiona en openspec/specs/{capacidad}/spec.md.")
    print(f"Se cerrará la tarea {identificador} (modo {modo_de(estado)}); Oracle {estado['oracle']['informe']}; revisión {estado['revision']['informe']}.")
    print(f"Spec aceptada por {quien(estado['spec_aprobada'])}; revisión registrada por {quien(estado['revision'])}.")
    for linea in commits_registrados(estado):
        print(linea + ".")
    for aviso in avisos_head(estado):
        print("Aviso: " + aviso + ".")
    forma = decidir(estado, "cierre", [], None, (f"Cerrar {identificador}", "Cerrar el cambio",
                    "fusiona la spec en openspec/specs/ y cierra la tarea"), "cierre cancelado; la tarea sigue abierta", None)
    falta = pendientes_actuales(carpeta, estado)
    if falta:
        raise FactoryError("el contexto cambió durante el cierre: " + "; ".join(falta))
    cierre = registro_decision(estado, forma)
    nota_tarea(identificador, f"Cierre: {quien(cierre)}, tras revisar el informe de código y el veredicto Oracle."
               + (" El cierre lo decidió un agente en modo autónomo." if cierre["tipo_actor"] == "agente" else ""))
    p = ejecutar(["tasks", "close", identificador, "--proyecto", str(ROOT)])
    if p.returncode:
        raise FactoryError(p.stderr.strip() or "oracle-task no pudo cerrar la tarea")
    estado["fase"] = "cerrada"
    estado["cierre"] = cierre
    evento(estado, "cierre", forma=forma, oracle=estado["oracle"]["informe"], revision=estado["revision"]["informe"])
    guardar(carpeta, estado)
    # Se fusiona después de cerrar: si se corta antes, nada quedó fusionado y el cierre se reintenta; si se corta
    # después, el cambio queda cerrado sin archivar y `archivar` lo completa.
    capacidad, indice = plan_archivo(estado)
    spec_consolidada = escribir_archivo(capacidad, indice)
    marcar_archivado(estado, capacidad, spec_consolidada, forma)
    guardar(carpeta, estado)
    print(f"Spec fusionada en {spec_consolidada}.")
    actualizar_resumen()
    print(p.stdout.strip() or "Tarea cerrada.")
    if cierre["tipo_actor"] == "agente":
        print(f"El cierre lo decidió el agente {cierre['actor']} en modo autónomo; las demás decisiones, como indica estado.")


def abandonar(identificador: str, motivo_agente: str | None = None) -> None:
    """Abandonar descarta las promesas del cambio: lo decide una persona en cualquier modo; un agente sólo propone el motivo."""
    carpeta = ruta_cambio(identificador)
    if ruta_segura(ruta_registro(carpeta)).is_file():
        _, previo = leer(identificador)
        quedan = [r for r in ((previo.get("abandono") or {}).get("requisitos_quitados") or [])
                  if (requisitos_dir() / f"{r}.requisito").is_file()] if previo.get("fase") == "abandonada" else []
        if quedan:  # un corte entre el registro y el borrado: la decisión ya está tomada, sólo falta completarla
            for rid in quedan:
                (requisitos_dir() / f"{rid}.requisito").unlink()
            actualizar_resumen()
            print(f"{identificador} ya estaba abandonado; quité de requisitos/ lo que había quedado: {', '.join(quedan)}.")
            return
        carpeta, estado = abierto(identificador)
    elif (carpeta / "proposal.md").is_file():  # una carpeta anterior al flujo: el abandono le da un registro mínimo
        primera = (carpeta / "proposal.md").read_text(encoding="utf-8").strip().splitlines()[:1]
        estado = {"id": identificador, "titulo": primera[0].lstrip("# ").strip() if primera else identificador,
                  "fase": "sin registro"}
    else:
        raise FactoryError(f"no encuentro el cambio {identificador}: ni su registro ni su propuesta")
    if AGENTE:
        if not (motivo_agente and motivo_agente.strip()):
            raise FactoryError("con --agente, abandonar propone el motivo: indicá --motivo; abandonar lo decide una persona")
        if estado["fase"] == "sin registro":
            raise FactoryError("una carpeta sin registro no guarda propuestas: la persona elige o escribe el motivo al abandonarla")
        # Fuera de «propuestas»: ésas son las decisiones canónicas de modos.DECISIONES.
        estado.setdefault("motivos_propuestos", {})["abandono"] = {"motivo": motivo_agente.strip(), **actor(), "cuando": ahora()}
        evento(estado, "abandono_propuesto", forma="propuso")
        guardar(carpeta, estado)
        print(f"Motivo propuesto por {AGENTE}: «{motivo_agente.strip()}». Abandonar lo decide una persona: "
              f"oracle-factory abandonar {identificador}")
        return
    if motivo_agente:
        raise FactoryError("--motivo es la propuesta de un agente; una persona elige el motivo en el menú")
    requisitos = [r for r in estado.get("requisitos", []) if (requisitos_dir() / f"{r}.requisito").is_file()]
    tarea = ROOT / "tareas" / identificador / "TAREA.md"
    print(f"{identificador} — {estado['titulo']} (fase {estado['fase']}).")
    print("Se quitan de requisitos/ (quedan en la historia de Git): " + (", ".join(requisitos) or "ninguno") + ".")
    print("La propuesta y la spec del cambio quedan como están; nada se fusiona en openspec/specs/.")
    confirmar_persona((f"Abandonar {identificador}", "Abandonar el cambio",
                       "pasa a abandonado, quita sus requisitos de requisitos/ y cierra su tarea"),
                      "abandono cancelado; el cambio sigue como estaba")
    propuesto = ((estado.get("motivos_propuestos") or {}).get("abandono") or {}).get("motivo")
    motivo = elegir_motivo(f"no se va a terminar: queda abandonado en la fase {estado['fase']}"
                           + (f" con {len(requisitos)} requisitos sin cerrar" if requisitos else "")
                           + "; lo que siga va en un cambio nuevo.", propuesto)
    if tarea.is_file():
        # El tracker antes que Factory: si falla, el cambio sigue abierto y repetir abandonar lo completa (una tarea ya
        # cerrada no se vuelve a cerrar y la nota no se repite). Cerrar va primero para no dejar la nota en una tarea abierta.
        if "ESTADO: CERRADA" not in tarea.read_text(encoding="utf-8"):
            p = ejecutar(["tasks", "close", identificador, "--proyecto", str(ROOT)])
            if p.returncode:
                raise FactoryError(p.stderr.strip() or "oracle-task no pudo cerrar la tarea")
        nota = f"Abandonado por una persona; motivo: {motivo[0]}"
        if nota not in tarea.read_text(encoding="utf-8"):
            nota_tarea(identificador, nota)
    else:
        print(f"Aviso: {identificador} no tiene tarea en tareas/; no hay nada que cerrar en el tracker.", file=sys.stderr)
    forma = "confirmo" if motivo[1] == "agente" else "decidio"
    estado["fase"] = "abandonada"
    estado["abandono"] = {**registro_decision(estado, forma, motivo), "requisitos_quitados": requisitos}
    (estado.get("motivos_propuestos") or {}).pop("abandono", None)
    evento(estado, "abandono", forma=forma, requisitos_quitados=requisitos)
    guardar(carpeta, estado)
    for rid in requisitos:  # después del registro: lo que se quitó queda dicho aunque se corte acá
        (requisitos_dir() / f"{rid}.requisito").unlink(missing_ok=True)
    actualizar_resumen()
    print(f"Abandonado: {identificador}; {quien(estado['abandono'])}.")


def cambiar_modo(identificador: str, nuevo_modo: str) -> None:
    carpeta, estado = abierto(identificador)
    actual = modo_de(estado)
    if nuevo_modo not in modos.MODOS:
        raise FactoryError("modo desconocido; usá " + ", ".join(modos.MODOS))
    if nuevo_modo == actual:
        print(f"El cambio ya está en modo {actual}.")
        return
    if modos.baja_intervencion(actual, nuevo_modo):
        if AGENTE:
            raise FactoryError(f"pasar de {actual} a {nuevo_modo} reduce la intervención humana: lo decide una persona, sin --agente")
        confirmar_persona((f"Pasar {identificador} de {actual} a {nuevo_modo}", f"Pasar a {nuevo_modo}",
                           "reduce la intervención humana; las propuestas que dejen de valer se invalidan"),
                          "cambio de modo cancelado; el modo sigue igual")
    estado["modo"] = nuevo_modo
    tipos = tipos_cambio(estado)
    propuestas, invalidadas = estado.setdefault("propuestas", {}), []

    def via_nueva(registro, decision, tipos_):
        # None: sigue valiendo. 'propone': pasa a propuesta. 'rechaza': se descarta, la decide una persona.
        if not registro or registro.get("tipo_actor") != "agente":
            return None
        via = modos.via_agente(nuevo_modo, decision, tipos_)
        return None if via == "decide" else via

    via = via_nueva(estado.get("spec_aprobada"), "spec", tipos)
    if via:
        sa = estado["spec_aprobada"]
        if via == "propone":
            propuestas["spec"] = {"firma": sa["documentos"], "actor": sa["actor"], "tipo_actor": "agente", "cuando": sa["cuando"]}
        estado.update(spec_aprobada=None, revision=None, oracle=None, fase="espera_aprobacion_spec")
        invalidadas.append(("spec", via))
    rev = estado.get("revision")
    via = via_nueva(rev, "revision", tipos)
    if via:
        if via == "propone":
            firma = firma_revision(rev["formato"], rev["sha256"], rev.get("decisiones_sha256"), rev["revisor"], rev["decision"], rev["contexto"])
            if rev["formato"] == "libre":
                firma["abiertos"] = rev["hallazgos_abiertos"]
            propuestas["revision"] = {"firma": firma, "actor": rev["actor"], "tipo_actor": "agente", "cuando": rev["cuando"]}
        estado.update(revision=None, oracle=None)
        invalidadas.append(("revision", via))
    for rid, medida in list((estado.get("medidas") or {}).items()):
        via = via_nueva(medida, "medidas", [(estado.get("tipos") or {}).get(rid, "funcional")])
        if via:
            ruta = requisitos_dir() / f"{rid}.requisito"
            estado.setdefault("medidas_pendientes", {})[rid] = {"sha256": medida.get("sha256") or sha256(ruta.read_bytes()), "actor": medida["actor"],
                                                                "tipo_actor": "agente", "cuando": medida["cuando"],
                                                                "descartada": via == "rechaza"}
            del estado["medidas"][rid]
            estado.update(oracle=None)
            invalidadas.append(("medidas de " + rid, via))
    for decision in list(propuestas):
        if decision != "cierre" and modos.via_agente(nuevo_modo, decision, tipos) == "rechaza":
            del propuestas[decision]
            invalidadas.append((f"propuesta de {decision}", "rechaza"))
    for rid, pendiente in (estado.get("medidas_pendientes") or {}).items():
        tipo_rid = [(estado.get("tipos") or {}).get(rid, "funcional")]
        if not pendiente.get("descartada") and modos.via_agente(nuevo_modo, "medidas", tipo_rid) == "rechaza":
            pendiente["descartada"] = True
            invalidadas.append((f"propuesta de medidas de {rid}", "rechaza"))
    texto = {"propone": "pasa a propuesta: una persona la confirma", "rechaza": "se descarta: la decide una persona"}
    evento(estado, "modo_cambiado", anterior=actual, nuevo=nuevo_modo, invalidadas=[f"{i}: {texto[v]}" for i, v in invalidadas])
    guardar(carpeta, estado)
    nota_tarea(identificador, f"Modo de trabajo: {actual} → {nuevo_modo}." + (
        " Decisiones de agente: " + "; ".join(f"{i} {texto[v]}" for i, v in invalidadas) + "." if invalidadas else ""))
    print(f"Modo de trabajo: {actual} → {nuevo_modo}.")
    for item, via in invalidadas:
        print(f"Decisión de agente sobre {item}: {texto[via]}.")


ESQUEMA_ESTADO, ESQUEMA_DONDE = "oracle-factory.estado/1", "oracle-factory.donde/1"


def imprimir_json(datos: dict) -> None:
    """Todo de una vez al final: si algo falla antes, stdout queda vacío y el error va a stderr."""
    print(json.dumps(datos, ensure_ascii=False, indent=2, sort_keys=True))


def _decision(registro: dict | None) -> dict | None:
    """Quién decidió, cómo, cuándo y por qué; lo mismo que `quien` muestra en texto."""
    if not registro:
        return None
    datos = {k: registro.get(k) for k in ("actor", "tipo_actor", "forma", "modo", "cuando", "motivo", "origen_motivo")}
    if "tipo_actor" not in registro:  # anterior a los modos: el actor estaba en «por» y no se sabe si era persona
        datos["actor"] = registro.get("actor") or registro.get("por")
    return datos


def comando_migrar(verificar: bool) -> None:
    """Pasa el estado de cada cambio y la configuración a .factory/ (fase 2 de la estructura)."""
    movimientos, problemas, avisos = migracion.planear(ROOT)
    for texto in problemas + avisos:
        print(f"Aviso: {texto}", file=sys.stderr)
    if verificar:
        for m in movimientos:
            print(f"{m['cambio']}: {m['origen'].relative_to(ROOT)} -> {m['destino'].relative_to(ROOT)}"
                  + ("" if m["estado"] == "escribir" else " (ya está en el lugar nuevo; sólo falta borrar el viejo)"))
        print(f"Por migrar: {len(movimientos)} archivos.")
        if any(m["origen"].name == "factory.json" and m["origen"].parent == ROOT for m in movimientos):
            print("Aviso: factory.json de la raíz es parte del producto: moverlo cambia la huella y vence las revisiones vigentes.")
        if movimientos or problemas:
            raise SystemExit(1)
        return
    if any(m["origen"].name == "factory.json" and m["origen"].parent == ROOT for m in movimientos):
        print("Aviso: factory.json de la raíz es parte del producto: moverlo cambia la huella y vence las revisiones vigentes; "
              "hay que volver a preparar y registrar la revisión de los cambios abiertos.")
    hechos = migracion.aplicar(movimientos)
    cambios = sorted({m["cambio"] for m in movimientos})
    print(f"Migrados {hechos} archivos de {len(cambios)} cambios y configuración. No hice commits: revisá con git status y confirmalos.")
    if problemas:
        raise SystemExit(1)


def comando_ruta(identificador: str, tipo: str) -> None:
    leer(identificador)  # el cambio tiene que existir
    head = ejecutar(["git", "rev-parse", "HEAD"])
    if head.returncode:
        raise FactoryError("ruta necesita un repositorio Git con al menos un commit")
    try:
        # El candidato vigente, como pedir-revision y juzgar: un commit que sólo guarda registros no es un candidato nuevo.
        # Si no hay, HEAD con los 7 primeros del hash completo (--short=7 lo alarga si es ambiguo y la carpeta cambiaría).
        sha = candidato_vigente(identificador) or head.stdout.strip()[:7]
        print(estructura.ruta_canonica(ROOT, identificador, tipo, sha))
    except ValueError as e:
        raise FactoryError(str(e)) from e


def comando_buscar(texto: str, maximo: int) -> None:
    if not texto.strip():
        raise FactoryError("indicá el texto a buscar")
    # Un .factory enlazado no es nuestra carpeta y no se lee a través de él: entonces se busca en la raíz. Una carpeta de
    # Oracle mal configurada, en cambio, falla y dice la causa.
    oracle = "" if (ROOT / estructura.DIR).is_symlink() else oracle_rel()
    lineas, total, omitidos = estructura.buscar(ROOT, texto, maximo, oracle)
    for linea in lineas:
        print(linea)
    print(f"{total} coincidencia(s)" + (f"; se muestran {len(lineas)}, usá --max para ver más" if total > len(lineas) else ""))
    if omitidos:
        print(f"Aviso: {omitidos} archivo(s) omitido(s) por superar {estructura.LIMITE_ARCHIVO // 1_000_000} MB; el texto podría estar ahí.")


def comando_procedencia(args) -> None:
    """El inventario de las dependencias, quién usó una y la auditoría contra avisos OSV. Local, salvo --consultar-osv --red."""
    if args.consultar_osv:
        if not args.red:
            raise FactoryError("--consultar-osv se conecta a OSV.dev: autorizalo con --red (sale sólo nombre, versión y ecosistema de cada dependencia)")
        if args.buscar or args.auditar or args.id or args.avisos:
            raise FactoryError("--consultar-osv mira todos los inventarios guardados y no se combina con --buscar, --auditar, --avisos ni un cambio")
        try:
            print(osv_mod.informe(ROOT, args.osv_url, args.salida, args.json), end="")
        except procedencia_mod.ProcedenciaError as e:
            raise FactoryError(str(e)) from e
        return
    if args.red or args.salida:
        raise FactoryError("--red y --salida son para --consultar-osv")
    if args.buscar and args.auditar:
        raise FactoryError("--buscar y --auditar no se combinan; usá uno")
    if (args.buscar or args.auditar) and args.id:
        raise FactoryError("--buscar y --auditar miran todos los inventarios guardados: no llevan un cambio")
    if args.auditar and not args.avisos:
        raise FactoryError("--auditar necesita --avisos ARCHIVO con avisos en formato OSV")
    if args.avisos and not args.auditar:
        raise FactoryError("--avisos es para --auditar")
    try:
        if args.buscar or args.auditar:
            print(procedencia_mod.informe_buscar(ROOT, args.buscar, args.json) if args.buscar
                  else procedencia_mod.informe_auditar(ROOT, args.avisos, args.json), end="")
            return
        python = procedencia_mod.python_del_proyecto(ROOT, args.python)
        bom, diferencias, confiable = procedencia_mod.inventario(ROOT, python)
    except procedencia_mod.ProcedenciaError as e:
        raise FactoryError(str(e)) from e
    cuerpo = procedencia_mod.texto(bom)
    guardado = None
    if args.id:
        carpeta, estado = abierto(args.id)
        head = ejecutar(["git", "rev-parse", "HEAD"])
        if head.returncode:
            raise FactoryError("procedencia necesita un repositorio Git con al menos un commit")
        sha = candidato_vigente(args.id) or head.stdout.strip()[:7]
        destino = ROOT / estructura.DIR / "cambios" / args.id / "candidatos" / sha / "procedencia" / "cyclonedx.json"
        ruta_segura(destino)
        destino.parent.mkdir(parents=True, exist_ok=True)
        escribir_atomico(destino, cuerpo.encode("utf-8"))
        huella = sha256(cuerpo.encode("utf-8"))
        evento(estado, "procedencia_registrada", candidato=sha, archivo=destino.relative_to(ROOT).as_posix(), huella=huella,
               componentes=len(bom["components"]), confiable=confiable, diferencias=len(diferencias))
        guardar(carpeta, estado)
        guardado = (destino.relative_to(ROOT).as_posix(), huella)
    if args.json:
        print(cuerpo, end="")
        return
    fuente = "uv.lock" if any(procedencia_mod.propiedad(c, "factory:fuente") == "uv.lock" for c in bom["components"]) else "el entorno instalado"
    print(f"Inventario de dependencias de Python: {len(bom['components'])} componentes, según {fuente}.")
    print("Confiable: sí." if confiable else "Confiable: no.")
    for d in diferencias:
        print(f"  - {d}")
    for c in bom["components"]:
        if procedencia_mod.propiedad(c, "factory:corregida"):
            print(f"  corregido por Lightwell: {c['name']} {c['version']}")
    if guardado:
        print(f"Guardado en {guardado[0]} (sha256 {guardado[1][:16]}…) y registrado en {args.id}.")
    else:
        print("No se guardó (indicá el cambio para guardarlo en su candidato) ni se mostró el CycloneDX (--json).")


def comando_agentes(verificar: bool) -> None:
    """El bloque para agentes de AGENTS.md (y la línea @AGENTS.md de CLAUDE.md), o --verificar que estén al día."""
    nuevo = agentes_mod.bloque(config_proyecto()["modo_por_defecto"])
    rutas = [ruta_segura(ROOT / "AGENTS.md"), ruta_segura(ROOT / "CLAUDE.md")]
    actuales = [r.read_text(encoding="utf-8") if r.is_file() else "" for r in rutas]
    try:
        esperados = [agentes_mod.con_bloque(actuales[0], nuevo), agentes_mod.con_claude(actuales[1])]
    except agentes_mod.MarcasRotas as e:
        raise FactoryError(str(e)) from e
    if verificar:
        viejos = [r.name for r, a, e in zip(rutas, actuales, esperados) if a != e]
        if viejos:
            raise FactoryError(f"la guía para agentes no está al día en {', '.join(viejos)}; corré oracle-factory agentes")
        print("La guía para agentes está al día en AGENTS.md (y CLAUDE.md la incluye).")
        return
    for ruta, actual, esperado in zip(rutas, actuales, esperados):
        if actual != esperado:
            escribir_atomico(ruta, esperado.encode("utf-8"))
    print("Guía para agentes en AGENTS.md (CLAUDE.md la incluye con @AGENTS.md): quién decide qué, los comandos de una "
          "persona y de un agente, y cómo consultar el proyecto.")


def comando_preguntar(args) -> None:
    if args.evaluar:
        if not args.salida:
            raise FactoryError("--evaluar necesita --salida CARPETA (nueva)")
        c = rag_mod.evaluar(sys.modules[__name__], args.salida.resolve(), casos=args.casos)
        print(f"{c['aciertos']} de {c['preguntas']} preguntas de oro con un archivo esperado entre los {rag_mod.PRIMEROS} "
              f"primeros (MRR {c['mrr']}, modo {c['modo']}, modelo {c['modelo']}). Hechos: {args.salida / 'hechos.json'}")
        hechos = json.loads((args.salida / 'hechos.json').read_text(encoding='utf-8'))
        for grupo in hechos['preguntar_grupo']:
            print(f"{grupo['grupo']}: {grupo['aciertos']}/{grupo['preguntas']}; errores: {grupo['errores']}; "
                  f"abstenciones incorrectas: {grupo['abstenciones_incorrectas']}; simulado: {bool(grupo['simulado'])}")
        return
    if args.casos:
        raise FactoryError('--casos se usa junto a --evaluar')
    datos = rag_mod.preguntar(sys.modules[__name__], args.texto, args.maximo)
    print(json.dumps(datos, ensure_ascii=False, indent=2) if args.json else rag_mod.texto(datos))


def mostrar(identificador: str) -> None:
    carpeta, estado = leer(identificador)
    if estado.get("fase") == "abandonada":  # sin pendientes ni próximo paso; un registro mínimo no tiene spec
        print(f"{estado['id']} — {estado['titulo']}\nFase: abandonada\nAbandonado por: {quien(estado.get('abandono'))}")
        quitados = (estado.get("abandono") or {}).get("requisitos_quitados") or []
        print("Requisitos quitados de requisitos/: " + (", ".join(quitados) or "ninguno"))
        for aviso in aviso_union(identificador, estado):  # dos ramas pudieron decidir distinto también sobre esto
            print(f"Aviso: {aviso}.")
        return
    print(f"{estado['id']} — {estado['titulo']}\nFase: {estado['fase']}\nModo de trabajo: {modo_de(estado)}")
    print("Requisitos Oracle: " + (", ".join(estado.get("requisitos", [])) or "todavía no importados"))
    print("Pendiente: " + ("; ".join(pendientes_actuales(carpeta, estado)) or "ninguno"))
    for linea in commits_registrados(estado):
        print(linea + ".")
    print(linea_commits(commits_del_cambio(identificador, estado)) + ".")
    print(linea_quien(quien_del_cambio(estado)) + ".")
    for aviso in (avisos_head(estado) + aviso_revision(estado) + aviso_lanzamientos(estado) + aviso_sin_autor(estado)
                  + aviso_sin_medir(identificador, estado) + aviso_notas(identificador, estado) + aviso_union(identificador, estado)):
        print("Aviso: " + aviso + ".")
    print("Aprobación spec: " + (f"sí, {quien(estado['spec_aprobada'])}" if estado.get("spec_aprobada") else "pendiente"))
    rev = estado.get("revision")
    print("Revisión: " + (f"{rev['revisor']} / {rev['decision']} / {rev['hallazgos_abiertos']} abiertos" if rev else "pendiente"))
    if rev:
        formato = rev.get('formato', 'libre histórico')
        print('Formato de revisión: ' + formato + ('; consistencia estructural, no calidad del análisis' if formato == 'guiado'
                                                 else '; declaración humana sin validación estructural'))
    oracle = estado.get("oracle")
    print("Oracle: " + (f"código {oracle['codigo']} ({oracle['informe']})" if oracle else "pendiente"))
    if rev:
        print("Revisión registrada por: " + quien(rev))
    for rid, medida in (estado.get("medidas") or {}).items():
        print(f"Medidas de {rid}: {quien(medida)}")
    if estado.get("cierre"):
        print("Cierre: " + quien(estado["cierre"]))
    if estado.get("archivo"):
        print(f"Archivo: {estado['archivo']['spec']}")
        for rid, situacion, por in situacion_requisitos(estado):
            print(f"  {rid}: {situacion}" + (f" por {por}" if por else ""))
    siguiente(identificador, estado["fase"])


LEEME_FACTORY = """# .factory/

Lo que Factory produce sobre este proyecto. Se versiona con el código para que quien clone el proyecto
lo tenga; `local/` no, porque es de cada máquina y Git la ignora.

- `config.json` es la configuración del proyecto: `modo_por_defecto`, `tipos_obligatorios`, `capacidades` (alias de capacidades),
  `revisores`, `oracle` (la carpeta del proyecto Oracle, si no es la raíz) y `confiar_escalares`.
- `cambios/<ID>/` guarda el estado del cambio: `factory.json`, `review.md` y `oracle-veredicto.txt`.
- `resumen.md` es el estado actual en una lectura (`oracle-factory resumen`); se lee con `glow -p .factory/resumen.md`.
- `specs/<capacidad>.json` es el índice de la spec consolidada en `openspec/specs/<capacidad>/`: de qué cambio y requisito de Oracle viene cada requisito vigente y cuáles fueron reemplazados.
- `cambios/<ID>/candidatos/<sha7>/` agrupa lo que se produjo sobre un commit: `evidencia/`, `clue/` y `revision/`.
- `local/revisiones/` guarda los checkouts estables y el clon aparte de cada pedido de revisión (`<sha7>-<revisor>-<n>/`).
- `local/revisores/` guarda el pedido, la salida y el informe de cada revisor (`<sha7>-<revisor>-<n>/`).
- `local/rag/` guarda el índice de `oracle-factory preguntar`. Nada de `local/` se versiona.

Este archivo existe también porque Git no versiona carpetas vacías: sin él, un clon no tendría `.factory/`.
Más detalle en `docs/estructura.md` del repositorio de Factory, y `oracle-factory donde ID` lista lo que hay.
"""


SIN_USO_DE_ORACLE = ("corpus", "relaciones", "diferencial")


def inicializar(oracle: str | None = None) -> None:
    """Prepara Factory en ROOT. Con `oracle`, adopta el proyecto Oracle que ya está en esa carpeta en vez de crear uno en la raíz."""
    marca = ROOT / estructura.DIR
    if marca.is_symlink() or (marca.exists() and not marca.is_dir()):
        raise FactoryError(f"{marca} existe y no es una carpeta de Factory: renombrala o quitala antes de ejecutar init; no creé nada")
    if oracle is None and (marca / "config.json").is_file():  # ya inicializado: se respeta la carpeta de Oracle configurada
        configurada = config_proyecto()["oracle"]
        oracle = None if configurada in (".", "") else configurada
    afuera = estructura.raiz_del_proyecto(ROOT.parent) if ROOT.parent != ROOT else None
    if afuera is not None:
        print(f"Aviso: esta carpeta está dentro del proyecto Factory {afuera}; init crea un proyecto anidado y los comandos "
              "usarán el más cercano.", file=sys.stderr)
    if oracle is not None:
        relativa = carpeta_relativa(oracle)
        if (oracle in ("", ".") or relativa is None
                or (ROOT / relativa).resolve() != ROOT / relativa or not (ROOT / relativa / "oracle.json").is_file()):
            raise FactoryError(f"--oracle es la carpeta de un proyecto Oracle que ya existe dentro de este proyecto "
                               f"(con oracle.json); «{oracle}» no lo es. No creé nada")
    ROOT.mkdir(parents=True, exist_ok=True)
    propios = ("tareas", ".gitignore", "openspec/changes", estructura.DIR)
    oracle_raiz = ("catalogos", "corpus", "diferencial", "relaciones", "requisitos", "macros", "oracle.json")
    for nombre in propios + (() if oracle else oracle_raiz):
        ruta_segura(ROOT / nombre)
    de_antes = {nombre for nombre in SIN_USO_DE_ORACLE if (ROOT / nombre).exists()}
    for comando in (["tasks", "init", str(ROOT), "--sin-readme"], *([] if oracle else [["oracle", "init", str(ROOT)]])):
        resultado = ejecutar(comando)
        if resultado.returncode:
            raise FactoryError(resultado.stderr or resultado.stdout)
    for nombre in SIN_USO_DE_ORACLE:  # las crea `oracle init` y Factory no las usa: vacías, sólo confunden
        carpeta = ROOT / nombre
        if nombre not in de_antes and carpeta.is_dir() and not carpeta.is_symlink() and not any(carpeta.iterdir()):
            carpeta.rmdir()
    ruta_segura(CHANGES).mkdir(parents=True, exist_ok=True)
    for sub in ('cambios', 'local'):
        ruta_segura(ROOT / estructura.DIR / sub).mkdir(parents=True, exist_ok=True)
    config = ruta_segura(ROOT / estructura.DIR / 'config.json')
    if not config.exists() and not (ROOT / 'factory.json').exists():  # con la configuración anterior en la raíz, la pasa `migrar`
        datos = {"modo_por_defecto": modos.POR_DEFECTO, "tipos_obligatorios": False}
        config.write_text(json.dumps({**datos, **({"oracle": oracle} if oracle else {})}, indent=2) + "\n", encoding='utf-8')
    elif oracle and config.exists():  # ya inicializado: sólo se anota dónde está el proyecto Oracle
        datos = json.loads(config.read_text(encoding='utf-8'))
        if datos.get("oracle") != oracle:
            escribir_atomico(config, (json.dumps({**datos, "oracle": oracle}, indent=2, ensure_ascii=False) + "\n").encode())
    leeme = ruta_segura(ROOT / estructura.DIR / 'LEEME.md')
    if not leeme.exists():
        leeme.write_text(LEEME_FACTORY, encoding='utf-8')
    ignore = ruta_segura(ROOT / '.gitignore')
    contenido = ignore.read_text(encoding='utf-8') if ignore.exists() else ''
    pendientes = [line for line in (estructura.IGNORAR_LOCAL, estructura.IGNORAR_CLUE, '__pycache__/', '*.py[cod]')
                  if line not in contenido.splitlines()]
    if pendientes:
        with ignore.open('a', encoding='utf-8') as archivo:
            archivo.write(('\n' if contenido and not contenido.endswith('\n') else '') + '\n'.join(pendientes) + '\n')
    versionados = ejecutar(["git", "ls-files", "--", ":(glob)" + estructura.IGNORAR_CLUE + "**"]).stdout.split()
    if versionados:  # el .gitignore no saca del índice lo que ya estaba versionado; init no toca el índice
        print("Aviso: hay paquetes de Clue versionados de antes; ahora son locales. Para dejar de versionarlos sin borrarlos: "
              "git rm -r --cached " + " ".join(sorted({str(Path(p).parent) for p in versionados})), file=sys.stderr)
    # Git no versiona carpetas vacías: sin esto, quien clona el proyecto no tiene tareas/ ni catalogos/ y no puede
    # crear un cambio. .factory/local/ no: es local y Git la ignora.
    raiz_oracle = ROOT / (oracle or "")
    for carpeta_vacia in (ROOT / "tareas", CHANGES, ROOT / estructura.DIR / "cambios", raiz_oracle / "catalogos",
                          raiz_oracle / "requisitos", raiz_oracle / "macros"):
        if carpeta_vacia.is_dir() and not any(carpeta_vacia.iterdir()):
            (ruta_segura(carpeta_vacia) / ".gitkeep").write_text("", encoding="utf-8")
        regla = ejecutar(["git", "check-ignore", "-v", "--", str(carpeta_vacia / ".gitkeep")])
        if not regla.returncode:  # un .gitignore del proyecto la excluye: Factory no pisa esa regla, pero avisa
            print(f"Aviso: Git ignora {carpeta_vacia.relative_to(ROOT)}/ ({regla.stdout.split(chr(9))[0].strip()}): quien "
                  "clone el proyecto no la va a tener. Si es de Factory, sacá esa regla del .gitignore.", file=sys.stderr)
    print(f'Factory inicializada en {ROOT}. No se crearon commits ni aprobaciones.')
    print(f'Acuerdos: {CHANGES}; tareas: {ROOT / "tareas"}; proyecto Oracle: {ROOT / (oracle or "")}.')
    print(f'Carpeta propia de Factory: {ROOT / estructura.DIR} (versionada, salvo local/, que Git ignora).')
    print('Conservé la configuración existente. .gitignore excluye salidas temporales y bytecode de Python.')
    print('Si el proyecto todavía no usa Git, ejecutá git init desde esta carpeta; Factory no crea commits.')
    print(instalar_hook())
    comando_agentes(False)
    if not ejecutar(["git", "rev-parse", "--git-dir"]).returncode:
        print(instalar_union())
    print('Próximo paso: oracle-factory nuevo --con-ejemplo notas "Comprobar el título de una nota"')
    print('Para recuperar cambios existentes: oracle-factory listar')


def copiar_ejemplo(destino: Path) -> None:
    if not destino.is_absolute():
        destino = ROOT / destino
    if destino.exists():
        raise FactoryError(f"el destino del ejemplo ya existe: {destino}")
    origen = resources.files("oracle_factory").joinpath("data/notas")
    def copiar(origen, destino):
        destino.mkdir(parents=True, exist_ok=False)
        for elemento in origen.iterdir():
            if elemento.is_dir():
                copiar(elemento, destino / elemento.name)
            else:
                (destino / elemento.name).write_bytes(elemento.read_bytes())
    copiar(origen, destino)
    print(f"Ejemplo copiado en {destino}")


def ruta_segura(ruta: Path) -> Path:
    """Rechaza enlaces y salidas del proyecto antes de leer o escribir."""
    ruta = Path(ruta)
    try:
        relativa = ruta.relative_to(ROOT)
    except ValueError as e:
        raise FactoryError(f"ruta fuera del proyecto: {ruta}") from e
    actual = ROOT
    for parte in relativa.parts:
        if parte in {'.', '..'}:
            raise FactoryError(f"ruta insegura: {ruta}")
        actual /= parte
        if actual.is_symlink():
            raise FactoryError(f"no se siguen enlaces simbólicos: {actual}")
    return ruta


def escribir_atomico(ruta: Path, datos: bytes, *, esperado: bytes | None = None) -> None:
    ruta_segura(ruta)
    temporal = None
    try:
        with tempfile.NamedTemporaryFile(dir=ruta.parent, prefix='.factory-', delete=False) as archivo:
            temporal = Path(archivo.name)
            archivo.write(datos)
            archivo.flush()
            os.fsync(archivo.fileno())
        if ruta.exists():
            os.chmod(temporal, ruta.stat().st_mode & 0o777)
        ruta_segura(ruta)
        # Comparar y reemplazar, sin que otro proceso de Factory escriba en la misma carpeta en el medio. El sistema
        # suelta el bloqueo si el proceso muere, y no deja archivos.
        carpeta = os.open(ruta.parent, os.O_RDONLY)
        try:
            fcntl.flock(carpeta, fcntl.LOCK_EX)
            try:  # un archivo que otro borró o movió también cambió
                cambio = esperado is not None and ruta.read_bytes() != esperado
            except FileNotFoundError:
                cambio = True
            if cambio:
                raise ArchivoCambiado(f"el archivo cambió durante la operación: {ruta}; volvé a leerlo")
            os.replace(temporal, ruta)
        finally:
            os.close(carpeta)
        if ruta in LEIDOS:
            LEIDOS[ruta] = datos
    finally:
        if temporal is not None and temporal.exists():
            temporal.unlink()


def plan_ejemplo() -> dict[Path, bytes]:
    destino = ruta_segura(ROOT / 'examples' / 'notas')
    if destino.exists():
        raise FactoryError(f"el destino del ejemplo ya existe: {destino}; usá nuevo --capacidad notas para otro cambio")
    oracle = proyecto_oracle()
    if not (oracle / 'catalogos').is_dir() or not (oracle / 'oracle.json').is_file():
        raise FactoryError('primero inicializá el proyecto con oracle-factory init')
    origen = resources.files('oracle_factory').joinpath('data/notas')
    plan = {}
    def recorrer(carpeta, relativa):
        for item in sorted(carpeta.iterdir(), key=lambda x: x.name):
            nombre = relativa / item.name
            if item.is_dir():
                recorrer(item, nombre)
            else:
                plan[destino / nombre] = item.read_bytes()
                if relativa == Path('catalogos'):
                    plan[oracle / 'catalogos' / item.name] = item.read_bytes()
    recorrer(origen, Path())
    for ruta in plan:
        ruta_segura(ruta)
        if ruta.exists():
            raise FactoryError(f"destino existente; no se creó ninguna tarea ni se sobrescribió: {ruta}")
        for padre in ruta.parents:
            if padre == ROOT:
                break
            if padre.exists() and not padre.is_dir():
                raise FactoryError(f"el directorio destino es un archivo: {padre}")
    return plan


def preparar_ejemplo(plan: dict[Path, bytes]) -> None:
    copiados = []
    try:
        for ruta, datos in plan.items():
            ruta_segura(ruta)
            ruta.parent.mkdir(parents=True, exist_ok=True)
            with ruta.open('xb') as archivo:
                archivo.write(datos)
            copiados.append(str(ruta.relative_to(ROOT)))
    except OSError as e:
        # No borrar archivos que otra sesión podría haber adoptado/modificado.
        raise FactoryError('copia incompleta; todavía no se creó una tarea. '
                           f'Destino fallido: {ruta}. Archivos copiados: {", ".join(copiados) or "ninguno"}. '
                           'Revisá esos destinos antes de reintentar; no se sobrescriben. ' + str(e)) from e


def archivos_faltantes(carpeta: Path, estado: dict) -> list[str]:
    """Los archivos que el registro del cambio referencia y no están en el disco, relativos a la raíz."""
    rev, oracle = estado.get("revision") or {}, estado.get("oracle") or {}
    rutas = [carpeta / "proposal.md", carpeta / "tasks.md", *([ROOT / estado["spec"]] if estado.get("spec") else []),
             *(requisitos_dir() / f"{r}.requisito" for r in estado.get("requisitos") or []),
             # Un valor que no es una ruta no es un archivo que recuperar: lo nombran pendientes y se rehace su gate.
             *(r for r in map(ruta_del_registro, (rev.get("informe"), rev.get("decisiones"), oracle.get("informe"),
                                                  *(ruta for ruta, _ in hechos_registrados(oracle)))) if r)]
    return [str(p.relative_to(ROOT)) if p.is_relative_to(ROOT) else str(p) for p in rutas if not p.is_file()]


def proximo_paso(identificador: str) -> str | None:
    """El próximo paso según lo que está vigente, en el orden del flujo.

    Un comando completo («oracle-factory …» sin MAYÚSCULAS por completar) se puede ofrecer para ejecutar; un texto que
    empieza con otra cosa indica algo que la persona tiene que hacer antes.
    """
    return (pasos(identificador) or [None])[0]


def pasos(identificador: str) -> list[str]:
    """El próximo paso seguido de las alternativas que también valen; vacía si el cambio terminó."""
    paso = _pasos(identificador)
    return [paso] if isinstance(paso, str) else paso or []


def _pasos(identificador: str) -> str | list[str] | None:
    carpeta, estado = leer(identificador)
    ident = identificador
    if estado.get("fase") in ("cerrada", "abandonada"):
        return None
    # Un archivo que el registro referencia y falta no se arregla con un comando de Factory: se recupera.
    faltan = archivos_faltantes(carpeta, estado)
    if faltan:
        # Con varios sensores, recuperados sus hechos, lo que sigue es juzgar otra vez con todos.
        varios = hechos_registrados(estado.get("oracle") or {})
        despues = comando_juzgar(ident, varios) if len(varios) > 1 else f"oracle-factory estado {ident}"
        return f"faltan archivos del cambio ({', '.join(faltan)}): recuperalos desde Git; después: {despues}"
    try:  # sin aprobar, o la propuesta/spec cambió después de aprobarla
        exigir_spec(carpeta, estado)
    except FactoryError:
        return f"oracle-factory aprobar-spec {ident}"
    if not estado.get("requisitos"):
        return f"oracle-factory importar {ident}"
    if propuestas_confirmables(estado):
        return f"oracle-factory medir {ident} --confirmar"
    medidas = estado.get("medidas") or {}
    if (any(rid not in medidas for rid in estado["requisitos"]) or medidas_sin_decision(estado)
            or estado.get("medidas_pendientes")):  # propuestas que ya no se pueden confirmar tal cual: se deciden
        return f"oracle-factory medir {ident} --listar"
    # ¿La revisión vale para el producto actual?
    rev = estado.get("revision") or {}
    revisado = (bool(rev) and mismo_producto(rev.get("contexto"), contexto_producto())
                and not problemas_de_revision(estado))  # mismas reglas que pendientes_actuales
    if not revisado:
        if cambios_locales_de_producto():
            return f"commiteá los cambios del producto; después: {pedido_de_revision(ident)}"
        sha = candidato_vigente(ident)
        # revisar necesita informes de revisores que la preparación pueda usar (mismas reglas), no sólo evidencia.
        corte = corte_del_candidato(ident, sha, estado) if sha else None
        if corte and corte[0]:  # o la persona los acepta como riesgo o los descarta, con motivo
            return [f"corregí los {len(corte[0])} hallazgos medios o más del candidato {sha} y commitealo; después: "
                    f"{pedido_de_revision(ident)}", f"oracle-factory revisar {ident}"]
        if corte is not None:
            return f"oracle-factory revisar {ident}"
        return pedido_de_revision(ident)
    if rev.get("decision") != "aprobar" or rev.get("hallazgos_abiertos") != 0:
        return f"corregí lo que pidió la revisión y commitealo; después: {pedido_de_revision(ident)}"
    # Revisión vigente y aprobada: ¿se juzgaron estos hechos?
    oracle = estado.get("oracle") or {}
    juzgados = ruta_del_registro(oracle.get("hechos"))
    varios = hechos_registrados(oracle)
    if len(varios) > 1 and not juicio_vigente(oracle, contexto_producto()):
        return comando_juzgar(ident, varios)
    try:  # hechos del candidato que no son los juzgados: juzgarlos
        del_candidato = hechos_del_candidato(ident)
        # También si los hechos registrados no son una ruta: los del candidato se juzgan sin pedir otra.
        if juzgados is None or sha256(ruta_segura(del_candidato).read_bytes()) != oracle.get("hechos_sha256"):
            return f"oracle-factory juzgar {ident}"
    except FactoryError:
        pass
    if juicio_vigente(oracle, contexto_producto()):
        if oracle.get("codigo") != 0:
            return f"corregí la evidencia o el producto; después: oracle-factory juzgar {ident}"
        if not pendientes_actuales(carpeta, estado):
            return f"oracle-factory cerrar {ident}"
        return f"resolvé lo pendiente que lista estado; después: oracle-factory cerrar {ident}"
    if juzgados is not None and juzgados.is_file():  # hechos que siguen ahí, con un juicio que ya no vale: juzgar de nuevo
        try:
            if juzgados.resolve() == hechos_del_candidato(ident).resolve():
                return f"oracle-factory juzgar {ident}"
        except FactoryError:
            pass
        return f"oracle-factory juzgar {ident} --con {shlex.quote(oracle['hechos'])}"
    return f"oracle-factory juzgar {ident} --con RUTA_DE_HECHOS"


def siguiente(identificador: str, fase: str | None = None) -> None:
    paso, *alternativas = pasos(identificador) or [None]
    if paso:
        print("Próximo paso: " + paso)
    for alternativa in alternativas:
        print(f"También: {alternativa}" + (" — para aceptarlos como riesgo o descartarlos, con motivo"
                                          if alternativa.startswith("oracle-factory revisar ") else ""))


def ofrecer_siguiente(identificador: str) -> int:
    """En una terminal y sin --agente, ofrece ejecutar el próximo paso si es un comando completo."""
    comandos = [p for p in pasos(identificador)
                if p.startswith("oracle-factory ") and not re.search(r"\b[A-Z][A-Z_]{2,}\b", p)]
    if not comandos or AGENTE or not terminal_interactiva() or not sys.stdout.isatty():
        return 0
    eleccion = elegir("¿Seguís?", [*((f"Ejecutar «{p}»", "como si lo escribieras; si es una decisión, abre su propio menú")
                                    for p in comandos), ("Salir", "no ejecuta nada")])
    if eleccion is None or eleccion >= len(comandos):
        return 0
    return main(["--proyecto", str(ROOT), *shlex.split(comandos[eleccion])[1:]])


def listar(fase: str | None = None, abiertos: bool = False, cerrados: bool = False) -> None:
    ruta_segura(CHANGES)
    if not CHANGES.exists():
        print('No hay cambios Factory. Empezá con oracle-factory init.')
        return
    encontrados = 0
    for carpeta in sorted(CHANGES.iterdir()):
        if not ID_RE.fullmatch(carpeta.name):
            continue
        ruta_segura(carpeta)
        if not (ruta_registro(carpeta)).exists():
            continue
        _, estado = leer(carpeta.name)
        if (fase and estado['fase'] != fase) or (abiertos and estado['fase'] in ('cerrada', 'abandonada')) \
                or (cerrados and estado['fase'] != 'cerrada'):
            continue
        print(f"{carpeta.name}  {estado['fase']}{' (archivado)' if estado.get('archivo') else ''}  {estado['titulo']}")
        encontrados += 1
    if not encontrados:
        print('No hay cambios que coincidan con el filtro.' if (fase or abiertos or cerrados)
              else 'No hay cambios Factory; las tareas del tracker por sí solas no son cambios Factory.')
    print(f'Acuerdos: {CHANGES}')


def main(argv: list[str] | None = None) -> int:
    global ROOT, CHANGES, AGENTE
    args = construir_parser().parse_args(argv)
    if args.proyecto is not None:
        ROOT = args.proyecto.expanduser().resolve()
    else:
        actual = Path.cwd().resolve()
        ROOT = actual if args.comando == "init" else (estructura.raiz_del_proyecto(actual) or actual)
        if ROOT != actual:
            print(f"Proyecto: {ROOT} (encontrado desde {actual})", file=sys.stderr)
    CHANGES = ROOT / "openspec" / "changes"
    AGENTE = (args.agente or "").strip() or None
    try:
        if args.comando != "init" and not ROOT.is_dir():
            raise FactoryError("el proyecto no existe; ejecutá primero init")
        if (args.comando != "init" and not (ROOT / estructura.DIR).is_symlink()
                and (ROOT / estructura.DIR / "config.json").is_file()):
            proyecto_oracle()  # una carpeta de Oracle mal configurada falla antes de que el comando escriba nada
        if args.comando == "init": inicializar(args.oracle)
        elif args.comando == "ejemplo": copiar_ejemplo(args.destino)
        elif args.comando == "nuevo": nuevo(args.titulo, args.capacidad, args.con_ejemplo, args.modo, args.sufijo, args.idioma)
        elif args.comando == "modo": cambiar_modo(args.id, args.nuevo_modo)
        elif args.comando == "listar": listar(args.fase, args.abiertos, args.cerrados)
        elif args.comando == "migrar": comando_migrar(args.verificar)
        elif args.comando == "archivar": archivar()
        elif args.comando == "log": comando_log(args.id, args.json)
        elif args.comando == "kb" and args.accion == "revisada":
            if not args.nota:
                raise FactoryError("kb revisada espera la nota: oracle-factory kb revisada kb/notas/NOMBRE.md")
            kb_revisada(args.nota)
        elif args.comando == "kb": comando_kb(args.verificar)
        elif args.comando == "por-que": por_que(args.referencia, args.json)
        elif args.comando == "tomar": tomar(args.id, args.con, args.relevo)
        elif args.comando == "soltar": soltar(args.id)
        elif args.comando == "mensaje": mensaje(args.id, args.texto, args.de)
        elif args.comando == "hooks": print(instalar_hook()); print(instalar_union())
        elif args.comando == "unir-registro": return unir_registro(args.base, args.nuestro, args.suyo)
        elif args.comando == "unir-generado": return 0  # lo generado se queda como está y se rehace en el post-merge
        elif args.comando == "rehacer-generado": rehacer_generado()
        elif args.comando == "decidir-union": decidir_union(args.id, args.campo, args.cual)
        elif args.comando == "trailer": poner_trailer(args.archivo)
        elif args.comando == "tablero": imprimir_json(tablero_mod.armar(sys.modules[__name__]))
        elif args.comando == "resumen" and args.json:
            if args.verificar or args.salida or args.ver:
                raise FactoryError("--json no se combina con --verificar, --salida ni --ver")
            imprimir_json(resumen.datos(*insumos_resumen()))
        elif args.comando == "resumen": comando_resumen(args.verificar, args.salida, args.ver)
        elif args.comando == "pedir-revision": pedir_revision(args.id, args.revisor, args.pedir, args.base)
        elif args.comando == "trazabilidad": comando_trazabilidad(args.id, args.json, args.base)
        elif args.comando == "donde" and args.json: imprimir_json(datos_donde(args.id, args.candidato))
        elif args.comando == "donde": comando_donde(args.id, args.candidato)
        elif args.comando == "ruta": comando_ruta(args.id, args.tipo)
        elif args.comando == "buscar": comando_buscar(args.texto, args.maximo)
        elif args.comando == "procedencia": comando_procedencia(args)
        elif args.comando == "preguntar": comando_preguntar(args)
        elif args.comando == "agentes": comando_agentes(args.verificar)
        elif args.comando == "mcp": return mcp_mod.servir(ROOT, sys.stdin, sys.stdout, __version__)
        elif args.comando == "medir" and args.confirmar:
            if args.requisito or args.medida or args.listar:
                raise FactoryError("--confirmar no se combina con --requisito, --medida ni --listar")
            confirmar_medidas(args.id)
        elif args.comando == "revisar":
            if AGENTE:
                if not (args.decision and args.motivo and args.motivo.strip()):
                    raise FactoryError("con --agente, revisar propone: indicá --decision y --motivo")
                proponer_revision(args.id, args.decision, args.motivo.strip())
            elif args.decision or args.motivo:
                raise FactoryError("--decision y --motivo son la propuesta de un agente; una persona elige en el menú")
            else:
                revisar_paso_a_paso(args.id)
        elif args.comando == "medir": medir(args.id, requisito_id=args.requisito, medidas=args.medida, listar_opciones=args.listar, sin_medir=args.sin_medir, quitar_sin_medir=args.quitar_sin_medir)
        elif args.comando == "aprobar-spec": aprobar_spec(args.id)
        elif args.comando == "importar": importar(args.id)
        elif args.comando == 'revision-preparar': preparar_revision(args.id)
        elif args.comando == "revision": revisar(args.id, ROOT / args.informe, args.revisor, args.decision, args.hallazgos_abiertos,
                                                formato=args.formato, decisiones=ROOT / args.decisiones if args.decisiones else None)
        elif args.comando == "juzgar": juzgar(args.id, [ROOT / c for c in args.con] if args.con else [hechos_del_candidato(args.id)])
        elif args.comando == "cerrar": cerrar(args.id)
        elif args.comando == "abandonar": abandonar(args.id, args.motivo)
        elif args.comando == "estado" and args.json: imprimir_json(datos_estado(args.id))
        elif args.comando == "estado":
            mostrar(args.id)
            return ofrecer_siguiente(args.id)
        refrescar_kb(args.comando, getattr(args, "id", None))
        return 0
    except ModuleNotFoundError as e:
        if not (e.name or "").startswith("oracle_metalenguaje"):
            raise
        print(f"FACTORY BLOQUEADA: falta oracle-metalenguaje en el intérprete {sys.executable}. En un clon de Factory, usá "
              "su entorno: .venv/bin/oracle-factory (en cualquier shell) o python fabrica.py; en otro proyecto, instalá Factory con "
              "uv tool install --with-executables-from oracle-metalenguaje,oracle-task oracle-factory", file=sys.stderr)
        return 1
    except (FactoryError, OSError, json.JSONDecodeError, EOFError) as e:
        print(f"FACTORY BLOQUEADA: {e}", file=sys.stderr)
        return 1


# Lo movido a otros módulos sigue disponible acá, con el mismo nombre (el código movido lee `cli` al usarlo).
from .parser import (  # noqa: E402
    construir_parser,
)
from .flujo_revision import (  # noqa: E402
    _revisar_paso_a_paso,
    anotar_intento,
    aviso_lanzamientos,
    aviso_revision,
    aviso_sin_autor,
    aviso_sin_medir,
    base_vacia,
    bytes_json,
    corte_del_candidato,
    exclusiones_del_paquete,
    guardar_par_revision,
    lanzamientos_abiertos,
    leer_regular,
    material_del_candidato,
    motivo_armado,
    pedido_de_revision,
    pedir_revision,
    preparar_revision,
    producto_excluido,
    proponer_revision,
    revisar,
    revisar_guiado,
    revisar_paso_a_paso,
    sin_medir_con_medidas,
    turno_de_pedidos,
)
from .flujo_medidas import (  # noqa: E402
    archivos_de_medidas,
    bloqueo_medidas,
    catalogo_del_proyecto,
    catalogos_cambiados,
    con_huellas,
    confirmar_medidas,
    describir_cambios,
    huellas_de_catalogo,
    inventario_medidas,
    medidas_en_uso,
    medidas_sin_decision,
    medir,
    nombre_de_archivo,
    propuestas_confirmables,
    registrar_medidas,
)
from .lecturas import (  # noqa: E402
    _fecha_corta,
    _json_de_revision,
    _lista,
    actualizar_kb,
    actualizar_resumen,
    archivos_de,
    aviso_notas,
    comando_donde,
    comando_kb,
    comando_resumen,
    comando_trazabilidad,
    datos_donde,
    datos_estado,
    datos_trazabilidad,
    dentro_del_tramo,
    escribir_kb,
    generadas_en_disco,
    insumos_resumen,
    kb_revisada,
    nombres,
    por_que,
    rangos,
    refrescar_kb,
    ruta_resumen,
    situacion_requisitos,
    texto_resumen,
    tocados_por,
)

if __name__ == "__main__":
    raise SystemExit(main())
