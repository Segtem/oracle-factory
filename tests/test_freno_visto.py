"""Frenos: el de pruebas editadas cede ante una revisión aprobada y vigente: escenario fv1, con Git de verdad para el estado."""
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import test_tests_editados as _te  # noqa: E402
from test_frenos import GRANDE, SIN, calcular, ids, juicio  # noqa: E402

f = _te.f
EDITADOS = [{'archivo': 'tests/test_a.py', 'estado': 'modificado', 'origen': None, 'lineas_quitadas': 2, 'tests_quitados': [], 'asserts_quitados': 1}]
PRUEBA = 'prueba_existente_editada'


class Calculo(unittest.TestCase):
    def test_fv1_la_revision_aprobada_levanta_el_freno_de_pruebas_editadas_y_sin_ella_sigue(self):
        self.assertEqual(ids(calcular(editados=EDITADOS)), [PRUEBA])
        self.assertEqual(ids(calcular(editados=EDITADOS, aprobada=False)), [PRUEBA])
        self.assertEqual(calcular(editados=EDITADOS, aprobada=True), [])
        self.assertEqual(calcular(editados=[], aprobada=True), [])
        self.assertEqual(calcular(editados=[], aprobada=False), [])  # sin tests editados no hay freno, con o sin revisión
        self.assertEqual(calcular(editados=None, aprobada=False), [])

    def test_fv1_los_demas_frenos_no_cambian_con_la_revision_aprobada(self):
        todo = calcular([juicio(1), juicio(1)], editados=EDITADOS, flujo=GRANDE, aprobada=True)
        self.assertEqual(ids(todo), ['juicios_rojos', 'cambio_grande', 'bucle_de_revision'])
        self.assertEqual(ids(calcular([juicio(1), juicio(1)], editados=EDITADOS, flujo=GRANDE)),
                         ['juicios_rojos', PRUEBA, 'cambio_grande', 'bucle_de_revision'])
        self.assertEqual(ids(calcular(editados=EDITADOS, flujo=SIN, aprobada=True)), [])


class EstadoReal(_te.Base):
    def test_fv1_con_estado_real_la_revision_vigente_la_levanta_y_otro_candidato_la_devuelve_y_el_aviso_queda(self):
        self.preparar()
        sha = self.candidato(lambda: (self.root / 'tests/test_b.py').unlink())
        _, estado = f.leer(self.ident)
        actual = f.contexto_producto()

        def frenos(decision, contexto, problemas=()):
            estado['revision'] = {'decision': decision, 'contexto': contexto}
            with patch.object(f, 'problemas_de_revision', return_value=list(problemas)):
                return ids(f.frenos_del_cambio(self.ident, estado, sha, actual, EDITADOS, {}))
        self.assertEqual(frenos('aprobar', actual), [])
        self.assertEqual(frenos('cambios', actual), [PRUEBA])
        self.assertEqual(frenos('aprobar', actual, ['algo']), [PRUEBA])
        self.assertEqual(frenos('aprobar', {'archivos_sha256': 'otro'}), [PRUEBA])
        self.assertEqual(frenos('aprobar', None), [PRUEBA])
        estado['revision'] = {'decision': 'aprobar', 'contexto': actual}
        self.assertEqual(ids(f.frenos_del_cambio(self.ident, estado, sha, None, EDITADOS, {})), [PRUEBA])  # producto ilegible: no rompe y frena
        texto, datos = self.estado()
        self.assertEqual(ids(datos['frenos']), [PRUEBA])  # sin revisión registrada todavía
        self.assertTrue(any('test existente editado' in a for a in datos['avisos']))
        carpeta, estado = f.leer(self.ident)
        estado['revision'] = {'decision': 'aprobar', 'contexto': f.contexto_producto()}
        f.guardar(carpeta, estado)
        with patch.object(f, 'problemas_de_revision', return_value=[]):
            datos = f.datos_estado(self.ident)
        self.assertEqual(datos['frenos'], [])
        self.assertTrue(any('test existente editado' in a for a in datos['avisos']))
        self.assertFalse(any(a.startswith('FRENO:') for a in datos['avisos']))
        # un candidato nuevo (otro producto) deja vieja esa revisión y el freno vuelve, con Git de verdad
        self.candidato(lambda: (self.root / 'src/modulo.py').write_text('def f():\n    return 3\n'))
        with patch.object(f, 'problemas_de_revision', return_value=[]):
            datos = f.datos_estado(self.ident)
        self.assertEqual(ids(datos['frenos']), [PRUEBA])
        self.assertTrue(any(a.startswith('FRENO:') for a in datos['avisos']))


if __name__ == '__main__':
    unittest.main()
