"""Autopilot: el segundo revisor del camino completo: escenarios sr1–sr2, con Git de verdad para el estado."""
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import test_tests_editados as _te  # noqa: E402
from oracle_factory import autopilot, estructura  # noqa: E402

f = _te.f
ID = '20261109-000000-abc-demo'
COMPLETO = {'tipo': 'completo', 'lineas': 900, 'umbral': 150, 'reglas_tocadas': []}
LIGERO = {'tipo': 'ligero', 'lineas': 10, 'umbral': 150, 'reglas_tocadas': []}
REVISORES = {'agy': {'proveedor': 'agy'}, 'agy2': {'proveedor': 'agy'}, 'codex': {'proveedor': 'codex'}}
PROPUESTA = {'decision': 'aprobar', 'candidato': 'abc1234', 'actor': 'claude-code', 'cuando': '2026-11-09T01:00:00+00:00'}


def informe(revisor, candidato='abc1234'):
    return {'revisor': revisor, 'candidato': candidato, 'hallazgos': []}


def segundo(camino=COMPLETO, informes=(informe('agy'),), revisores=REVISORES):
    return autopilot.segundo_revisor(camino, list(informes) if informes is not None else None, revisores)


def decidir(extra, paso=f'oracle-factory revisar {ID}', frenos=()):
    return autopilot.decidir({'fase': 'requisitos_importados', 'proximo_paso': paso, 'frenos': list(frenos), 'candidato': 'abc1234',
                              'propuesta_de_revision': PROPUESTA, **extra})


class Calculo(unittest.TestCase):
    def test_sr1_el_segundo_revisor_es_el_de_otro_proveedor_y_solo_en_el_camino_completo(self):
        self.assertEqual(segundo(), 'codex')  # agy2 es del mismo proveedor que agy
        self.assertEqual(segundo(informes=[informe('agy2')]), 'codex')
        self.assertEqual(segundo(informes=[informe('codex')]), 'agy')
        self.assertIsNone(segundo(informes=[informe('agy'), informe('codex', 'otro123')]))  # dos proveedores, aunque de candidatos distintos
        self.assertEqual(segundo(informes=[informe('agy'), informe('agy2')]), 'codex')
        self.assertIsNone(segundo(camino=LIGERO))
        self.assertIsNone(segundo(camino=None))
        self.assertIsNone(segundo(camino={'tipo': 'otro'}))
        self.assertEqual(segundo(informes=[]), 'agy')
        # sin otro proveedor, o datos ilegibles: null y sin romper
        self.assertIsNone(segundo(revisores={'agy': {'proveedor': 'agy'}, 'agy2': {'proveedor': 'agy'}}))
        self.assertIsNone(segundo(revisores={}))
        for malo in (None, [], 'x', 3):
            self.assertIsNone(segundo(revisores=malo))
        self.assertIsNone(segundo(informes=None))
        self.assertEqual(segundo(informes=[1, None, {'revisor': 3}, {}]), 'agy')  # informes sin revisor legible no cuentan
        # el proveedor falta: cuenta el nombre; un nombre que no sirve para un comando no se ofrece
        self.assertEqual(segundo(revisores={'agy': {}, 'otro': 'x'}), 'otro')
        self.assertIsNone(segundo(revisores={'agy': {}, 'con espacio': {}, 'a;b': {}}))
        self.assertEqual(segundo(informes=[informe('agy'), 7], revisores=REVISORES), 'codex')

class EstadoReal(_te.Base):
    def test_sr1_con_estado_real_aparece_en_el_json_y_se_va_con_el_segundo_proveedor(self):
        self.preparar()
        grande = ''.join(f'def f{i}():\n    return {i}\n\n\n' for i in range(60))
        sha = self.candidato(lambda: (self.root / 'src/grande.py').write_text(grande))

        def escribir(revisor, candidato):
            carpeta = estructura.ruta_canonica(self.root, self.ident, 'revision', candidato)
            carpeta.mkdir(parents=True, exist_ok=True)
            (carpeta / f'{revisor}-1.json').write_text(json.dumps({'findings': []}))
        real = f.config_proyecto

        def con(revisores):
            return lambda: {**real(), 'revisores': revisores}
        with patch.object(f, 'config_proyecto', side_effect=con(REVISORES)):
            datos = f.datos_estado(self.ident)
            self.assertEqual(datos['camino']['tipo'], 'completo')
            self.assertEqual(datos['segundo_revisor'], 'agy')  # todavía ningún informe
            escribir('agy', sha)
            self.assertEqual(f.datos_estado(self.ident)['segundo_revisor'], 'codex')
            escribir('codex', 'otro1234')
            self.assertIsNone(f.datos_estado(self.ident)['segundo_revisor'])
        with patch.object(f, 'config_proyecto', side_effect=con('no es un objeto')):
            self.assertIsNone(f.datos_estado(self.ident)['segundo_revisor'])
        for error in (f.FactoryError('ilegible'), OSError('x'), ValueError('y')):
            with patch.object(f, 'config_proyecto', side_effect=error):
                self.assertIsNone(f.segundo_revisor_del_cambio(self.ident, COMPLETO))


class Conductor(unittest.TestCase):
    def test_sr2_con_segundo_revisor_el_conductor_lo_pide_antes_de_la_revision(self):
        d = decidir({'segundo_revisor': 'codex'})
        self.assertEqual((d['accion'], d['quien'], d['comando']), ('actuar', 'agente', f'oracle-factory pedir-revision {ID} --a codex'))
        # la propuesta propia no cambia el orden: primero el segundo revisor
        self.assertEqual(decidir({'segundo_revisor': 'codex', 'propuesta_de_revision': None})['accion'], 'actuar')
        self.assertEqual(decidir({'segundo_revisor': 'agy2-flash'})['comando'], f'oracle-factory pedir-revision {ID} --a agy2-flash')
        for sin in ({}, {'segundo_revisor': None}, {'segundo_revisor': ''}):
            self.assertEqual(decidir(sin)['accion'], 'pedir_a_persona')
        self.assertEqual(decidir({'segundo_revisor': None, 'propuesta_de_revision': None})['accion'], 'delegar_al_agente')

    def test_sr2_un_nombre_invalido_o_otro_paso_no_corre_nada_y_un_freno_va_primero(self):
        for malo in ('codex; rm', 'con espacio', 'a b', 5, ['codex'], '--a', ''):
            d = decidir({'segundo_revisor': malo})
            self.assertEqual(d['accion'], 'pedir_a_persona', malo)
            self.assertNotIn('pedir-revision', d.get('comando') or '')
        self.assertEqual(decidir({'segundo_revisor': 'codex'}, paso=f'oracle-factory cerrar {ID}')['accion'], 'pedir_a_persona')
        self.assertEqual(decidir({'segundo_revisor': 'codex'}, paso=f'oracle-factory juzgar {ID}')['comando'], f'oracle-factory juzgar {ID}')
        self.assertEqual(decidir({'segundo_revisor': 'codex'}, frenos=[{'id': 'cambio_grande', 'motivo': 'x'}])['accion'], 'frenar')


if __name__ == '__main__':
    unittest.main()
