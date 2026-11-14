"""El pedido le dice al revisor dónde trabajar (rv1) y una revisión incompleta dice por qué y cómo seguir (rv2)."""
import contextlib
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import test_clue_dependencia as _cd  # noqa: E402
from oracle_factory import revisores  # noqa: E402

f = _cd.f


# --- rv1: el pedido dice dónde trabajar -----------------------------------------------------------------------------------
class Pedido(unittest.TestCase):
    def test_rv1_el_pedido_nombra_el_checkout_como_lugar_de_trabajo(self):
        with tempfile.TemporaryDirectory() as tmp:
            texto = revisores.pedido(revisores.plantilla(Path(tmp)), {'checkout': '/ruta/al/checkout', 'id': 'ID'}, None)
        self.assertRegex(texto, r'(?i)trabaj[aá] en el checkout[^\n]*/ruta/al/checkout')
        self.assertIn('las pruebas', texto)
        self.assertRegex(texto, r'(?i)tu carpeta de trabajo[^\n]*(?:\n[^\n]*)?sólo tiene (?:este|el) pedido y tu salida')
        self.assertRegex(texto, r'(?i)no es el checkout')


# --- rv2: una revisión incompleta dice por qué y cómo seguir --------------------------------------------------------------
class Incompleta(_cd.ClueDependencia):
    def test_rv2_aprobar_con_un_informe_incompleto_dice_el_limite_y_el_comando(self):
        ident = self.candidato_con(('codex-1.json', 'incompleto', []))
        antes = json.loads(f.ruta_registro(f.leer(ident)[0]).read_bytes())
        salida = io.StringIO()
        with _cd._ap.clue_acepta(), patch('builtins.input', side_effect=['1', '1']), contextlib.redirect_stdout(salida), \
                contextlib.redirect_stderr(io.StringIO()), self.assertRaises(f.FactoryError) as error:
            f.revisar_paso_a_paso(ident)
        for texto in (salida.getvalue(), str(error.exception)):
            self.assertIn('Límite de codex.', texto)  # el primer límite que declaró el revisor (el informe de prueba lo trae)
            self.assertIn(f'oracle-factory pedir-revision {ident} --a codex', texto)
        despues = json.loads(f.ruta_registro(f.leer(ident)[0]).read_bytes())
        self.assertEqual([e['accion'] for e in despues['eventos'][len(antes['eventos']):]], ['revision_cancelada'])
        self.assertIsNone(despues.get('revision'))  # ninguna decisión

    def test_rv2_con_un_informe_completo_no_se_menciona(self):
        ident = self.candidato_con(('codex-1.json', 'completo', []))
        salida = io.StringIO()
        with _cd._ap.clue_acepta(), patch('builtins.input', side_effect=['1', '3']), contextlib.redirect_stdout(salida), \
                contextlib.redirect_stderr(io.StringIO()), self.assertRaises(f.FactoryError):
            f.revisar_paso_a_paso(ident)  # completa y cancela: sólo se mira el menú
        self.assertNotIn('pedir-revision', salida.getvalue())


for _nombre in dir(_cd.ClueDependencia):  # su entorno, no sus pruebas
    if _nombre.startswith('test_') and _nombre not in vars(Incompleta):
        setattr(Incompleta, _nombre, None)
del _nombre


if __name__ == '__main__':
    unittest.main()
