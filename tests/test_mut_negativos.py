"""Un entero negativo se muta y se describe como se escribe: escenarios mn1."""
import ast
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from tools import mutar_cambio  # noqa: E402


def mutantes(texto: str) -> dict[str, str]:
    """{descripción: texto mutado} de los mutantes de la única línea con una comparación."""
    arbol = ast.parse(texto)
    linea = next(n.lineno for n in ast.walk(arbol) if isinstance(n, ast.Compare))
    return {d: mutar_cambio._aplicar(arbol, p, v) for p, v, d in mutar_cambio._mutaciones(arbol, {linea})}


class Negativos(unittest.TestCase):
    # --- mn1: un entero negativo se muta y se describe como se escribe ------------------------------------------------------
    def test_mn1_una_comparacion_con_un_negativo(self):
        m = mutantes('def f(x):\n    return x == -5\n')
        self.assertIn('-5 → -4', m)
        self.assertIn('x == -4', m['-5 → -4'])
        self.assertNotIn('5 → 6', m)
        self.assertNotIn('x == -6', ''.join(m.values()))
        self.assertIn('== → !=', m)  # la comparación sigue mutándose

    def test_mn1_un_positivo_sigue_igual(self):
        m = mutantes('def f(x):\n    return x == 5\n')
        self.assertIn('5 → 6', m)
        self.assertIn('x == 6', m['5 → 6'])


if __name__ == '__main__':
    unittest.main()
