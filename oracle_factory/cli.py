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
from . import robusto
from . import resumen
from . import revisores as revisores_mod
from . import sensor as sensor_mod
from . import contexto as contexto_mod
from . import estructura
from . import migracion
from . import preparacion
from . import trazabilidad as trazabilidad_mod
from . import autopilot
from . import conductor
from . import modos
from . import plantillas
from . import alarmas as alarmas_mod
from . import almacenes
from . import skill as skill_mod
from . import osv as osv_mod
from . import pruebas as pruebas_mod
from . import procedencia as procedencia_mod
from . import puerta as puerta_mod
from . import despliegue as despliegue_mod
from . import verificar as verificar_mod
from . import revision as documentos_revision
from . import tablero as tablero_mod
from . import kb as kb_mod
from . import agentes as agentes_mod
from . import mcp as mcp_mod
from . import rag as rag_mod
from . import unir as unir_mod
from pathlib import Path, PurePosixPath, PureWindowsPath

ROOT = Path.cwd().resolve()  # la raíz de los REGISTROS (con --registros, el almacén; si no, la del producto)
PRODUCTO: Path | None = None  # la raíz del producto, sólo con registros aparte (main la fija y la suelta al terminar)
REGISTROS = ROOT  # = ROOT, con el nombre de la spec
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
    try:
        estado = json.loads(datos.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as e:
        raise FactoryError(f"el registro {archivo} no es JSON válido ({e}): restauralo desde Git (git restore)") from e
    problema = robusto.forma_invalida(estado)
    if problema:
        raise FactoryError(f"el registro {archivo} {problema}: restauralo desde Git (git restore)")
    return carpeta, sin_eventos_raros(estado, identificador)


def sin_eventos_raros(estado, identificador: str):
    """El registro con sólo los eventos que son objetos (un `eventos` que no es una lista, vacío), con un aviso una vez por cambio.
    Sólo se lee: el archivo no se toca, y un comando que guarda el registro no vuelve a escribir lo que se ignoró."""
    if not isinstance(estado, dict) or "eventos" not in estado:
        return estado
    eventos = estado["eventos"]
    ignorados = 1 if not isinstance(eventos, list) else sum(not isinstance(e, dict) for e in eventos)
    if ignorados:
        estado = {**estado, "eventos": [e for e in eventos if isinstance(e, dict)] if isinstance(eventos, list) else []}
        if ("eventos", identificador) not in AVISADOS:
            AVISADOS.add(("eventos", identificador))
            print(f"Aviso: el registro de {identificador} trae {ignorados} evento(s) que no son objetos (o un «eventos» que no es una lista): "
                  "los ignoro al leer y no se vuelven a escribir si un comando guarda el registro.", file=sys.stderr)
    return estado


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
              "idioma": datos.get("idioma", plantillas.POR_DEFECTO),
              "autonomia": datos.get("autonomia", {}), "sensor": datos.get("sensor")}
    try:
        config["sensor"] = sensor_mod.validar(config["sensor"])
    except ValueError as e:
        raise FactoryError(f"{ruta}: {e}; por ejemplo: {sensor_mod.EJEMPLO}") from e
    try:
        config["autonomia"] = modos.autonomia(config["autonomia"])
    except ValueError as e:
        raise FactoryError(f"{ruta}: {e}") from e
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
                           "confiar_escalares (true/false), rag (sus embeddings, ver oracle-factory preguntar) idioma (es o en, el de las plantillas de un cambio nuevo) y sensor")
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


def git_producto(args: list[str]) -> subprocess.CompletedProcess[str]:
    """Git sobre el producto: `ejecutar` sin almacén aparte; con almacén, en su repo y sin escrituras opcionales."""
    if PRODUCTO is None:
        return ejecutar(args)
    return subprocess.run(args, cwd=PRODUCTO, env={**os.environ, "GIT_OPTIONAL_LOCKS": "0"}, capture_output=True, text=True,
                          encoding="utf-8", check=False)


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


