"""Comprueba el wheel de la 0.1.0a17 instalado en un entorno nuevo y desde fuera del checkout, y deja un registro.

Uso: python tools/probar_entrega_a17.py [--salida CARPETA]   (por omisión, .factory/local/entrega-a17/)

Construye el wheel y el sdist con `uv build`, instala el wheel en un venv nuevo y corre las comprobaciones con el PYTHONPATH limpio y otra carpeta
de trabajo. `observar` junta lo que ve; `validar` lo juzga (aparte, para poder probarlo con datos armados); `registro` lo guarda con los hashes
y los límites. No publica nada."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parents[1]
VERSION = "0.1.0a17"
SKILL_EN_EL_WHEEL = "oracle_factory/data/skill/SKILL.md"
SUBCOMANDOS_NUEVOS = ("skill", "puerta", "hooks")
LIMITES = (
    "No publica nada: ni PyPI, ni el tag, ni la release de GitHub.",
    "La construcción no es reproducible bit a bit: los hashes dicen qué se probó, no que otra construcción dé los mismos.",
    "Se probó en Linux, con el Python del entorno y las dependencias que resolvió uv en este momento.",
    "No se repiten las comprobaciones con servidores de prueba de las entregas anteriores (elaboración con un modelo simulado, avisos de OSV): esas funciones no cambiaron y las cubre la suite.",
    "No se probó la instalación desde PyPI: eso es posterior a la subida que hace una persona.",
)


def correr(argv, **kwargs):
    return subprocess.run(argv, capture_output=True, text=True, stdin=subprocess.DEVNULL, **kwargs)


def sha256(ruta: Path) -> str:
    return hashlib.sha256(ruta.read_bytes()).hexdigest()


def entorno_limpio() -> dict:
    env = {**os.environ, "UV_LINK_MODE": "copy", "PYTHONDONTWRITEBYTECODE": "1"}
    for variable in ("PYTHONPATH", "VIRTUAL_ENV"):
        env.pop(variable, None)
    return env


def construir(salida: Path, raiz: Path = ROOT, version: str = VERSION) -> dict:
    """Wheel y sdist de `raiz` con `uv build`, en una carpeta que no existía."""
    salida.mkdir(parents=True, exist_ok=False)
    r = correr(["uv", "build", "--wheel", "--sdist", "--out-dir", str(salida)], cwd=raiz, env=entorno_limpio())
    if r.returncode:
        raise RuntimeError(f"uv build falló: {r.stderr.strip()[-400:]}")
    wheels, sdists = list(salida.glob(f"oracle_factory-{version}-*.whl")), list(salida.glob(f"oracle_factory-{version}.tar.gz"))
    if len(wheels) != 1 or len(sdists) != 1:
        raise FileNotFoundError(f"no encuentro exactamente un wheel y un sdist de {version} en {salida}")
    return {"wheel": wheels[0], "sdist": sdists[0], "wheel_sha256": sha256(wheels[0]), "sdist_sha256": sha256(sdists[0])}


def instalar(entorno: Path, wheel: Path) -> tuple[Path, Path]:
    """(oracle-factory, python) de un venv nuevo con el wheel instalado."""
    env = entorno_limpio()
    r = correr(["uv", "venv", str(entorno), "--python", "3.13"], env=env)
    if r.returncode:
        raise RuntimeError(f"uv venv falló: {r.stderr.strip()[-300:]}")
    python = entorno / "bin" / "python"
    r = correr(["uv", "pip", "install", "--python", str(python), str(wheel)], env=env)
    if r.returncode:
        raise RuntimeError(f"no pude instalar el wheel: {r.stderr.strip()[-400:]}")
    return entorno / "bin" / "oracle-factory", python


def observar(wheel: Path, factory: Path, python: Path, trabajo: Path, raiz: Path = ROOT) -> dict:
    """Lo que se ve del wheel instalado, desde `trabajo` (otra carpeta) y sin PYTHONPATH."""
    env = entorno_limpio()
    obs: dict = {}
    with zipfile.ZipFile(wheel) as z:
        obs["archivos_del_wheel"] = sorted(z.namelist())
    r = correr([str(python), "-c", "import oracle_factory, sys; print(oracle_factory.__file__); print(oracle_factory.__version__)"], cwd=trabajo, env=env)
    archivo, version = (r.stdout.splitlines() + ["", ""])[:2]
    obs["importacion"] = {"rc": r.returncode, "archivo": archivo, "version": version,
                          "desde_el_checkout": bool(archivo) and raiz.resolve() in Path(archivo).resolve().parents,
                          "en_el_entorno": bool(archivo) and python.parent.parent.resolve() in Path(archivo).resolve().parents}
    r = correr([str(factory), "--version"], cwd=trabajo, env=env)
    obs["cli_version"] = {"rc": r.returncode, "salida": r.stdout.strip()}
    for nombre in SUBCOMANDOS_NUEVOS:
        r = correr([str(factory), nombre, "--help"], cwd=trabajo, env=env)
        obs[f"ayuda_{nombre}"] = {"rc": r.returncode, "usage": r.stdout.strip().splitlines()[0] if r.stdout.strip() else ""}
    r = correr([str(factory), "skill"], cwd=trabajo, env=env)
    obs["skill"] = {"rc": r.returncode, "empieza_bien": r.stdout.startswith("---\nname: oracle-factory\n"), "largo": len(r.stdout)}
    proyecto = trabajo / "proyecto"
    proyecto.mkdir()
    env_git = {**env, "GIT_CEILING_DIRECTORIES": str(trabajo), "GIT_AUTHOR_NAME": "Prueba", "GIT_AUTHOR_EMAIL": "p@example.invalid",
               "GIT_COMMITTER_NAME": "Prueba", "GIT_COMMITTER_EMAIL": "p@example.invalid"}
    correr(["git", "init", "-q", "-b", "main"], cwd=proyecto, env=env_git)
    r = correr([str(factory), "skill", "--instalar"], cwd=proyecto, env=env_git)
    destino = proyecto / ".claude/skills/oracle-factory/SKILL.md"
    obs["skill_instalar"] = {"rc": r.returncode, "stdout": r.stdout.strip(), "archivo_existe": destino.is_file(),
                             "igual_a_la_del_comando": destino.is_file() and destino.read_text(encoding="utf-8") == correr([str(factory), "skill"], cwd=proyecto, env=env_git).stdout}
    (proyecto / "hola.txt").write_text("nada secreto\n", encoding="utf-8")  # un commit limpio: la puerta tiene algo que mirar y no encuentra nada
    correr(["git", "add", "-A"], cwd=proyecto, env=env_git)
    correr(["git", "commit", "-qm", "base"], cwd=proyecto, env=env_git)
    r = correr([str(factory), "puerta"], cwd=proyecto, env=env_git)
    obs["puerta"] = {"rc": r.returncode, "salida": (r.stdout + r.stderr).strip()[-300:]}
    r = correr([str(factory), "init"], cwd=proyecto, env=env_git)
    r = correr([str(factory), "agentes"], cwd=proyecto, env=env_git)
    guia = proyecto / "AGENTS.md"
    texto = guia.read_text(encoding="utf-8") if guia.is_file() else ""
    obs["agentes"] = {"rc": r.returncode, "nombra_la_skill": "oracle-factory skill --instalar" in texto, "nombra_el_camino_ligero": "camino ligero" in texto}
    return obs


def validar(obs: dict, version: str = VERSION) -> list[str]:
    """Lo que está mal en lo observado; vacío si todo coincide con lo prometido."""
    p = []
    imp = obs.get("importacion", {})
    if imp.get("rc") != 0 or imp.get("version") != version:
        p.append(f"la versión importada es «{imp.get('version')}» y debería ser {version}")
    if imp.get("desde_el_checkout") or not imp.get("archivo") or not imp.get("en_el_entorno"):
        p.append(f"el módulo se importa de «{imp.get('archivo')}», fuera del entorno nuevo")
    if obs.get("cli_version", {}) != {"rc": 0, "salida": f"oracle-factory {version}"}:
        p.append(f"oracle-factory --version dice «{obs.get('cli_version', {}).get('salida')}»")
    if SKILL_EN_EL_WHEEL not in obs.get("archivos_del_wheel", []):
        p.append(f"el wheel no trae {SKILL_EN_EL_WHEEL}")
    for nombre in SUBCOMANDOS_NUEVOS:
        a = obs.get(f"ayuda_{nombre}", {})
        if a.get("rc") != 0 or f"oracle-factory {nombre}" not in a.get("usage", ""):
            p.append(f"la ayuda de {nombre} no responde como se espera")
    s = obs.get("skill", {})
    if s.get("rc") != 0 or not s.get("empieza_bien"):
        p.append("oracle-factory skill no muestra la skill (falta su encabezado)")
    i = obs.get("skill_instalar", {})
    if i.get("rc") != 0 or not i.get("archivo_existe") or not i.get("igual_a_la_del_comando"):
        p.append("skill --instalar no deja la skill instalada y igual a la que muestra el comando")
    if obs.get("puerta", {}).get("rc") != 0:
        p.append("puerta no sale limpia en un repositorio con un commit limpio")
    g = obs.get("agentes", {})
    if g.get("rc") != 0 or not g.get("nombra_la_skill") or not g.get("nombra_el_camino_ligero"):
        p.append("agentes no escribe una guía que nombre la skill y el camino ligero")
    return p


def registro(artefactos: dict, obs: dict, problemas: list[str], version: str = VERSION) -> dict:
    return {"version": version, "publicada": False, "ok": not problemas, "problemas": problemas,
            "hashes": {"wheel": artefactos["wheel_sha256"], "sdist": artefactos["sdist_sha256"]},
            "archivos": {"wheel": Path(artefactos["wheel"]).name, "sdist": Path(artefactos["sdist"]).name},
            "versiones": {"python": sys.version.split()[0], "plataforma": platform.platform(), "uv": correr(["uv", "--version"]).stdout.strip()},
            "observaciones": {k: v for k, v in obs.items() if k != "archivos_del_wheel"},
            "archivos_del_wheel": len(obs.get("archivos_del_wheel", [])), "limites": list(LIMITES)}


def problemas_del_registro(reg: dict) -> list[str]:
    """Lo que le falta a un registro para valer: los dos hashes, las versiones, las observaciones, los límites y no estar marcado publicado."""
    p = []
    for clave in ("wheel", "sdist"):
        if not isinstance(reg.get("hashes", {}).get(clave), str) or len(reg["hashes"][clave]) != 64:
            p.append(f"falta el hash sha256 del {clave}")
    if not reg.get("versiones", {}).get("python") or not reg.get("versiones", {}).get("uv"):
        p.append("faltan las versiones de las herramientas")
    if not reg.get("observaciones"):
        p.append("faltan las observaciones")
    if not reg.get("limites"):
        p.append("faltan los límites")
    if reg.get("publicada") is not False:
        p.append("el registro no puede declarar la entrega como publicada")
    return p


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--salida", type=Path, default=ROOT / ".factory/local/entrega-a17", help="carpeta nueva con dist/ y registro.json")
    args = parser.parse_args(argv)
    salida = args.salida.expanduser().resolve()
    artefactos = construir(salida / "dist")
    with tempfile.TemporaryDirectory(prefix="entrega-a17-") as tmp:
        factory, python = instalar(Path(tmp) / "venv", artefactos["wheel"])
        trabajo = Path(tmp) / "trabajo"
        trabajo.mkdir()
        obs = observar(artefactos["wheel"], factory, python, trabajo)
    problemas = validar(obs)
    reg = registro(artefactos, obs, problemas)
    problemas += problemas_del_registro(reg)
    reg["ok"] = not problemas  # `problemas` es la lista del registro: tras sumar los suyos, el «ok» se vuelve a calcular
    (salida / "registro.json").write_text(json.dumps(reg, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Entrega {VERSION}: {'ok' if not problemas else 'CON PROBLEMAS'}; wheel {reg['hashes']['wheel'][:12]}, sdist {reg['hashes']['sdist'][:12]}; registro en {salida / 'registro.json'}")
    for linea in problemas:
        print(f"  - {linea}")
    return 0 if not problemas else 1


if __name__ == "__main__":
    raise SystemExit(main())
