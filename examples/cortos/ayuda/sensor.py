"""Hecho: la página de uso enlaza su primer paso existente."""

import argparse
import json
from pathlib import Path
import re


def observar(raiz=Path(".")):
    try:
        texto = (raiz / "uso.md").read_text(encoding="utf-8")
        enlace = re.search(r"\[primer paso\]\(([^)]+)\)", texto, re.I)
        correcto = bool(enlace and enlace.group(1) == "pasos.md" and (raiz / "pasos.md").is_file())
    except OSError:
        correcto = False
    return {"casos": [{"caso": "enlace", "codigo": int(not correcto)}],
            "corrida": [{"completa": 1, "casos": 1}]}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--salida", type=Path, required=True)
    destino = parser.parse_args().salida
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(json.dumps(observar(), indent=2) + "\n", encoding="utf-8")
