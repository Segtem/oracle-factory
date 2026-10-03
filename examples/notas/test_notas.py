import unittest
from notas import puede_guardar

class Notas(unittest.TestCase):
    def test_rechaza_titulo_vacio(self):
        self.assertFalse(puede_guardar(""))

    def test_rechaza_solo_espacios(self):
        self.assertFalse(puede_guardar("   "))

    def test_acepta_titulo_con_texto(self):
        self.assertTrue(puede_guardar("Mi nota"))

if __name__ == "__main__":
    unittest.main()
