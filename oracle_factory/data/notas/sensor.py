"""Observa tres casos reales del ejemplo y guarda hechos para Oracle."""
import argparse
import json
from pathlib import Path
from notas import puede_guardar


def observar():
    casos = [("vacío", "", False), ("espacios", "   ", False), ("válido", "Mi nota", True)]
    return {"comprobacion": [
        {"caso": nombre, "codigo": int(puede_guardar(titulo) != esperado)}
        for nombre, titulo, esperado in casos
    ]}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--salida", type=Path, required=True)
    args = parser.parse_args()
    args.salida.parent.mkdir(parents=True, exist_ok=True)
    args.salida.write_text(json.dumps(observar(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Hechos de 3 casos escritos en {args.salida}")
