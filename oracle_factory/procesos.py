"""Correr un proceso con un plazo y, si vence o se interrumpe la espera, detener a todo su grupo: el proceso y los que lanzó
(Astra H2 y N1).

`subprocess.run(timeout=…)` mata sólo al proceso que lanza: un agente que corre herramientas seguiría trabajando después del tope.
Acá el proceso arranca en su propia sesión y el plazo alcanza a todo su grupo, primero con SIGTERM y, tras una gracia, con SIGKILL.
Como está en su propia sesión, el Ctrl-C de la terminal le llega sólo a quien espera: ante esa interrupción (o cualquier excepción) se
detiene al grupo de la misma forma y después sigue la excepción."""
from __future__ import annotations

import contextlib
import os
import signal
import subprocess

GRACIA = 5.0  # segundos entre SIGTERM y SIGKILL


def _senal(grupo: int, senal: int) -> None:
    with contextlib.suppress(ProcessLookupError, PermissionError):  # el grupo ya terminó
        os.killpg(grupo, senal)


def _detener(p: subprocess.Popen, gracia: float) -> None:
    """SIGTERM al grupo, una gracia y SIGKILL. Otra interrupción durante la gracia no reemplaza a la excepción que llevó acá: se la
    absorbe, el SIGKILL se manda igual y quien llamó relanza la original."""
    try:
        _senal(p.pid, signal.SIGTERM)
        p.wait(timeout=gracia)
    except BaseException:  # vence la gracia, o llega otro Ctrl-C: igual se termina abajo
        pass
    finally:
        _senal(p.pid, signal.SIGKILL)  # también a un hijo que ignoró SIGTERM, y aunque llegue otro Ctrl-C en la gracia
        with contextlib.suppress(BaseException):
            p.wait(timeout=gracia)
            p.stdout.close()


def correr_en_grupo(argv, cwd, plazo: float, env=None, gracia: float = GRACIA) -> tuple[int, str, str | None]:
    """(código, salida, motivo): la salida junta stdout y stderr; el motivo es «plazo» si venció (código 124), «no_arranca» si el
    proceso no se pudo iniciar (código 127) y None si terminó solo. Una interrupción o excepción mientras espera detiene al grupo y sigue."""
    try:
        p = subprocess.Popen(argv, cwd=cwd, env=env, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                             text=True, start_new_session=True)
    except (OSError, ValueError) as e:
        return 127, str(e), "no_arranca"
    try:
        salida, _ = p.communicate(timeout=plazo)
        return p.returncode, salida or "", None
    except subprocess.TimeoutExpired:
        pass
    except BaseException:  # Ctrl-C (KeyboardInterrupt), SystemExit o un error: el grupo no sigue trabajando solo
        _detener(p, gracia)
        raise
    salida = ""
    try:  # venció el plazo: se detiene al grupo y se junta lo que alcanzó a escribir
        _senal(p.pid, signal.SIGTERM)
        try:
            salida, _ = p.communicate(timeout=gracia)
        except subprocess.TimeoutExpired:
            _senal(p.pid, signal.SIGKILL)
            salida, _ = p.communicate()
    finally:
        _senal(p.pid, signal.SIGKILL)  # un hijo que ignoró SIGTERM y no tiene la salida abierta no frena communicate: se lo barre igual
    return 124, salida or "", "plazo"
