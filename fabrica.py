#!/usr/bin/env python3
"""Compatibilidad con el checkout; la distribución expone oracle-factory."""
import importlib.util
import os
from pathlib import Path
import sys

if __name__ == "__main__" and any(importlib.util.find_spec(m) is None for m in ("oracle_metalenguaje", "oracle_task")):
    # El python del sistema no tiene las dependencias: usar el entorno del clon, si existe, con los mismos argumentos.
    # Se compara el prefijo y no el ejecutable: el python de un venv suele ser un enlace al mismo binario de base.
    venv = Path(__file__).resolve().parent / ".venv"
    if ((venv / "bin" / "python").exists() and Path(sys.prefix).resolve() != venv.resolve()
            and not os.environ.get("FACTORY_REEJECUTADO")):
        os.environ["FACTORY_REEJECUTADO"] = "1"  # una sola vez: si el .venv tampoco sirve, falla con el mensaje de la CLI
        os.execv(str(venv / "bin" / "python"), [str(venv / "bin" / "python"), __file__, *sys.argv[1:]])

from oracle_factory import cli  # noqa: E402

if __name__ == "__main__":
    raise SystemExit(cli.main())
# Mantener compatibles los consumidores y fixtures que importan fabrica.
sys.modules[__name__] = cli
