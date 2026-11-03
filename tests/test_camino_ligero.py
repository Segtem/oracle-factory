"""El camino ligero de revisión: escenarios cl1–cl3, con repositorios Git temporales y la CLI de verdad."""
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parent))
import test_archivo as _archivo  # noqa: E402
import test_tests_editados as _te  # noqa: E402
from oracle_factory import agentes, alarmas  # noqa: E402
from tools.terminal import en_terminal  # noqa: E402

f = _archivo.f
SOURCE = Path(__file__).resolve().parents[1]
CLI = [sys.executable, '-c', 'import sys; from oracle_factory.cli import main; sys.exit(main())']
LINEAS = lambda n: ''.join(f'x{i} = {i}\n' for i in range(n))  # noqa: E731
CUERPO = ''.join(f'def f{i}():\n    return {i}\n\n\n' for i in range(12))  # para que un renombre se reconozca como tal


class Camino(_te.Base):
    # --- cl1: el estado dice si el candidato califica ------------------------------------------------------------------------
    def camino(self, editar, en_la_base=None):
        self.preparar()
        if en_la_base:
            self.en_la_base(en_la_base)
        self.candidato(editar)
        texto, datos = self.estado()
        return texto, datos, datos['camino']

    def test_cl1_un_cambio_chico_es_ligero_y_el_estado_y_el_json_lo_dicen(self):
        texto, datos, camino = self.camino(lambda: (self.root / 'src/chico.py').write_text(LINEAS(40)))
        self.assertEqual((camino['tipo'], camino['lineas'], camino['umbral'], camino['reglas_tocadas']), ('ligero', 40, 150, []))
        linea = next(l for l in texto.splitlines() if l.startswith('Camino de revisión:'))
        self.assertIn('ligero', linea)
        self.assertIn('40 líneas', linea)

    def test_cl1_un_cambio_de_151_lineas_es_completo_y_nombra_las_lineas_y_el_umbral(self):
        texto, datos, camino = self.camino(lambda: (self.root / 'src/grande.py').write_text(LINEAS(151)))
        self.assertEqual((camino['tipo'], camino['lineas']), ('completo', 151))
        linea = next(l for l in texto.splitlines() if l.startswith('Camino de revisión:'))
        self.assertIn('completo', linea)
        self.assertIn('151', linea)
        self.assertIn('150', linea)

    def test_cl1_justo_en_el_umbral_sigue_siendo_ligero(self):
        _, _, camino = self.camino(lambda: (self.root / 'src/justo.py').write_text(LINEAS(150)))
        self.assertEqual((camino['tipo'], camino['lineas']), ('ligero', 150))

    def test_cl1_tocar_una_regla_de_decision_es_completo_aunque_sea_chico_y_la_nombra(self):
        texto, datos, camino = self.camino(lambda: (self.root / 'oracle_factory/modos.py').write_text(CUERPO + 'y = 2\n'),
                                           en_la_base={'oracle_factory/modos.py': CUERPO})
        self.assertEqual((camino['tipo'], camino['reglas_tocadas']), ('completo', ['oracle_factory/modos.py']))
        self.assertLess(camino['lineas'], 10)
        self.assertIn('oracle_factory/modos.py', next(l for l in texto.splitlines() if l.startswith('Camino de revisión:')))

    def test_cl1_renombrar_desde_una_regla_de_decision_tambien_cuenta(self):
        def editar():
            self.git('mv', 'oracle_factory/flujo_revision.py', 'oracle_factory/otro_nombre.py')
        _, _, camino = self.camino(editar, en_la_base={'oracle_factory/flujo_revision.py': CUERPO})
        self.assertEqual((camino['tipo'], camino['reglas_tocadas']), ('completo', ['oracle_factory/flujo_revision.py']))

    def test_cl1_renombrar_hacia_una_regla_de_decision_tambien_cuenta(self):
        def editar():
            self.git('mv', 'src/modulo.py', 'oracle_factory/puerta.py')
        self.preparar()
        (self.root / 'oracle_factory').mkdir(exist_ok=True)
        self.candidato(editar)
        self.assertEqual(self.estado()[1]['camino']['reglas_tocadas'], ['oracle_factory/puerta.py'])

    def test_cl1_las_pruebas_no_cuentan_en_las_lineas(self):
        def editar():
            (self.root / 'src/chico.py').write_text(LINEAS(100))
            (self.root / 'tests/test_enorme.py').write_text('def test_x():\n    assert 1\n' + LINEAS(800))
        _, _, camino = self.camino(editar)
        self.assertEqual((camino['tipo'], camino['lineas']), ('ligero', 100))

    def test_cl1_sin_candidato_vigente_no_afirma_un_camino(self):
        from unittest.mock import patch
        self.preparar()
        with patch.object(alarmas, '_git', side_effect=AssertionError('sin candidato no se llama a Git')):
            texto, datos = self.estado()
        self.assertIsNone(datos['camino'])
        self.assertNotIn('Camino de revisión', texto)

    def test_cl1_un_cambio_abandonado_no_lleva_camino_aunque_tenga_candidato(self):
        self.preparar()
        self.candidato(lambda: (self.root / 'src/chico.py').write_text(LINEAS(10)))
        self.assertEqual(f.datos_estado(self.ident)['camino']['tipo'], 'ligero')
        carpeta, estado = f.leer(self.ident)
        estado['fase'] = 'abandonada'
        f.guardar(carpeta, estado)
        self.assertIsNone(f.datos_estado(self.ident)['camino'])


