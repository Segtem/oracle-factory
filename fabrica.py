#!/usr/bin/env python3
"""Orquestación mínima con aprobaciones humanas explícitas."""
from __future__ import annotations

import argparse
import datetime as dt
import getpass
import hashlib
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
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
        raise FactoryError("id inválido; usá el id completo que imprimió trackertast")
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
    return subprocess.run(args, cwd=ROOT, capture_output=True, text=True, check=False)


def nota_tarea(identificador: str, texto: str) -> None:
    p = ejecutar(["tasks", "note", identificador, texto, "--proyecto", str(ROOT)])
    if p.returncode:
        raise FactoryError(f"trackertast no pudo registrar la nota: {p.stderr.strip()}")


def nuevo(titulo: str, capacidad: str) -> str:
    if not SLUG_RE.fullmatch(capacidad):
        raise FactoryError("capacidad debe ser un slug OpenSpec: minúsculas, números y guiones")
    p = ejecutar(["tasks", "new", titulo, "--json", "--proyecto", str(ROOT)])
    if p.returncode:
        raise FactoryError(f"trackertast no pudo crear la tarea: {p.stderr.strip()}")
    try:
        identificador = json.loads(p.stdout)["id"]
    except (json.JSONDecodeError, KeyError) as e:
        raise FactoryError("trackertast no devolvió el id completo de la tarea") from e
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


def aprobar_spec(identificador: str) -> None:
    carpeta, estado = leer(identificador)
    spec = ROOT / estado["spec"]
    propuesta = carpeta / "proposal.md"
    tareas = carpeta / "tasks.md"
    for archivo in (propuesta, spec, tareas):
        if not archivo.is_file() or "TODO:" in archivo.read_text(encoding="utf-8"):
            raise FactoryError(f"hay que completar y revisar primero: {archivo.relative_to(ROOT)}")
    contenido = spec.read_text(encoding="utf-8")
    if not re.search(r"(?m)^### Requirement:", contenido) or not re.search(r"(?m)^#### Scenario:", contenido):
        raise FactoryError("la spec debe tener al menos un Requirement y un Scenario de OpenSpec")
    huella = sha256(spec.read_bytes())
    print(f"Vas a aceptar esta spec: {spec.relative_to(ROOT)}")
    print(f"SHA-256: {huella}")
    if input(f"Escribí APROBAR ESPECIFICACION {identificador}: ").strip() != f"APROBAR ESPECIFICACION {identificador}":
        raise FactoryError("aprobación cancelada; no cambié el estado")
    estado["spec_sha256"] = huella
    estado["spec_aprobada"] = {"por": getpass.getuser(), "cuando": ahora(), "sha256": huella}
    estado["fase"] = "spec_aprobada"
    evento(estado, "spec_aprobada", sha256=huella)
    guardar(carpeta, estado)
    nota_tarea(identificador, f"Persona aprobó la spec OpenSpec {estado['spec']} (sha256 {huella}).")
    print("Spec aprobada por la persona; todavía no implica que sus requisitos estén medidos.")


def importar(identificador: str) -> None:
    carpeta, estado = leer(identificador)
    if not estado.get("spec_aprobada"):
        raise FactoryError("primero una persona debe aprobar la propuesta y la spec")
    spec = ROOT / estado["spec"]
    if sha256(spec.read_bytes()) != estado.get("spec_sha256"):
        raise FactoryError("la spec cambió después de aprobarse; pedí una nueva aprobación humana")
    dominio = estado["capacidad"].replace("-", "_")
    p = ejecutar(["oracle", "requisito", "importar", str(spec), "--dominio", dominio, "--escribir", "--proyecto", str(ROOT)])
    sys.stdout.write(p.stdout)
    if p.returncode:
        raise FactoryError(p.stderr.strip() or "Oracle no pudo importar los requisitos")
    ids = sorted(set(re.findall(r"(?m)^[+=]\s+([a-z][a-z0-9_.]*)", p.stdout)))
    if not ids:
        raise FactoryError("Oracle no devolvió ids; no doy la importación por confirmada")
    estado["requisitos"] = ids
    estado["fase"] = "requisitos_importados_sin_medicion"
    evento(estado, "requisitos_importados", ids=ids)
    guardar(carpeta, estado)
    nota_tarea(identificador, "Oracle importó requisitos como SIN MEDIR: " + ", ".join(ids) + ". Falta decisión humana sobre medidas y límites.")
    print("La persona debe decidir cómo medir cada requisito; no se inventó cobertura.")


def revisar(identificador: str, informe: Path, revisor: str, decision: str, abiertos: int) -> None:
    carpeta, estado = leer(identificador)
    if not estado.get("spec_aprobada"):
        raise FactoryError("no se registra revisión de código antes de aceptar la spec")
    if not informe.is_file():
        raise FactoryError(f"no encuentro el informe: {informe}")
    if abiertos < 0 or (decision == "aprobar" and abiertos):
        raise FactoryError("una revisión aprobada exige cero hallazgos abiertos")
    contenido = informe.read_bytes()
    destino = carpeta / "review.md"
    if informe.resolve() != destino.resolve():
        shutil.copyfile(informe, destino)
    huella = sha256(contenido)
    print(f"Revisor: {revisor}; decisión humana: {decision}; hallazgos abiertos: {abiertos}")
    if input(f"Escribí REGISTRAR REVISION {identificador}: ").strip() != f"REGISTRAR REVISION {identificador}":
        raise FactoryError("registro de revisión cancelado")
    estado["revision"] = {
        "revisor": revisor, "decision": decision, "hallazgos_abiertos": abiertos,
        "informe": str(destino.relative_to(ROOT)), "sha256": huella,
        "por": getpass.getuser(), "cuando": ahora(),
    }
    estado["fase"] = "revision_aprobada" if decision == "aprobar" else "cambios_pedidos"
    evento(estado, "revision_registrada", revisor=revisor, decision=decision, abiertos=abiertos, sha256=huella)
    guardar(carpeta, estado)
    nota_tarea(identificador, f"Revisión {revisor}: {decision}; {abiertos} hallazgos abiertos; informe {destino.relative_to(ROOT)}.")


