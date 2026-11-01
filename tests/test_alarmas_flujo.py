"""Avisar de los bucles de revisión y de los cambios demasiado grandes: escenarios af1–af3, con repositorios Git temporales."""
import json
from pathlib import Path
import re
import subprocess
import sys
import unittest
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parent))
import test_archivo as _archivo  # noqa: E402
import test_tests_editados as _te  # noqa: E402
from oracle_factory import alarmas  # noqa: E402

f = _archivo.f
SOURCE = Path(__file__).resolve().parents[1]
LINEAS = lambda n: ''.join(f'x{i} = {i}\n' for i in range(n))  # noqa: E731


def evento(accion, candidato, cuando='2026-11-01T10:00:00'):
    return {'accion': accion, 'candidato': candidato, 'cuando': cuando}


class Rondas(unittest.TestCase):
    # --- af1: el estado avisa cuando la revisión lleva cuatro rondas -------------------------------------------------------
    def test_af1_cuatro_candidatos_revisados_son_cuatro_rondas_y_avisan(self):
        eventos = [evento('revision_pedida', c) for c in ('aaaaaaa', 'bbbbbbb', 'ccccccc', 'ddddddd')]
        self.assertEqual(alarmas.rondas({'eventos': eventos}), 4)
        [aviso] = alarmas.avisos_de_flujo(rondas=4, lineas=None)
        self.assertIn('4 rondas', aviso)

    def test_af1_dos_revisores_del_mismo_candidato_son_una_sola_ronda(self):
        eventos = [evento('revision_pedida', 'aaaaaaa'), evento('revision_pedida', 'aaaaaaa'), evento('revision_lanzada', 'aaaaaaa'),
                   evento('revision_pedida', 'bbbbbbb'), evento('revision_pedida', 'ccccccc')]
        self.assertEqual(alarmas.rondas({'eventos': eventos}), 3)
        self.assertEqual(alarmas.avisos_de_flujo(rondas=3, lineas=None), [])

    def test_af1_un_registro_ilegible_no_se_cuenta_ni_rompe(self):
        for estado in ({}, {'eventos': None}, {'eventos': 'x'}, {'eventos': [None, 3, 'x', {'accion': 'revision_pedida'}, {'candidato': 'a'}]}):
            with self.subTest(estado=estado):
                self.assertIn(alarmas.rondas(estado), (0, None))
        self.assertEqual(alarmas.avisos_de_flujo(rondas=None, lineas=None), [])

    def test_af1_el_umbral_es_cuatro_y_el_aviso_sugiere_parar_a_arreglar_la_clase(self):
        self.assertEqual(alarmas.UMBRAL_RONDAS, 4)
        self.assertEqual(alarmas.avisos_de_flujo(rondas=3, lineas=None), [])
        [aviso] = alarmas.avisos_de_flujo(rondas=6, lineas=None)
        self.assertIn('6 rondas', aviso)
        self.assertIn('lista previa', aviso)


    def test_af1_una_revision_lanzada_cuenta_como_ronda_igual_que_una_pedida(self):
        eventos = [evento('revision_lanzada', c) for c in ('aaaaaaa', 'bbbbbbb')] + [evento('revision_pedida', 'ccccccc')]
        self.assertEqual(alarmas.rondas({'eventos': eventos}), 3)

    def test_af1_el_dato_del_json_dice_si_avisa_justo_en_el_umbral(self):
        sin_git = lambda argv: SimpleNamespace(returncode=1, stdout='', stderr='')  # noqa: E731
        for n, avisa in ((3, False), (4, True)):
            with self.subTest(rondas=n):
                estado = {'eventos': [evento('revision_pedida', f'{i}' * 7) for i in range(n)]}
                dato = alarmas.del_flujo(sin_git, estado, None)['bucle_de_revision']
                self.assertEqual((dato['rondas'], dato['umbral'], dato['avisa']), (n, 4, avisa))