class CaminoPuro(unittest.TestCase):
    def ejecutor(self, numstat='', nombres='', base_ok=True, falla_numstat=False):
        def ejecutar(argv):
            if argv[:2] == ['git', 'merge-base']:
                return SimpleNamespace(returncode=0 if base_ok else 1, stdout='basebase\n', stderr='')
            if '--numstat' in argv:
                return SimpleNamespace(returncode=1 if falla_numstat else 0, stdout=numstat, stderr='')
            return SimpleNamespace(returncode=0, stdout=nombres, stderr='')
        return ejecutar

    def test_cl1_la_lista_y_el_umbral_son_los_del_documento(self):
        self.assertEqual(alarmas.UMBRAL_LIGERO, 150)
        self.assertEqual(set(alarmas.REGLAS_DE_DECISION), {
            'oracle_factory/cli.py', 'oracle_factory/modos.py', 'oracle_factory/flujo_revision.py', 'oracle_factory/flujo_medidas.py',
            'oracle_factory/revision.py', 'oracle_factory/preparacion.py', 'oracle_factory/puerta.py', 'oracle_factory/unir.py',
            'oracle_factory/alarmas.py'})
        for regla in alarmas.REGLAS_DE_DECISION:
            self.assertTrue((SOURCE / regla).is_file(), regla)  # la lista no apunta a un archivo que ya no existe

    def test_cl1_si_git_no_puede_decirlo_no_se_afirma_ni_ligero_ni_completo(self):
        for ejecutor in (self.ejecutor(base_ok=False), self.ejecutor(falla_numstat=True)):
            self.assertIsNone(alarmas.camino_del_candidato(ejecutor, 'cand1234', es_producto=lambda ruta: True))
        self.assertIsNone(alarmas.camino_del_candidato(self.ejecutor(), '', es_producto=lambda ruta: True))
        self.assertIsNone(alarmas.camino_del_candidato(self.ejecutor(), None, es_producto=lambda ruta: True))

    def test_cl1_si_falla_solo_la_lista_de_archivos_tampoco_se_afirma_un_camino(self):
        def ejecutar(argv):
            if argv[:2] == ['git', 'merge-base']:
                return SimpleNamespace(returncode=0, stdout='basebase\n', stderr='')
            if '--numstat' in argv:
                return SimpleNamespace(returncode=0, stdout='5\t0\tsrc/a.py\0', stderr='')
            return SimpleNamespace(returncode=1, stdout='', stderr='boom')  # --name-status
        self.assertIsNone(alarmas.camino_del_candidato(ejecutar, 'cand1234', es_producto=lambda ruta: True))

        def no_utf8(argv):
            raise UnicodeDecodeError('utf-8', b'\xff', 0, 1, 'invalid start byte')
        self.assertIsNone(alarmas.camino_del_candidato(no_utf8, 'cand1234', es_producto=lambda ruta: True))

    def test_cl1_las_reglas_tocadas_salen_ordenadas_y_sin_repetir(self):
        todas = ''.join(f'M\0{r}\0' for r in reversed(alarmas.REGLAS_DE_DECISION))
        nombres = todas + 'R100\0oracle_factory/unir.py\0oracle_factory/x.py\0A\0src/a.py\0'
        camino = alarmas.camino_del_candidato(self.ejecutor(numstat='5\t0\tsrc/a.py\0', nombres=nombres), 'cand1234', es_producto=lambda ruta: True)
        self.assertEqual(camino['reglas_tocadas'], sorted(alarmas.REGLAS_DE_DECISION))  # todas, una vez cada una y en orden alfabético
        self.assertEqual(camino['tipo'], 'completo')

    def test_cl1_el_motivo_del_completo_nombra_solo_lo_que_pasa(self):
        regla = 'M\0oracle_factory/modos.py\0'
        justo = alarmas.camino_del_candidato(self.ejecutor(numstat='150\t0\tsrc/a.py\0', nombres=regla), 'cand1234', es_producto=lambda r: True)
        linea = alarmas.linea_camino(justo)
        self.assertIn('toca reglas de decisión: oracle_factory/modos.py', linea)
        self.assertNotIn('más de', linea)  # 150 líneas no son más de 150
        grande = alarmas.camino_del_candidato(self.ejecutor(numstat='151\t0\tsrc/a.py\0', nombres='M\0src/a.py\0'), 'cand1234', es_producto=lambda r: True)
        self.assertIn('151 líneas de producto, más de 150', alarmas.linea_camino(grande))
        self.assertNotIn('reglas', alarmas.linea_camino(grande))
        self.assertIsNone(alarmas.linea_camino(None))

    def test_cl1_un_archivo_que_se_llama_parecido_a_una_regla_no_es_una_regla(self):
        nombres = 'M\0oracle_factory/modos_extra.py\0M\0docs/modos.py\0M\0oracle_factory/sub/modos.py\0'
        camino = alarmas.camino_del_candidato(self.ejecutor(numstat='5\t0\tsrc/a.py\0', nombres=nombres), 'cand1234', es_producto=lambda ruta: True)
        self.assertEqual((camino['tipo'], camino['reglas_tocadas']), ('ligero', []))


