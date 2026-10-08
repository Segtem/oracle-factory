#!/usr/bin/env python3
"""Orquestación mínima con aprobaciones humanas explícitas."""
from __future__ import annotations

import argparse
import contextlib
import io
import datetime as dt
import getpass
import hashlib
import json
import os
import shutil
import tempfile
from contextlib import contextmanager
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
from . import modos
from . import revision as documentos_revision
from pathlib import Path

ROOT = Path.cwd().resolve()
AGENTE: str | None = None  # --agente o FACTORY_AGENTE: la vía de agente nunca se registra como persona
CHANGES = ROOT / "openspec" / "changes"
ID_RE = re.compile(r"^\d{8}-\d{6}-[a-z0-9_-]+$")
SLUG_RE = re.compile(r"^[a-z][a-z0-9-]*$")


class FactoryError(Exception):
    pass


def ahora() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")


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


def leer(identificador: str) -> tuple[Path, dict]:
    carpeta = ruta_cambio(identificador)
    archivo = ruta_segura(ruta_registro(carpeta))
    if not archivo.is_file():
        raise FactoryError(f"no encuentro el registro de factory: {archivo}")
    if estructura.es_anterior(ROOT, identificador) and identificador not in AVISADOS:
        AVISADOS.add(identificador)
        print(f"Aviso: el estado de {identificador} está en el lugar anterior a la fase 2 (openspec/changes/); "
              "oracle-factory migrar lo pasa a .factory/cambios/.", file=sys.stderr)
    return carpeta, json.loads(archivo.read_text(encoding="utf-8"))


def guardar(carpeta: Path, estado: dict) -> None:
    destino = ruta_registro(carpeta)
    destino.parent.mkdir(parents=True, exist_ok=True)
    if destino.exists() and not os.access(destino, os.W_OK):  # el reemplazo atómico saltearía la protección del archivo
        raise FactoryError(f"{destino.relative_to(ROOT)} es de sólo lectura; no lo modifico")
    escribir_atomico(destino, (json.dumps(estado, ensure_ascii=False, indent=2) + "\n").encode("utf-8"))  # un corte no lo trunca


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
              "revisores": datos.get("revisores", {})}
    try:
        revisores_mod.validar_config(config["revisores"])
    except revisores_mod.RevisorInvalido as e:
        raise FactoryError(f"{ruta}: {e}; por ejemplo: {revisores_mod.EJEMPLO}") from e
    alias = config["capacidades"]
    if (set(datos) - set(config) or config["modo_por_defecto"] not in modos.MODOS
            or type(config["tipos_obligatorios"]) is not bool
            or not isinstance(alias, dict) or not all(isinstance(k, str) and isinstance(v, str) and v not in alias
                                                      for k, v in alias.items())):
        raise FactoryError(f"{ruta}: se admiten modo_por_defecto ({', '.join(modos.MODOS)}), tipos_obligatorios (true/false), "
                           "capacidades (alias → capacidad, sin cadenas de alias) y revisores")
    return config


def evento(estado: dict, accion: str, forma: str = "decidio", **datos) -> None:
    estado.setdefault("eventos", []).append({
        "accion": accion, **actor(), "modo": modo_de(estado), "forma": forma, "cuando": ahora(), **datos})


def exigir_terminal(que: str = "esta decisión") -> None:
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
    paquetes = {"oracle": "oracle-metalenguaje", "tasks": "oracle-task"}
    if args[0] in paquetes:
        paquete = paquetes[args[0]]
        try:
            metadata.distribution(paquete)
        except metadata.PackageNotFoundError:
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
          sufijo: str | None = None) -> str:
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
    p = ejecutar(["tasks", "new", titulo, "--sufijo", sufijo, "--json", "--proyecto", str(ROOT)])
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
        (carpeta / "proposal.md").write_text(f"""# {titulo}

## Why

TODO: qué problema humano resuelve y para quién.

## What changes

TODO: comportamiento observable que se propone.

## Out of scope

TODO: qué queda explícitamente fuera.

## Human decisions

TODO: preguntas que requieren una decisión de Brian/equipo.
""", encoding="utf-8")
        spec.write_text(f"""# Capability: {capacidad}

### Requirement: comportamiento principal
The system SHALL TODO: write one testable promise.

#### Scenario: caso esperado
- GIVEN TODO: a known starting state
- WHEN TODO: the user performs an action
- THEN TODO: an observable result follows
""", encoding="utf-8")
        (carpeta / "design.md").write_text("# Design\n\nTODO: completar si la solución necesita una decisión técnica.\n", encoding="utf-8")
        (carpeta / "tasks.md").write_text("""# Tasks

- [ ] Persona: revisar y aceptar proposal.md + spec.md.
- [ ] Agente: importar requisitos Oracle y señalar lo aún sin medir.
- [ ] Persona + agente: acordar medidas y evidencia para cada requisito.
- [ ] Agente: implementar y correr las pruebas del producto.
- [ ] Revisor: revisar el diff; registrar y resolver hallazgos.
- [ ] Agente: correr Oracle sobre hechos observados.
- [ ] Persona: revisar el informe y decidir si se cierra.
""", encoding="utf-8")
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
        print(f'Ejemplo y catálogos preparados en {ROOT / "examples/notas"} y {ROOT / "catalogos"}. No se ejecutó el programa.')
    else:
        print('Completá los TODO antes de pedir aceptación.')
    print(f"Próximo paso humano: revisar {carpeta / 'proposal.md'} y {spec}")
    siguiente(identificador, 'espera_aprobacion_spec')
    return identificador


