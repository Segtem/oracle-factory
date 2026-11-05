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

    def test_rb1_todas_las_razones_de_binario_de_clue(self):
        for razon in ('contenido no UTF-8', 'contenido binario', 'Git lo clasifica como binario'):
            self.assertEqual(preparacion.omisiones({'omissions': [{'file': PNG, 'reason': razon}]}), ([PNG], []), razon)
        self.assertEqual(preparacion.omisiones({'omissions': [{'file': 'k', 'reason': 'ruta de credenciales conocida'}]}), ([], ['k']))

    def test_rb1_la_ruta_puede_llevar_prefijo_o_comillas(self):
        for texto in (f'Abrí /tmp/co/{PNG} con Pillow.', f'Abrí ./{PNG}.', f'Abrí "{PNG}"', f'({PNG}): abierto', f'Abrí `{PNG}`.'):
            self.assertEqual(comprobacion(revisor([texto]))[1], 'cumple', texto)

    def test_rb1_otra_frase_negativa_no_anula_la_que_nombra(self):
        _, resultado = comprobacion(revisor([f'Abrí {PNG} con Pillow. No ejecuté la suite completa.']))
        self.assertEqual(resultado, 'cumple')

    def test_rb2_decir_que_no_se_abrio_no_cuenta(self):
        for texto in (f'No abrí {PNG} por falta de visor.', f'{PNG}: no pude abrirlo.', f'Sin abrir {PNG}.',
                      f'No revisé {PNG}', f'Nunca abrí {PNG}.', f'Faltó abrir {PNG}.', f'Abrí x{PNG}.', f'No inspeccioné {PNG}.', f'{PNG} quedó sin revisar.'):
            self.assertEqual(comprobacion(revisor([texto]))[1], 'no_ejecutada', texto)

    def test_rb1_material_del_candidato_pasa_las_omisiones_de_su_paquete(self):
        import json, tempfile
        from unittest import mock
        from oracle_factory import cli, estructura, flujo_revision
        with tempfile.TemporaryDirectory() as t:
            raiz, checkout = Path(t), Path(t) / 'co'
            checkout.mkdir()
            ident, sha = 'c1', 'abc1234'
            base = estructura.ruta_canonica(raiz, ident, 'evidencia', sha).parent
            (base / 'clue').mkdir(parents=True)
            (base / 'revision').mkdir()
            paquete = {'diff_sha256': 'd', 'context_sha256': 'c', 'repo': str(checkout), 'files': [],
                       'omissions': [{'file': PNG, 'reason': 'contenido binario'}, {'file': 'x.py', 'reason': 'otra'}]}
            otro = {**paquete, 'diff_sha256': 'otro', 'omissions': []}
            (base / 'clue/paquete-a-1.json').write_text(json.dumps(otro))
            (base / 'clue/paquete-b-1.json').write_text(json.dumps(paquete))
            informe = {'schema_version': preparacion.ESQUEMA_CLUE, 'head': sha, 'diff_sha256': 'd', 'context_sha256': 'c',
                       'review_status': 'incompleto', 'limitations': [], 'findings': []}
            (base / 'revision/b-1.json').write_text(json.dumps(informe))
            ok = mock.Mock(returncode=0, stdout='', stderr='')
            with mock.patch.object(cli, 'ROOT', raiz), mock.patch.object(cli, 'ejecutar', return_value=ok):
                revisores_, _, _, avisos = flujo_revision.material_del_candidato(ident, sha)
            self.assertEqual(avisos, [])
            self.assertEqual(revisores_[0]['omisiones_binarias'], [PNG])
            self.assertEqual(revisores_[0]['otras_omisiones'], ['x.py'])

    def test_rb3_el_pedido_indica_abrir_y_nombrar_binarios(self):
        texto = revisores.plantilla(Path(__file__).resolve().parent.parent / 'sin-plantilla-propia')
        self.assertIn('no es texto', texto)
        self.assertIn('limitations', texto.split('no es texto')[1])
        self.assertIn('relativa', texto)


if __name__ == '__main__':
    unittest.main()