class Pendientes(_te.Base):
    # --- cl2: nada de lo que decide una persona cambia ------------------------------------------------------------------------
    def test_cl2_los_pendientes_y_el_proximo_paso_no_dependen_del_camino(self):
        from unittest.mock import patch
        self.preparar()
        self.candidato(lambda: (self.root / 'src/chico.py').write_text(LINEAS(10)))
        ligero = self.estado()[1]
        self.assertEqual(ligero['camino']['tipo'], 'ligero')
        for camino in ({'tipo': 'completo', 'lineas': 900, 'umbral': 150, 'reglas_tocadas': ['oracle_factory/cli.py']}, None):
            with patch.object(alarmas, 'camino_del_candidato', return_value=camino):
                otro = f.datos_estado(self.ident)
            self.assertEqual((otro['pendientes'], otro['proximo_paso'], otro['alternativas'], otro['decisiones']),
                             (ligero['pendientes'], ligero['proximo_paso'], ligero['alternativas'], ligero['decisiones']))
        self.assertFalse(any('ligero' in p.lower() or 'camino' in p.lower() for p in ligero['pendientes']))

    def test_cl2_el_camino_no_es_un_aviso_ni_un_pendiente_del_texto(self):
        self.preparar()
        self.candidato(lambda: (self.root / 'src/grande.py').write_text(LINEAS(300)))
        texto, datos = self.estado()
        self.assertFalse(any('camino' in a.lower() for a in datos['avisos']))
        self.assertFalse(any(l.startswith('Aviso: ') and 'Camino' in l for l in texto.splitlines()))
        pendiente = next(l for l in texto.splitlines() if l.startswith('Pendiente:'))
        self.assertNotIn('camino', pendiente.lower())


