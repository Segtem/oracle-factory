import unittest

from lector import sumar


class CSV(unittest.TestCase):
    def test_filas_validas(self):
        self.assertEqual(sumar("A,3\nB,4\n"), 7)

    def test_fila_invalida(self):
        for texto in ("A,3\nB,-4\n", "A,3\nB\n"):
            with self.assertRaises(ValueError):
                sumar(texto)


if __name__ == "__main__":
    unittest.main()
