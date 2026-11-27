"""Lo que hace que un registro roto o dos cierres a la vez no rompan nada (cambio registros-robustos)."""
from __future__ import annotations

from contextlib import contextmanager
import fcntl
import hashlib
from pathlib import Path
import tempfile

from . import modos


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
    # Los campos que consumen las consultas, sólo su tipo (registros-campos); ausentes valen: los registros viejos no los tienen.
    if "requisitos" in estado and not (isinstance(estado["requisitos"], list) and all(isinstance(r, str) for r in estado["requisitos"])):
        return "tiene unos «requisitos» que no son una lista de textos"
    for campo in ("aceptados", "pendientes_de_union"):
        if campo in estado and not (isinstance(estado[campo], list) and all(isinstance(a, dict) for a in estado[campo])):
            return f"tiene «{campo}» que no es una lista de objetos"
    if not isinstance(estado.get("spec"), (str, type(None))):
        return "tiene una «spec» que no es texto ni nula"
    for campo in ("spec_aprobada", "revision", "oracle", "cierre", "archivo", "responsable", "abandono"):
        if not isinstance(estado.get(campo), (dict, type(None))):
            return f"tiene «{campo}» que no es un objeto ni nulo"
    for campo in ("medidas", "tipos", "propuestas", "medidas_pendientes"):
        if campo in estado and not isinstance(estado[campo], dict):
            return f"tiene «{campo}» que no es un objeto"
    # Y lo que tienen adentro, que las consultas recorren (registros-internos, Astra A4-03): cada decisión, un objeto; cada tipo, uno
    # de los dos.
    for campo in ("medidas", "propuestas", "medidas_pendientes"):
        for clave, valor in (estado.get(campo) or {}).items():
            if not isinstance(valor, dict):
                return f"tiene en «{campo}» un valor para «{clave}» que no es un objeto"
    for clave, valor in (estado.get("tipos") or {}).items():
        if valor not in modos.TIPOS:
            return f"tiene en «tipos» un valor para «{clave}» que no es «funcional» ni «no funcional»"
    if estado.get("spec_aprobada") is not None and not isinstance(estado.get("spec_sha256"), str):
        return "tiene la spec aprobada sin su huella «spec_sha256» como texto"
    return None


def sin_errno(error: OSError, raiz: Path) -> str:
    """Un error de archivo dicho con su ruta (relativa a `raiz` si está adentro) y, si falta, cómo recuperarlo; sin «[Errno N]»."""
    if error.filename is None:
        return str(error)
    if isinstance(error, FileNotFoundError):
        return falta(Path(error.filename), raiz)
    return f"{error.strerror or type(error).__name__}: {_relativa(Path(error.filename), raiz)}"


def falta(ruta: Path, raiz: Path) -> str:
    """Que falta `ruta` (relativa a `raiz` si está adentro) y cómo recuperarla."""
    ruta = _relativa(ruta, raiz)
    return f"falta el archivo {ruta}: recuperalo desde Git (git restore {ruta})"


def _relativa(ruta: Path, raiz: Path) -> Path:
    return ruta.relative_to(raiz) if ruta.is_absolute() and ruta.is_relative_to(raiz) else ruta


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
