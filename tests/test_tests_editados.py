"""Avisar de los tests que ya existían y el cambio modificó o borró: escenarios te1–te3, con repositorios Git temporales."""
import contextlib
import io
import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import test_archivo as _archivo  # noqa: E402
import test_revisores as _revisores  # noqa: E402
from oracle_factory import alarmas, estructura  # noqa: E402

f = _archivo.f
SPEC = ('# Capability: demo\n\n## ADDED Requirements\n\n### Requirement: hacer algo\nTipo: funcional\nEl sistema DEBE hacer algo.\n\n'
        '#### Scenario: uno\n- DADO a\n- CUANDO b\n- ENTONCES c\n')
TEST_A = '''import unittest


class A(unittest.TestCase):
    def test_uno(self):
        self.assertEqual(1, 1)
        self.assertTrue(True)

    def test_dos(self):
        assert 2 == 2
'''
TEST_B = '''def test_b():
    assert True
'''


class Base(unittest.TestCase):
    setUp, escribe, git, salida, archivos, cambio_importado = (
        _archivo.Archivo.setUp, _archivo.Archivo.escribe, _archivo.Archivo.git, _archivo.Archivo.salida, _archivo.Archivo.archivos,
        _archivo.Archivo.cambio_importado)

    def preparar(self):
        """Un cambio, un commit base en main con tests/, y una rama de trabajo."""
        self.ident = self.cambio_importado('Demo', 'demo', SPEC)
        (self.root / 'tests').mkdir()
        (self.root / 'tests/test_a.py').write_text(TEST_A)
        (self.root / 'tests/test_b.py').write_text(TEST_B)
        (self.root / 'docs').mkdir()
        (self.root / 'docs/tests.md').write_text('uno\ndos\n')
        (self.root / 'src').mkdir()
        (self.root / 'src/modulo.py').write_text('def f():\n    return 1\n\n\ndef g():\n    return 2\n')
        self.git('add', '.')
        self.git('commit', '-qm', 'base')
        self.base = self.git('rev-parse', 'HEAD')
        self.git('checkout', '-qb', 'tarea')

    def candidato(self, editar):
        """Aplica `editar`, hace el commit de producto y deja la carpeta de evidencia que lo vuelve el candidato vigente."""
        editar()
        self.git('add', '-A')
        self.git('commit', '-qm', 'producto')
        sha = self.git('rev-parse', 'HEAD')[:7]
        evidencia = estructura.ruta_canonica(self.root, self.ident, 'evidencia', sha)
        evidencia.mkdir(parents=True)
        (evidencia / 'hechos.json').write_text('{}')
        self.git('add', '-A')
        self.git('commit', '-qm', 'evidencia')
        return sha

    def estado(self):
        self.salida()
        f.mostrar(self.ident)
        return self.salida(), f.datos_estado(self.ident)


