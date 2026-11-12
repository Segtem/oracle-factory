"""Ensaya `oracle-factory migrar --almacen` sobre una copia de un proyecto (etapa 6 de «registros fuera del repo del producto»).

Uso: python tools/ensayar_migracion.py PROYECTO [--informe ARCHIVO.json] [--pruebas]

Clona el HEAD de PROYECTO en una carpeta temporal, crea un almacén temporal y migra ahí con la CLI de este checkout, con
XDG_CONFIG_HOME y XDG_DATA_HOME temporales: no toca PROYECTO ni la configuración del usuario (la identidad de Git sí es la
del usuario: el commit del almacén temporal la usa). El informe dice los cambios que lista Factory antes y después (sin la
línea «Acuerdos:», que nombra dónde están los registros) y si coinciden; con --pruebas corre las pruebas de la copia
(`python -m unittest discover -s tests`) antes y después de migrar y lista las que fallan sólo después. Sale con 1 si la
migración falla o los cambios no coinciden. La carpeta temporal se borra al terminar.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import time

CLI = [sys.executable, "-c", "import sys; from oracle_factory.cli import main; sys.exit(main())"]
FALLA = re.compile(r"^(?:FAIL|ERROR): (\S+) \((\S+)\)", re.M)


def correr(comando: list[str], carpeta: Path, entorno: dict) -> subprocess.CompletedProcess:
    return subprocess.run(comando, cwd=carpeta, env=entorno, capture_output=True, text=True, stdin=subprocess.DEVNULL)


def listado(copia: Path, entorno: dict) -> str:
    r = correr([*CLI, "listar"], copia, entorno)
    if r.returncode:
        raise SystemExit(f"listar falló en la copia: {r.stderr.strip()}")
    return "\n".join(l for l in r.stdout.splitlines() if not l.startswith("Acuerdos:"))


def pruebas(copia: Path, entorno: dict) -> tuple[int, set[str], str]:
    r = correr([sys.executable, "-m", "unittest", "discover", "-s", "tests"], copia, entorno)
    resumen = [l for l in r.stderr.splitlines() if l.startswith(("Ran ", "OK", "FAILED"))]
    return r.returncode, {f"{clase}.{nombre}" for nombre, clase in FALLA.findall(r.stderr)}, " · ".join(resumen)


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("proyecto", type=Path)
    p.add_argument("--informe", type=Path, help="dónde escribir el informe JSON (si no, se imprime)")
    p.add_argument("--pruebas", action="store_true", help="correr las pruebas de la copia antes y después de migrar")
    args = p.parse_args(argv)
    proyecto = args.proyecto.resolve()
    inicio = time.monotonic()
    with tempfile.TemporaryDirectory(prefix="ensayo-migracion-") as tmp:
        base = Path(tmp)
        copia, almacen = base / "copia", base / "almacen"
        entorno = {**os.environ, "XDG_CONFIG_HOME": str(base / "config"), "XDG_DATA_HOME": str(base / "datos")}
        entorno.pop("FACTORY_AGENTE", None)
        for k in ("GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE", "GIT_COMMON_DIR"):
            entorno.pop(k, None)
        for comando, carpeta in ((["git", "clone", "-q", "--no-hardlinks", str(proyecto), str(copia)], base),
                                 (["git", "init", "-q", str(almacen)], base)):
            r = correr(comando, carpeta, entorno)
            if r.returncode:
                raise SystemExit(f"{' '.join(comando[:2])} falló: {r.stderr.strip()}")
        informe: dict = {"proyecto": str(proyecto), "commit": correr(["git", "rev-parse", "HEAD"], copia, entorno).stdout.strip()}
        antes = listado(copia, entorno)
        if args.pruebas:
            codigo_antes, fallas_antes, resumen_antes = pruebas(copia, entorno)
        migrado = correr([*CLI, "migrar", "--almacen", str(almacen)], copia, entorno)
        informe["migrar"] = {"codigo": migrado.returncode, "salida": migrado.stdout.strip(), "error": migrado.stderr.strip()}
        if migrado.returncode:
            informe["coinciden"] = False
        else:
            despues = listado(copia, entorno)
            informe.update(antes=antes, despues=despues, coinciden=antes == despues,
                           baja_sin_commitear=len(correr(["git", "diff", "--cached", "--name-only"], copia, entorno).stdout.splitlines()))
            if args.pruebas:
                codigo, fallas, resumen = pruebas(copia, entorno)
                informe["pruebas"] = {"codigo": codigo, "resumen": resumen, "fallan": sorted(fallas - fallas_antes),
                                      "antes": {"codigo": codigo_antes, "resumen": resumen_antes, "fallan": sorted(fallas_antes)}}
        informe["segundos"] = round(time.monotonic() - inicio, 1)
    texto = json.dumps(informe, indent=2, ensure_ascii=False) + "\n"
    if args.informe:
        args.informe.write_text(texto, encoding="utf-8")
    else:
        sys.stdout.write(texto)
    return 0 if informe["coinciden"] else 1


if __name__ == "__main__":
    sys.exit(main())
