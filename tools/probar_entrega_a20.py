"""Construye e instala la candidata 0.1.0a20; conserva los hashes y comprueba que el wheel trae firmas."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools import probar_entrega_a19 as anterior  # noqa: E402

VERSION = "0.1.0a20"
FIRMAS_EN_EL_WHEEL = "oracle_factory/firmas.py"
OBLIGATORIOS = (anterior.SKILL_EN_EL_WHEEL, FIRMAS_EN_EL_WHEEL)
sha256 = anterior.sha256
problemas_del_registro = anterior.problemas_del_registro


def observar(wheel: Path, factory: Path, python: Path, trabajo: Path) -> dict:
    obs = anterior.observar(wheel, factory, python, trabajo)
    r = anterior.correr([str(python), "-c", "import oracle_factory.firmas as f; print(f.__file__)"],
                       cwd=trabajo, env=anterior.entorno_limpio())
    archivo = r.stdout.strip()
    obs["firma_importada"] = {"rc": r.returncode, "archivo": archivo,
                               "en_el_entorno": bool(archivo) and python.parent.parent.resolve() in Path(archivo).resolve().parents}
    return obs


def validar(obs: dict) -> list[str]:
    problemas = anterior.validar(obs, VERSION)
    for archivo in OBLIGATORIOS:
        if archivo not in obs.get("archivos_del_wheel", []):
            problemas.append(f"el wheel no trae {archivo}")
    firma = obs.get("firma_importada") or {}
    if firma.get("rc") != 0 or not firma.get("en_el_entorno"):
        problemas.append("oracle_factory.firmas no se importa desde el entorno nuevo")
    return list(dict.fromkeys(problemas))


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--salida", type=Path, default=ROOT / ".factory/local/entrega-a20")
    args = parser.parse_args(argv)
    salida = args.salida.expanduser().resolve()
    artefactos = anterior.construir(salida / "dist", raiz=ROOT, version=VERSION)
    with tempfile.TemporaryDirectory(prefix="entrega-a20-") as tmp:
        factory, python = anterior.instalar(Path(tmp) / "venv", artefactos["wheel"])
        trabajo = Path(tmp) / "trabajo"
        trabajo.mkdir()
        obs = observar(artefactos["wheel"], factory, python, trabajo)
    problemas = validar(obs)
    registro = anterior.registro(artefactos, obs, problemas, version=VERSION)
    registro["archivos_obligatorios"] = [p for p in OBLIGATORIOS if p in obs["archivos_del_wheel"]]
    problemas += problemas_del_registro(registro)
    registro["problemas"] = problemas
    registro["ok"] = not problemas
    (salida / "registro.json").write_text(json.dumps(registro, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Entrega {VERSION}: {'ok' if not problemas else 'CON PROBLEMAS'}; wheel {registro['hashes']['wheel'][:12]}, "
          f"sdist {registro['hashes']['sdist'][:12]}; registro en {salida / 'registro.json'}")
    for problema in problemas:
        print(f"  - {problema}")
    return 0 if not problemas else 1


if __name__ == "__main__":
    raise SystemExit(main())