class EstadoAvisa(Base):
    # --- te1: el estado avisa de los tests existentes que el cambio modificó o borró ---------------------------------------
    def test_te1_un_archivo_borrado_y_un_test_con_su_asercion_quitados(self):
        self.preparar()

        def editar():
            (self.root / 'tests/test_b.py').unlink()
            (self.root / 'tests/test_a.py').write_text('''import unittest


class A(unittest.TestCase):
    def test_uno(self):
        self.assertEqual(1, 1)
''')
        self.candidato(editar)
        antes = f.datos_estado(self.ident)
        texto, datos = self.estado()
        editados = {e['archivo']: e for e in datos['tests_editados']}
        self.assertEqual(set(editados), {'tests/test_a.py', 'tests/test_b.py'})
        self.assertEqual(editados['tests/test_b.py']['estado'], 'borrado')
        self.assertEqual(editados['tests/test_b.py']['tests_quitados'], ['test_b'])
        self.assertEqual(editados['tests/test_a.py']['estado'], 'modificado')
        self.assertEqual(editados['tests/test_a.py']['tests_quitados'], ['test_dos'])
        self.assertEqual(editados['tests/test_a.py']['asserts_quitados'], 2)  # assertTrue y el assert de test_dos
        self.assertIn('tests/test_a.py', texto)
        self.assertIn('tests/test_b.py', texto)
        self.assertIn('test_dos', texto)
        self.assertIn('Aviso: ', ''.join(l for l in texto.splitlines() if 'tests/test_a.py' in l))
        self.assertTrue(any('tests/test_a.py' in aviso and 'test_dos' in aviso for aviso in datos['avisos']))  # y en el JSON
        # no bloquea: pendientes y próximo paso iguales
        self.assertEqual((datos['pendientes'], datos['proximo_paso']), (antes['pendientes'], antes['proximo_paso']))
        self.assertFalse(any('test' in p.lower() for p in datos['pendientes']))

    def test_te1_un_archivo_de_pruebas_renombrado_con_tests_quitados(self):
        self.preparar()

        def editar():
            self.git('mv', 'tests/test_a.py', 'tests/test_nuevo.py')
            (self.root / 'tests/test_nuevo.py').write_text(TEST_A.replace('    def test_dos(self):\n        assert 2 == 2\n', ''))
        self.candidato(editar)
        [e] = self.estado()[1]['tests_editados']
        self.assertEqual((e['archivo'], e['estado']), ('tests/test_nuevo.py', 'renombrado'))
        self.assertEqual(e['origen'], 'tests/test_a.py')
        self.assertEqual(e['tests_quitados'], ['test_dos'])

    def test_te1_solo_agregar_tests_y_archivos_nuevos_no_avisa(self):
        self.preparar()

        def editar():
            (self.root / 'tests/test_a.py').write_text(TEST_A + '\n    def test_tres(self):\n        self.assertTrue(True)\n')
            (self.root / 'tests/test_nuevo.py').write_text('def test_nuevo():\n    assert 1\n')
        self.candidato(editar)
        texto, datos = self.estado()
        self.assertEqual(datos['tests_editados'], [])
        self.assertNotIn('tests/test_a.py', texto)

    def test_te1_sin_candidato_vigente_no_se_calcula(self):
        self.preparar()
        texto, datos = self.estado()
        self.assertIsNone(datos['tests_editados'])
        self.assertNotIn('Tests editados', texto)

    def test_te1_un_cambio_de_linea_en_un_test_cuenta_como_quitada(self):
        self.preparar()
        self.candidato(lambda: (self.root / 'tests/test_a.py').write_text(TEST_A.replace('self.assertEqual(1, 1)', 'self.assertEqual(1, 2 - 1)')))
        [e] = self.estado()[1]['tests_editados']
        self.assertEqual((e['lineas_quitadas'], e['asserts_quitados'], e['tests_quitados']), (1, 1, []))

    def test_te1_el_texto_del_estado_nombra_cada_archivo_y_no_es_un_pendiente(self):
        self.preparar()
        self.candidato(lambda: (self.root / 'tests/test_b.py').unlink())
        texto, datos = self.estado()
        linea = [l for l in texto.splitlines() if 'tests/test_b.py' in l]
        self.assertTrue(linea)
        self.assertTrue(all(l.startswith('Aviso: ') for l in linea), linea)


class PedidoAlRevisor(Base):
    configurar = _revisores.Revisores.configurar

    def preparar_revisor(self, modo):
        """El revisor de prueba de test_revisores: un script que lee el paquete y deja un informe válido."""
        script = Path(self.tmp.name) / 'revisor.py'
        script.write_text(_revisores.REVISOR)
        self.configurar(modo, script)

    def pedir(self):
        with contextlib.redirect_stdout(io.StringIO()):
            destino = f.pedir_revision(self.ident, 'prueba', base=self.base)
        return destino.with_name(destino.name.replace('.json', '.pedido.md')).read_text(encoding='utf-8')

    # --- te2: el pedido al revisor lleva la lista ---------------------------------------------------------------------------
    def test_te2_el_pedido_nombra_los_tests_quitados_y_pide_mencionarlos(self):
        self.preparar()
        self.preparar_revisor('ok')
        self.candidato(lambda: (self.root / 'tests/test_a.py').write_text(TEST_A.replace('    def test_dos(self):\n        assert 2 == 2\n', '')))
        pedido = self.pedir()
        self.assertIn('tests/test_a.py', pedido)
        self.assertIn('test_dos', pedido)
        self.assertRegex(pedido, r'(?i)mencion[aá]')

    def test_te2_sin_tests_editados_el_pedido_es_el_mismo(self):
        self.preparar()
        self.preparar_revisor('ok')
        self.candidato(lambda: (self.root / 'tests/test_nuevo.py').write_text('def test_nuevo():\n    assert 1\n'))
        con = self.pedir()
        from unittest.mock import patch
        with patch.object(alarmas, 'texto_para_el_revisor', return_value=''):
            sin = self.pedir()
        self.assertEqual(con.replace('prueba-1', 'prueba-N'), sin.replace('prueba-2', 'prueba-N'))
        self.assertNotRegex(con, r'(?i)tests existentes que')

    def test_te2_la_revision_se_pide_igual_aunque_haya_tests_editados(self):
        self.preparar()
        self.preparar_revisor('ok')
        self.candidato(lambda: (self.root / 'tests/test_a.py').write_text(TEST_A.replace('    def test_dos(self):\n        assert 2 == 2\n', '')))
        with contextlib.redirect_stdout(io.StringIO()):
            destino = f.pedir_revision(self.ident, 'prueba', base=self.base)
        self.assertTrue(destino.is_file())


