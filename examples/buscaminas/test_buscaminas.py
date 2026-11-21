"""Casos que se escriben antes de implementar buscaminas.py."""

import unittest

from buscaminas import MINAS, Partida


class Reglas(unittest.TestCase):
    def test_numero_y_minas_ocultas(self):
        partida = Partida()
        self.assertEqual(partida.numero(2, 2), 2)
        partida.destapar(2, 2)
        self.assertNotIn("*", partida.vista())

    def test_cero_y_bandera(self):
        partida = Partida()
        partida.alternar_bandera(1, 1)
        with self.assertRaises(ValueError):
            partida.destapar(1, 1)
        partida.destapar(3, 1)
        self.assertEqual(partida.destapadas, {(2, 1), (2, 2), (3, 1), (3, 2), (4, 1), (4, 2)})
        self.assertFalse(partida.destapadas & MINAS)

    def test_derrota_y_victoria(self):
        derrota = Partida()
        derrota.destapar(1, 1)
        self.assertEqual(derrota.estado, "perdida")
        victoria = Partida()
        for fila in range(1, 6):
            for columna in range(1, 6):
                if (fila, columna) not in MINAS and victoria.estado == "jugando":
                    victoria.destapar(fila, columna)
        self.assertEqual(victoria.estado, "ganada")

    def test_errores_no_alteran_estado(self):
        partida = Partida()
        with self.assertRaises(ValueError):
            partida.destapar(0, 1)
        self.assertEqual(partida.destapadas, set())
        self.assertEqual(partida.estado, "jugando")


if __name__ == "__main__":
    unittest.main()
