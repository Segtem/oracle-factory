import unittest

from total import calcular


class Precio(unittest.TestCase):
    def test_limite_y_redondeo(self):
        self.assertEqual(calcular(1001, 50), 501)
        self.assertEqual(calcular(1001, 0), 1001)

    def test_fuera_de_limite(self):
        for descuento in (-1, 51):
            with self.assertRaises(ValueError):
                calcular(1001, descuento)


if __name__ == "__main__":
    unittest.main()
