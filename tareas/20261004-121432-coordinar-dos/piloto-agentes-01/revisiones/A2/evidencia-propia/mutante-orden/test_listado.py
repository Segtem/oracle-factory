import unittest
from listado import listar_notas

# Dicts a mano según el contrato «nota v1»; no se importa crear_nota.
COMPRAS = {"titulo": "Compras", "cuerpo": "pan"}
IDEAS = {"titulo": "Ideas", "cuerpo": "viaje"}


class Listado(unittest.TestCase):
    def test_dos_notas_en_orden(self):
        self.assertEqual(listar_notas([COMPRAS, IDEAS]), "- Compras\n- Ideas")

    def test_el_cuerpo_no_aparece(self):
        texto = listar_notas([COMPRAS])
        self.assertEqual(texto, "- Compras")
        self.assertNotIn("pan", texto)

    def test_sin_notas(self):
        self.assertEqual(listar_notas([]), "")


if __name__ == "__main__":
    unittest.main()