def documentos_o_nada(carpeta: Path, estado: dict) -> dict | None:
    """Las huellas actuales de la propuesta y la spec, o None si no corresponde o no se pueden leer (para mostrar, sin fallar).

    Antes de leer nada se comprueba que las dos rutas estén dentro del proyecto y sin enlaces simbólicos, y un cambio cerrado o
    abandonado no lee nada."""
    if estado.get("fase") in ("cerrada", "abandonada"):
        return None
    try:
        for ruta in (carpeta / "proposal.md", ROOT / estado["spec"]):
            pruebas_mod.exigir_dentro(ROOT, ruta)
        return documentos(carpeta, estado)
    except (OSError, KeyError, TypeError, ValueError, procedencia_mod.ProcedenciaError):
        return None


def exigir_spec(carpeta: Path, estado: dict) -> None:
    aprobacion = estado.get("spec_aprobada") or {}
    if not aprobacion:
        raise FactoryError("primero hay que aceptar la propuesta y la spec (aprobar-spec)")
    if aprobacion.get("documentos") != documentos(carpeta, estado):
        raise FactoryError("la propuesta/spec cambió o su aprobación es antigua; renová la aceptación")


def es_producto(nombre: str) -> bool:
    """Si un archivo (ruta relativa) cuenta en la huella del producto. Con almacén aparte, todo el repo del producto lo es."""
    if PRODUCTO is not None:
        return True
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
    locales = git_producto(["git", "diff", "--name-only", "HEAD"]).stdout.splitlines()
    locales += git_producto(["git", "ls-files", "--others", "--exclude-standard"]).stdout.splitlines()
    return [n for n in locales if es_producto(n)]


def candidatos_anteriores(identificador: str, sha: str | None) -> list[str]:
    """Los candidatos del cambio con informes de revisores, ancestros de HEAD y distintos de `sha`, del más viejo al más nuevo."""
    base = ROOT / estructura.DIR / "cambios" / identificador / "candidatos"
    if base.is_symlink() or not base.is_dir():
        return []
    con_informes = {p.name for p in base.iterdir() if p.is_dir() and not p.is_symlink() and any((p / "revision").glob("*.json"))}
    orden = [c[:7] for c in git_producto(["git", "rev-list", "HEAD"]).stdout.split()]
    return [c for c in reversed(orden) if c in con_informes and c != sha]


def candidato_vigente(identificador: str) -> str | None:
    """El commit (7 caracteres) del candidato con carpeta propia más cercano a HEAD, si el producto no cambió desde él.

    La evidencia se produce sobre el commit de producto y se guarda en un commit posterior: ese commit no cambia el producto,
    así que el candidato sigue siendo el anterior.
    """
    base = ROOT / estructura.DIR / "cambios" / identificador / "candidatos"
    if base.is_symlink() or not base.is_dir():
        return None
    existentes = {p.name for p in base.iterdir() if p.is_dir() and not p.is_symlink()  # con almacén: sólo con su evidencia
                  and (PRODUCTO is None or ((p / "evidencia").is_dir() and not (p / "evidencia").is_symlink()))}
    # Un cambio de producto sin commit (modificado, en el índice o nuevo) también deja viejo a cualquier candidato.
    if cambios_locales_de_producto():
        return None
    for commit in git_producto(["git", "rev-list", "HEAD"]).stdout.split():
        if commit[:7] in existentes:
            cambiados = git_producto(["git", "diff", "--name-only", commit, "HEAD"]).stdout.splitlines()
            return None if any(es_producto(n) for n in cambiados) else commit[:7]
    return None


def hechos_del_candidato(identificador: str) -> Path:
    """`hechos.json` de la evidencia del candidato vigente; FactoryError con la ruta esperada si no está."""
    leer(identificador)
    sha = candidato_vigente(identificador) or git_producto(["git", "rev-parse", "HEAD"]).stdout.strip()[:7]
    hechos = estructura.ruta_canonica(ROOT, identificador, "evidencia", sha) / "hechos.json"
    if not ruta_segura(hechos).is_file():
        raise FactoryError(f"no encuentro los hechos del candidato: {hechos.relative_to(ROOT)}. Generalos ahí "
                           f"(oracle-factory ruta {identificador} evidencia) o indicá --con RUTA")
    return hechos


