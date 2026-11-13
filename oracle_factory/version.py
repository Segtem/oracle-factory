"""La versión de Factory, con el commit cuando corre desde un checkout que no es una versión publicada."""
from __future__ import annotations

import argparse
import os
from pathlib import Path
import subprocess

from . import __version__


def version_completa(raiz: Path | None = None) -> str:
    """La versión, y si Factory corre desde un checkout cuyo HEAD no es el commit del tag `vVERSIÓN`, también el commit: el mismo
    número puede tener otro código (H6 de la auditoría de Fable). Instalado desde un paquete, o sin Git a mano, sólo la versión."""
    raiz = raiz or Path(__file__).resolve().parents[1]
    if not (raiz / ".git").exists() or not (raiz / "pyproject.toml").is_file():
        return __version__
    entorno = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}

    def git(*args: str) -> str | None:
        r = subprocess.run(["git", *args], cwd=raiz, capture_output=True, text=True, timeout=10, env=entorno, stdin=subprocess.DEVNULL)
        return r.stdout.strip() if r.returncode == 0 and r.stdout.strip() else None
    try:
        cabeza, tag = git("rev-parse", "HEAD"), git("rev-parse", "-q", "--verify", f"refs/tags/v{__version__}^{{commit}}")
    except (OSError, subprocess.SubprocessError):
        return __version__
    if cabeza is None or cabeza == tag:
        return __version__
    return f"{__version__}+{cabeza[:7]} (checkout, sin publicar)"


class Version(argparse.Action):
    """--version calcula la versión recién cuando se la pide: ningún otro comando corre Git por esto."""

    def __init__(self, option_strings, dest=argparse.SUPPRESS, default=argparse.SUPPRESS, help="show program's version number and exit"):
        super().__init__(option_strings=option_strings, dest=dest, default=default, nargs=0, help=help)

    def __call__(self, parser, namespace, values, option_string=None):
        print(f"oracle-factory {version_completa()}")  # por la salida estándar, como el --version de argparse
        parser.exit()