def abierto(identificador: str) -> tuple[Path, dict]:
    carpeta, estado = leer(identificador)
    if estado.get("fase") == "cerrada":
        raise FactoryError("el cambio ya está cerrado; creá una nueva tarea")
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
    return not (partes[0] in ("tareas", estructura.DIR) or gestionada or (len(partes) == 4 and partes[:2] == ("openspec", "changes")
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


def aprobar_spec(identificador: str) -> None:
    carpeta, estado = abierto(identificador)
    spec = ROOT / estado["spec"]
    for archivo in (carpeta / "proposal.md", spec, carpeta / "tasks.md"):
        if not archivo.is_file() or "TODO:" in archivo.read_text(encoding="utf-8"):
            raise FactoryError(f"hay que completar y revisar primero: {archivo.relative_to(ROOT)}")
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
    p = ejecutar(["oracle", "requisito", "importar", str(spec), "--dominio", dominio, "--escribir", "--proyecto", str(ROOT)])
    sys.stdout.write(p.stdout)
    if p.returncode:
        raise FactoryError(p.stderr.strip() or "Oracle no pudo importar los requisitos")
    ids = sorted(set(re.findall(r"(?m)^[+=]\s+([a-z][a-z0-9_.]*)", p.stdout)))
    if not ids:
        raise FactoryError("Oracle no devolvió ids; no doy la importación por confirmada")
    exigir_spec(carpeta, estado)
    sin_tipo = [i for i in ids if i.split(".", 1)[1] not in tipos]
    if sin_tipo:
        raise FactoryError("no pude asociar el tipo de estos requisitos a la spec: " + ", ".join(sin_tipo))
    for rid in ids:
        fuente_relativa(ROOT / "requisitos" / f"{rid}.requisito")
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


def bytes_json(valor: dict) -> bytes:
    return (json.dumps(valor, ensure_ascii=False, indent=2) + '\n').encode('utf-8')


def leer_regular(ruta: Path, nombre: str) -> bytes:
    if not ruta.is_file():
        raise FactoryError(f'{nombre}: se requiere un archivo regular: {ruta}')
    return ruta.read_bytes()


def guardar_par_revision(identificador: str, prefijo: str, informe: bytes, decisiones: bytes) -> tuple[Path, Path]:
    raiz = ruta_segura(ROOT / 'tareas' / identificador / 'revisiones')
    destino = None
    try:
        if not ruta_segura(raiz.parent / 'TAREA.md').is_file():
            raise FactoryError(f'no encuentro la tarea: {raiz.parent / "TAREA.md"}')
        raiz.mkdir(parents=True, exist_ok=True)
        destino = Path(tempfile.mkdtemp(prefix=prefijo + '-', dir=raiz))
        for nombre, datos in (('informe.json', informe), ('decisiones.json', decisiones)):
            archivo = ruta_segura(destino / nombre)
            with archivo.open('xb') as salida:
                salida.write(datos)
        return destino / 'informe.json', destino / 'decisiones.json'
    except (OSError, FactoryError) as e:
        raise FactoryError(f'no se completaron los documentos de revisión: {e}. '
                           f'Revisá posibles archivos residuales en {destino or raiz}; no se sobrescribieron antecedentes ni se publicó un gate nuevo.') from e


def preparar_revision(identificador: str) -> tuple[Path, Path]:
    carpeta, estado = abierto(identificador)
    registro = (ruta_registro(carpeta)).read_bytes()
    if json.loads(registro) != estado:
        raise FactoryError('registro cambió durante la lectura; volvé a preparar')
    exigir_spec(carpeta, estado)
    contexto, docs = contexto_producto(), documentos(carpeta, estado)
    informe, decisiones = documentos_revision.plantillas(identificador, contexto, docs)
    sha = candidato_vigente(identificador)
    if not sha:
        print("Aviso: no hay candidato vigente (un commit con su carpeta de candidato y sin cambios de producto después), así "
              "que el informe queda sin informes de revisores ni evidencia. Pedí una revisión con oracle-factory "
              f"pedir-revision {identificador} --a NOMBRE o producí la evidencia del commit actual.", file=sys.stderr)
    if sha:
        revisores, evidencia, archivos, avisos = material_del_candidato(identificador, sha)
        informe, decisiones = preparacion.completar(informe, decisiones, revisores, evidencia, archivos)
        vueltas = []
        for anterior in candidatos_anteriores(identificador, sha):
            # Las vueltas anteriores pasan por la misma validación que las del candidato vigente.
            anteriores, _, _, avisos_anteriores = material_del_candidato(identificador, anterior)
            vueltas += [{"candidato": anterior, **r} for r in anteriores]
            avisos += avisos_anteriores
        informe["comprobaciones"] = (informe["comprobaciones"] or []) + preparacion.vueltas_anteriores(vueltas) or None
        for aviso in avisos:
            print(f'Aviso: {aviso}', file=sys.stderr)
        print(f'Candidato {sha}: {len(revisores)} informe(s) de revisores, '
              f'{len(informe["hallazgos"])} hallazgo(s), evidencia {"sí" if evidencia else "no"}.')
    rutas = guardar_par_revision(identificador, 'preparacion', bytes_json(informe), bytes_json(decisiones))
    try:
        exigir_spec(carpeta, estado)
        if (not mismo_producto(contexto, contexto_producto()) or documentos(carpeta, estado) != docs
                or (ruta_registro(carpeta)).read_bytes() != registro):
            raise FactoryError('cambió el producto o el registro durante la preparación')
    except (FactoryError, OSError) as e:
        raise FactoryError(f'{e}; no uses la preparación en {rutas[0].parent}; prepará una nueva. No se cambiaron gates.') from e
    print(f'Informe pendiente: {rutas[0]}\nDecisiones pendientes: {rutas[1]}')
    print(f"Cambio: {identificador}; HEAD: {contexto['head']}; huella de archivos: {contexto['archivos_sha256']}")
    print('La huella incluye cambios locales; confirmá el producto antes de revisar. Preparar no analiza ni aprueba.')
    print('Completá el informe y luego su SHA-256 en decisiones; resolvé los hallazgos con criterio humano.')
    print(f'Próximo paso: oracle-factory revision {identificador} --formato guiado --informe RUTA_INFORME '
          '--decisiones RUTA_DECISIONES --revisor NOMBRE --decision DECISION')
    print('DECISION debe ser aprobar o cambios, elegida por la persona después de revisar.')
    return rutas


def material_del_candidato(identificador: str, sha: str) -> tuple[list[dict], dict | None, list[str], list[str]]:
    """(informes de revisores usables, evidencia, archivos del paquete, avisos) de la carpeta del candidato."""
    raiz = estructura.ruta_canonica(ROOT, identificador, "evidencia", sha).parent
    avisos: list[str] = []

    def cargar(ruta: Path):
        try:
            datos = json.loads(ruta_segura(ruta).read_text(encoding="utf-8"))
        except (OSError, ValueError, FactoryError) as e:
            avisos.append(f"{ruta.relative_to(ROOT)} no se pudo leer ({type(e).__name__}); no lo uso")
            return None
        return datos if isinstance(datos, dict) else None

    paquetes = [p for p in (cargar(r) for r in sorted((raiz / "clue").glob("*.json"))) if p] if (raiz / "clue").is_dir() else []
    archivos = sorted({f["file"] for p in paquetes for f in p.get("files") or [] if isinstance(f, dict) and f.get("file")})
    clue = shutil.which("oracle-clue")
    revisores = []
    for ruta in sorted((raiz / "revision").glob("*.json")) if (raiz / "revision").is_dir() else []:
        datos, rel = cargar(ruta), ruta.relative_to(ROOT).as_posix()
        if datos is None:
            continue
        if datos.get("schema_version") != preparacion.ESQUEMA_CLUE:
            avisos.append(f"{rel} no es un informe de Oracle Clue; no lo uso")
            continue
        if not str(datos.get("head") or "").startswith(sha):
            avisos.append(f"{rel} es de otro candidato ({str(datos.get('head'))[:7]}); no lo uso")
            continue
        paquete = next((p for p in paquetes if p.get("diff_sha256") == datos.get("diff_sha256")
                        and p.get("context_sha256") == datos.get("context_sha256")), None)
        if clue is None:
            validacion = "sin validar: oracle-clue no está instalado"
        elif paquete is None or not Path(str(paquete.get("repo"))).is_dir():
            # Con Clue disponible, un informe que no se puede validar no se usa (falta su paquete o su checkout).
            falta = "su paquete en clue/" if paquete is None else f"el checkout del paquete ({paquete.get('repo')})"
            avisos.append(f"{rel} no se puede validar: falta {falta}; recrealo con oracle-factory ruta {identificador} "
                          "checkout y no lo uso")
            continue
        else:
            ruta_paquete = next(r for r in sorted((raiz / "clue").glob("*.json")) if cargar(r) == paquete)
            p = ejecutar([clue, "validar", str(ruta), "--paquete", str(ruta_paquete), "--repo", str(paquete["repo"])])
            if p.returncode:
                avisos.append(f"{rel} no pasa la validación de Clue: {(p.stderr or p.stdout).strip()[:300]}; no lo uso")
                continue
            validacion = "validado con oracle-clue"
        if validacion.startswith("sin validar"):
            avisos.append(f"{rel}: {validacion}")
        revisores.append({"ruta": rel, "datos": datos, "validacion": validacion})
    resultado = raiz / "evidencia" / "resultado.json"
    evidencia = None
    if resultado.is_file():
        datos = cargar(resultado)
        if datos is not None:
            evidencia = {"ruta": resultado.relative_to(ROOT).as_posix(), "resultado": datos}
    return revisores, evidencia, archivos, avisos


def pedir_revision(identificador: str, nombre: str, extra: str | None = None, base: str | None = None) -> Path:
    """Pide una revisión del candidato actual al revisor configurado y guarda su informe si Clue lo valida."""
    carpeta, estado = abierto(identificador)
    revisor = config_proyecto()["revisores"].get(nombre)
    if revisor is None:
        raise FactoryError(f"no hay un revisor «{nombre}» en .factory/config.json; por ejemplo: {revisores_mod.EJEMPLO}")
    clue = shutil.which("oracle-clue")
    if clue is None:
        raise FactoryError("pedir-revision necesita oracle-clue para preparar el paquete y validar el informe")
    if cambios_locales_de_producto():
        raise FactoryError("hay cambios del producto sin commit: confirmalos antes de pedir una revisión ("
                           + ", ".join(cambios_locales_de_producto()[:5]) + ")")
    # Un commit que sólo guarda informes o evidencia no cambia el producto: el candidato sigue siendo el vigente.
    head = ejecutar(["git", "rev-parse", candidato_vigente(identificador) or "HEAD"]).stdout.strip()
    sha = head[:7]
    if base is None:
        p = ejecutar(["git", "merge-base", "HEAD", "main"])
        if p.returncode:
            raise FactoryError("no encuentro la rama main para la base del paquete; indicá --base REF")
        base = p.stdout.strip()
    checkout = estructura.ruta_canonica(ROOT, identificador, "checkout", sha)
    clue_dir = estructura.ruta_canonica(ROOT, identificador, "clue", sha)
    revision_dir = estructura.ruta_canonica(ROOT, identificador, "revision", sha)
    for d in (checkout.parent, clue_dir):  # revision/ se crea sólo con un informe válido
        ruta_segura(d).mkdir(parents=True, exist_ok=True)
    if not checkout.exists():
        p = ejecutar(["git", "worktree", "add", "--detach", str(checkout), head])
        if p.returncode:
            raise FactoryError(f"no pude crear el checkout de revisión: {p.stderr.strip()}")
    n = len(list(clue_dir.glob(f"paquete-{nombre}-*.json"))) + 1
    paquete = clue_dir / f"paquete-{nombre}-{n}.json"
    p = ejecutar([clue, "preparar", "--repo", str(checkout), "--base", base, "--contexto", estado["spec"], "--salida", str(paquete)])
    if p.returncode:
        raise FactoryError(f"oracle-clue no pudo preparar el paquete: {(p.stderr or p.stdout).strip()[:500]}")
    trabajo = ROOT / estructura.DIR / "local" / "revisores" / f"{sha}-{nombre}-{n}"
    ruta_segura(trabajo).mkdir(parents=True, exist_ok=True)
    informe, registro, pedido_archivo = trabajo / "informe.json", trabajo / "salida.log", trabajo / "pedido.md"
    anteriores = [r.relative_to(ROOT).as_posix() for c in candidatos_anteriores(identificador, sha)
                  for r in sorted(estructura.ruta_canonica(ROOT, identificador, "revision", c).glob("*.json"))]
    vueltas = ("Vueltas anteriores de este cambio (ya corregidas; mirá que sigan cerradas y que no haya regresiones):\n"
               + "\n".join(f"- {r}" for r in anteriores) + "\n") if anteriores else ""
    valores = {"id": identificador, "titulo": estado.get("titulo", ""), "propuesta": str(carpeta / "proposal.md"),
               "spec": str(ROOT / estado["spec"]), "candidato": sha, "checkout": str(checkout), "paquete": str(paquete),
               "informe": str(informe), "proveedor": revisor["proveedor"], "modelo": revisor["modelo"], "vueltas": vueltas}
    texto = revisores_mod.pedido(revisores_mod.plantilla(ROOT), valores, extra)
    pedido_archivo.write_text(texto, encoding="utf-8")
    argv = revisores_mod.argumentos(revisor["comando"], {"pedido": texto, "pedido_archivo": pedido_archivo, "carpeta": trabajo,
                                                         "informe": informe, "registro": registro, "paquete": paquete,
                                                         "checkout": checkout})
    print(f"Revisor {nombre} ({revisor['proveedor']}, {revisor['modelo']}) sobre el candidato {sha}; tope {revisor['tope_minutos']} min.")
    print("Comando: " + " ".join(a if len(a) < 80 else a[:77] + "..." for a in argv))
    resultado = revisores_mod.ejecutar_revisor(argv, trabajo, registro, revisor["tope_minutos"])
    hallazgos, motivo = 0, None
    if resultado == "tope":
        motivo = f"el revisor no terminó dentro del tope de {revisor['tope_minutos']} minutos"
    elif resultado == "no_inicia":
        motivo = f"no se pudo iniciar el revisor ({argv[0]})"
    elif not informe.is_file():
        resultado, motivo = "sin_informe", f"el revisor no dejó el informe en {informe}"
    else:
        p = ejecutar([clue, "validar", str(informe), "--paquete", str(paquete), "--repo", str(checkout)])
        if p.returncode:
            resultado, motivo = "rechazado", f"Clue rechazó el informe: {(p.stderr or p.stdout).strip()[:500]}"
        else:
            datos = json.loads(informe.read_text(encoding="utf-8"))
            hallazgos = len(datos.get("findings") or [])
    _, estado = leer(identificador)
    evento(estado, "revision_pedida", forma="registro", revisor=nombre, proveedor=revisor["proveedor"], modelo=revisor["modelo"],
           candidato=sha, resultado=resultado, hallazgos=hallazgos)
    guardar(carpeta, estado)
    if motivo:
        raise FactoryError(f"{motivo}. La salida del revisor quedó en {registro.relative_to(ROOT)}; revision/ no cambió.")
    ruta_segura(revision_dir).mkdir(parents=True, exist_ok=True)
    destino = revision_dir / f"{nombre}-{n}.json"
    escribir_atomico(destino, informe.read_bytes())
    escribir_atomico(revision_dir / f"{nombre}-{n}.pedido.md", pedido_archivo.read_bytes())
    print(f"Informe de {nombre}: {destino.relative_to(ROOT)} ({hallazgos} hallazgo{'s' if hallazgos != 1 else ''}), validado con oracle-clue.")
    print(f"Próximo paso: corregir lo que corresponda, o preparar la revisión con oracle-factory revision-preparar {identificador}")
    return destino


def revisar_guiado(identificador: str, informe: Path, decisiones: Path, revisor: str, decision: str,
                   confirmado: tuple[str, str] | None = None) -> None:
    carpeta, estado = abierto(identificador)
    registro_ruta = ruta_segura(ruta_registro(carpeta))
    registro = registro_ruta.read_bytes()
    if json.loads(registro) != estado:
        raise FactoryError('registro cambió durante la lectura; volvé a revisar')
    exigir_spec(carpeta, estado)
    contenido, resoluciones = leer_regular(informe, 'informe'), leer_regular(decisiones, 'decisiones')
    contexto, docs = contexto_producto(), documentos(carpeta, estado)
    try:
        analisis, triage, pendientes_ids = documentos_revision.validar(
            contenido, resoluciones, identificador=identificador, contexto=contexto, documentos=docs, revisor=revisor)
    except documentos_revision.RevisionInvalida as e:
        raise FactoryError(str(e)) from e
    abiertos = len(pendientes_ids)
    print('Formato: guiado; consistencia estructural, sin verificar calidad del análisis ni identidad de actores.')
    print(f"Revisor: {revisor}; decisión solicitada: {decision}; commit: {contexto['head']}; huella: {contexto['archivos_sha256']}")
    print(f"Revisión declarada completa: {analisis['completa']}; archivos: {', '.join(analisis['archivos_revisados'])}")
    print('Límites: ' + ('; '.join(analisis['limites']) or 'sin límites adicionales declarados; no implica cobertura universal'))
    for comprobacion in analisis['comprobaciones']:
        print(f"Comprobación {comprobacion['resultado']}: {comprobacion['descripcion']} · {comprobacion['evidencia']}")
    for hallazgo in analisis['hallazgos']:
        print(f"Hallazgo {hallazgo['id']}: {hallazgo['descripcion']} · {hallazgo['ubicacion']} · {hallazgo['evidencia']}")
    if not analisis['hallazgos']:
        print('Ausencia de hallazgos declarada: ' + analisis['sin_hallazgos_motivo'])
    for resolucion in triage['decisiones']:
        print(f"Resolución {resolucion['hallazgo_id']}: {resolucion['estado']} · {resolucion['actor']} · {resolucion['fecha']} · {resolucion['motivo']}")
    print(f"Actor de decisión: {triage['actor']}; motivo: {triage['motivo']}")
    print(f"Abiertos derivados: {abiertos}; IDs: {', '.join(pendientes_ids) or 'ninguno'}")
    if decision == 'aprobar':
        causas = ([f"comprobación en {c['resultado']}: {c['descripcion']}" for c in analisis['comprobaciones'] if c['resultado'] != 'cumple']
                  + [f"hallazgo abierto: {h}" for h in pendientes_ids] + ([] if analisis['completa'] else ['la revisión está declarada incompleta']))
        if causas:
            raise FactoryError('no se puede aprobar:\n  - ' + '\n  - '.join(causas)
                               + '\nRegistrá la decisión «cambios» o, si corresponde, resolvé lo que falta y prepará la revisión de nuevo.')

    def revalidar():
        exigir_spec(carpeta, estado)
        if (leer_regular(informe, 'informe') != contenido or leer_regular(decisiones, 'decisiones') != resoluciones):
            raise FactoryError('informe o decisiones cambiaron durante la operación; volvé a revisarlos')
        if (not mismo_producto(contexto, contexto_producto()) or documentos(carpeta, estado) != docs
                or registro_ruta.read_bytes() != registro):
            raise FactoryError('producto, spec o registro cambió durante la operación; volvé a revisar')

    firma = firma_revision('guiado', sha256(contenido), sha256(resoluciones), revisor, decision, contexto)

    def publicar_propuesta(e):
        revalidar()
        escribir_atomico(registro_ruta, bytes_json(e), esperado=registro)

    forma = decidir(estado, 'revision', tipos_cambio(estado), firma, menu_revision(identificador, decision),
                    'registro de revisión cancelado', publicar_propuesta, confirmado)
    if forma is None:
        return
    revalidar()
    destino, destino_decisiones = guardar_par_revision(identificador, 'registro', contenido, resoluciones)
    preparado = analisis['contexto'].get('head')  # lo declara el informe: sólo se guarda si es un commit
    preparado = preparado if isinstance(preparado, str) and re.fullmatch(r'[0-9a-f]{40}', preparado) else None
    try:
        revalidar()
        if leer_regular(destino, 'informe archivado') != contenido or leer_regular(destino_decisiones, 'decisiones archivadas') != resoluciones:
            raise FactoryError('las copias archivadas cambiaron antes de registrar')
        estado['revision'] = {
            'formato': 'guiado', 'revisor': revisor, 'decision': decision, 'hallazgos_abiertos': abiertos,
            'informe': str(destino.relative_to(ROOT)), 'sha256': sha256(contenido),
            'decisiones': str(destino_decisiones.relative_to(ROOT)), 'decisiones_sha256': sha256(resoluciones),
            **registro_decision(estado, forma), 'contexto': contexto,
            **({'head_preparacion': preparado} if preparado and preparado != contexto['head'] else {}),
        }
        estado.update(oracle=None, fase='revision_aprobada' if decision == 'aprobar' else 'cambios_pedidos')
        evento(estado, 'revision_registrada', forma=forma, formato='guiado', revisor=revisor, decision=decision,
               abiertos=abiertos, sha256=sha256(contenido), decisiones_sha256=sha256(resoluciones))
        escribir_atomico(registro_ruta, bytes_json(estado), esperado=registro)
    except (FactoryError, OSError) as e:
        raise FactoryError(f'no se publicó la nueva revisión: {e}. Copias residuales en {destino.parent}; '
                           'se conservó el registro anterior o la edición concurrente.') from e
    try:
        nota_tarea(identificador, f'Revisión guiada {revisor}: {decision}; registrada por {quien(estado["revision"])}; {abiertos} abiertos derivados; '
                   f"commit {contexto['head']}; informe {destino.relative_to(ROOT)}; decisiones {destino_decisiones.relative_to(ROOT)}.")
    except (FactoryError, OSError) as e:
        raise FactoryError(f'La revisión quedó registrada en {registro_ruta}; nota del tracker pendiente: {e}. '
                           'Consultá estado y recuperá sólo la nota; no se revirtió el registro.') from e
    print(f'Informe registrado: {destino}\nDecisiones registradas: {destino_decisiones}')
    siguiente(identificador, estado['fase'])


def motivo_armado(informe: dict, sha: str, decision: str, resoluciones: list[dict]) -> str:
    hallazgos = informe.get("hallazgos") or []
    partes = [f"{'Apruebo' if decision == 'aprobar' else 'Pido cambios en'} el candidato {sha}"]
    partes.append(f"{len(hallazgos)} hallazgo{'s' if len(hallazgos) != 1 else ''} de los revisores"
                  + (": " + ", ".join(f"{r['hallazgo_id']} {r['estado'].replace('_', ' ')}" for r in resoluciones)
                     if resoluciones else ""))
    evidencia = next((c["descripcion"] for c in informe.get("comprobaciones") or []
                      if c["descripcion"].startswith("Evidencia del candidato")), None)
    if evidencia:
        partes.append(evidencia[0].lower() + evidencia[1:])
    vueltas = sum(c["descripcion"].startswith("Vuelta anterior") for c in informe.get("comprobaciones") or [])
    if vueltas:
        partes.append(f"{vueltas} vuelta{'s' if vueltas != 1 else ''} anterior{'es' if vueltas != 1 else ''} registrada{'s' if vueltas != 1 else ''}")
    return "; ".join(partes) + "."


def proponer_revision(identificador: str, decision: str, motivo: str) -> None:
    """El agente deja la decisión y el motivo que propone; la persona los ve como opción en revisar."""
    carpeta, estado = abierto(identificador)
    sha = candidato_vigente(identificador)
    if sha is None:
        raise FactoryError("no hay candidato vigente para proponer una revisión")
    # Fuera de «propuestas»: ésas son las decisiones canónicas de modos.DECISIONES, con firma.
    estado.setdefault("motivos_propuestos", {})["revision"] = {"decision": decision, "motivo": motivo, "candidato": sha,
                                                      **actor(), "cuando": ahora()}
    evento(estado, "revision_propuesta", forma="propuso", decision=decision, candidato=sha)
    guardar(carpeta, estado)
    print(f"Propuesta de {AGENTE} para el candidato {sha}: {decision}; motivo «{motivo}». "
          f"La persona la ve como opción con oracle-factory revisar {identificador}.")


def revisar_paso_a_paso(identificador: str) -> None:
    """La revisión del candidato vigente, guiada: prepara, muestra, pregunta y registra sin editar JSON."""
    abierto(identificador)
    exigir_terminal("registrar la revisión")
    sha = candidato_vigente(identificador)
    if sha is None:
        raise FactoryError("no hay candidato vigente: hace falta un commit con su carpeta de candidato (evidencia o informes "
                           f"de revisores) y sin cambios de producto después; pedí una revisión con oracle-factory pedir-revision {identificador}")
    with contextlib.redirect_stdout(io.StringIO()):
        ruta_informe, ruta_decisiones = preparar_revision(identificador)
    informe = json.loads(ruta_informe.read_text(encoding="utf-8"))
    decisiones = json.loads(ruta_decisiones.read_text(encoding="utf-8"))
    if not informe.get("archivos_revisados") or not informe.get("comprobaciones"):
        raise FactoryError(f"el candidato {sha} no tiene informes de revisores ni evidencia: pedí una revisión con "
                           f"oracle-factory pedir-revision {identificador} y producí la evidencia antes de revisar")
    print(f"Revisión de {identificador} · candidato {sha}")
    for c in informe["comprobaciones"]:
        print(f"  {'✓' if c['resultado'] == 'cumple' else '✗'} {c['descripcion']}\n      Evidencia: {c['evidencia']}")
    for limite in informe.get("limites") or []:
        print(f"  Límite: {limite}")
    persona = actor()["actor"]
    resoluciones = []
    for h in informe.get("hallazgos") or []:
        print(f"\nHallazgo {h['id']} en {h['ubicacion']}:\n  {h['descripcion']}\n  Evidencia: {h['evidencia']}")
        i = elegir(f"¿Qué hacés con {h['id']}?", [("Aceptar el riesgo", "queda registrado como riesgo aceptado"),
                                                  ("Descartar", "no aplica o no es un defecto"),
                                                  ("Dejar abierto", "sólo se podrá pedir cambios")])
        if i is None:
            raise FactoryError("revisión cancelada; no registré nada")
        if i == 2:
            continue
        estado_h = ("riesgo_aceptado", "descartado")[i]
        motivo_h, origen_h = elegir_motivo(f"{'Acepto el riesgo' if i == 0 else 'Descarto el hallazgo'}: {h['descripcion']}")
        resoluciones.append({"hallazgo_id": h["id"], "estado": estado_h, "motivo": motivo_h, "origen_motivo": origen_h,
                             "actor": persona, "fecha": ahora()})
    abiertos = len(informe.get("hallazgos") or []) - len(resoluciones)
    # «Completa» lo declara la persona: Factory no lo supone.
    alcance = elegir("¿Revisaste todo lo que abarca el informe?", [
        ("Sí, la revisión está completa", "se registra como completa"),
        ("No, quedó incompleta", "se registra incompleta, con sus límites; sólo se podrá pedir cambios")])
    if alcance is None:
        raise FactoryError("revisión cancelada; no registré nada")
    completa = alcance == 0
    if not completa and not informe.get("limites"):
        limite = input("¿Qué quedó sin revisar? ").strip()
        if not limite:
            raise FactoryError("una revisión incompleta necesita su límite; no registré nada")
        informe["limites"] = [limite]
    if abiertos or not completa or any(c["resultado"] != "cumple" for c in informe["comprobaciones"]):
        opciones = [("cambios", "Pedir cambios", f"quedan {abiertos} hallazgo(s) abiertos, la revisión está incompleta o hay "
                     "comprobaciones que no cumplen; no se puede aprobar")]
    else:
        opciones = [("aprobar", "Aprobar", "la revisión queda aprobada; después corre juzgar y se puede cerrar"),
                    ("cambios", "Pedir cambios", "la revisión queda registrada pidiendo cambios")]
    i = elegir(f"Decisión sobre el candidato {sha}:", [(e, d) for _, e, d in opciones] + [("Cancelar", "no registra nada")])
    if i is None or i == len(opciones):
        raise FactoryError("revisión cancelada; no registré nada")
    decision = opciones[i][0]
    _, estado = leer(identificador)
    propuesta = (estado.get("motivos_propuestos") or {}).get("revision") or {}
    propuesto = propuesta.get("motivo") if propuesta.get("decision") == decision and propuesta.get("candidato") == sha else None
    motivo = elegir_motivo(motivo_armado(informe, sha, decision, resoluciones), propuesto)
    informe.update(revisor=persona, completa=completa)
    contenido = bytes_json(informe)
    escribir_atomico(ruta_informe, contenido)
    decisiones.update(informe_sha256=sha256(contenido), actor=persona, motivo=motivo[0], decisiones=resoluciones)
    escribir_atomico(ruta_decisiones, bytes_json(decisiones))
    revisar_guiado(identificador, ruta_informe, ruta_decisiones, persona, decision, motivo)
    carpeta, estado = leer(identificador)
    if (estado.get("motivos_propuestos") or {}).pop("revision", None) is not None:  # la propuesta ya se decidió
        guardar(carpeta, estado)


def revisar(identificador: str, informe: Path, revisor: str, decision: str, abiertos: int | None = None,
            *, formato: str = 'libre', decisiones: Path | None = None) -> None:
    if decision not in {'aprobar', 'cambios'} or not revisor.strip():
        raise FactoryError('indicá revisor y una decisión válida')
    if formato == 'guiado':
        if abiertos is not None or decisiones is None:
            raise FactoryError('modo guiado requiere --decisiones y calcula abiertos; no admite --hallazgos-abiertos')
        return revisar_guiado(identificador, informe, decisiones, revisor, decision)
    if formato != 'libre' or decisiones is not None:
        raise FactoryError('usá --formato guiado con decisiones, o libre sin decisiones; no hay conversión automática')
    if type(abiertos) is not int or abiertos < 0:
        raise FactoryError('modo libre requiere --hallazgos-abiertos N explícito, entero no negativo')
    carpeta, estado = abierto(identificador)
    registro = (ruta_registro(carpeta)).read_bytes()
    if json.loads(registro) != estado:
        raise FactoryError('registro cambió durante la lectura; volvé a revisar')
    exigir_spec(carpeta, estado)
    if not informe.is_file():
        raise FactoryError(f"no encuentro el informe: {informe}")
    if decision not in {"aprobar", "cambios"} or not revisor.strip():
        raise FactoryError("indicá revisor y una decisión válida")
    if abiertos < 0 or (decision == "aprobar" and abiertos):
        raise FactoryError("una revisión aprobada exige cero hallazgos abiertos")
    contenido = informe.read_bytes()
    if not contenido.strip():
        raise FactoryError("el informe de revisión está vacío")
    contexto = contexto_producto()
    huella = sha256(contenido)
    destino = dir_estado(carpeta) / 'review.md'
    print('Formato: libre; declaración humana sin validación estructural del contenido, alcance ni límites.')
    print(f"Revisor: {revisor}; decisión: {decision}; abiertos: {abiertos}; commit: {contexto['head']}")
    firma = {**firma_revision("libre", huella, None, revisor, decision, contexto), "abiertos": abiertos}

    def publicar_propuesta(e):
        if (ruta_registro(carpeta)).read_bytes() != registro:
            raise FactoryError("registro cambió durante la operación; repetí la revisión")
        guardar(carpeta, e)

    forma = decidir(estado, "revision", tipos_cambio(estado), firma, menu_revision(identificador, decision),
                    "registro de revisión cancelado", publicar_propuesta)
    if forma is None:
        return
    exigir_spec(carpeta, estado)
    if not mismo_producto(contexto, contexto_producto()):
        raise FactoryError("el producto cambió durante la confirmación; repetí la revisión")
    if leer_regular(informe, 'informe') != contenido or (ruta_registro(carpeta)).read_bytes() != registro:
        raise FactoryError('informe o registro cambió durante la confirmación; repetí la revisión')
    destino.write_bytes(contenido)
    estado["revision"] = {
        "formato": "libre",
        "revisor": revisor, "decision": decision, "hallazgos_abiertos": abiertos,
        "informe": str(destino.relative_to(ROOT)), "sha256": huella,
        **registro_decision(estado, forma), "contexto": contexto,
    }
    estado["oracle"] = None
    estado["fase"] = "revision_aprobada" if decision == "aprobar" else "cambios_pedidos"
    evento(estado, "revision_registrada", forma=forma, revisor=revisor, decision=decision, abiertos=abiertos, sha256=huella)
    guardar(carpeta, estado)
    nota_tarea(identificador, f"Revisión {revisor}: {decision}; registrada por {quien(estado['revision'])}; {abiertos} abiertos; commit {contexto['head']}; informe {destino.relative_to(ROOT)}.")
    print(f"Informe registrado: {destino}")
    siguiente(identificador, estado["fase"])

def juzgar(identificador: str, hechos: Path) -> None:
    carpeta, estado = abierto(identificador)
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
    hechos = hechos.resolve()
    if not hechos.is_file():
        raise FactoryError(f"no encuentro los hechos del sensor: {hechos}")
    # Con ruta relativa al proyecto, el registro vale en cualquier clon; fuera de él, sólo en esta máquina.
    try:
        ruta_hechos = hechos.relative_to(ROOT).as_posix()
    except ValueError:
        ruta_hechos = str(hechos)
        print(f"Aviso: los hechos están fuera del proyecto ({hechos}); otra máquina no podrá verificarlos. "
              "Guardalos dentro de tareas/ para que viajen con el repositorio.", file=sys.stderr)
    else:
        if ejecutar(["git", "check-ignore", "-q", str(hechos)]).returncode == 0:
            print(f"Aviso: los hechos ({ruta_hechos}) están ignorados por Git y no viajan con el repositorio; otra máquina "
                  "no podrá verificarlos. Guardalos fuera de las carpetas ignoradas, por ejemplo en tareas/.", file=sys.stderr)
    contexto = contexto_producto()
    huella = sha256(hechos.read_bytes())
    cobertura = ejecutar(["oracle", "cobertura", "--proyecto", str(ROOT)])
    if cobertura.returncode or not requisitos_verdes(cobertura.stdout, estado["requisitos"]):
        raise FactoryError("Oracle todavía no tiene cobertura completa de cada requisito importado")
    p = ejecutar(["oracle", "cobertura", "--con", str(hechos), "--proyecto", str(ROOT)])
    sys.stdout.write(p.stdout)
    if p.stderr:
        sys.stderr.write(p.stderr)
    if not mismo_producto(contexto, contexto_producto()) or sha256(hechos.read_bytes()) != huella:
        raise FactoryError("el producto o los hechos cambiaron durante el juicio; repetí la corrida")
    exigir_spec(carpeta, estado)
    informe = dir_estado(carpeta) / 'oracle-veredicto.txt'
    informe.write_text(p.stdout + p.stderr, encoding="utf-8")
    ok = p.returncode == 0 and requisitos_verdes(p.stdout, estado["requisitos"])
    estado["oracle"] = {
        "codigo": 0 if ok else 1, "codigo_oracle": p.returncode,
        "hechos": ruta_hechos, "hechos_sha256": huella,
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


def registrar_medidas(estado: dict, rid: str, forma: str, motivo: str | None, contenido: bytes) -> dict:
    registro = {**registro_decision(estado, forma, motivo), "sha256": sha256(contenido)}
    estado.setdefault("medidas", {})[rid] = registro
    return registro


def medidas_sin_decision(estado: dict) -> list[tuple[str, str]]:
    """Requisitos con medidas en su archivo y sin decisión registrada (cambios con modo)."""
    if "modo" not in estado and "medidas" not in estado:
        return []  # cambio anterior a los modos
    medidas, pendientes = estado.get("medidas") or {}, estado.get("medidas_pendientes") or {}
    faltan = []
    for rid in estado.get("requisitos", []):
        ruta = ROOT / "requisitos" / f"{rid}.requisito"
        if not ruta.is_file() or rid in pendientes:
            continue
        contenido = ruta.read_bytes()
        if not any(linea.startswith("    medido_por ") for linea in contenido.decode("utf-8").splitlines()):
            continue
        if rid not in medidas:
            faltan.append((rid, "sin decisión registrada; registrala con medir y las mismas medidas"))
        elif medidas[rid].get("sha256") not in (None, sha256(contenido)):
            # None: decisión anterior a que se guardara el hash; no se puede comparar.
            faltan.append((rid, "cambió después de la decisión registrada; volvé a decidirla con medir"))
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
    rev = estado.get("revision") or {}
    oracle = estado.get("oracle") or {}
    for etiqueta, ruta, huella in (
        ("informe de revisión", rev.get("informe"), rev.get("sha256")),
        ("decisiones de revisión", rev.get("decisiones"), rev.get("decisiones_sha256")),
        ("informe Oracle", oracle.get("informe"), oracle.get("informe_sha256")),
        ("hechos", oracle.get("hechos"), oracle.get("hechos_sha256")),
    ):
        if not ruta and not huella:
            continue
        try:
            if not ruta or not huella or sha256((ROOT / ruta).read_bytes()) != huella:
                faltan.append(etiqueta + " cambiado o sin huella")
        except OSError:
            if etiqueta == "hechos":
                faltan.append(f"hechos ausentes ({ruta}); en esta máquina se recuperan juzgando de nuevo con los hechos "
                              f"del clon: oracle-factory juzgar {estado['id']} --con RUTA_DE_LOS_HECHOS")
            else:
                faltan.append(etiqueta + " ausente")
    # Los registros antiguos sólo tenían un código numérico: no son evidencia vigente.
    if rev and not all(rev.get(k) for k in ("informe", "sha256", "contexto")):
        faltan.append("revisión sin evidencia vinculada")
    if rev.get('formato') == 'guiado' and not all(rev.get(k) for k in ('decisiones', 'decisiones_sha256')):
        faltan.append('revisión guiada sin decisiones vinculadas')
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


def situacion_requisitos(estado: dict) -> list[tuple[str, str, str | None]]:
    """[(requisito, 'vigente'|'reemplazado'|'ausente', cambio que lo reemplazó)] de un cambio archivado."""
    if not estado.get("archivo"):
        return []
    indice = leer_indice(estado["archivo"]["capacidad"])
    return [(rid, *archivo.situacion(indice, rid)) for rid in estado.get("requisitos", [])]


def _json_de_revision(relativa, nombre: str) -> tuple[dict, str | None]:
    """(datos, problema): un documento ausente, inválido o fuera del proyecto se informa, no se toma por vacío."""
    if not relativa:  # sólo se llama para revisiones guiadas, que siempre registran los dos documentos
        return {}, f"la revisión guiada no registra su {nombre}"
    try:
        datos = json.loads(ruta_segura(ROOT / relativa).read_text(encoding="utf-8"))
    except (OSError, ValueError, TypeError, FactoryError) as e:
        return {}, f"no se pudo leer el {nombre} de la revisión ({relativa}): {type(e).__name__}"
    if not isinstance(datos, dict):
        return {}, f"el {nombre} de la revisión ({relativa}) no es un objeto JSON"
    return datos, None


def _lista(valor) -> list:
    return valor if isinstance(valor, list) else []


def texto_resumen(salida: Path | None = None) -> str:
    """Junta los datos de los registros y genera el resumen (sin escribir nada)."""
    carpeta_specs = ROOT / estructura.DIR / "specs"
    indices = [json.loads(p.read_text(encoding="utf-8")) for p in sorted(carpeta_specs.glob("*.json"))] \
        if carpeta_specs.is_dir() else []
    registros, abiertos, revisiones, sin_registro = {}, [], {}, []
    for carpeta in sorted(CHANGES.iterdir()) if CHANGES.is_dir() else []:
        if not ID_RE.fullmatch(carpeta.name):
            continue
        if not ruta_registro(carpeta).is_file():
            sin_registro.append(carpeta.name)
            continue
        _, estado = leer(carpeta.name)
        registros[estado["id"]] = estado
        if estado.get("fase") != "cerrada":
            abiertos.append({"id": estado["id"], "titulo": estado.get("titulo", ""), "fase": estado.get("fase", "?"),
                             "modo": modo_de(estado), "capacidad": capacidad_destino(estado.get("capacidad", "?")),
                             "pendientes": pendientes_actuales(carpeta, estado)})
            continue
        rev = estado.get("revision") if isinstance(estado.get("revision"), dict) else {}
        problemas = []
        informe, decisiones = {}, {}
        if rev.get("formato") == "guiado":  # la revisión libre (review.md) no declara riesgos ni límites con estructura
            informe, p1 = _json_de_revision(rev.get("informe"), "informe")
            decisiones, p2 = _json_de_revision(rev.get("decisiones"), "documento de decisiones")
            problemas = [p for p in (p1, p2) if p]
        hallazgos = {h.get("id"): h for h in _lista(informe.get("hallazgos")) if isinstance(h, dict)}
        revisiones[estado["id"]] = {"decisiones": [d for d in _lista(decisiones.get("decisiones")) if isinstance(d, dict)],
                                    "hallazgos": hallazgos, "problemas": problemas,
                                    "limites": [l for l in _lista(informe.get("limites")) if isinstance(l, str)]}
    medidas = {}
    for indice in indices:
        for req in indice["requisitos"].values():
            ruta = ROOT / "requisitos" / f"{req['requisito']}.requisito"
            texto = ruta.read_text(encoding="utf-8") if ruta.is_file() else ""
            m = re.search(r"(?m)^\s+medido_por\s+(.+?)\s*$", texto)
            medidas[req["requisito"]] = [x.strip() for x in m[1].split(",")] if m else []
    destino = ruta_resumen(salida)
    raiz_relativa = os.path.relpath(ROOT, destino.parent).replace(os.sep, "/") + "/"
    return resumen.generar(indices, registros, medidas, abiertos, revisiones, sin_registro,
                           "" if raiz_relativa == "./" else raiz_relativa)


def ruta_resumen(salida: Path | None = None) -> Path:
    return ruta_segura(ROOT / salida if salida else ROOT / estructura.DIR / "resumen.md")


def comando_resumen(verificar: bool, salida: Path | None, ver: bool = False) -> None:
    destino, texto = ruta_resumen(salida), texto_resumen(salida)
    if verificar:
        actual = destino.read_text(encoding="utf-8") if destino.is_file() else None
        if actual != texto:
            print(f"{destino.relative_to(ROOT)} " + ("no existe" if actual is None else "quedó viejo o se editó a mano")
                  + "; regeneralo con oracle-factory resumen.")
            raise SystemExit(1)
        print(f"{destino.relative_to(ROOT)} está al día.")
        return
    destino.parent.mkdir(parents=True, exist_ok=True)
    escribir_atomico(destino, texto.encode("utf-8"))
    if not ver:
        print(f"Resumen: {destino.relative_to(ROOT)}. Para verlo con formato: oracle-factory resumen --ver")
    elif shutil.which("glow") and sys.stdout.isatty():
        subprocess.run(["glow", "-p", str(destino)], check=False)
    else:
        print(texto, end="")


def actualizar_resumen() -> None:
    """Después de cerrar o archivar: si falla, lo cerrado ya está hecho y `resumen` lo repara."""
    try:
        escribir_atomico(ruta_resumen(), texto_resumen().encode("utf-8"))
    except Exception as e:  # noqa: BLE001 — el cierre ya está hecho; cualquier falla del resumen sólo se avisa
        print(f"Aviso: no pude actualizar el resumen ({type(e).__name__}: {e}); corré oracle-factory resumen.", file=sys.stderr)


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
    for _, identificador in sorted(pendientes):
        carpeta, estado = leer(identificador)
        capacidad, indice = plan_archivo(estado)
        spec = escribir_archivo(capacidad, indice)
        marcar_archivado(estado, capacidad, spec, "migracion")
        guardar(carpeta, estado)
        print(f"Archivado {identificador} en {spec}.")
    actualizar_resumen()


def cerrar(identificador: str) -> None:
    carpeta, estado = abierto(identificador)
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
            ruta = ROOT / "requisitos" / f"{rid}.requisito"
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


def comando_donde(identificador: str, candidato: str | None) -> None:
    _, estado = leer(identificador)
    print(f"{estado['id']} — {estado['titulo']}" + (f" (candidato {candidato})" if candidato else ""))
    for fila in estructura.donde(ROOT, identificador, estado, candidato):
        marca = ("no válido" if fila.get("invalida") else "histórico" if fila["gate"] == "histórico"
                 else "existe" if fila["existe"] else "AUSENTE")
        print(f"{fila['gate']:<10} {marca:<9} {fila['ruta']}" + (f"  — {fila['nota']}" if fila["nota"] else ""))


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
        # Los 7 primeros del hash completo: --short=7 lo alarga si es ambiguo y el nombre de la carpeta cambiaría.
        print(estructura.ruta_canonica(ROOT, identificador, tipo, head.stdout.strip()[:7]))
    except ValueError as e:
        raise FactoryError(str(e)) from e


def comando_buscar(texto: str, maximo: int) -> None:
    if not texto.strip():
        raise FactoryError("indicá el texto a buscar")
    lineas, total, omitidos = estructura.buscar(ROOT, texto, maximo)
    for linea in lineas:
        print(linea)
    print(f"{total} coincidencia(s)" + (f"; se muestran {len(lineas)}, usá --max para ver más" if total > len(lineas) else ""))
    if omitidos:
        print(f"Aviso: {omitidos} archivo(s) omitido(s) por superar {estructura.LIMITE_ARCHIVO // 1_000_000} MB; el texto podría estar ahí.")


def mostrar(identificador: str) -> None:
    carpeta, estado = leer(identificador)
    print(f"{estado['id']} — {estado['titulo']}\nFase: {estado['fase']}\nModo de trabajo: {modo_de(estado)}")
    print("Requisitos Oracle: " + (", ".join(estado.get("requisitos", [])) or "todavía no importados"))
    print("Pendiente: " + ("; ".join(pendientes_actuales(carpeta, estado)) or "ninguno"))
    for linea in commits_registrados(estado):
        print(linea + ".")
    for aviso in avisos_head(estado):
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

- `config.json` es la configuración del proyecto: `modo_por_defecto`, `tipos_obligatorios` y `capacidades` (alias de capacidades).
- `cambios/<ID>/` guarda el estado del cambio: `factory.json`, `review.md` y `oracle-veredicto.txt`.
- `resumen.md` es el estado actual en una lectura (`oracle-factory resumen`); se lee con `glow -p .factory/resumen.md`.
- `specs/<capacidad>.json` es el índice de la spec consolidada en `openspec/specs/<capacidad>/`: de qué cambio y requisito de Oracle viene cada requisito vigente y cuáles fueron reemplazados.
- `cambios/<ID>/candidatos/<sha7>/` agrupa lo que se produjo sobre un commit: `evidencia/`, `clue/` y `revision/`.
- `local/revisiones/<sha7>/` guarda los checkouts estables para que Clue revise.

Este archivo existe también porque Git no versiona carpetas vacías: sin él, un clon no tendría `.factory/`.
Más detalle en `docs/estructura.md` del repositorio de Factory, y `oracle-factory donde ID` lista lo que hay.
"""


def inicializar() -> None:
    marca = ROOT / estructura.DIR
    if marca.is_symlink() or (marca.exists() and not marca.is_dir()):
        raise FactoryError(f"{marca} existe y no es una carpeta de Factory: renombrala o quitala antes de ejecutar init; no creé nada")
    afuera = estructura.raiz_del_proyecto(ROOT.parent) if ROOT.parent != ROOT else None
    if afuera is not None:
        print(f"Aviso: esta carpeta está dentro del proyecto Factory {afuera}; init crea un proyecto anidado y los comandos "
              "usarán el más cercano.", file=sys.stderr)
    ROOT.mkdir(parents=True, exist_ok=True)
    for nombre in ("tareas", "catalogos", "corpus", "diferencial", "relaciones", "requisitos", "macros", "oracle.json", ".gitignore", "openspec/changes", estructura.DIR):
        ruta_segura(ROOT / nombre)
    for comando in (["tasks", "init", str(ROOT), "--sin-readme"], ["oracle", "init", str(ROOT)]):
        resultado = ejecutar(comando)
        if resultado.returncode:
            raise FactoryError(resultado.stderr or resultado.stdout)
    ruta_segura(CHANGES).mkdir(parents=True, exist_ok=True)
    for sub in ('cambios', 'local'):
        ruta_segura(ROOT / estructura.DIR / sub).mkdir(parents=True, exist_ok=True)
    config = ruta_segura(ROOT / estructura.DIR / 'config.json')
    if not config.exists() and not (ROOT / 'factory.json').exists():  # con la configuración anterior en la raíz, la pasa `migrar`
        config.write_text(json.dumps({"modo_por_defecto": modos.POR_DEFECTO, "tipos_obligatorios": False}, indent=2) + "\n",
                          encoding='utf-8')
    leeme = ruta_segura(ROOT / estructura.DIR / 'LEEME.md')
    if not leeme.exists():
        leeme.write_text(LEEME_FACTORY, encoding='utf-8')
    ignore = ruta_segura(ROOT / '.gitignore')
    contenido = ignore.read_text(encoding='utf-8') if ignore.exists() else ''
    pendientes = [line for line in ('.factory-demo/', estructura.IGNORAR_LOCAL, estructura.IGNORAR_CLUE, '__pycache__/', '*.py[cod]')
                  if line not in contenido.splitlines()]
    if pendientes:
        with ignore.open('a', encoding='utf-8') as archivo:
            archivo.write(('\n' if contenido and not contenido.endswith('\n') else '') + '\n'.join(pendientes) + '\n')
    versionados = ejecutar(["git", "ls-files", "--", ":(glob)" + estructura.IGNORAR_CLUE + "**"]).stdout.split()
    if versionados:  # el .gitignore no saca del índice lo que ya estaba versionado; init no toca el índice
        print("Aviso: hay paquetes de Clue versionados de antes; ahora son locales. Para dejar de versionarlos sin borrarlos: "
              "git rm -r --cached " + " ".join(sorted({str(Path(p).parent) for p in versionados})), file=sys.stderr)
    print(f'Factory inicializada en {ROOT}. No se crearon commits ni aprobaciones.')
    print(f'Acuerdos: {CHANGES}; tareas: {ROOT / "tareas"}; configuración: {ROOT / "oracle.json"}.')
    print(f'Carpeta propia de Factory: {ROOT / estructura.DIR} (versionada, salvo local/, que Git ignora).')
    print('Conservé la configuración existente. .gitignore excluye salidas temporales y bytecode de Python.')
    print('Si el proyecto todavía no usa Git, ejecutá git init desde esta carpeta; Factory no crea commits.')
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
        if esperado is not None and ruta.read_bytes() != esperado:
            raise FactoryError(f"el archivo cambió durante la operación: {ruta}; volvé a leerlo")
        os.replace(temporal, ruta)
    finally:
        if temporal is not None and temporal.exists():
            temporal.unlink()


def plan_ejemplo() -> dict[Path, bytes]:
    destino = ruta_segura(ROOT / 'examples' / 'notas')
    if destino.exists():
        raise FactoryError(f"el destino del ejemplo ya existe: {destino}; usá nuevo --capacidad notas para otro cambio")
    if not (ROOT / 'catalogos').is_dir() or not (ROOT / 'oracle.json').is_file():
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
                    plan[ROOT / 'catalogos' / item.name] = item.read_bytes()
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


def proximo_paso(identificador: str) -> str | None:
    """El próximo paso según lo que está vigente, en el orden del flujo.

    Un comando completo («oracle-factory …» sin MAYÚSCULAS por completar) se puede ofrecer para ejecutar; un texto que
    empieza con otra cosa indica algo que la persona tiene que hacer antes.
    """
    carpeta, estado = leer(identificador)
    ident = identificador
    if estado.get("fase") == "cerrada":
        return None
    try:  # sin aprobar, o la propuesta/spec cambió después de aprobarla
        exigir_spec(carpeta, estado)
    except FactoryError:
        return f"oracle-factory aprobar-spec {ident}"
    if not estado.get("requisitos"):
        return f"oracle-factory importar {ident}"
    if any(not p.get("descartada") for p in (estado.get("medidas_pendientes") or {}).values()):
        return f"oracle-factory medir {ident} --confirmar"
    medidas = estado.get("medidas") or {}
    if any(rid not in medidas for rid in estado["requisitos"]) or medidas_sin_decision(estado):
        return f"oracle-factory medir {ident} --listar"
    # ¿La revisión vale para el producto actual?
    rev = estado.get("revision") or {}
    revisado = bool(rev) and rev.get("contexto", {}).get("archivos_sha256") == contexto_producto()["archivos_sha256"]
    if not revisado:
        if cambios_locales_de_producto():
            return f"commiteá los cambios del producto; después: oracle-factory pedir-revision {ident}"
        sha = candidato_vigente(ident)
        # revisar necesita informes de revisores que la preparación pueda usar (mismas reglas), no sólo evidencia.
        if sha and material_del_candidato(ident, sha)[0]:
            return f"oracle-factory revisar {ident}"
        revisores = sorted(config_proyecto()["revisores"])
        return f"oracle-factory pedir-revision {ident} --a {revisores[0] if revisores else 'NOMBRE'}"
    if rev.get("decision") != "aprobar" or rev.get("hallazgos_abiertos") != 0:
        return f"corregí lo que pidió la revisión y commitealo; después: oracle-factory pedir-revision {ident}"
    # Revisión vigente y aprobada: ¿se juzgaron estos hechos?
    oracle = estado.get("oracle") or {}
    juzgados = ROOT / oracle["hechos"] if oracle.get("hechos") else None
    try:  # hechos del candidato que no son los juzgados: juzgarlos
        del_candidato = hechos_del_candidato(ident)
        if sha256(ruta_segura(del_candidato).read_bytes()) != oracle.get("hechos_sha256"):
            return f"oracle-factory juzgar {ident}"
    except FactoryError:
        pass
    if juzgados is not None and juzgados.is_file() and sha256(juzgados.read_bytes()) == oracle.get("hechos_sha256"):
        if oracle.get("codigo") != 0:
            return f"corregí la evidencia o el producto; después: oracle-factory juzgar {ident}"
        if not pendientes_actuales(carpeta, estado):
            return f"oracle-factory cerrar {ident}"
        return f"resolvé lo pendiente que lista estado; después: oracle-factory cerrar {ident}"
    if juzgados is not None and juzgados.is_file():  # hechos dados con --con que cambiaron desde el juicio
        return f"oracle-factory juzgar {ident} --con {shlex.quote(oracle['hechos'])}"
    return f"oracle-factory juzgar {ident} --con RUTA_DE_HECHOS"


def siguiente(identificador: str, fase: str | None = None) -> None:
    paso = proximo_paso(identificador)
    if paso:
        print("Próximo paso: " + paso)


def ofrecer_siguiente(identificador: str) -> int:
    """En una terminal y sin --agente, ofrece ejecutar el próximo paso si es un comando completo."""
    paso = proximo_paso(identificador)
    if (not paso or AGENTE or not terminal_interactiva() or not sys.stdout.isatty()
            or not paso.startswith("oracle-factory ") or re.search(r"\b[A-Z][A-Z_]{2,}\b", paso)):
        return 0
    if elegir("¿Seguís?", [(f"Ejecutar «{paso}»", "como si lo escribieras; si es una decisión, abre su propio menú"),
                            ("Salir", "no ejecuta nada")]) != 0:
        return 0
    return main(["--proyecto", str(ROOT), *shlex.split(paso)[1:]])


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
        if (fase and estado['fase'] != fase) or (abiertos and estado['fase'] == 'cerrada') \
                or (cerrados and estado['fase'] != 'cerrada'):
            continue
        print(f"{carpeta.name}  {estado['fase']}{' (archivado)' if estado.get('archivo') else ''}  {estado['titulo']}")
        encontrados += 1
    if not encontrados:
        print('No hay cambios que coincidan con el filtro.' if (fase or abiertos or cerrados)
              else 'No hay cambios Factory; las tareas del tracker por sí solas no son cambios Factory.')
    print(f'Acuerdos: {CHANGES}')


@contextmanager
def bloqueo_medidas(identificador: str):
    ruta = ruta_segura(ROOT / '.factory-demo' / 'locks' / (identificador + '.medir.lock'))
    ruta.parent.mkdir(parents=True, exist_ok=True)
    try:
        descriptor = os.open(ruta, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError as e:
        raise FactoryError(f'otra operación medir está en curso: {ruta}; si fue interrumpida, comprobá que terminó antes de retirar ese bloqueo') from e
    try:
        os.close(descriptor)
        yield
    finally:
        ruta.unlink()


def inventario_medidas(estado: dict):
    # Oracle es quien valida la sintaxis, forma única, ids y catálogo efectivo.
    from oracle_metalenguaje.nucleo import requisito
    from oracle_metalenguaje.nucleo.proyecto import resolver, catalogo_efectivo
    ruta_segura(ROOT / 'requisitos')
    requisitos = {}
    for rid in estado.get('requisitos', []):
        if not requisito.ID_RE.fullmatch(rid):
            raise FactoryError(f'id de requisito inválido en el registro: {rid}')
        ruta = ruta_segura(ROOT / 'requisitos' / f'{rid}.requisito')
        requisitos[rid] = requisito.cargar(ruta)
    proyecto = resolver(['--proyecto', str(ROOT)])
    catalogo = catalogo_efectivo(proyecto)
    huella = sha256(json.dumps([
        [mid, str(catalogo.entradas[mid].ruta), sha256(catalogo.entradas[mid].ruta.read_bytes()), repr(m)]
        for mid, m in sorted(catalogo.items())
    ], ensure_ascii=False).encode())
    return requisitos, catalogo, huella


def medir(identificador: str, *, requisito_id: str | None = None,
          medidas: list[str] | None = None, listar_opciones: bool = False,
          sin_medir: str | None = None, quitar_sin_medir: bool = False) -> None:
    carpeta, estado = abierto(identificador)
    ruta_segura(ruta_registro(carpeta))
    ruta_segura(ROOT / estado['spec'])
    ruta_segura(carpeta / 'proposal.md')
    exigir_spec(carpeta, estado)
    if not estado.get('requisitos'):
        raise FactoryError(f'primero importá los requisitos: oracle-factory importar {identificador}')
    try:
        requisitos, catalogo, catalogo_sha = inventario_medidas(estado)
    except ValueError as e:
        raise FactoryError(f'Oracle rechazó requisito o catálogo: {e}') from e
    if listar_opciones:
        if requisito_id is not None or medidas or sin_medir is not None or quitar_sin_medir:
            raise FactoryError('--listar no acepta opciones de edición')
        print('Requisitos de este cambio (sin evaluar cumplimiento):')
        for rid, r in requisitos.items():
            print(f"{rid}\n  Archivo: {ROOT / 'requisitos' / (rid + '.requisito')}\n  Texto: {r.texto}\n  Fuente: {r.fuente}")
            print('  Medidas: ' + (', '.join(r.medido_por) or 'ninguna'))
            print('  SIN MEDIR: ' + (r.sin_medir or 'sin límite adicional declarado; no prueba cobertura semántica'))
        print('Medidas efectivas disponibles:')
        for mid, m in sorted(catalogo.items()):
            print(f'{mid}\n  Archivo: {catalogo.entradas[mid].ruta}\n  Umbral: {m.op} {m.limite} · según {m.segun}\n  Ámbito: {m.ambito}\n  Alcance: {m.alcance}')
        print('La persona elige y justifica la pertinencia. No se ejecutaron pruebas ni un juicio.')
        return
    if requisito_id not in requisitos:
        raise FactoryError('usá el id completo de un requisito importado por este cambio; recuperalo con medir ID --listar')
    if not medidas:
        raise FactoryError('indicá al menos una --medida con su id completo')
    if len(set(medidas)) != len(medidas):
        raise FactoryError('no repitas una medida')
    desconocidas = sorted(set(medidas) - set(catalogo))
    if desconocidas:
        raise FactoryError('medidas inexistentes o no efectivas en este proyecto: ' + ', '.join(desconocidas))
    if sin_medir is not None and (not sin_medir.strip() or quitar_sin_medir):
        raise FactoryError('--sin-medir necesita un límite no vacío y no se combina con --quitar-sin-medir')
    tipo = (estado.get('tipos') or {}).get(requisito_id, 'funcional')
    via = modos.via_agente(modo_de(estado), 'medidas', [tipo]) if AGENTE else 'persona'
    if via == 'rechaza':
        raise FactoryError(f'en modo {modo_de(estado)}, las medidas de un requisito {tipo} las elige una persona desde una terminal interactiva, sin --agente')
    if via == 'persona' and not terminal_interactiva():
        raise FactoryError('elegir medidas es una decisión de persona y se toma desde una terminal interactiva; un agente usa --agente')
    motivo = pedir_motivo(estado, 'medidas', [tipo], f'Medidas de {requisito_id}') if via == 'persona' else None
    from dataclasses import replace
    from oracle_metalenguaje.nucleo import requisito
    from oracle_metalenguaje.nucleo.forma import error_forma
    ruta = ROOT / 'requisitos' / f'{requisito_id}.requisito'
    original = ruta.read_bytes()
    registro_original = (ruta_registro(carpeta)).read_bytes()
    doc_original = documentos(carpeta, estado)
    r = requisitos[requisito_id]
    if (requisito.Requisito.de_datos(requisito.leer(original.decode('utf-8'))) != r
            or json.loads(registro_original) != estado
            or doc_original != estado['spec_aprobada']['documentos']):
        raise FactoryError('las entradas cambiaron durante la lectura; volvé a listar')
    limite = '' if quitar_sin_medir else (sin_medir if sin_medir is not None else r.sin_medir)
    nuevo_r = replace(r, medido_por=tuple(medidas), sin_medir=limite)
    if nuevo_r == r:
        # El archivo ya tiene estas medidas: lo que falta, si algo, es el registro de quién las decidió.
        pendiente = (estado.get('medidas_pendientes') or {}).get(requisito_id)
        registro = (estado.get('medidas') or {}).get(requisito_id)
        huella = sha256(original)
        if registro and registro.get('sha256') in (None, huella) and not pendiente:
            print('Sin cambios en la asociación; conservé la revisión y el juicio existentes.')
            return
        if via == 'propone':
            if pendiente and pendiente['sha256'] == huella and not pendiente.get('descartada'):
                print('Sin cambios: la propuesta ya está registrada, a la espera de una persona.')
                return
            estado.setdefault('medidas_pendientes', {})[requisito_id] = {'sha256': huella, **actor(), 'cuando': ahora()}
            (estado.get('medidas') or {}).pop(requisito_id, None)
            evento(estado, 'medidas_propuestas', forma='propuso', requisito=requisito_id, medidas=medidas)
            escribir_atomico(ruta_registro(carpeta), bytes_json(estado), esperado=registro_original)
            nota_tarea(identificador, f'Medidas de {requisito_id} propuestas por {AGENTE} (agente, modo {modo_de(estado)}); '
                       'no cuentan hasta que una persona las confirme.')
            print(f'Propuesta de {AGENTE} (modo {modo_de(estado)}): las medidas que el archivo ya tiene no cuentan hasta que '
                  f'una persona las confirme desde una terminal interactiva: oracle-factory medir {identificador} --confirmar')
            return
        # La persona confirma tal cual lo propuesto (mismos bytes) o decide; el agente que ahora decide
        # reemplaza su propia propuesta.
        forma = 'confirmo' if (via == 'persona' and pendiente and pendiente['sha256'] == huella
                               and not pendiente.get('descartada')) else 'decidio'
        (estado.get('medidas_pendientes') or {}).pop(requisito_id, None)
        registrar_medidas(estado, requisito_id, forma, motivo, original)
        evento(estado, 'medidas_confirmadas' if forma == 'confirmo' else 'medidas_elegidas', forma=forma,
               requisito=requisito_id, medidas=medidas)
        escribir_atomico(ruta_registro(carpeta), bytes_json(estado), esperado=registro_original)
        nota_tarea(identificador, f'Medidas de {requisito_id}: {quien(estado["medidas"][requisito_id])}.')
        print(f'Medidas de {requisito_id} confirmadas tal como las propuso {pendiente["actor"]}.' if forma == 'confirmo'
              else f'Medidas de {requisito_id} registradas como decisión de {quien(estado["medidas"][requisito_id])}.')
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
            raise FactoryError(error)
    except ValueError as e:
        raise FactoryError(f'Oracle rechazó la asociación propuesta: {e}') from e
    with bloqueo_medidas(identificador):
        ruta_segura(ruta)
        ruta_segura(ruta_registro(carpeta))
        if (ruta.read_bytes() != original or (ruta_registro(carpeta)).read_bytes() != registro_original
                or documentos(carpeta, estado) != doc_original):
            raise FactoryError('requisito, registro o spec cambió durante la operación; volvé a listar')
        try:
            _, _, actual_sha = inventario_medidas(estado)
        except (ValueError, OSError) as e:
            raise FactoryError(f'el catálogo cambió durante la operación: {e}') from e
        if actual_sha != catalogo_sha:
            raise FactoryError('el catálogo cambió durante la operación; volvé a listar')
        # Invalidar primero: si falla después la escritura, nunca queda un verde anterior vigente.
        estado.update(revision=None, oracle=None, fase='requisitos_importados')
        if via == 'propone':
            estado.setdefault('medidas_pendientes', {})[requisito_id] = {'sha256': sha256(datos), **actor(), 'cuando': ahora()}
            (estado.get('medidas') or {}).pop(requisito_id, None)
        else:
            (estado.get('medidas_pendientes') or {}).pop(requisito_id, None)
            registrar_medidas(estado, requisito_id, 'decidio', motivo, datos)
        evento(estado, 'medidas_propuestas' if via == 'propone' else 'medidas_elegidas',
               forma='propuso' if via == 'propone' else 'decidio', requisito=requisito_id, medidas=medidas, sin_medir=limite)
        escribir_atomico(ruta_registro(carpeta), (json.dumps(estado, ensure_ascii=False, indent=2) + '\n').encode(), esperado=registro_original)
        escribir_atomico(ruta, datos, esperado=original)
    nota_tarea(identificador, f'Medidas de {requisito_id}: {", ".join(medidas)}; {"propuestas" if via == "propone" else "elegidas"} por {quien(registro_decision(estado, "propuso" if via == "propone" else "decidio", motivo))}. SIN MEDIR: {limite or "sin límite adicional declarado"}. Revisión y juicio anteriores invalidados; no se declara cumplimiento ni aprobación de pertinencia.')
    print(f'Asociación guardada: {ruta}')
    print('SIN MEDIR: ' + (limite or 'sin límite adicional declarado; revisá la pertinencia y el alcance de las medidas'))
    print('Revisión y juicio anteriores invalidados. Ejecutá pruebas/sensor, registrá la versión y renová la revisión antes de juzgar.')
    if via == 'propone':
        print(f'Propuesta de {AGENTE} (modo {modo_de(estado)}): no cuenta hasta que una persona la confirme desde una '
              f'terminal interactiva: oracle-factory medir {identificador} --confirmar')


def confirmar_medidas(identificador: str) -> None:
    """Las medidas que propuso el agente, por requisito, confirmadas de una vez o de a una."""
    _, estado = abierto(identificador)
    exigir_terminal("confirmar medidas")
    propuestas = {r: p for r, p in (estado.get("medidas_pendientes") or {}).items() if not p.get("descartada")}
    # Sólo se confirma lo que el agente propuso: si el requisito cambió después, ya no es su propuesta.
    cambiadas = sorted(r for r, p in propuestas.items()
                       if sha256((ROOT / "requisitos" / f"{r}.requisito").read_bytes()) != p["sha256"])
    for rid in cambiadas:
        print(f"Aviso: {rid} cambió después de la propuesta; no se confirma acá. Revisalo con oracle-factory medir "
              f"{identificador} --listar y decidilo con medir --requisito.")
    pendientes = sorted(set(propuestas) - set(cambiadas))
    if not pendientes:
        print("No hay medidas propuestas pendientes de confirmar.")
        return
    try:
        requisitos, _, _ = inventario_medidas(estado)
    except ValueError as e:
        raise FactoryError(f"Oracle rechazó requisito o catálogo: {e}") from e
    print(f"Medidas propuestas en {identificador}:")
    for rid in pendientes:
        r = requisitos[rid]
        print(f"  {rid}\n    Medidas: {', '.join(r.medido_por) or 'ninguna'}\n    "
              + (f"SIN MEDIR: {r.sin_medir} (queda a medio cubrir: juzgar no lo dará cubierto)" if r.sin_medir
                 else "Sin límite sin medir: queda cubierto"))
    i = elegir(f"¿Qué hacés con las {len(pendientes)} propuestas?",
               [("Confirmar todas", "quedan como decisión tuya, tal como las propuso el agente"),
                ("Decidir de a una", "te pregunto por cada requisito"), ("Cancelar", "no registra nada")])
    if i not in (0, 1):
        raise FactoryError("confirmación cancelada; no registré nada")
    elegidos = pendientes
    if i == 1:  # primero todas las respuestas: una que no es opción cancela sin haber registrado ninguna
        elegidos = []
        for rid in pendientes:
            j = elegir(f"¿Confirmás las medidas de {rid}?", [("Confirmar", "queda como decisión tuya"),
                                                            ("Saltear", "sigue pendiente")])
            if j is None:
                raise FactoryError("confirmación cancelada; no registré nada")
            if j == 0:
                elegidos.append(rid)
    for rid in elegidos:
        medir(identificador, requisito_id=rid, medidas=list(requisitos[rid].medido_por))


def construir_parser() -> argparse.ArgumentParser:
    """La interfaz de la CLI; también la usan las pruebas que comprueban que la web sólo nombra comandos que existen."""
    parser = argparse.ArgumentParser(prog="oracle-factory", description="Factory local con gates humanos, OpenSpec, oracle-task y Oracle")
    parser.add_argument("--version", action="version", version=f"oracle-factory {__version__}")
    parser.add_argument("--proyecto", type=Path, default=None, help="carpeta del proyecto; por defecto se busca .factory/ subiendo desde la carpeta actual y, si no hay, se usa la actual; colocar antes del subcomando")
    parser.add_argument("--agente", default=os.environ.get("FACTORY_AGENTE"), help="actuar como agente con este nombre (o FACTORY_AGENTE); queda registrado como agente, nunca como persona")
    sub = parser.add_subparsers(dest="comando", required=True)
    sub.add_parser("init", help="inicializar Oracle, tareas y acuerdos sin sobrescribir configuración")
    p = sub.add_parser("ejemplo", help="copiar el ejemplo incluido a una carpeta nueva")
    p.add_argument("nombre", choices=["notas"])
    p.add_argument("--destino", type=Path, default=Path("examples/notas"))
    p = sub.add_parser("nuevo", help="crear tarea y paquete OpenSpec")
    p.add_argument("--capacidad")
    p.add_argument("--con-ejemplo", choices=["notas"], help="preparar documentos y catálogos del ejemplo en destinos nuevos")
    p.add_argument("--modo", choices=modos.MODOS, help="modo de trabajo del cambio (por defecto, el del proyecto)")
    p.add_argument("--sufijo", help="cómo termina el ID del cambio (por defecto, la capacidad)")
    p.add_argument("titulo")
    q = sub.add_parser('listar', help='recuperar IDs completos y fases de cambios Factory')
    q.add_argument('--fase', help='sólo los cambios en esta fase')
    grupo = q.add_mutually_exclusive_group()
    grupo.add_argument('--abiertos', action='store_true', help='sólo los cambios abiertos')
    grupo.add_argument('--cerrados', action='store_true', help='sólo los cambios cerrados')
    q = sub.add_parser('pedir-revision', help='pedir una revisión independiente del candidato actual a un revisor configurado')
    q.add_argument('id'); q.add_argument('--a', dest='revisor', required=True, help='nombre del revisor en .factory/config.json')
    q.add_argument('--pedir', help='indicaciones que se agregan al pedido'); q.add_argument('--base', help='base del paquete de Clue')
    q = sub.add_parser('resumen', help='escribir .factory/resumen.md: lo vigente, los cambios abiertos, riesgos aceptados y límites')
    q.add_argument('--verificar', action='store_true', help='no escribe; falla si el resumen falta o quedó viejo')
    q.add_argument('--salida', type=Path, help='otra ruta dentro del proyecto (fuera de .factory/ cuenta en la huella)')
    q.add_argument('--ver', action='store_true', help='además, mostrarlo: con glow si está instalado, si no como texto')
    sub.add_parser('archivar', help='fusionar en openspec/specs/ la spec de los cambios cerrados que todavía no lo están')
    q = sub.add_parser('migrar', help='pasar el estado de cada cambio y la configuración a .factory/ (fase 2 de la estructura)')
    q.add_argument('--verificar', action='store_true', help='listar lo que movería sin escribir; falla si hay algo por migrar')
    q = sub.add_parser('donde', help='listar los artefactos de un cambio, su ruta y el gate que respaldan (sólo lectura)')
    q.add_argument('id'); q.add_argument('--candidato', help='limitarse a los artefactos de este commit (prefijo del SHA)')
    q = sub.add_parser('ruta', help='imprimir la ruta canónica donde producir un artefacto sobre el HEAD actual (no crea nada)')
    q.add_argument('id'); q.add_argument('tipo', help='evidencia, clue, revision o checkout')
    q = sub.add_parser('buscar', help='buscar un texto en propuestas, specs, requisitos, tareas y registros (sólo lectura)')
    q.add_argument('texto'); q.add_argument('--max', type=int, default=200, dest='maximo', help='máximo de líneas a mostrar')
    q = sub.add_parser('modo', help='cambiar el modo de trabajo de un cambio')
    q.add_argument('id'); q.add_argument('nuevo_modo', choices=modos.MODOS)
    q = sub.add_parser('medir', help='listar y asociar medidas explícitas sin editar requisitos a mano')
    q.add_argument('id')
    q.add_argument('--listar', action='store_true')
    q.add_argument('--requisito', help='id completo importado por este cambio')
    q.add_argument('--medida', action='append', help='id completo de una medida efectiva; repetible')
    limites = q.add_mutually_exclusive_group()
    limites.add_argument('--sin-medir', help='declarar el límite que permanece sin medir')
    limites.add_argument('--quitar-sin-medir', action='store_true', help='eliminar explícitamente ese límite; no prueba pertinencia ni cumplimiento')
    limites.add_argument('--confirmar', action='store_true', help='confirmar con un menú las medidas que propuso el agente')
    q = sub.add_parser('revisar', help='revisión guiada del candidato vigente: muestra, pregunta y registra (persona); '
                       'con --agente deja la decisión y el motivo que propone')
    q.add_argument('id')
    q.add_argument('--decision', choices=['aprobar', 'cambios'], help='sólo con --agente: la decisión que propone')
    q.add_argument('--motivo', help='sólo con --agente: el motivo que propone')
    for nombre, ayuda in (("aprobar-spec", "aceptación humana explícita de la propuesta/spec"),
                          ("revision-preparar", "preparar informe guiado y decisiones pendientes sin aprobar"),
                          ("importar", "importar requisitos de la spec aceptada a Oracle"),
                          ("estado", "mostrar estado y gates pendientes"),
                          ("cerrar", "cierre humano si todos los gates pasaron")):
        q = sub.add_parser(nombre, help=ayuda)
        q.add_argument("id")
    p = sub.add_parser("revision", help="registrar un informe de CodeRabbit/revisor y decisión humana")
    p.add_argument("id"); p.add_argument("--informe", type=Path, required=True)
    p.add_argument("--revisor", required=True); p.add_argument("--decision", choices=("aprobar", "cambios"), required=True)
    p.add_argument('--formato', choices=('libre', 'guiado'), default='libre')
    p.add_argument('--decisiones', type=Path, help='documento de decisiones separado, sólo en modo guiado')
    p.add_argument("--hallazgos-abiertos", type=int, help='obligatorio en formato libre; se deriva en guiado')
    p = sub.add_parser("juzgar", help="correr Oracle sobre evidencia del sensor")
    p.add_argument("id"); p.add_argument("--con", type=Path, help="hechos del sensor; por defecto, los del candidato (oracle-factory ruta ID evidencia)")
    return parser


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
        if args.comando == "init": inicializar()
        elif args.comando == "ejemplo": copiar_ejemplo(args.destino)
        elif args.comando == "nuevo": nuevo(args.titulo, args.capacidad, args.con_ejemplo, args.modo, args.sufijo)
        elif args.comando == "modo": cambiar_modo(args.id, args.nuevo_modo)
        elif args.comando == "listar": listar(args.fase, args.abiertos, args.cerrados)
        elif args.comando == "migrar": comando_migrar(args.verificar)
        elif args.comando == "archivar": archivar()
        elif args.comando == "resumen": comando_resumen(args.verificar, args.salida, args.ver)
        elif args.comando == "pedir-revision": pedir_revision(args.id, args.revisor, args.pedir, args.base)
        elif args.comando == "donde": comando_donde(args.id, args.candidato)
        elif args.comando == "ruta": comando_ruta(args.id, args.tipo)
        elif args.comando == "buscar": comando_buscar(args.texto, args.maximo)
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
        elif args.comando == "juzgar": juzgar(args.id, ROOT / args.con if args.con else hechos_del_candidato(args.id))
        elif args.comando == "cerrar": cerrar(args.id)
        elif args.comando == "estado":
            mostrar(args.id)
            return ofrecer_siguiente(args.id)
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


if __name__ == "__main__":
    raise SystemExit(main())
