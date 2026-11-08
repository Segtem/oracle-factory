"""Conductor autopilot (decide, no actúa): escenarios ap1–ap3, con Git de verdad para el comando."""
import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import test_tests_editados as _te  # noqa: E402
from oracle_factory import autopilot  # noqa: E402

f = _te.f
ID = '20261108-000000-abc-demo'
FRENO = {'id': 'cambio_grande', 'motivo': 'el candidato agrega 900 líneas de producto: considerá partir el cambio'}


def decidir(paso, fase='requisitos_importados', frenos=(), candidato='abc1234'):
    return autopilot.decidir({'fase': fase, 'proximo_paso': paso, 'frenos': list(frenos), 'candidato': candidato})


class Reglas(unittest.TestCase):
    # --- ap1: el conductor decide el siguiente paso por reglas ---------------------------------------------------------------
    def test_ap1_una_decision_de_persona_se_le_pide_a_la_persona_con_su_comando(self):
        for sub in ('aprobar-spec', 'revisar', 'cerrar', 'abandonar', 'modo', 'autonomia', 'soltar', 'decidir-union'):
            with self.subTest(sub=sub):
                paso = f'oracle-factory {sub} {ID}'
                d = decidir(paso)
                self.assertEqual((d['accion'], d['quien'], d['comando']), ('pedir_a_persona', 'persona', paso))
                self.assertTrue(d['motivo'])
        d = decidir(f'oracle-factory medir {ID} --confirmar')
        self.assertEqual((d['accion'], d['quien'], d['comando']), ('pedir_a_persona', 'persona', f'oracle-factory medir {ID} --confirmar'))

    def test_ap1_un_comando_mecanico_lo_corre_un_agente(self):
        for sub in ('importar', 'juzgar', 'pedir-revision', 'revision-preparar', 'tomar', 'mensaje'):
            with self.subTest(sub=sub):
                paso = f'oracle-factory {sub} {ID}'
                d = decidir(paso)
                self.assertEqual((d['accion'], d['quien'], d['comando']), ('actuar', 'agente', paso))
        d = decidir(f'oracle-factory pedir-revision {ID} --a agy')
        self.assertEqual((d['accion'], d['comando']), ('actuar', f'oracle-factory pedir-revision {ID} --a agy'))

    def test_ap1_la_prosa_y_elegir_medidas_son_trabajo_del_agente_y_sin_candidato_se_construye(self):
        for paso in (f'corregí los 2 hallazgos medios o más del candidato abc1234 y commitealo; después: oracle-factory pedir-revision {ID} --a agy',
                     f'commiteá los cambios del producto; después: oracle-factory pedir-revision {ID} --a agy',
                     f'resolvé lo pendiente que lista estado; después: oracle-factory cerrar {ID}',
                     f'corregí la evidencia o el producto; después: oracle-factory juzgar {ID}'):
            with self.subTest(paso=paso):
                d = decidir(paso)
                self.assertEqual((d['accion'], d['quien'], d['comando']), ('delegar_al_agente', 'agente', None))
                self.assertEqual(d['instruccion'], paso)
        d = decidir(f'oracle-factory medir {ID} --listar')
        self.assertEqual((d['accion'], d['quien']), ('delegar_al_agente', 'agente'))
        self.assertIn('medidas', d['instruccion'])
        d = decidir(f'oracle-factory pedir-revision {ID} --a agy', candidato=None)
        self.assertEqual((d['accion'], d['quien'], d['comando']), ('delegar_al_agente', 'agente', None))
        self.assertIn('constru', d['instruccion'])
        self.assertEqual(decidir(f'oracle-factory pedir-revision {ID} --a agy', candidato='abc1234')['accion'], 'actuar')

    # --- ap2: el conductor frena -------------------------------------------------------------------------------------------
    def test_ap2_un_freno_gana_a_cualquier_otra_regla_y_no_trae_comando(self):
        for paso in (f'oracle-factory juzgar {ID}', f'oracle-factory cerrar {ID}', f'corregí algo; después: oracle-factory juzgar {ID}'):
            with self.subTest(paso=paso):
                d = decidir(paso, frenos=[FRENO])
                self.assertEqual((d['accion'], d['quien'], d['comando'], d['instruccion']), ('frenar', 'persona', None, None))
                self.assertEqual(d['frenos'], [FRENO])
                self.assertIn('cambio_grande', d['motivo'])

    def test_ap2_un_paso_desconocido_incompleto_o_con_archivos_faltantes_frena(self):
        for paso in (None, '', 3, ['x'], 'hacé lo que quieras', f'oracle-factory estado {ID}', 'oracle-factory', 'oracle-factory medir',
                     f'oracle-factory medir {ID} --otra', f'oracle-factory juzgar {ID} --con RUTA_DE_HECHOS',
                     f'oracle-factory juzgar {ID} --con RUTA_DE_LOS_HECHOS', "oracle-factory juzgar 'sin cerrar",
                     f'faltan archivos del cambio (a.json): recuperalos desde Git; después: oracle-factory estado {ID}',
                     f'faltan archivos del cambio (a.json): corregí algo; después: oracle-factory juzgar {ID}'):
            with self.subTest(paso=paso):
                d = decidir(paso)
                self.assertEqual((d['accion'], d['quien'], d['comando'], d['instruccion']), ('frenar', 'persona', None, None))
                self.assertTrue(d['motivo'])
        self.assertEqual(decidir(None, frenos=[])['frenos'], [])

    def test_ap2_un_cambio_cerrado_o_abandonado_esta_terminado(self):
        for fase in ('cerrada', 'abandonada'):
            with self.subTest(fase=fase):
                d = decidir(None, fase=fase)
                self.assertEqual((d['accion'], d['quien'], d['comando']), ('terminado', None, None))
        self.assertEqual(decidir(None, fase='cerrada', frenos=[FRENO])['accion'], 'terminado')  # un cambio ya cerrado no se frena
        self.assertEqual(decidir(None, fase='requisitos_importados')['accion'], 'frenar')  # sin paso y sin terminar: algo no se entiende

    def test_ap2_un_dato_ilegible_frena_y_no_rompe(self):
        for datos in (None, {}, {'fase': None}, {'proximo_paso': 3, 'frenos': 'x'}, {'proximo_paso': f'oracle-factory juzgar {ID}', 'frenos': [None, 3]}):
            with self.subTest(datos=datos):
                self.assertIn(autopilot.decidir(datos)['accion'], ('frenar',))


