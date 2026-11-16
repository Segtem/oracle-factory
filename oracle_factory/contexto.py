"""El contexto explícito de un comando: el producto, los registros, el agente y si hay almacén aparte.

Hoy lo arman las variables globales de `cli` (`ROOT`, `PRODUCTO`, `AGENTE`); `actual(cli)` lo lee de ahí, así coincide siempre con lo
que usa la CLI. El código nuevo lo pide acá en vez de leer las globales, y los usos viejos se mudan de a poco (cambio 11 del plan de las
auditorías, Fable H13).

`producto_fijo` es un ámbito explícito: mientras dura, la huella del producto que se le pasó vale para todos los que la pidan (lo usa
`verificar`, que recorre todos los cambios sobre el mismo producto). Fuera de él, la huella se calcula cada vez."""
from __future__ import annotations

from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass
from pathlib import Path

_HUELLA: ContextVar[dict | None] = ContextVar("huella_del_producto", default=None)


@dataclass(frozen=True)
class Contexto:
    producto: Path
    registros: Path
    agente: str | None

    @property
    def con_almacen(self) -> bool:
        return self.producto != self.registros


def actual(cli) -> Contexto:
    """El contexto de lo que corre ahora, armado desde el estado de la CLI."""
    return Contexto(producto=cli.PRODUCTO or cli.ROOT, registros=cli.ROOT, agente=cli.AGENTE)


@contextmanager
def producto_fijo(huella: dict | None):
    """Mientras dura, `huella_fija()` devuelve esta huella (None: no fija nada y cada uno la calcula)."""
    marca = _HUELLA.set(huella)
    try:
        yield
    finally:
        _HUELLA.reset(marca)


def huella_fija() -> dict | None:
    return _HUELLA.get()
