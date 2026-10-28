"""Los archivos fuente del paquete tienen que quedar lejos del límite de Oracle Clue (256000 bytes por archivo): si uno lo pasa, la
revisión independiente no puede ni empezar. `problemas` devuelve lo que se pasa de los topes propios, con margen."""
from __future__ import annotations

from pathlib import Path

LIMITE_CLUE = 256_000
TOPE_GENERAL = 200_000  # ningún archivo del paquete
TOPE_CLI = 160_000      # cli.py, el que más crece


def problemas(raiz: Path, general: int = TOPE_GENERAL, cli: int = TOPE_CLI) -> list[str]:
    salida = []
    for archivo in sorted((raiz / "oracle_factory").rglob("*.py")):
        tam = archivo.stat().st_size
        tope = cli if archivo.name == "cli.py" and archivo.parent.name == "oracle_factory" else general
        if tam >= tope:
            salida.append(f"{archivo.relative_to(raiz).as_posix()} mide {tam} bytes y el tope es {tope} (Oracle Clue no acepta archivos de {LIMITE_CLUE}); "
                          "partilo en módulos")
    return salida


if __name__ == "__main__":
    import sys
    errores = problemas(Path(__file__).resolve().parents[1])
    print("\n".join(errores) or "ok")
    sys.exit(1 if errores else 0)
