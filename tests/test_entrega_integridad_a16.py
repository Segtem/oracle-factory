"""Regresiones contra evidencia incompleta o ajena al candidato de entrega."""
from collections import Counter
from copy import deepcopy
import json
from pathlib import Path
import subprocess
from types import SimpleNamespace
import tempfile
import unittest

from tools import verify_entrega_a16 as sensor


class IntegridadEntrega(unittest.TestCase):
    def test_mutaciones_exigen_identidades_y_fuentes_actuales(self):
        from tools.mutar_entrega_a16 import MUTACIONES, CASOS
        fuentes = {'head': 'abc', 'sha256': {'a': '1'}}
        filas = [{'id': m[0], 'detectada': True, 'codigo': 1} for m in MUTACIONES]
        datos = {'fuentes': fuentes, 'mutaciones': filas, 'todas_detectadas': True,
                 'linea_base': [{'caso': n, 'codigo': 0} for n in sorted({CASOS[m[4]] for m in MUTACIONES})]}
        self.assertTrue(sensor.mutaciones_validas(datos, fuentes))
        for cambio in ('ausente', 'duplicada', 'vieja', 'viva', 'salida', 'base_ausente', 'base_fallida', 'base_duplicada'):
            roto = deepcopy(datos)
            if cambio == 'ausente': roto['mutaciones'].pop()
            if cambio == 'duplicada': roto['mutaciones'][0] = roto['mutaciones'][1]
            if cambio == 'vieja': roto['fuentes']['sha256']['a'] = 'viejo'
            if cambio == 'viva': roto['mutaciones'][0]['detectada'] = False
            if cambio == 'salida': roto['mutaciones'][0]['codigo'] = 0
            if cambio == 'base_ausente': roto.pop('linea_base')
            if cambio == 'base_fallida': roto['linea_base'][0]['codigo'] = 1
            if cambio == 'base_duplicada': roto['linea_base'][0] = roto['linea_base'][1]
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

    def test_el_arbol_debe_coincidir_con_head_para_atar_la_evidencia_al_commit(self):
        with tempfile.TemporaryDirectory() as tmp:
            raiz = Path(tmp)
            env = {'GIT_CONFIG_GLOBAL': '/dev/null', 'GIT_CONFIG_NOSYSTEM': '1', 'GIT_AUTHOR_NAME': 'x', 'GIT_AUTHOR_EMAIL': 'x@x',
                   'GIT_COMMITTER_NAME': 'x', 'GIT_COMMITTER_EMAIL': 'x@x', 'PATH': __import__('os').environ['PATH']}
            git = lambda *a: subprocess.run(['git', *a], cwd=raiz, env=env, check=True, capture_output=True)
            git('init', '-q')
            (raiz / 'a.py').write_text('x = 1\n')
            (raiz / '.factory').mkdir()
            git('add', '-A')
            git('commit', '-q', '-m', 'base')
            self.assertTrue(sensor.arbol_limpio(raiz))
            (raiz / '.factory' / 'registro.json').write_text('{}')  # los registros generados no cuentan
            (raiz / 'kb').mkdir()
            (raiz / 'kb' / 'nota.md').write_text('n')
            self.assertTrue(sensor.arbol_limpio(raiz))
            (raiz / 'a.py').write_text('x = 2\n')
            self.assertFalse(sensor.arbol_limpio(raiz))  # un archivo cambiado sin commitear
            git('checkout', '--', 'a.py')
            (raiz / 'nuevo.py').write_text('y = 1\n')
            self.assertFalse(sensor.arbol_limpio(raiz))  # un archivo nuevo sin commitear

    def test_la_evidencia_de_instalacion_no_lleva_rutas_de_esta_maquina(self):
        raiz, casa = str(sensor.ROOT), str(Path.home())
        datos = {'cwd': raiz, 'wheel': f'{raiz}/.factory/local/dist/x.whl', 'otro': f'{casa}/Dev/algo', 'tmp': '/tmp/factory-entrega-abc/venv/bin/python',
                 'lista': [f'cd {raiz}', '/var/tmp/xyz/archivo'], 'sin_rutas': 'texto', 'n': 3}
        limpio = json.dumps(sensor.sin_rutas_locales(datos), ensure_ascii=False)
        for ruta in (raiz, casa, '/tmp/factory-entrega', '/var/tmp/xyz'):
            self.assertNotIn(ruta, limpio)
        self.assertEqual(sensor.sin_rutas_locales({'sin_rutas': 'texto', 'n': 3}), {'sin_rutas': 'texto', 'n': 3})
        self.assertIn('<repo>', limpio)

    def test_la_trazabilidad_exige_que_cada_caso_haya_salido_bien(self):
        bueno = {'requisitos': {'r': ['c1', 'c2']}, 'casos': {'c1': {'resultado': 'ok'}, 'c2': {'resultado': 'ok'}}}
        self.assertTrue(sensor.trazabilidad_valida(bueno))
        for nombre, roto in {
            'una falla': {**bueno, 'casos': {**bueno['casos'], 'c2': {'resultado': 'falla'}}},
            'una omisión': {**bueno, 'casos': {**bueno['casos'], 'c1': {'resultado': 'omitido'}}},
            'un caso ausente': {**bueno, 'casos': {'c1': {'resultado': 'ok'}}},
            'sin requisitos': {'requisitos': {}, 'casos': {}},
            'forma rara': {'requisitos': [], 'casos': {}},
        }.items():
            with self.subTest(nombre):
                self.assertFalse(sensor.trazabilidad_valida(roto))
        self.assertFalse(sensor.trazabilidad_valida(None))

