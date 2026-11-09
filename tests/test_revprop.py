"""Autopilot: la propuesta de revisión es trabajo del agente: escenarios rp1–rp2, con Git de verdad para el estado."""
import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import test_tests_editados as _te  # noqa: E402
from test_conductor import Fabrica  # noqa: E402
from oracle_factory import autopilot  # noqa: E402

f = _te.f
ID = '20261109-000000-abc-demo'
FRENO = {'id': 'cambio_grande', 'motivo': 'el candidato agrega 900 líneas'}


def propuesta(candidato='abc1234', decision='aprobar'):
    return {'decision': decision, 'candidato': candidato, 'actor': 'claude-code', 'cuando': '2026-11-09T01:00:00+00:00'}


def decidir(paso=f'oracle-factory revisar {ID}', candidato='abc1234', prop=None, frenos=()):
    return autopilot.decidir({'fase': 'requisitos_importados', 'proximo_paso': paso, 'frenos': list(frenos), 'candidato': candidato,
                              'propuesta_de_revision': prop})


class Estado(_te.Base):
    # --- rp1: estado dice la última propuesta de revisión de un agente -------------------------------------------------------
    def evento_propuesta(self, candidato, decision, actor='claude-code'):
        carpeta, estado = f.leer(self.ident)
        estado['eventos'].append({'accion': 'revision_propuesta', 'actor': actor, 'tipo_actor': 'agente', 'forma': 'propuso',
                                  'cuando': f'2026-11-09T0{len(estado["eventos"]) % 10}:00:00+00:00', 'decision': decision, 'candidato': candidato})
        f.guardar(carpeta, estado)

    def test_rp1_sin_propuesta_es_null_con_propuestas_trae_la_ultima_y_no_cambia_lo_demas(self):
        self.preparar()
        sin = f.datos_estado(self.ident)
        self.assertIn('propuesta_de_revision', sin)
        self.assertIsNone(sin['propuesta_de_revision'])
        self.evento_propuesta('aaaaaaa', 'cambios')
        self.evento_propuesta('bbbbbbb', 'aprobar', actor='codex')
        con = f.datos_estado(self.ident)
        p = con['propuesta_de_revision']
        self.assertEqual((p['decision'], p['candidato'], p['actor']), ('aprobar', 'bbbbbbb', 'codex'))
        self.assertTrue(p['cuando'])
        self.assertEqual(set(p), {'decision', 'candidato', 'actor', 'cuando'})
        for clave in ('pendientes', 'proximo_paso', 'alternativas', 'fase', 'avisos', 'frenos', 'revision', 'oracle'):
            self.assertEqual(con[clave], sin[clave], clave)  # la clave es aditiva: nada más cambia

    def test_rp1_un_registro_ilegible_no_rompe_y_da_null(self):
        for estado in (None, {}, {'eventos': None}, {'eventos': 'x'}, {'eventos': [None, 3, 'x', {'accion': 'mensaje'}, {'accion': 'revision_propuesta'}]}):
            with self.subTest(estado=estado):
                p = autopilot.ultima_propuesta(estado)
                self.assertTrue(p is None or set(p) == {'decision', 'candidato', 'actor', 'cuando'})
        self.assertIsNone(autopilot.ultima_propuesta({'eventos': [None, 3, 'x', {'accion': 'mensaje'}]}))
        self.assertEqual(autopilot.ultima_propuesta({'eventos': [{'accion': 'revision_propuesta'}]}),
                         {'decision': None, 'candidato': None, 'actor': None, 'cuando': None})


