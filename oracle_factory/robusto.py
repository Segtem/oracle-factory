"""Lo que hace que un registro roto o dos cierres a la vez no rompan nada (cambio registros-robustos)."""
from __future__ import annotations

from contextlib import contextmanager
import fcntl
import hashlib
from pathlib import Path
import tempfile


def forma_invalida(estado) -> str | None:
    """Qué le falta a un registro para leerse sin romper nada (Astra H7, Fable H11), o None. Un «eventos» raro se tolera aparte
    (sin_eventos_raros); la capacidad puede faltar: los cambios abandonados antes de que existiera no la tienen."""
    if not isinstance(estado, dict):
        return f"no es un objeto JSON (es {type(estado).__name__})"
    for campo in ("id", "titulo", "fase"):
        if not isinstance(estado.get(campo), str):
            return f"no tiene «{campo}» como texto" if campo in estado else f"no tiene «{campo}»"
    if "capacidad" in estado and not isinstance(estado["capacidad"], str):
        return "tiene una «capacidad» que no es texto"
    return None


@contextmanager
def bloqueo_capacidad(raiz: Path, capacidad: str):
    """Un bloqueo de archivo por capacidad (flock), para que calcular el índice fusionado y escribirlo no se intercalen con otro
    cierre o archivado de la misma capacidad (Astra H1)."""
    # Fuera del proyecto: un intento rechazado no deja nada en él. El nombre sale de la ruta de los registros y de la capacidad.
    clave = hashlib.sha256(f"{raiz.resolve()}\0{capacidad}".encode("utf-8")).hexdigest()[:24]
    with open(Path(tempfile.gettempdir()) / f"oracle-factory-fusion-{clave}.lock", "a", encoding="utf-8") as candado:
        fcntl.flock(candado, fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(candado, fcntl.LOCK_UN)