class GitFalso(unittest.TestCase):
    """Los caminos de error y el formato, sin repositorio: un ejecutor de Git que responde lo que se le diga."""

    @staticmethod
    def ejecutor(respuestas):
        from types import SimpleNamespace
        llamadas = []

        def correr(argv):
            llamadas.append(argv)
            r = respuestas(argv)
            return SimpleNamespace(returncode=r[0], stdout=r[1])
        correr.llamadas = llamadas
        return correr

    def test_te1_si_git_falla_al_listar_o_al_leer_un_archivo_no_se_calcula_nada(self):
        listar_falla = self.ejecutor(lambda argv: (1, ''))
        self.assertIsNone(alarmas.tests_editados(listar_falla, 'b', 'c'))
        diff_falla = self.ejecutor(lambda argv: (0, 'M\0tests/a.py\0') if '--name-status' in argv else (1, ''))
        self.assertIsNone(alarmas.tests_editados(diff_falla, 'b', 'c'))

    def test_te1_sin_candidato_o_sin_base_no_se_calcula_y_no_se_llama_a_git_de_mas(self):
        nunca = self.ejecutor(lambda argv: (0, ''))
        self.assertIsNone(alarmas.del_candidato(nunca, ''))
        self.assertIsNone(alarmas.del_candidato(nunca, None))
        self.assertEqual(nunca.llamadas, [])
        sin_base = self.ejecutor(lambda argv: (1, '') if 'merge-base' in argv else (0, ''))
        self.assertIsNone(alarmas.del_candidato(sin_base, 'abc1234'))
        self.assertEqual(len(sin_base.llamadas), 1)  # se detuvo en el merge-base

    def test_te1_con_la_base_dada_no_se_busca_el_merge_base(self):
        git = self.ejecutor(lambda argv: (0, ''))
        self.assertEqual(alarmas.del_candidato(git, 'abc1234', base='deadbee'), [])
        self.assertFalse(any('merge-base' in a for a in git.llamadas))

    def test_te1_la_lista_sale_ordenada_por_archivo_y_nombra_el_origen_de_un_renombre(self):
        def respuesta(argv):
            if '--name-status' in argv:
                return 0, 'M\0tests/z.py\0R090\0tests/vieja.py\0tests/a_nueva.py\0'
            return 0, '-def test_x():\n-    assert 1\n'
        editados = alarmas.tests_editados(self.ejecutor(respuesta), 'b', 'c')
        self.assertEqual([e['archivo'] for e in editados], ['tests/a_nueva.py', 'tests/z.py'])
        linea = alarmas.avisos(editados)[0]
        self.assertIn('(antes tests/vieja.py)', linea)
        self.assertIn('renombrado', linea)
        self.assertIn('test_x', linea)
        self.assertIn('1 aserción(es) quitada(s)', linea)

    def test_te2_el_texto_para_el_revisor_nombra_cada_archivo_y_sin_nada_es_vacio(self):
        self.assertEqual(alarmas.texto_para_el_revisor([]), '')
        self.assertEqual(alarmas.texto_para_el_revisor(None), '')
        self.assertEqual(alarmas.avisos(None), [])
        e = {'archivo': 'tests/a.py', 'estado': 'modificado', 'origen': None, 'lineas_quitadas': 2, 'tests_quitados': ['test_q'], 'asserts_quitados': 1}
        texto = alarmas.texto_para_el_revisor([e])
        self.assertIn('- tests/a.py, modificado: 2 línea(s) quitada(s); tests quitados: test_q; 1 aserción(es) quitada(s)', texto)
        self.assertTrue(texto.endswith('\n'))


class QueEsUnTest(unittest.TestCase):
    # --- te3: sólo cuentan los archivos de pruebas -------------------------------------------------------------------------
    def test_te3_los_nombres_de_archivos_de_pruebas(self):
        for ruta in ('tests/a.py', 'test/a.py', 'pkg/tests/a.py', 'pkg/test_b.py', 'pkg/c_test.go', 'web/d.test.js', 'web/e.test.ts',
                     'test_f.py', 'x/y_test.py', 'web/g.test.cjs'):
            with self.subTest(ruta=ruta):
                self.assertTrue(alarmas.es_de_pruebas(ruta), ruta)

    def test_te3_los_que_no_son_de_pruebas(self):
        for ruta in ('src/contest.py', 'docs/tests.md', 'src/latest.py', 'src/modulo.py', 'README.md', 'tools/verify_x.py', 'testing/a.py',
                     'src/attest_b.py', 'src/protest.js', 'pkg/test.py'):
            with self.subTest(ruta=ruta):
                self.assertFalse(alarmas.es_de_pruebas(ruta), ruta)


class ProductoNoAvisa(Base):
    def test_te3_un_archivo_de_producto_que_pierde_lineas_no_avisa(self):
        self.preparar()
        self.candidato(lambda: (self.root / 'src/modulo.py').write_text('def f():\n    return 1\n'))
        self.assertEqual(self.estado()[1]['tests_editados'], [])

    def test_te3_un_archivo_de_documentacion_sobre_tests_tampoco(self):
        self.preparar()
        self.candidato(lambda: (self.root / 'docs/tests.md').write_text('uno\n'))
        self.assertEqual(self.estado()[1]['tests_editados'], [])


if __name__ == '__main__':
    unittest.main()