class Reglas(unittest.TestCase):
    # --- rp2: el conductor delega la propuesta antes de pedir la revisión ---------------------------------------------------------
    def test_rp2_sin_propuesta_para_el_candidato_se_delega_con_la_instruccion(self):
        for prop in (None, propuesta('fffffff'), 'x', [], {}, {'candidato': 3}, {'candidato': None}, {'candidato': ''}, 3):
            with self.subTest(prop=prop):
                d = decidir(prop=prop)
                self.assertEqual((d['accion'], d['quien'], d['comando']), ('delegar_al_agente', 'agente', None))
                for texto in ('abc1234', 'revision-preparar', ID, 'revisar', '--decision', 'persona', f'oracle-factory revisar {ID}'):
                    self.assertIn(texto, d['instruccion'])
                self.assertTrue(d['motivo'])

    def test_rp2_con_propuesta_del_candidato_vigente_se_pide_a_la_persona(self):
        for prop, candidato in ((propuesta('abc1234'), 'abc1234'), (propuesta('abc1234'), 'ABC1234567'), (propuesta('ABC1234567'), 'abc1234'),
                                (propuesta('abc1234', decision='cambios'), 'abc1234')):
            with self.subTest(prop=prop, candidato=candidato):
                paso = f'oracle-factory revisar {ID}'
                d = decidir(paso, candidato=candidato, prop=prop)
                self.assertEqual((d['accion'], d['quien'], d['comando']), ('pedir_a_persona', 'persona', paso))
        paso = f'oracle-factory --agente a revisar {ID}'  # también con las opciones globales delante
        self.assertEqual(decidir(paso, prop=None)['accion'], 'delegar_al_agente')
        self.assertEqual(decidir(paso, prop=propuesta())['accion'], 'pedir_a_persona')

    def test_rp2_sin_candidato_vigente_no_cambia_y_lo_demas_de_la_persona_tampoco(self):
        paso = f'oracle-factory revisar {ID}'
        for candidato in (None, '', 3, ['x'], {'a': 1}, True):  # sin un candidato que sea texto no hay a qué atar la propuesta
            d = decidir(paso, candidato=candidato, prop=None)
            self.assertEqual((d['accion'], d['comando']), ('pedir_a_persona', paso))
        for sub in ('cerrar', 'aprobar-spec', 'abandonar'):  # las otras decisiones no piden propuesta
            self.assertEqual(decidir(f'oracle-factory {sub} {ID}', prop=None)['accion'], 'pedir_a_persona')
        self.assertEqual(decidir(f'oracle-factory medir {ID} --confirmar', prop=None)['accion'], 'pedir_a_persona')

    def test_rp2_los_frenos_y_los_datos_ilegibles_van_primero(self):
        d = decidir(prop=None, frenos=[FRENO])
        self.assertEqual((d['accion'], d['comando'], d['instruccion']), ('frenar', None, None))
        self.assertEqual(autopilot.decidir({'proximo_paso': f'oracle-factory revisar {ID}', 'candidato': 'abc1234'})['accion'], 'frenar')  # sin frenos
        self.assertEqual(autopilot.decidir({'proximo_paso': f'oracle-factory revisar {ID}', 'candidato': 'abc1234', 'frenos': []})['accion'], 'delegar_al_agente')  # sin la clave

    def test_rp2_en_el_bucle_sin_lanzar_se_detiene_con_la_instruccion_y_con_lanzar_el_agente_la_deja(self):
        paso = f'oracle-factory revisar {ID}'
        sin = {'fase': 'x', 'proximo_paso': paso, 'frenos': [], 'candidato': 'abc1234', 'propuesta_de_revision': None}
        con = {**sin, 'propuesta_de_revision': propuesta()}
        fab = Fabrica([sin])
        r = fab.bucle()
        self.assertEqual((r['pasos'], r['decision']['accion'], r['fallo']), ([], 'delegar_al_agente', False))
        self.assertIn('--lanzar', r['motivo'])
        self.assertIn('revision-preparar', r['decision']['instruccion'])
        fab = Fabrica([sin, con])  # el agente lanzado deja su propuesta y el conductor se la pasa a la persona
        r = fab.bucle(lanzar=['claude', '-p'])
        self.assertEqual([p['accion'] for p in r['pasos']], ['delegar_al_agente'])
        self.assertEqual(len(fab.lanzadas), 1)
        self.assertIn('revision-preparar', fab.lanzadas[0][-1])
        self.assertEqual((r['decision']['accion'], r['decision']['comando']), ('pedir_a_persona', paso))


if __name__ == '__main__':
    unittest.main()
