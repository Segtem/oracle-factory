"""Hecho: ninguna fila defectuosa se acepta como total."""

import argparse
import json
from pathlib import Path

from lector import sumar


def observar():
    try:
        correcto = sumar("A,3\nB,4\n") == 7
        for texto in ("A,3\nB,-4\n", "A,3\nB\n"):
            try:
                sumar(texto)
            except ValueError:
                pass
            else:
                correcto = False
    except Exception:
        correcto = False
    return {"casos": [{"caso": "fila", "codigo": int(not correcto)}],
            "corrida": [{"completa": 1, "casos": 1}]}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--salida", type=Path, required=True)
    destino = parser.parse_args().salida
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(json.dumps(observar(), indent=2) + "\n", encoding="utf-8")
