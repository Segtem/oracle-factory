#!/usr/bin/env python3
"""Compatibilidad con el checkout; la distribución expone oracle-factory."""
import importlib.util
import os
from pathlib import Path
import sys

if __name__ == "__main__" and importlib.util.find_spec("oracle_metalenguaje") is None:
    # El python del sistema no tiene las dependencias: usar el entorno del clon, si existe, con los mismos argumentos.
    venv = Path(__file__).resolve().parent / ".venv" / "bin" / "python"
    if venv.is_file() and Path(sys.executable).resolve() != venv.resolve():
        os.execv(str(venv), [str(venv), __file__, *sys.argv[1:]])

from oracle_factory import cli  # noqa: E402

if __name__ == "__main__":
    raise SystemExit(cli.main())
# Mantener compatibles los consumidores y fixtures que importan fabrica.
sys.modules[__name__] = cli
