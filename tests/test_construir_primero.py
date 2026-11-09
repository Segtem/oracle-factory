"""Autopilot: ante medir --listar el conductor manda construir antes de elegir medidas: escenario cp1."""
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from test_autopilot import FRENO, ID, decidir  # noqa: E402


class Conductor(unittest.TestCase):
    def test_cp1_la_instruccion_manda_construir_y_despues_proponer_las_medidas_y_dice_que_confirma_una_persona(self):
        d = decidir(f'oracle-factory medir {ID} --listar')
        self.assertEqual((d['accion'], d['quien'], d['comando']), ('delegar_al_agente', 'agente', None))
        self.assertEqual(d['motivo'], 'elegir medidas es trabajo del agente; confirmarlas es de una persona')
        texto = d['instruccion']
        orden = ['construí primero', 'pruebas', 'catálogos', 'antes que el código', 'evidencia del candidato y los catálogos', 'después elegí las medidas de cada requisito',
                 'oracle-factory medir ... --requisito R --medida M', 'proponelas', 'confirmarlas es de una persona']
        posiciones = [texto.find(x) for x in orden]
        self.assertNotIn(-1, posiciones, texto)
        self.assertEqual(posiciones, sorted(posiciones), texto)

    def test_cp1_el_resto_de_las_decisiones_no_cambia(self):
        confirmar = decidir(f'oracle-factory medir {ID} --confirmar')
        self.assertEqual((confirmar['accion'], confirmar['quien']), ('pedir_a_persona', 'persona'))
        self.assertEqual(decidir(f'oracle-factory medir {ID} --listar', frenos=[FRENO])['accion'], 'frenar')
        self.assertEqual(decidir(f'oracle-factory importar {ID}')['accion'], 'actuar')


if __name__ == '__main__':
    unittest.main()