def contexto_producto() -> dict:
    """Vincula revisión y juicio con HEAD y archivos no ignorados, incluidos los nuevos.

    Los registros generados del flujo no son código del producto; las specs y las
    medidas Oracle sí forman parte de lo revisado. No sigue enlaces simbólicos. Dentro de `contexto.producto_fijo` vale la huella fijada.
    """
    if (fija := contexto_mod.huella_fija()) is not None:
        return fija
    head = git_producto(["git", "rev-parse", "--verify", "HEAD"])
    lista = git_producto(["git", "ls-files", "-z", "--cached", "--others", "--exclude-standard"])
    if head.returncode or lista.returncode:
        raise FactoryError("la revisión necesita un repositorio Git con al menos un commit")
    archivos = [[n, dato_de_archivo(n, (PRODUCTO or ROOT) / n)] for n in sorted(set(lista.stdout.split("\0")) - {""}) if es_producto(n)]
    return {"head": head.stdout.strip(), "archivos_sha256": sha256(json.dumps(archivos).encode())}


def dato_de_archivo(nombre: str, p: Path) -> list:
    if p.is_symlink():
        return ["enlace", str(p.readlink())]
    if p.is_file():
        return ["archivo", sha256(p.read_bytes()), bool(p.stat().st_mode & 0o111)]
    if p.is_dir():
        raise FactoryError("los submódulos/directorios Git requieren revisión externa explícita: " + nombre)
    return ["ausente"]


def contexto_del_cambio(identificador: str) -> dict:
    """La huella de lo revisado de un cambio: la del producto y, con almacén aparte, la de sus archivos en el almacén."""
    contexto = contexto_producto()
    return contexto if PRODUCTO is None else almacenes.con_el_cambio(sys.modules[__name__], identificador, contexto)


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


def drivers_de_union() -> list[tuple[str, str]]:
    """[(clave de configuración de Git, valor)] de los drivers de unión de Factory: `hooks` los escribe en el clon; `sincronizar`
    los pasa con `git -c` en cada orden."""
    py = shlex.quote(sys.executable)
    codigo = "'import sys; from oracle_factory.cli import main; sys.exit(main())'"
    return [par for nombre, orden, que in (("oracle-factory-registro", "unir-registro %O %A %B %P", "une el registro de un cambio"),
                                           ("oracle-factory-generado", "unir-generado %O %A %B %P", "deja lo generado para rehacerlo"))
            for par in ((f"merge.{nombre}.name", f"Factory: {que}"), (f"merge.{nombre}.driver", f"{py} -c {codigo} {orden}"))]


LLAMADA_PUERTA = ("{py} -c 'import sys; from oracle_factory.cli import main; sys.exit(main())' puerta --hook")


def argumentos_de_raiz() -> list[str]:
    return ["--proyecto", str(PRODUCTO), "--registros", str(ROOT)] if PRODUCTO else ["--proyecto", str(ROOT)]


def verificar_en_proceso(argv: list[str]) -> tuple[int, str]:
    """Corre un comando de Factory en este proceso con la salida capturada; (código, salida). Para las verificaciones de la puerta."""
    global ROOT, CHANGES, AGENTE, PRODUCTO, REGISTROS
    guardado = (ROOT, CHANGES, AGENTE, PRODUCTO, REGISTROS)
    salida = io.StringIO()
    try:
        with contextlib.redirect_stdout(salida), contextlib.redirect_stderr(salida):
            codigo = main([*argumentos_de_raiz(), *argv])
    except SystemExit as e:
        codigo = e.code if isinstance(e.code, int) else 1
    finally:
        ROOT, CHANGES, AGENTE, PRODUCTO, REGISTROS = guardado
    return codigo or 0, salida.getvalue()


