#!/usr/bin/env python3
"""Orquestación mínima con aprobaciones humanas explícitas."""
from __future__ import annotations

import argparse
import datetime as dt
import getpass
import hashlib
import json
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
    return ruta


def leer(identificador: str) -> tuple[Path, dict]:
    carpeta = ruta_cambio(identificador)
    archivo = carpeta / "factory.json"
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


def nuevo(titulo: str, capacidad: str) -> str:
    if not SLUG_RE.fullmatch(capacidad):
        raise FactoryError("capacidad debe ser un slug OpenSpec: minúsculas, números y guiones")
    p = ejecutar(["tasks", "new", titulo, "--json", "--proyecto", str(ROOT)])
    if p.returncode:
        raise FactoryError(f"oracle-task no pudo crear la tarea: {p.stderr.strip()}")
    try:
        identificador = json.loads(p.stdout)["id"]
    except (json.JSONDecodeError, KeyError) as e:
        raise FactoryError("oracle-task no devolvió el id completo de la tarea") from e
    carpeta = ruta_cambio(identificador)
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
    guardar(carpeta, estado)
    nota_tarea(identificador, f"OpenSpec: {carpeta.relative_to(ROOT)}. Estado de factory: espera aprobación humana de proposal.md y spec.md.")
    print(f"Cambio creado: {identificador}")
    print(f"Tarea: {ROOT / 'tareas' / identificador / 'TAREA.md'}")
    print(f"Propuesta/spec/tasks: {carpeta}")
    print(f"Próximo paso humano: editar los TODO y revisar {carpeta / 'proposal.md'} y {spec}")
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


def inicializar() -> None:
    ROOT.mkdir(parents=True, exist_ok=True)
    for comando in (["tasks", "init", str(ROOT), "--sin-readme"], ["oracle", "init", str(ROOT)]):
        resultado = ejecutar(comando)
        if resultado.returncode:
            raise FactoryError(resultado.stderr or resultado.stdout)
        print(resultado.stdout, end="")
    CHANGES.mkdir(parents=True, exist_ok=True)
    ignore = ROOT / ".gitignore"
    contenido = ignore.read_text(encoding="utf-8") if ignore.exists() else ""
    if ".factory-demo/" not in contenido.splitlines():
        with ignore.open("a", encoding="utf-8") as archivo:
            archivo.write(("\n" if contenido and not contenido.endswith("\n") else "") + ".factory-demo/\n")
    print(f"Factory inicializada en {ROOT}. No se crearon commits ni aprobaciones.")


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
    p.add_argument("--capacidad", required=True)
    p.add_argument("titulo")
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
        elif args.comando == "nuevo": nuevo(args.titulo, args.capacidad)
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
