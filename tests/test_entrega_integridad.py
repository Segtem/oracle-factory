"""Regresiones contra evidencia incompleta o ajena al candidato de entrega."""
from collections import Counter
from copy import deepcopy
from types import SimpleNamespace
import unittest

from tools import verify_entrega_a14 as sensor


class IntegridadEntrega(unittest.TestCase):
    def test_mutaciones_exigen_identidades_y_fuentes_actuales(self):
        from tools.mutar_entrega_a14 import MUTACIONES
        fuentes = {'head': 'abc', 'sha256': {'a': '1'}}
        filas = [{'id': m[0], 'detectada': True, 'codigo': 1} for m in MUTACIONES]
        datos = {'fuentes': fuentes, 'mutaciones': filas, 'todas_detectadas': True}
        self.assertTrue(sensor.mutaciones_validas(datos, fuentes))
        for cambio in ('ausente', 'duplicada', 'vieja', 'viva', 'salida'):
            roto = deepcopy(datos)
            if cambio == 'ausente': roto['mutaciones'].pop()
            if cambio == 'duplicada': roto['mutaciones'][0] = roto['mutaciones'][1]
            if cambio == 'vieja': roto['fuentes']['sha256']['a'] = 'viejo'
            if cambio == 'viva': roto['mutaciones'][0]['detectada'] = False
            if cambio == 'salida': roto['mutaciones'][0]['codigo'] = 0
            with self.subTest(cambio=cambio):
                self.assertFalse(sensor.mutaciones_validas(roto, fuentes))
        self.assertFalse(sensor.mutaciones_validas(None, fuentes))

    def test_suite_exige_todos_los_casos_sin_omisiones_ni_fallas(self):
        esperado = Counter({'a': 1, 'b': 1})
        resultado = SimpleNamespace(cantidad=esperado.copy(), observados={'a': 0, 'b': 0},
                                    skipped=[], expectedFailures=[], unexpectedSuccesses=[],
                                    wasSuccessful=lambda: True)
        self.assertTrue(sensor.suite_completa(resultado, esperado))
        resultado.cantidad = Counter({'a': 1})
        self.assertFalse(sensor.suite_completa(resultado, esperado))
        resultado.cantidad = Counter({'a': 2, 'b': 1})
        self.assertFalse(sensor.suite_completa(resultado, esperado))
        resultado.cantidad = esperado.copy()
        resultado.observados['b'] = 1
        self.assertFalse(sensor.suite_completa(resultado, esperado))
        resultado.observados['b'] = 0
        resultado.skipped = [('b', 'omitido')]
        self.assertFalse(sensor.suite_completa(resultado, esperado))

    def test_resultado_exige_arneses_y_fuentes_estables(self):
        fuentes = {'head': 'abc', 'sha256': {'a': '1'}}
        arneses = {'verify_installed': {'returncode': 0}, 'verify_guide': {'returncode': 0}}
        self.assertTrue(sensor.corrida_valida(True, True, fuentes, fuentes, arneses))
        self.assertFalse(sensor.corrida_valida(True, True, fuentes, {'head': 'otro'}, arneses))
        self.assertFalse(sensor.corrida_valida(True, False, fuentes, fuentes, arneses))
        self.assertFalse(sensor.corrida_valida(False, True, fuentes, fuentes, arneses))
        arneses['verify_guide']['returncode'] = 1
        self.assertFalse(sensor.corrida_valida(True, True, fuentes, fuentes, arneses))
        self.assertFalse(sensor.corrida_valida(True, True, fuentes, fuentes, {}))
