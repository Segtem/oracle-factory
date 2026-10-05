"""Observa los tres escenarios de la spec de listado y guarda hechos para Oracle."""
import argparse
import json
from pathlib import Path
from listado import listar_notas

COMPRAS = {"titulo": "Compras", "cuerpo": "pan"}
IDEAS = {"titulo": "Ideas", "cuerpo": "viaje"}


def observar():
    casos = [
        ("dos notas en orden", [COMPRAS, IDEAS], lambda t: t == "- Compras\n- Ideas"),
        ("el cuerpo no aparece", [COMPRAS], lambda t: t == "- Compras" and "pan" not in t),
        ("sin notas", [], lambda t: t == ""),
    ]
    return {"listado_comprobacion": [
        {"caso": nombre, "codigo": int(not cumple(listar_notas(notas)))}
        for nombre, notas, cumple in casos
    ]}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--salida", type=Path, required=True)
    args = parser.parse_args()
    args.salida.parent.mkdir(parents=True, exist_ok=True)
    args.salida.write_text(json.dumps(observar(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Hechos de 3 casos escritos en {args.salida}")
