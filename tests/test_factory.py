import unittest

from fabrica import pendientes


class GatesHumanos(unittest.TestCase):
    def setUp(self):
        self.estado = {
            "spec_aprobada": {"por": "persona"},
            "requisitos": ["notas.titulo_no_vacio"],
            "revision": {"decision": "aprobar", "hallazgos_abiertos": 0},
            "oracle": {"codigo": 0},
        }

    def test_solo_se_puede_cerrar_con_todos_los_gates(self):
        self.assertEqual(pendientes(self.estado), [])

    def test_sin_aprobacion_humana_no_se_cierra(self):
        self.estado["spec_aprobada"] = None
        self.assertIn("aprobación humana de spec", pendientes(self.estado))

    def test_review_con_hallazgos_abiertos_no_se_cierra(self):
        self.estado["revision"]["hallazgos_abiertos"] = 1
        self.assertIn("revisión humana aprobada y sin hallazgos abiertos", pendientes(self.estado))

    def test_oracle_rojo_no_se_cierra(self):
        self.estado["oracle"]["codigo"] = 1
        self.assertIn("veredicto Oracle exitoso con evidencia", pendientes(self.estado))

    def test_requisitos_sin_importar_no_se_cierra(self):
        self.estado["requisitos"] = []
        self.assertIn("importación OpenSpec → requisitos Oracle", pendientes(self.estado))


if __name__ == "__main__":
    unittest.main()