class Tamano(unittest.TestCase):
    # --- af2: el estado avisa cuando el candidato agrega más de 450 líneas de producto -------------------------------------
    def numstat(self, filas):
        """Un ejecutor falso de git: la lista de archivos y el numstat con -z, como los entrega Git."""
        def ejecutar(argv):
            if '--numstat' in argv:
                return SimpleNamespace(returncode=0, stdout=''.join(f'{a}\t{q}\t{ruta}\0' for a, q, ruta in filas))
            return SimpleNamespace(returncode=1, stdout='', stderr='')
        return ejecutar

    def test_af2_cuentan_las_lineas_agregadas_de_producto_y_no_las_de_pruebas(self):
        ejecutar = self.numstat([('100', '5', 'src/a.py'), ('800', '0', 'tests/test_a.py'), ('20', '0', 'docs/x.md'), ('-', '-', 'img.png')])
        self.assertEqual(alarmas.lineas_de_producto(ejecutar, 'base', 'cand', es_producto=lambda ruta: True), 120)

    def test_af2_lo_que_no_es_producto_no_cuenta(self):
        ejecutar = self.numstat([('100', '0', 'src/a.py'), ('900', '0', 'kb/cambios/x.md')])
        self.assertEqual(alarmas.lineas_de_producto(ejecutar, 'base', 'cand', es_producto=lambda ruta: not ruta.startswith('kb/')), 100)

    def test_af2_un_renombre_con_numstat_z_se_lee_con_su_destino(self):
        def ejecutar(argv):
            return SimpleNamespace(returncode=0, stdout='3\t1\t\0src/viejo.py\0src/nuevo.py\0' + '10\t0\tsrc/b.py\0')
        self.assertEqual(alarmas.lineas_de_producto(ejecutar, 'base', 'cand', es_producto=lambda ruta: True), 13)

    def test_af2_si_git_falla_no_se_calcula(self):
        ejecutar = lambda argv: SimpleNamespace(returncode=1, stdout='', stderr='boom')  # noqa: E731
        self.assertIsNone(alarmas.lineas_de_producto(ejecutar, 'base', 'cand', es_producto=lambda ruta: True))
        self.assertIsNone(alarmas.lineas_de_producto(ejecutar, '', '', es_producto=lambda ruta: True))

    def test_af2_el_umbral_es_450_y_justo_en_el_umbral_no_avisa(self):
        self.assertEqual(alarmas.UMBRAL_LINEAS, 450)
        self.assertEqual(alarmas.avisos_de_flujo(rondas=None, lineas=450), [])
        [aviso] = alarmas.avisos_de_flujo(rondas=None, lineas=451)
        self.assertIn('451 líneas', aviso)
        self.assertIn('partir', aviso)
        self.assertEqual(alarmas.avisos_de_flujo(rondas=None, lineas=None), [])

    def test_af2_el_dato_del_json_dice_si_avisa_justo_en_el_umbral(self):
        def con(lineas):
            def ejecutar(argv):
                if argv[:2] == ['git', 'merge-base']:
                    return SimpleNamespace(returncode=0, stdout='basebase\n')
                return SimpleNamespace(returncode=0, stdout=f'{lineas}\t0\tsrc/a.py\0')
            return ejecutar
        for lineas, avisa in ((450, False), (451, True)):
            with self.subTest(lineas=lineas):
                dato = alarmas.del_flujo(con(lineas), {}, 'cand1234')['cambio_grande']
                self.assertEqual((dato['lineas'], dato['umbral'], dato['avisa']), (lineas, 450, avisa))

    def test_af2_si_no_se_encuentra_la_base_no_se_calcula_nada(self):
        llamadas = []

        def ejecutar(argv):
            llamadas.append(argv[:2])
            return SimpleNamespace(returncode=1, stdout='999\t0\tsrc/a.py\0', stderr='sin base')
        self.assertIsNone(alarmas.del_flujo(ejecutar, {}, 'cand1234')['cambio_grande'])
        self.assertEqual(llamadas, [['git', 'merge-base']])  # y no se le pregunta el diff a Git sin base

    def test_af2_un_avisos_de_cada_uno_cuando_hay_los_dos(self):
        self.assertEqual(len(alarmas.avisos_de_flujo(rondas=5, lineas=900)), 2)


