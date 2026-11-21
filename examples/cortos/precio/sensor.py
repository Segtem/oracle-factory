"""Hecho: el límite de descuento se aplica."""

import argparse
import json
from pathlib import Path

from total import calcular


def observar():
    try:
        correcto = calcular(1001, 50) == 501 and calcular(1001, 0) == 1001
        for descuento in (-1, 51):
            try:
                calcular(1001, descuento)
            except ValueError:
                pass
            else:
                correcto = False
    except Exception:
        correcto = False
    return {"casos": [{"caso": "limite", "codigo": int(not correcto)}],
            "corrida": [{"completa": 1, "casos": 1}]}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--salida", type=Path, required=True)
    destino = parser.parse_args().salida
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(json.dumps(observar(), indent=2) + "\n", encoding="utf-8")