def comando_puerta(en_hook: bool, rango: list[str]) -> int:
    """La puerta local de salida. Sale con CODIGO_BLOQUEO si encuentra algo; con otro código distinto de cero, si no pudo mirar.

    Con almacén aparte, lo que se empuja es del producto (git_producto) y las verificaciones miran los registros del almacén, salvo
    la guía de agentes, que está en el producto."""
    def existe(archivo: str) -> bool:
        return ((PRODUCTO or ROOT) if archivo in almacenes.GUIA else ROOT).joinpath(archivo).exists()

    try:
        if en_hook:
            rangos = puerta_mod.rangos_del_hook(sys.stdin.read(), git_producto)
        elif rango:
            rangos = [rango]
        else:
            arriba = git_producto(["git", "rev-parse", "--verify", "--quiet", "@{upstream}"])
            rangos = [["@{upstream}..HEAD"] if arriba.returncode == 0 else ["HEAD", "--not", "--remotes"]]
        if not rangos:
            print("Puerta local de salida: nada nuevo que publicar.")
            return 0
        codigo, texto = puerta_mod.correr(git_producto, rangos, verificar_en_proceso, existe)
        print(texto, end="")
        return codigo
    except Exception as e:  # noqa: BLE001 — una puerta rota avisa y deja pasar; sólo bloquea cuando encuentra algo
        print(f"Aviso: la puerta local de salida no pudo comprobar ({type(e).__name__}: {e}); el push sigue.", file=sys.stderr)
        return 2


def comando_destinos(como_json: bool, sin_consultar: bool) -> None:
    """Los destinos del proyecto con su estado; --json es el contrato que lee el tablero."""
    try:
        decl = despliegue_mod.cargar(ROOT)
    except despliegue_mod.DeclaracionInvalida as e:
        raise FactoryError(str(e)) from e
    lista = despliegue_mod.estados(ROOT, decl, consultar=not sin_consultar)
    historia = despliegue_mod.registros(ROOT)
    ultima = despliegue_mod.resumen_corrida(historia[-1] if historia else None)
    if como_json:
        print(json.dumps({"version": 1, "rama": decl["rama"], "destinos": lista, "ultima_corrida": ultima}, ensure_ascii=False, indent=1))
        return
    print(f"Destinos de despliegue (rama {decl['rama']}, política ante un fallo: {decl['politica']}):")
    for d in lista:
        deps = f"  depende de {', '.join(d['depende_de'])}" if d["depende_de"] else ""
        marca = {True: "desactualizado", False: "al día", "desconocido": "versión desconocida"}[d["desactualizado"]]
        print(f"  {d['nombre']} [{d['tipo']}]  {d['estado']}  ({marca}){deps}")
    print("Última corrida: " + (f"{ultima['id']} — {ultima['resultado']}: {ultima['motivo']} (autorizó {ultima['autorizo']})" if ultima else "ninguna todavía"))


# Qué comando de Factory aplica hoy la autonomía de cada etapa; integración y publicación se hacen con git y gh.
APLICA_AUTONOMIA = {"construccion": "oracle-factory modo ID MODO", "integracion": None, "publicacion": None,
                    "produccion": "oracle-factory desplegar --autorizar"}


def filas_autonomia() -> list[dict]:
    """Las cuatro etapas con su modo, quién decide por la vía de agente y si hoy hay un comando que la aplique."""
    config = config_proyecto()
    quien = {"autonomo": "agente", "confirmacion": "persona (el agente propone)", "funcional": "persona en lo funcional"}
    filas = [{"etapa": "construccion", "modo": config["modo_por_defecto"], "decide": quien[config["modo_por_defecto"]]}]
    filas += [{"etapa": e, "modo": m, "decide": "agente" if modos.via_agente_etapa(m) == "decide" else "persona"}
              for e, m in config["autonomia"].items()]
    return [{**f, "aplica_hoy": APLICA_AUTONOMIA[f["etapa"]] is not None, "comando": APLICA_AUTONOMIA[f["etapa"]]} for f in filas]


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


