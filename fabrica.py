#!/usr/bin/env python3
"""Compatibilidad con el checkout; la distribución expone oracle-factory."""
import sys
from oracle_factory import cli

if __name__ == "__main__":
    raise SystemExit(cli.main())
# Mantener compatibles los consumidores y fixtures que importan fabrica.
sys.modules[__name__] = cli
