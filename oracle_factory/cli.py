#!/usr/bin/env python3
"""Orquestación mínima con aprobaciones humanas explícitas."""
from __future__ import annotations

import argparse
import datetime as dt
import getpass
import hashlib
import json
import os
import tempfile
from contextlib import contextmanager
import re
import subprocess
import sys
from importlib import metadata, resources

from . import __version__
from pathlib import Path

ROOT = Path.cwd().resolve()
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


def leer(identificador: str) -> tuple[Path, dict]:
    carpeta = ruta_cambio(identificador)
    archivo = ruta_segura(carpeta / "factory.json")
    if not archivo.is_file():
        raise FactoryError(f"no encuentro el registro de factory: {archivo}")
    return carpeta, json.loads(archivo.read_text(encoding="utf-8"))


def guardar(carpeta: Path, estado: dict) -> None:
    (carpeta / "factory.json").write_text(
        json.dumps(estado, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def evento(estado: dict, accion: str, **datos) -> None:
    estado.setdefault("eventos", []).append({
        "accion": accion, "por": getpass.getuser(), "cuando": ahora(), **datos})


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


def nuevo(titulo: str, capacidad: str | None = None, con_ejemplo: str | None = None) -> str:
    if con_ejemplo and (con_ejemplo != 'notas' or capacidad not in (None, 'notas')):
        raise FactoryError('--con-ejemplo notas requiere capacidad notas, o no indicar --capacidad')
    capacidad = capacidad or ('notas' if con_ejemplo else None)
    if capacidad is None:
        raise FactoryError('indicá --capacidad o --con-ejemplo notas')
    ruta_segura(CHANGES)
    ruta_segura(ROOT / "tareas")
    if not SLUG_RE.fullmatch(capacidad):
        raise FactoryError("capacidad debe ser un slug OpenSpec: minúsculas, números y guiones")
    plan = plan_ejemplo() if con_ejemplo else {}
    if plan:
        preparar_ejemplo(plan)
    p = ejecutar(["tasks", "new", titulo, "--json", "--proyecto", str(ROOT)])
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
            "eventos": [],
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
    nota_tarea(identificador, f"OpenSpec: {carpeta.relative_to(ROOT)}. Estado de factory: espera aprobación humana de proposal.md y spec.md.")
    print(f"Cambio creado: {identificador}")
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
        raise FactoryError("primero una persona debe aprobar la propuesta y la spec")
    if aprobacion.get("documentos") != documentos(carpeta, estado):
        raise FactoryError("la propuesta/spec cambió o su aprobación es antigua; renová la aprobación humana")


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
        partes = Path(nombre).parts
        if partes[0] == "tareas" or (len(partes) == 4 and partes[:2] == ("openspec", "changes")
                and partes[-1] in {"factory.json", "review.md", "oracle-veredicto.txt"}):
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
    print("Aceptar reinicia importación, revisión y veredicto de este cambio.")
    if input(f"Escribí APROBAR ESPECIFICACION {identificador}: ").strip() != f"APROBAR ESPECIFICACION {identificador}":
        raise FactoryError("aprobación cancelada; no cambié el estado")
    if documentos(carpeta, estado) != huellas:
        raise FactoryError("los documentos cambiaron durante la aprobación; volvé a revisarlos")
    estado["spec_sha256"] = huellas[estado["spec"]]
    estado["spec_aprobada"] = {"por": getpass.getuser(), "cuando": ahora(), "documentos": huellas}
    estado.update(requisitos=[], revision=None, oracle=None, fase="spec_aprobada")
    evento(estado, "spec_aprobada", documentos=huellas)
    guardar(carpeta, estado)
    nota_tarea(identificador, f"Persona aprobó propuesta y spec {estado['spec']}; se reiniciaron las validaciones dependientes.")
    print("Alcance aprobado; sus requisitos todavía deben importarse y medirse.")
    siguiente(identificador, estado["fase"])

def importar(identificador: str) -> None:
    carpeta, estado = abierto(identificador)
    exigir_spec(carpeta, estado)
    spec = ROOT / estado["spec"]
    # Oracle preserva requisitos existentes. Aislamos cada tarea y versión de spec
    # para que una promesa nueva no herede medidas de una promesa anterior.
    version = sha256((identificador + ":" + estado["spec_sha256"]).encode())[:16]
    dominio = estado["capacidad"].replace("-", "_") + "_c" + version
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
    estado["requisitos"] = ids
    estado["fase"] = "requisitos_importados"
    evento(estado, "requisitos_importados", ids=ids)
    guardar(carpeta, estado)
    nota_tarea(identificador, "Requisitos importados: " + ", ".join(ids) + ". Los nuevos nacen SIN MEDIR; verificá cobertura antes del juicio.")
    print("La persona debe revisar medidas y límites de cada requisito.")
    siguiente(identificador, estado["fase"])

def revisar(identificador: str, informe: Path, revisor: str, decision: str, abiertos: int) -> None:
    carpeta, estado = abierto(identificador)
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
    destino = carpeta / "review.md"
    print(f"Revisor: {revisor}; decisión: {decision}; abiertos: {abiertos}; commit: {contexto['head']}")
    if input(f"Escribí REGISTRAR REVISION {identificador}: ").strip() != f"REGISTRAR REVISION {identificador}":
        raise FactoryError("registro de revisión cancelado")
    exigir_spec(carpeta, estado)
    if contexto_producto() != contexto:
        raise FactoryError("el producto cambió durante la confirmación; repetí la revisión")
    destino.write_bytes(contenido)
    estado["revision"] = {
        "revisor": revisor, "decision": decision, "hallazgos_abiertos": abiertos,
        "informe": str(destino.relative_to(ROOT)), "sha256": huella,
        "por": getpass.getuser(), "cuando": ahora(), "contexto": contexto,
    }
    estado["oracle"] = None
    estado["fase"] = "revision_aprobada" if decision == "aprobar" else "cambios_pedidos"
    evento(estado, "revision_registrada", revisor=revisor, decision=decision, abiertos=abiertos, sha256=huella)
    guardar(carpeta, estado)
    nota_tarea(identificador, f"Revisión {revisor}: {decision}; {abiertos} abiertos; commit {contexto['head']}; informe {destino.relative_to(ROOT)}.")
    print(f"Informe registrado: {destino}")
    siguiente(identificador, estado["fase"])

def juzgar(identificador: str, hechos: Path) -> None:
    carpeta, estado = abierto(identificador)
    # Una corrida fallida nunca debe dejar disponible el verde de la anterior.
    estado.update(oracle=None, fase="juicio_pendiente")
    guardar(carpeta, estado)
    exigir_spec(carpeta, estado)
    if not estado.get("requisitos"):
        raise FactoryError("importá primero los requisitos de la spec aprobada")
    hechos = hechos.resolve()
    if not hechos.is_file():
        raise FactoryError(f"no encuentro los hechos del sensor: {hechos}")
    contexto = contexto_producto()
    huella = sha256(hechos.read_bytes())
    cobertura = ejecutar(["oracle", "cobertura", "--proyecto", str(ROOT)])
    if cobertura.returncode or not requisitos_verdes(cobertura.stdout, estado["requisitos"]):
        raise FactoryError("Oracle todavía no tiene cobertura completa de cada requisito importado")
    p = ejecutar(["oracle", "cobertura", "--con", str(hechos), "--proyecto", str(ROOT)])
    sys.stdout.write(p.stdout)
    if p.stderr:
        sys.stderr.write(p.stderr)
    if contexto_producto() != contexto or sha256(hechos.read_bytes()) != huella:
        raise FactoryError("el producto o los hechos cambiaron durante el juicio; repetí la corrida")
    exigir_spec(carpeta, estado)
    informe = carpeta / "oracle-veredicto.txt"
    informe.write_text(p.stdout + p.stderr, encoding="utf-8")
    ok = p.returncode == 0 and requisitos_verdes(p.stdout, estado["requisitos"])
    estado["oracle"] = {
        "codigo": 0 if ok else 1, "codigo_oracle": p.returncode,
        "hechos": str(hechos), "hechos_sha256": huella,
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
    if not estado.get("spec_aprobada"):
        faltan.append("aprobación humana de spec")
    if not estado.get("requisitos"):
        faltan.append("importación OpenSpec → requisitos Oracle")
    rev = estado.get("revision") or {}
    if rev.get("decision") != "aprobar" or rev.get("hallazgos_abiertos") != 0:
        faltan.append("revisión humana aprobada y sin hallazgos abiertos")
    oracle = estado.get("oracle") or {}
    if oracle.get("codigo") != 0:
        faltan.append("veredicto Oracle exitoso con evidencia")
    return faltan


def pendientes_actuales(carpeta: Path, estado: dict) -> list[str]:
    faltan = pendientes(estado)
    try:
        exigir_spec(carpeta, estado)
    except (FactoryError, OSError) as e:
        faltan.append(str(e))
    if estado.get("revision") or estado.get("oracle"):
        try:
            contexto = contexto_producto()
            for nombre in ("revision", "oracle"):
                registro = estado.get(nombre)
                if registro and registro.get("contexto") != contexto:
                    faltan.append(nombre + " desactualizado respecto del producto")
        except (FactoryError, OSError) as e:
            faltan.append(str(e))
    rev = estado.get("revision") or {}
    oracle = estado.get("oracle") or {}
    for etiqueta, ruta, huella in (
        ("informe de revisión", rev.get("informe"), rev.get("sha256")),
        ("informe Oracle", oracle.get("informe"), oracle.get("informe_sha256")),
        ("hechos", oracle.get("hechos"), oracle.get("hechos_sha256")),
    ):
        if not ruta and not huella:
            continue
        try:
            if not ruta or not huella or sha256((ROOT / ruta).read_bytes()) != huella:
                faltan.append(etiqueta + " cambiado o sin huella")
        except OSError:
            faltan.append(etiqueta + " ausente")
    # Los registros antiguos sólo tenían un código numérico: no son evidencia vigente.
    if rev and not all(rev.get(k) for k in ("informe", "sha256", "contexto")):
        faltan.append("revisión sin evidencia vinculada")
    if oracle and not all(oracle.get(k) for k in ("informe", "informe_sha256", "hechos", "hechos_sha256", "contexto")):
        faltan.append("juicio sin evidencia vinculada")
    return faltan


def cerrar(identificador: str) -> None:
    carpeta, estado = abierto(identificador)
    falta = pendientes_actuales(carpeta, estado)
    if falta:
        raise FactoryError("no se puede cerrar: " + "; ".join(falta))
    print(f"Se cerrará la tarea {identificador}; Oracle {estado['oracle']['informe']}; revisión {estado['revision']['informe']}.")
    if input(f"Escribí CERRAR {identificador}: ").strip() != f"CERRAR {identificador}":
        raise FactoryError("cierre cancelado; la tarea sigue abierta")
    falta = pendientes_actuales(carpeta, estado)
    if falta:
        raise FactoryError("el contexto cambió durante el cierre: " + "; ".join(falta))
    nota_tarea(identificador, "Persona autorizó el cierre tras revisar el informe de código y el veredicto Oracle.")
    p = ejecutar(["tasks", "close", identificador, "--proyecto", str(ROOT)])
    if p.returncode:
        raise FactoryError(p.stderr.strip() or "oracle-task no pudo cerrar la tarea")
    estado["fase"] = "cerrada"
    evento(estado, "cierre_humano", oracle=estado["oracle"]["informe"], revision=estado["revision"]["informe"])
    guardar(carpeta, estado)
    print(p.stdout.strip() or "Tarea cerrada.")


def mostrar(identificador: str) -> None:
    carpeta, estado = leer(identificador)
    print(f"{estado['id']} — {estado['titulo']}\nFase: {estado['fase']}")
    print("Requisitos Oracle: " + (", ".join(estado.get("requisitos", [])) or "todavía no importados"))
    print("Pendiente: " + ("; ".join(pendientes_actuales(carpeta, estado)) or "ninguno"))
    print("Aprobación spec: " + ("sí" if estado.get("spec_aprobada") else "esperando a la persona"))
    rev = estado.get("revision")
    print("Revisión: " + (f"{rev['revisor']} / {rev['decision']} / {rev['hallazgos_abiertos']} abiertos" if rev else "pendiente"))
    oracle = estado.get("oracle")
    print("Oracle: " + (f"código {oracle['codigo']} ({oracle['informe']})" if oracle else "pendiente"))
    siguiente(identificador, estado["fase"])


def inicializar() -> None:
    ROOT.mkdir(parents=True, exist_ok=True)
    for nombre in ("tareas", "catalogos", "corpus", "diferencial", "relaciones", "requisitos", "macros", "oracle.json", ".gitignore", "openspec/changes"):
        ruta_segura(ROOT / nombre)
    for comando in (["tasks", "init", str(ROOT), "--sin-readme"], ["oracle", "init", str(ROOT)]):
        resultado = ejecutar(comando)
        if resultado.returncode:
            raise FactoryError(resultado.stderr or resultado.stdout)
    ruta_segura(CHANGES).mkdir(parents=True, exist_ok=True)
    ignore = ruta_segura(ROOT / '.gitignore')
    contenido = ignore.read_text(encoding='utf-8') if ignore.exists() else ''
    pendientes = [line for line in ('.factory-demo/', '__pycache__/', '*.py[cod]') if line not in contenido.splitlines()]
    if pendientes:
        with ignore.open('a', encoding='utf-8') as archivo:
            archivo.write(('\n' if contenido and not contenido.endswith('\n') else '') + '\n'.join(pendientes) + '\n')
    print(f'Factory inicializada en {ROOT}. No se crearon commits ni aprobaciones.')
    print(f'Acuerdos: {CHANGES}; tareas: {ROOT / "tareas"}; configuración: {ROOT / "oracle.json"}.')
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


def siguiente(identificador: str, fase: str) -> None:
    acciones = {
        'espera_aprobacion_spec': f'oracle-factory aprobar-spec {identificador}',
        'spec_aprobada': f'oracle-factory importar {identificador}',
        'requisitos_importados': f'oracle-factory medir {identificador} --listar',
        'revision_aprobada': f'oracle-factory juzgar {identificador} --con RUTA_DE_HECHOS',
        'cambios_pedidos': f'oracle-factory estado {identificador}',
        'oracle_verde': f'oracle-factory estado {identificador}',
        'oracle_rojo': f'oracle-factory estado {identificador}',
    }
    if fase in acciones:
        print('Próximo paso: ' + acciones[fase])


def listar() -> None:
    ruta_segura(CHANGES)
    if not CHANGES.exists():
        print('No hay cambios Factory. Empezá con oracle-factory init.')
        return
    encontrados = 0
    for carpeta in sorted(CHANGES.iterdir()):
        if not ID_RE.fullmatch(carpeta.name):
            continue
        ruta_segura(carpeta)
        if not (carpeta / 'factory.json').exists():
            continue
        _, estado = leer(carpeta.name)
        print(f"{carpeta.name}  {estado['fase']}  {estado['titulo']}")
        encontrados += 1
    if not encontrados:
        print('No hay cambios Factory; las tareas del tracker por sí solas no son cambios Factory.')
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
    ruta_segura(carpeta / 'factory.json')
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
    from dataclasses import replace
    from oracle_metalenguaje.nucleo import requisito
    from oracle_metalenguaje.nucleo.forma import error_forma
    ruta = ROOT / 'requisitos' / f'{requisito_id}.requisito'
    original = ruta.read_bytes()
    registro_original = (carpeta / 'factory.json').read_bytes()
    doc_original = documentos(carpeta, estado)
    r = requisitos[requisito_id]
    if (requisito.Requisito.de_datos(requisito.leer(original.decode('utf-8'))) != r
            or json.loads(registro_original) != estado
            or doc_original != estado['spec_aprobada']['documentos']):
        raise FactoryError('las entradas cambiaron durante la lectura; volvé a listar')
    limite = '' if quitar_sin_medir else (sin_medir if sin_medir is not None else r.sin_medir)
    nuevo_r = replace(r, medido_por=tuple(medidas), sin_medir=limite)
    if nuevo_r == r:
        print('Sin cambios en la asociación; conservé la revisión y el juicio existentes.')
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
        ruta_segura(carpeta / 'factory.json')
        if (ruta.read_bytes() != original or (carpeta / 'factory.json').read_bytes() != registro_original
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
        evento(estado, 'medidas_elegidas', requisito=requisito_id, medidas=medidas, sin_medir=limite)
        escribir_atomico(carpeta / 'factory.json', (json.dumps(estado, ensure_ascii=False, indent=2) + '\n').encode(), esperado=registro_original)
        escribir_atomico(ruta, datos, esperado=original)
    nota_tarea(identificador, f'Medidas de {requisito_id}: {", ".join(medidas)}. SIN MEDIR: {limite or "sin límite adicional declarado"}. Revisión y juicio anteriores invalidados; no se declara cumplimiento ni aprobación de pertinencia.')
    print(f'Asociación guardada: {ruta}')
    print('SIN MEDIR: ' + (limite or 'sin límite adicional declarado; revisá la pertinencia y el alcance de las medidas'))
    print('Revisión y juicio anteriores invalidados. Ejecutá pruebas/sensor, registrá la versión y renová la revisión antes de juzgar.')


def main(argv: list[str] | None = None) -> int:
    global ROOT, CHANGES
    parser = argparse.ArgumentParser(prog="oracle-factory", description="Factory local con gates humanos, OpenSpec, oracle-task y Oracle")
    parser.add_argument("--version", action="version", version=f"oracle-factory {__version__}")
    parser.add_argument("--proyecto", type=Path, default=Path.cwd(), help="carpeta de trabajo (por defecto, la actual); colocar antes del subcomando")
    sub = parser.add_subparsers(dest="comando", required=True)
    sub.add_parser("init", help="inicializar Oracle, tareas y acuerdos sin sobrescribir configuración")
    p = sub.add_parser("ejemplo", help="copiar el ejemplo incluido a una carpeta nueva")
    p.add_argument("nombre", choices=["notas"])
    p.add_argument("--destino", type=Path, default=Path("examples/notas"))
    p = sub.add_parser("nuevo", help="crear tarea y paquete OpenSpec")
    p.add_argument("--capacidad")
    p.add_argument("--con-ejemplo", choices=["notas"], help="preparar documentos y catálogos del ejemplo en destinos nuevos")
    p.add_argument("titulo")
    sub.add_parser('listar', help='recuperar IDs completos y fases de cambios Factory')
    q = sub.add_parser('medir', help='listar y asociar medidas explícitas sin editar requisitos a mano')
    q.add_argument('id')
    q.add_argument('--listar', action='store_true')
    q.add_argument('--requisito', help='id completo importado por este cambio')
    q.add_argument('--medida', action='append', help='id completo de una medida efectiva; repetible')
    limites = q.add_mutually_exclusive_group()
    limites.add_argument('--sin-medir', help='declarar el límite que permanece sin medir')
    limites.add_argument('--quitar-sin-medir', action='store_true', help='eliminar explícitamente ese límite; no prueba pertinencia ni cumplimiento')
    for nombre, ayuda in (("aprobar-spec", "aceptación humana explícita de la propuesta/spec"),
                          ("importar", "importar requisitos de la spec aceptada a Oracle"),
                          ("estado", "mostrar estado y gates pendientes"),
                          ("cerrar", "cierre humano si todos los gates pasaron")):
        q = sub.add_parser(nombre, help=ayuda)
        q.add_argument("id")
    p = sub.add_parser("revision", help="registrar un informe de CodeRabbit/revisor y decisión humana")
    p.add_argument("id"); p.add_argument("--informe", type=Path, required=True)
    p.add_argument("--revisor", required=True); p.add_argument("--decision", choices=("aprobar", "cambios"), required=True)
    p.add_argument("--hallazgos-abiertos", type=int, default=0)
    p = sub.add_parser("juzgar", help="correr Oracle sobre evidencia del sensor")
    p.add_argument("id"); p.add_argument("--con", type=Path, required=True)
    args = parser.parse_args(argv)
    ROOT = args.proyecto.expanduser().resolve()
    CHANGES = ROOT / "openspec" / "changes"
    try:
        if args.comando != "init" and not ROOT.is_dir():
            raise FactoryError("el proyecto no existe; ejecutá primero init")
        if args.comando == "init": inicializar()
        elif args.comando == "ejemplo": copiar_ejemplo(args.destino)
        elif args.comando == "nuevo": nuevo(args.titulo, args.capacidad, args.con_ejemplo)
        elif args.comando == "listar": listar()
        elif args.comando == "medir": medir(args.id, requisito_id=args.requisito, medidas=args.medida, listar_opciones=args.listar, sin_medir=args.sin_medir, quitar_sin_medir=args.quitar_sin_medir)
        elif args.comando == "aprobar-spec": aprobar_spec(args.id)
        elif args.comando == "importar": importar(args.id)
        elif args.comando == "revision": revisar(args.id, ROOT / args.informe, args.revisor, args.decision, args.hallazgos_abiertos)
        elif args.comando == "juzgar": juzgar(args.id, ROOT / args.con)
        elif args.comando == "cerrar": cerrar(args.id)
        elif args.comando == "estado": mostrar(args.id)
        return 0
    except (FactoryError, OSError, json.JSONDecodeError, EOFError) as e:
        print(f"FACTORY BLOQUEADA: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
