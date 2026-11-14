"""Correr un proceso con un plazo y, si vence, detener a todo su grupo: el proceso y los que lanzó (Astra H2).

`subprocess.run(timeout=…)` mata sólo al proceso que lanza: un agente que corre herramientas seguiría trabajando después del tope.
Acá el proceso arranca en su propia sesión y el plazo alcanza a todo su grupo, primero con SIGTERM y, tras una gracia, con SIGKILL."""
from __future__ import annotations

import contextlib
import os
import signal
import subprocess

GRACIA = 5.0  # segundos entre SIGTERM y SIGKILL


def _senal(grupo: int, senal: int) -> None:
    with contextlib.suppress(ProcessLookupError, PermissionError):  # el grupo ya terminó
        os.killpg(grupo, senal)


def correr_en_grupo(argv, cwd, plazo: float, env=None, gracia: float = GRACIA) -> tuple[int, str, str | None]:
    """(código, salida, motivo): la salida junta stdout y stderr; el motivo es «plazo» si venció (código 124), «no_arranca» si el
    proceso no se pudo iniciar (código 127) y None si terminó solo."""
    try:
        p = subprocess.Popen(argv, cwd=cwd, env=env, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                             text=True, start_new_session=True)
    except (OSError, ValueError) as e:
        return 127, str(e), "no_arranca"
    try:
        salida, _ = p.communicate(timeout=plazo)
        return p.returncode, salida or "", None
    except subprocess.TimeoutExpired:
        _senal(p.pid, signal.SIGTERM)
        try:
            salida, _ = p.communicate(timeout=gracia)
        except subprocess.TimeoutExpired:
            _senal(p.pid, signal.SIGKILL)
            salida, _ = p.communicate()
        _senal(p.pid, signal.SIGKILL)  # un hijo que ignoró SIGTERM y no tiene la salida abierta no frena communicate: se lo barre igual
        return 124, salida or "", "plazo"
