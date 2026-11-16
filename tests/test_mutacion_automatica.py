"""La evidencia mide con mutación automática si las pruebas de un cambio vigilan sus líneas: escenarios mu1 (la mutación) y mu2 (la
medida). Con repositorios Git temporales, commits con el trailer «Cambio:» y Oracle de verdad."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

SOURCE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SOURCE))
from tools import mutar_cambio, verificar_cambio  # noqa: E402

CAMBIO = '20990101-000000-abc-demo'
ENTORNO = {**os.environ, 'GIT_AUTHOR_NAME': 'Persona fixture', 'GIT_AUTHOR_EMAIL': 'p@example.invalid',
           'GIT_COMMITTER_NAME': 'Persona fixture', 'GIT_COMMITTER_EMAIL': 'p@example.invalid',
           'GIT_CEILING_DIRECTORIES': str(Path(tempfile.gettempdir()).resolve())}
VIGILA = '''import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from paquete import modulo


class Demo(unittest.TestCase):
    def test_es_mayor(self):
        self.assertTrue(modulo.es_mayor(11))
        self.assertFalse(modulo.es_mayor(10))
'''


class Repo(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.raiz = Path(self.tmp.name) / 'producto'
        self.raiz.mkdir()
        self.git('init', '-q', '-b', 'main')
        self.escribir('paquete/__init__.py', '')
        self.escribir('paquete/viejo.py', 'def antes(a):\n    return a == 1\n')  # de un commit sin el trailer: no se muta
        self.escribir('tests/__init__.py', '')
        self.git('add', '-A')
        self.git('commit', '-qm', 'base')

    def git(self, *args):
        return subprocess.run(['git', *args], cwd=self.raiz, env=ENTORNO, capture_output=True, text=True, check=True).stdout

    def escribir(self, ruta, texto):
        (self.raiz / ruta).parent.mkdir(parents=True, exist_ok=True)
        (self.raiz / ruta).write_text(texto, encoding='utf-8')

    def commit_del_cambio(self, archivos: dict):
        for ruta, texto in archivos.items():
            self.escribir(ruta, texto)
        self.git('add', '-A')
        self.git('commit', '-qm', f'cambio\n\nCambio: {CAMBIO}')

    def mutar(self, modulo='test_demo', tope=40):
        return mutar_cambio.mutar(self.raiz, CAMBIO, modulo, tope=tope)


class Mutacion(Repo):
    # --- mu1: la evidencia muta las líneas del cambio ---------------------------------------------------------------------
    def test_mu1_un_mutante_vigilado_y_uno_no(self):
        self.commit_del_cambio({'paquete/modulo.py': 'def es_mayor(a):\n    return a > 10\n\n\ndef otra(a):\n    return a != 3\n',
                                'paquete/viejo.py': 'def antes(a):\n    return a == 1\n\n\ndef nueva(a):\n    return a is None\n',
                                'tests/test_demo.py': VIGILA})
        r = self.mutar()
        por = {(m['archivo'], m['linea'], m['operador']): m['muerto'] for m in r['mutantes']}
        self.assertEqual(por[('paquete/modulo.py', 2, '> → <=')], 1)  # lo vigila test_es_mayor
        self.assertEqual(por[('paquete/modulo.py', 6, '!= → ==')], 0)  # nadie prueba otra()
        self.assertEqual([k for k in por if k[0] == 'paquete/viejo.py'], [('paquete/viejo.py', 6, 'is → is not')])  # la línea 2 es de antes
        self.assertFalse([k for k in por if k[0].startswith('tests/')])
        resumen = r['resumen']
        self.assertEqual((resumen['generados'], resumen['muertos']), (len(por), sum(por.values())))
        self.assertEqual(resumen['porcentaje'], resumen['muertos'] * 100 // resumen['generados'])
        self.assertEqual(resumen['tope_alcanzado'], 0)

    def test_mu1_el_producto_no_se_toca(self):
        registro = Path(self.tmp.name) / 'donde.txt'  # el módulo de pruebas anota desde dónde corre: nunca desde el producto
        anota = VIGILA + f"\n\nopen({str(registro)!r}, 'a').write(str(Path(__file__).resolve().parents[1]) + '\\n')\n"
        self.commit_del_cambio({'paquete/modulo.py': 'def es_mayor(a):\n    return a > 10\n', 'tests/test_demo.py': anota})
        antes = {p: p.read_bytes() for p in self.raiz.rglob('*.py')}
        self.mutar()
        corridas = registro.read_text().split()
        self.assertTrue(corridas)
        self.assertFalse([c for c in corridas if Path(c).is_relative_to(self.raiz.resolve())], corridas)
        self.assertEqual({p: p.read_bytes() for p in self.raiz.rglob('*.py')}, antes)
        self.assertEqual(self.git('status', '--porcelain', '--untracked-files=all'), '')

    def test_mu1_mas_de_40_mutantes(self):
        cuerpo = ''.join(f'def f{i}(a):\n    return a == {i}\n\n\n' for i in range(50))  # 100 posibles: el == y el entero de cada una
        self.commit_del_cambio({'paquete/modulo.py': cuerpo,
                                'tests/test_demo.py': 'import unittest\n\n\nclass Demo(unittest.TestCase):\n    def test_nada(self):\n        pass\n'})
        uno, dos = self.mutar(), self.mutar()
        clave = lambda r: [(m['archivo'], m['linea'], m['operador']) for m in r['mutantes']]  # noqa: E731
        self.assertEqual(len(uno['mutantes']), 40)
        self.assertEqual(clave(uno), clave(dos))
        self.assertEqual(uno['resumen']['tope_alcanzado'], 1)
        self.assertGreater(max(m['linea'] for m in uno['mutantes']), 150)  # repartidos, no los 40 primeros
        self.assertEqual({m['operador'].split(' → ')[0] == '==' for m in uno['mutantes']}, {True, False})  # de los dos tipos

    def test_mu1_sin_lineas_de_producto(self):
        self.commit_del_cambio({'tests/test_demo.py': VIGILA.replace('from paquete import modulo', 'from paquete import viejo as modulo')
                                .replace('modulo.es_mayor(11)', 'True').replace('modulo.es_mayor(10)', 'False')})
        r = self.mutar()
        self.assertEqual(r['mutantes'], [])
        self.assertEqual(r['resumen'], {'generados': 0, 'muertos': 0, 'porcentaje': 100, 'tope_alcanzado': 0})

    def test_mu1_pruebas_que_ya_fallan_sin_mutar(self):
        self.commit_del_cambio({'paquete/modulo.py': 'def es_mayor(a):\n    return a > 10\n',
                                'tests/test_demo.py': VIGILA.replace('self.assertFalse(modulo.es_mayor(10))', 'self.fail("adrede")')})
        r = self.mutar()
        self.assertEqual(r['resumen']['porcentaje'], 0)
        self.assertEqual(r['resumen']['muertos'], 0)  # que fallen ya no prueba que maten a nadie

    def test_mu1_verificar_cambio_deja_los_hechos(self):
        # Al producir la evidencia, los hechos traen las dos relaciones de la mutación.
        hechos = {}
        verificar_cambio.sumar_mutacion(hechos, 'demo', self.mutar())
        self.assertEqual(set(hechos), {'demo_mutante', 'demo_mutacion'})
        self.assertEqual(len(hechos['demo_mutacion']), 1)


@unittest.skipUnless(shutil.which('oracle'), 'hace falta Oracle')
class Medida(unittest.TestCase):
    # --- mu2: la medida de mutación pide el 80 por ciento ------------------------------------------------------------------
    def juzgar(self, generados, muertos):
        with tempfile.TemporaryDirectory() as tmp:
            proyecto = Path(tmp)
            subprocess.run(['oracle', 'init', str(proyecto)], capture_output=True, check=True, stdin=subprocess.DEVNULL)
            (proyecto / 'catalogos').mkdir(exist_ok=True)
            (proyecto / 'catalogos/factory_demo.mutacion.oracle').write_text(verificar_cambio.catalogo_de_mutacion('demo', 'prueba'))
            hechos = proyecto / 'hechos.json'
            porcentaje = muertos * 100 // generados
            hechos.write_text(json.dumps({'demo_mutacion': [{'generados': generados, 'muertos': muertos, 'porcentaje': porcentaje,
                                                             'tope_alcanzado': 0}]}))
            return subprocess.run(['oracle', 'juzgar', '--con', str(hechos), '--medida', 'factory_demo.mutacion', '--parcial',
                                   '--proyecto', str(proyecto)], capture_output=True, text=True, stdin=subprocess.DEVNULL)

    def test_mu2_8_de_10(self):
        r = self.juzgar(10, 8)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn('✓ factory_demo.mutacion', r.stdout)

    def test_mu2_7_de_10(self):
        r = self.juzgar(10, 7)
        self.assertNotEqual(r.returncode, 0, r.stdout)
        self.assertIn('✗ factory_demo.mutacion', r.stdout)


if __name__ == '__main__':
    unittest.main()