def juzgar(identificador: str, hechos: Path) -> None:
    carpeta, estado = leer(identificador)
    if not estado.get("requisitos"):
        raise FactoryError("importá primero los requisitos de la spec aprobada")
    if not hechos.is_file():
        raise FactoryError(f"no encuentro los hechos del sensor: {hechos}")
    cobertura = ejecutar(["oracle", "cobertura", "--proyecto", str(ROOT)])
    if cobertura.returncode:
        raise FactoryError(cobertura.stderr.strip() or "Oracle no pudo leer la cobertura")
    faltan = [rid for rid in estado["requisitos"] if any(
        rid in linea and ("SIN MEDIR" in linea or "EN PARTE" in linea)
        for linea in cobertura.stdout.splitlines())]
    ausentes = [rid for rid in estado["requisitos"] if not any(rid in linea for linea in cobertura.stdout.splitlines())]
    if faltan or ausentes:
        raise FactoryError("Oracle todavía no tiene cobertura completa: " + ", ".join(faltan + ausentes))
    p = ejecutar(["oracle", "cobertura", "--con", str(hechos), "--proyecto", str(ROOT)])
    sys.stdout.write(p.stdout)
    if p.stderr:
        sys.stderr.write(p.stderr)
    informe = carpeta / "oracle-veredicto.txt"
    informe.write_text(p.stdout + p.stderr, encoding="utf-8")
    estado["oracle"] = {
        "codigo": p.returncode, "hechos": str(hechos.resolve()),
        "hechos_sha256": sha256(hechos.read_bytes()), "informe": str(informe.relative_to(ROOT)),
        "cuando": ahora(),
    }
    estado["fase"] = "oracle_verde" if p.returncode == 0 else "oracle_rojo"
    evento(estado, "oracle_ejecutado", codigo=p.returncode, hechos_sha256=estado["oracle"]["hechos_sha256"])
    guardar(carpeta, estado)
    nota_tarea(identificador, f"Oracle cobertura con hechos {hechos.resolve()} terminó con código {p.returncode}; informe {informe.relative_to(ROOT)}.")
    if p.returncode:
        raise FactoryError("Oracle no dio verde; la persona ve el informe y decide cómo seguir")


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


def cerrar(identificador: str) -> None:
    carpeta, estado = leer(identificador)
    falta = pendientes(estado)
    if falta:
        raise FactoryError("no se puede cerrar: " + "; ".join(falta))
    print(f"Se cerrará la tarea {identificador}; Oracle {estado['oracle']['informe']}; revisión {estado['revision']['informe']}.")
    if input(f"Escribí CERRAR {identificador}: ").strip() != f"CERRAR {identificador}":
        raise FactoryError("cierre cancelado; la tarea sigue abierta")
    nota_tarea(identificador, "Persona autorizó el cierre tras revisar el informe de código y el veredicto Oracle.")
    p = ejecutar(["tasks", "close", identificador, "--proyecto", str(ROOT)])
    if p.returncode:
        raise FactoryError(p.stderr.strip() or "trackertast no pudo cerrar la tarea")
    estado["fase"] = "cerrada"
    evento(estado, "cierre_humano", oracle=estado["oracle"]["informe"], revision=estado["revision"]["informe"])
    guardar(carpeta, estado)
    print(p.stdout.strip() or "Tarea cerrada.")


def mostrar(identificador: str) -> None:
    _, estado = leer(identificador)
    print(f"{estado['id']} — {estado['titulo']}\nFase: {estado['fase']}")
    print("Requisitos Oracle: " + (", ".join(estado.get("requisitos", [])) or "todavía no importados"))
    print("Pendiente: " + ("; ".join(pendientes(estado)) or "ninguno"))
    print("Aprobación spec: " + ("sí" if estado.get("spec_aprobada") else "esperando a la persona"))
    rev = estado.get("revision")
    print("Revisión: " + (f"{rev['revisor']} / {rev['decision']} / {rev['hallazgos_abiertos']} abiertos" if rev else "pendiente"))
    oracle = estado.get("oracle")
    print("Oracle: " + (f"código {oracle['codigo']} ({oracle['informe']})" if oracle else "pendiente"))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="fabrica.py", description="Factory local con gates humanos, OpenSpec, trackertast y Oracle")
    sub = parser.add_subparsers(dest="comando", required=True)
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
    try:
        if args.comando == "nuevo": nuevo(args.titulo, args.capacidad)
        elif args.comando == "aprobar-spec": aprobar_spec(args.id)
        elif args.comando == "importar": importar(args.id)
        elif args.comando == "revision": revisar(args.id, args.informe, args.revisor, args.decision, args.hallazgos_abiertos)
        elif args.comando == "juzgar": juzgar(args.id, args.con)
        elif args.comando == "cerrar": cerrar(args.id)
        elif args.comando == "estado": mostrar(args.id)
        return 0
    except (FactoryError, OSError, json.JSONDecodeError) as e:
        print(f"FACTORY BLOQUEADA: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