def cambios_abiertos() -> list[str]:
    if not CHANGES.is_dir():
        return []
    return [c.name for c in sorted(CHANGES.iterdir()) if ID_RE.fullmatch(c.name) and ruta_registro(c).exists()
            and leer(c.name)[1].get("fase") not in ("cerrada", "abandonada")]


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
        actual = contexto_del_cambio(estado.get("id"))
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
        pruebas_mod.excepciones(contenido)
    except (modos.TipoInvalido, pruebas_mod.PruebasInvalidas) as e:
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
        pruebas_mod.excepciones(spec.read_text(encoding="utf-8"))
    except (modos.TipoInvalido, pruebas_mod.PruebasInvalidas) as e:
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


DESACTUALIZADO = " desactualizado respecto del producto"


def conflictos_de_union(estado: dict, salvo: str | None = None) -> list[str]:
    """Lo que dos ramas decidieron distinto y nadie eligió todavía (H5 de la auditoría): frena hasta que una persona lo
    resuelva. Con `salvo`, una acción, se dejan afuera los conflictos que esa misma acción resuelve."""
    caminos = unir_mod.resueltos_por(salvo) if salvo else ()
    return [f"al unir dos ramas, {x.get('campo')} quedó con dos valores y nadie eligió: "
            f"{unir_mod.como_resolver(x.get('campo', ''), estado.get('id', 'ID'))}"
            for x in estado.get("pendientes_de_union") or [] if not (caminos and unir_mod.resuelto(x, caminos))]


def pendientes_actuales(carpeta: Path, estado: dict) -> list[str]:
    faltan = pendientes(estado) + conflictos_de_union(estado)
    faltan += [f"medidas de {rid}: {motivo}" for rid, motivo in medidas_sin_decision(estado)]
    try:
        exigir_spec(carpeta, estado)
    except (FactoryError, OSError) as e:
        faltan.append(str(e))
    if estado.get("revision") or estado.get("oracle"):
        try:
            contexto = contexto_del_cambio(carpeta.name)
            for nombre in ("revision", "oracle"):
                registro = estado.get(nombre)
                if registro and not mismo_producto(registro.get("contexto"), contexto):
                    faltan.append(nombre + DESACTUALIZADO)
        except (FactoryError, OSError) as e:
            faltan.append(str(e))
    faltan += problemas_de_revision(estado) + sensor_mod.pendientes(carpeta.name, estado)
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


def fusionar_capacidad(estado: dict) -> tuple[str, str]:
    """(capacidad, spec consolidada): fusiona la spec del cambio leyendo el índice recién, bajo el bloqueo de la capacidad."""
    with robusto.bloqueo_capacidad(ROOT, capacidad_destino(estado["capacidad"])):
        capacidad, indice = plan_archivo(estado)
        return capacidad, escribir_archivo(capacidad, indice)


def marcar_archivado(estado: dict, capacidad: str, spec: str, forma: str) -> None:
    estado["archivo"] = {"capacidad": capacidad, "spec": spec, "cuando": ahora()}
    evento(estado, "archivado", forma=forma, capacidad=capacidad, spec=spec)


SOLO_LECTURA = {"estado", "donde", "log", "tablero", "por-que", "kb", "resumen", "listar", "ruta", "buscar", "trazabilidad",
               "trailer", "hooks", "init", "ejemplo", "preguntar", "unir-registro", "unir-generado", "rehacer-generado",
               "agentes", "puerta", "skill", "destinos", "desplegar", "verificar"}  # agentes escribe AGENTS.md y skill --instalar un archivo del proyecto, no el registro: no hay kb que refrescar


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
        capacidad, spec = fusionar_capacidad(estado)
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
    for aviso in avisos_head(estado) + sensor_mod.avisos(identificador, estado):
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
    capacidad, spec_consolidada = fusionar_capacidad(estado)
    marcar_archivado(estado, capacidad, spec_consolidada, forma)
    guardar(carpeta, estado)
    print(f"Spec fusionada en {spec_consolidada}.")
    actualizar_resumen()
    print(p.stdout.strip() or "Tarea cerrada.")
    if cierre["tipo_actor"] == "agente":
        print(f"El cierre lo decidió el agente {cierre['actor']} en modo autónomo; las demás decisiones, como indica estado.")


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