class Comando(_te.Base):
    # --- ap3: autopilot solo lee y lo muestra ------------------------------------------------------------------------------
    def decision(self, como_json):
        self.salida()
        self.assertEqual(f.comando_autopilot(self.ident, como_json), 0)
        return self.salida()

    def test_ap3_texto_y_json_dicen_lo_mismo_y_no_escriben_nada(self):
        self.preparar()
        self.candidato(lambda: (self.root / 'src/chico.py').write_text('x = 1\n'))
        carpeta, _ = f.leer(self.ident)
        registro = f.ruta_registro(carpeta).read_bytes()
        arbol = self.git('status', '--porcelain')
        texto = self.decision(False)
        datos = json.loads(self.decision(True))
        _, estado = self.estado()[0], f.datos_estado(self.ident)
        self.assertEqual(datos['accion'], autopilot.decidir(estado)['accion'])
        self.assertEqual(datos['comando'], autopilot.decidir(estado)['comando'])
        self.assertTrue({'accion', 'quien', 'comando', 'instruccion', 'motivo', 'frenos'} <= set(datos))
        self.assertIn(datos['accion'], texto)
        self.assertIn(datos['motivo'], texto)
        if datos['comando']:
            self.assertIn(datos['comando'], texto)
        self.assertEqual(f.ruta_registro(carpeta).read_bytes(), registro)  # ni el registro del cambio
        self.assertEqual(self.git('status', '--porcelain'), arbol)  # ni el árbol de trabajo

    def test_ap3_un_cambio_que_no_existe_falla_nombrandolo(self):
        self.preparar()
        with self.assertRaises(f.FactoryError) as e:
            f.comando_autopilot('20261108-000000-zzz-nada', False)
        self.assertIn('20261108-000000-zzz-nada', str(e.exception))


if __name__ == '__main__':
    unittest.main()