class EstadoReal(_te.Base):
    """El estado con un repositorio Git de verdad: el aviso sale en el texto y en el JSON, y no cambia los pendientes."""

    def agregar_eventos(self, candidatos):
        carpeta, estado = f.leer(self.ident)
        for c in candidatos:
            estado.setdefault('eventos', []).append(evento('revision_pedida', c))
        f.guardar(carpeta, estado)

    def test_af2_un_candidato_grande_avisa_en_el_texto_y_en_el_json_sin_cambiar_los_pendientes(self):
        self.preparar()
        from unittest.mock import patch
        self.candidato(lambda: (self.root / 'src/grande.py').write_text(LINEAS(600)))
        with patch.object(alarmas, 'lineas_de_producto', return_value=None):
            antes = f.datos_estado(self.ident)
        self.assertIsNone(antes['cambio_grande'])  # no se pudo calcular
        texto, datos = self.estado()
        self.assertEqual((datos['cambio_grande']['lineas'], datos['cambio_grande']['avisa']), (600, True))
        self.assertTrue(any('600 líneas' in a for a in datos['avisos']))
        self.assertIn('600 líneas', ''.join(l for l in texto.splitlines() if l.startswith('Aviso: ')))
        self.assertEqual((datos['pendientes'], datos['proximo_paso']), (antes['pendientes'], antes['proximo_paso']))

    def test_af2_las_pruebas_no_cuentan_en_un_candidato_real(self):
        self.preparar()

        def editar():
            (self.root / 'src/chico.py').write_text(LINEAS(100))
            (self.root / 'tests/test_enorme.py').write_text('def test_x():\n    assert 1\n' + LINEAS(800))
        self.candidato(editar)
        datos = self.estado()[1]
        self.assertEqual((datos['cambio_grande']['lineas'], datos['cambio_grande']['avisa']), (100, False))
        self.assertFalse(any('líneas de producto' in a for a in datos['avisos']))

    def test_af2_sin_candidato_vigente_no_se_calcula(self):
        self.preparar()
        from unittest.mock import patch
        with patch.object(alarmas, 'lineas_de_producto', side_effect=AssertionError('sin candidato no se llama a Git')):
            texto, datos = self.estado()
        self.assertIsNone(datos['cambio_grande'])

    def test_af1_cuatro_rondas_avisan_en_el_texto_y_en_el_json(self):
        self.preparar()
        self.candidato(lambda: (self.root / 'src/chico.py').write_text(LINEAS(10)))
        antes = f.datos_estado(self.ident)
        self.agregar_eventos(['aaaaaaa', 'bbbbbbb', 'ccccccc', 'ddddddd'])
        texto, datos = self.estado()
        self.assertEqual(datos['bucle_de_revision']['rondas'], 4)
        self.assertTrue(any('4 rondas' in a for a in datos['avisos']))
        self.assertIn('4 rondas de revisión', texto)
        self.assertEqual((datos['pendientes'], datos['proximo_paso']), (antes['pendientes'], antes['proximo_paso']))

    def test_af1_con_tres_rondas_no_avisa(self):
        self.preparar()
        self.agregar_eventos(['aaaaaaa', 'bbbbbbb', 'ccccccc'])
        texto, datos = self.estado()
        self.assertEqual((datos['bucle_de_revision']['rondas'], datos['bucle_de_revision']['avisa']), (3, False))
        self.assertNotIn('rondas de revisión', texto)

    def test_af1_un_registro_con_eventos_rotos_no_hace_fallar_el_estado(self):
        self.preparar()
        carpeta, estado = f.leer(self.ident)
        estado['eventos'] = [{'accion': 'revision_pedida'}, {'candidato': 'x'}] + (estado.get('eventos') or [])
        f.guardar(carpeta, estado)
        self.assertFalse(self.estado()[1]['bucle_de_revision']['avisa'])


class Documento(unittest.TestCase):
    # --- af3: el documento coincide con el código -------------------------------------------------------------------------
    def test_af3_el_documento_nombra_los_dos_umbrales_y_el_conteo_aproximado(self):
        documento = (SOURCE / 'docs/tests.md').read_text(encoding='utf-8')
        self.assertIn(f'{alarmas.UMBRAL_RONDAS} rondas', documento)
        self.assertIn(f'{alarmas.UMBRAL_LINEAS} líneas', documento)
        self.assertRegex(documento, r'(?is)aserciones[^.]*aproximad|aproximad[^.]*aserciones')
        self.assertIn('bucle_de_revision', documento)
        self.assertIn('cambio_grande', documento)

    def test_af3_el_contrato_del_verificador_nombra_exactamente_los_casos_que_existen(self):
        from tools import verify_alarmas_flujo as verificador
        import ast
        reales = set()
        for nodo in ast.parse(Path(__file__).read_text(encoding='utf-8')).body:
            if isinstance(nodo, ast.ClassDef):
                reales |= {f'{nodo.name}.{m.name}' for m in nodo.body if isinstance(m, ast.FunctionDef) and re.match(r'test_af\d_', m.name)}
        contratados = [n for nombres in verificador.CONTRACTS.values() for n in nombres]
        self.assertEqual(sorted(contratados), sorted(set(contratados)))
        self.assertEqual(set(contratados), reales)


if __name__ == '__main__':
    unittest.main()