def main(argv: list[str] | None = None) -> int:
    """La CLI. Si la salida estándar se cierra a mitad (`oracle-factory listar | head -1`), sale con 141 en silencio."""
    try:
        codigo = _main(argv)
        sys.stdout.flush()  # adentro: una tubería rota se ve acá y no al cerrar Python («Exception ignored…»)
        return codigo
    except BrokenPipeError:
        try:  # lo que quede en el búfer va a /dev/null: al salir, Python no vuelve a fallar al vaciarlo
            os.dup2(os.open(os.devnull, os.O_WRONLY), sys.stdout.fileno())
        except (OSError, ValueError, AttributeError):
            pass
        return 141


def _main(argv: list[str] | None = None) -> int:
    global ROOT, CHANGES, AGENTE, PRODUCTO, REGISTROS
    args = construir_parser().parse_args(argv)
    if args.proyecto is not None:
        ROOT = args.proyecto.expanduser().resolve()
    else:
        actual = Path.cwd().resolve()
        ROOT = actual if args.comando == "init" else (estructura.raiz_del_proyecto(actual) or actual)
        if ROOT != actual:
            print(f"Proyecto: {ROOT} (encontrado desde {actual})", file=sys.stderr)
    PRODUCTO = previo = None
    AGENTE = (args.agente or "").strip() or None
    try:
        if args.comando == "migrar" and args.almacen is not None:  # también opera sobre el producto, que todavía tiene sus registros
            return almacenes.migrar(sys.modules[__name__], args.almacen, args.verificar)
        if args.comando in ("conectar", "desconectar"):  # operan sobre el producto: no se redirigen a su almacén
            return almacenes.comando(sys.modules[__name__], args.comando, getattr(args, "almacen", None), getattr(args, "json", False))
        registros = args.registros.expanduser().resolve() if args.registros is not None else almacenes.conectado(sys.modules[__name__])
        if args.registros is None:
            if registros is None:
                almacenes.exigir_conexion(sys.modules[__name__])  # un producto marcado sin conexión no trabaja
            else:
                almacenes.avisar_si_no_coincide(almacenes.raiz_git(ROOT) or ROOT, registros)
        if registros is not None and registros != ROOT:
            PRODUCTO, ROOT = almacenes.raiz_git(ROOT) or ROOT, registros  # ROOT sigue siendo «donde están los registros»
        REGISTROS = ROOT
        CHANGES = ROOT / "openspec" / "changes"
        if PRODUCTO and (ROOT.is_relative_to(PRODUCTO) or PRODUCTO.is_relative_to(ROOT)):  # un almacén dentro del producto (o al revés) lo ensucia
            raise FactoryError(f"--registros ({ROOT}) y el producto ({PRODUCTO}) no pueden estar uno dentro del otro: el almacén de registros va "
                               "en una carpeta aparte, para que el repo del producto no reciba nada de Factory. No se escribió nada.")
        if PRODUCTO and args.comando == "hooks":
            raise FactoryError("con registros aparte no se instala ningún hook en el repo del producto: los commits de un cambio "
                               "se deducen de sus candidatos (oracle-factory log ID). No se escribió nada.")
        if args.comando != "init" and not ROOT.is_dir():
            raise FactoryError("el proyecto no existe; ejecutá primero init")
        previo = almacenes.foto(ROOT) if PRODUCTO else None  # con almacén aparte, lo que el comando escriba se commitea al terminar
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
        elif args.comando == "puerta": return comando_puerta(args.hook, args.rango)
        elif args.comando == "verificar": return verificar_mod.comando(sys.modules[__name__], args.json)
        elif args.comando == "destinos": comando_destinos(args.json, args.sin_consultar)
        elif args.comando == "autonomia": return comando_autonomia(args.etapa, args.modo, args.json)
        elif args.comando == "autopilot": return comando_autopilot(args.id, args.json, args.ejecutar, args.lanzar, args.max_pasos, args.max_minutos, args.entorno)
        elif args.comando == "desplegar": return comando_desplegar(args.simular, args.autorizar, args.commit, args.destino, args.cambios)
        elif args.comando == "unir-registro": return unir_registro(args.base, args.nuestro, args.suyo)
        elif args.comando == "unir-generado": return 0  # lo generado se queda como está y se rehace en el post-merge
        elif args.comando == "rehacer-generado": rehacer_generado()
        elif args.comando == "sincronizar": return almacenes.sincronizar(sys.modules[__name__])
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
        elif args.comando == "agentes": comando_agentes(args.verificar, args.en_el_repo)
        elif args.comando == "skill": return comando_skill(args.instalar, args.forzar)
        elif args.comando == "mcp": return mcp_mod.servir(PRODUCTO or ROOT, sys.stdin, sys.stdout, __version__,
                                                          registros=ROOT if args.registros is not None else None)
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
        elif args.comando == "evidencia": sensor_mod.producir(args.id, args.extra[1:] if args.extra[:1] == ["--"] else args.extra)
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
    except BrokenPipeError:
        raise  # no es un error de Factory: lo resuelve main
    except (FactoryError, OSError, json.JSONDecodeError, EOFError) as e:
        print(f"FACTORY BLOQUEADA: {e}", file=sys.stderr)
        return 1
    finally:
        if PRODUCTO:
            almacenes.commitear(sys.modules[__name__], ROOT, previo, args.comando, getattr(args, "id", None))
        PRODUCTO = None


