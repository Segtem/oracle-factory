"""Los binarios omitidos del paquete: escenarios rb1–rb3."""
from pathlib import Path
import unittest

from oracle_factory import preparacion, revisores

BASE = {'revisor': None, 'completa': None, 'archivos_revisados': None, 'comprobaciones': None, 'limites': None,
        'hallazgos': None, 'sin_hallazgos_motivo': None}
PNG, PNG2 = 'site/img/a.png', 'site/img/b.png'


def revisor(limites, estado='incompleto', binarias=(PNG,), otras=()):
    return {'ruta': 'r.json', 'validacion': 'validado', 'omisiones_binarias': list(binarias), 'otras_omisiones': list(otras),
            'datos': {'provider': {'name': 'codex', 'model': 'm'}, 'review_status': estado, 'findings': [], 'limitations': limites}}


def comprobacion(rev):
    informe, _ = preparacion.completar(BASE, {'decisiones': None}, [rev], None, [])
    return informe, informe['comprobaciones'][0]['resultado']


class Binarios(unittest.TestCase):
    def test_rb1_los_binarios_nombrados_cumplen(self):
        informe, resultado = comprobacion(revisor([f'Abrí {PNG} en el checkout con Pillow.']))
        self.assertEqual(resultado, 'cumple')
        self.assertTrue(any('binarios que el paquete no trae' in l and PNG in l for l in informe['limites']), informe['limites'])

    def test_rb1_varios_binarios_todos_nombrados(self):
        _, resultado = comprobacion(revisor([f'Abrí {PNG}.', f'Abrí {PNG2}.'], binarias=(PNG, PNG2)))
        self.assertEqual(resultado, 'cumple')

    def test_rb2_un_binario_sin_nombrar_bloquea(self):
        _, resultado = comprobacion(revisor([f'Abrí {PNG}.'], binarias=(PNG, PNG2)))
        self.assertEqual(resultado, 'no_ejecutada')

    def test_rb2_una_ruta_parecida_no_cuenta(self):
        _, resultado = comprobacion(revisor(['Abrí site/img/a.png.bak y otros.']))
        self.assertEqual(resultado, 'no_ejecutada')

    def test_rb2_otra_omision_bloquea(self):
        _, resultado = comprobacion(revisor([f'Abrí {PNG}.'], otras=['x.py']))
        self.assertEqual(resultado, 'no_ejecutada')

    def test_rb2_incompleto_sin_omisiones_bloquea(self):
        _, resultado = comprobacion(revisor(['No corrí la suite.'], binarias=()))
        self.assertEqual(resultado, 'no_ejecutada')

    def test_rb2_completo_sigue_cumpliendo(self):
        _, resultado = comprobacion(revisor(['Todo.'], estado='completo', binarias=()))
        self.assertEqual(resultado, 'cumple')

    def test_rb2_las_omisiones_del_paquete_se_separan(self):
        paquete = {'omissions': [{'file': PNG, 'reason': 'contenido no UTF-8'}, {'file': 'x.py', 'reason': 'demasiado grande'},
                                 {'reason': 'sin archivo'}]}
        self.assertEqual(preparacion.omisiones(paquete), ([PNG], ['x.py', '?']))
        self.assertEqual(preparacion.omisiones({}), ([], []))

    def test_rb3_el_pedido_indica_abrir_y_nombrar_binarios(self):
        texto = revisores.plantilla(Path(__file__).resolve().parent.parent / 'sin-plantilla-propia')
        self.assertIn('no es texto', texto)
        self.assertIn('limitations', texto.split('no es texto')[1])


if __name__ == '__main__':
    unittest.main()
