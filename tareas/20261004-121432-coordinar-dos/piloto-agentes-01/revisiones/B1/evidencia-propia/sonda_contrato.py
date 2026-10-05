"""Sonda de revisión B1: crear_nota de A (checkout de revisión) + listar_notas de B (ed3476b), en memoria."""
import sys
sys.path[:0] = [sys.argv[1], sys.argv[2]]
from notas import crear_nota
from listado import listar_notas

def prueba(desc, f):
    try:
        print(f"{desc}: {f()!r}")
    except Exception as e:
        print(f"{desc}: {type(e).__name__}: {e}")

prueba("orden y recorte", lambda: listar_notas([crear_nota("  Ideas  ", "x"), crear_nota("Compras")]))
for nombre, sep in [("U+2028", " "), ("U+2029", " "), ("U+0085", "\x85"), ("VT \\x0b", "\x0b"), ("FF \\x0c", "\x0c")]:
    def f(sep=sep):
        nota = crear_nota(f"Mi{sep}nota")
        texto = listar_notas([nota, crear_nota("Otra")])
        return {"nota": nota, "notas": 2, "lineas_splitlines": len(texto.splitlines())}
    prueba(f"título con {nombre}", f)
prueba("cuerpo None", lambda: crear_nota("Mi nota", None))
prueba("título None", lambda: crear_nota(None))