# Lo movido a otros módulos sigue disponible acá, con el mismo nombre (el código movido lee `cli` al usarlo).
from .ganchos import (  # noqa: E402
    cambio_del_commit,
    commits_del_cambio,
    escribir_atributos,
    hook_pre_push,
    instalar_hook,
    instalar_pre_push,
    instalar_union,
    lineas_para_encadenar,
    poner_trailer,
    rehacer_generado,
    unir_registro,
)
from .acciones import (  # noqa: E402
    abandonar,
    aviso_union,
    cambiar_modo,
    decidir_union,
)
from .proyecto import (  # noqa: E402
    comando_agentes,
    comando_autonomia,
    comando_autopilot,
    comando_buscar,
    comando_desplegar,
    comando_migrar,
    comando_preguntar,
    comando_procedencia,
    comando_ruta,
    comando_skill,
    inicializar,
    listar,
    plan_ejemplo,
)
from .parser import (  # noqa: E402
    construir_parser,
)
from .flujo_revision import (  # noqa: E402
    _revisar_paso_a_paso,
    anotar_intento,
    artefactos_de,
    aviso_lanzamientos,
    aviso_revision,
    aviso_sin_autor,
    aviso_sin_medir,
    base_vacia,
    base_vacia_en,
    bytes_json,
    como_seguir,
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
    juzgar,
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
    _pasos,
    actualizar_kb,
    actualizar_resumen,
    archivos_de,
    archivos_faltantes,
    aviso_ignorados,
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
    frenos_del_cambio,
    generadas_en_disco,
    insumos_resumen,
    kb_revisada,
    linea_quien,
    mostrar,
    nombres,
    ofrecer_siguiente,
    pasos,
    por_que,
    proximo_paso,
    quien_del_cambio,
    rangos,
    refrescar_kb,
    ruta_resumen,
    segundo_revisor_del_cambio,
    siguiente,
    situacion_requisitos,
    texto_resumen,
    tocados_por,
)

if __name__ == "__main__":
    raise SystemExit(main())