class Guia(unittest.TestCase):
    # --- cl3: la guía para agentes lo explica y no se desactualiza ------------------------------------------------------------
    def test_cl3_la_guia_dice_los_numeros_y_los_archivos_aprobados_no_solo_lo_que_diga_el_codigo(self):
        texto = agentes.bloque('confirmacion')
        self.assertIn('hasta 150 líneas de producto', texto)  # literales: si alguien cambia la constante, esta prueba lo nota
        for regla in ('cli', 'modos', 'flujo_revision', 'flujo_medidas', 'revision', 'preparacion', 'puerta', 'unir', 'alarmas'):
            self.assertIn(f'`oracle_factory/{regla}.py`', texto)

    def test_cl3_el_documento_nombra_el_umbral_las_reglas_y_los_limites(self):
        documento = (SOURCE / 'docs/agentes.md').read_text(encoding='utf-8')
        self.assertIn(f'{alarmas.UMBRAL_LIGERO} líneas', documento)
        for regla in alarmas.REGLAS_DE_DECISION:
            self.assertIn(f"`{regla.rsplit('/', 1)[-1]}`", documento)
        self.assertRegex(documento, r'(?s)Límites conocidos.*binario.*renombre')

    def test_cl3_la_guia_nombra_el_umbral_cada_regla_y_el_criterio_de_la_ronda(self):
        texto = agentes.bloque('confirmacion')
        self.assertIn(f'{alarmas.UMBRAL_LIGERO} líneas', texto)
        for regla in alarmas.REGLAS_DE_DECISION:
            self.assertIn(f'`{regla}`', texto)
        self.assertIn('un revisor y una ronda', texto)
        self.assertRegex(texto, r'(?s)camino ligero.*hallazgos medios o altos.*camino completo')

    def test_cl3_la_guia_es_igual_a_la_del_repositorio_y_se_nota_si_queda_vieja(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        root = Path(tmp.name) / 'producto'
        root.mkdir()
        env = {**os.environ, 'PYTHONPATH': str(SOURCE), 'GIT_CEILING_DIRECTORIES': tmp.name}
        for args in (('init', '-q', '-b', 'main'), ('config', 'user.name', 'Ana'), ('config', 'user.email', 'ana@x.invalid')):
            subprocess.run(['git', *args], cwd=root, env=env, check=True, capture_output=True)
        self.assertEqual(en_terminal([*CLI, 'init'], cwd=root, env=env, entrada='1\n1\n1\n').returncode, 0)
        self.assertEqual(en_terminal([*CLI, 'agentes'], cwd=root, env=env, entrada='').returncode, 0)
        self.assertEqual(en_terminal([*CLI, 'agentes', '--verificar'], cwd=root, env=env, entrada='').returncode, 0)
        guia = root / 'AGENTS.md'
        guia.write_text(guia.read_text().replace(f'{alarmas.UMBRAL_LIGERO} líneas', '100 líneas'))
        self.assertNotEqual(en_terminal([*CLI, 'agentes', '--verificar'], cwd=root, env=env, entrada='').returncode, 0)
        guia.write_text(guia.read_text().replace('100 líneas', f'{alarmas.UMBRAL_LIGERO} líneas').replace(next(iter(alarmas.REGLAS_DE_DECISION)), 'x/y.py', 1))
        self.assertNotEqual(en_terminal([*CLI, 'agentes', '--verificar'], cwd=root, env=env, entrada='').returncode, 0)


if __name__ == '__main__':
    unittest.main()
