"""La puerta local corre `verificar`: escenarios pv1–pv4 (la puerta se prueba con un `verificar` falso y con el de verdad)."""
from pathlib import Path
import sys
import tempfile
import unittest
from types import SimpleNamespace

SOURCE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SOURCE))
from oracle_factory import cli, puerta  # noqa: E402

PRIMERA = 'Miré 3 cambios: 1 con problemas.'
LIMPIO = lambda argv: SimpleNamespace(returncode=0, stdout='commit:abc1234\n')  # noqa: E731


def verificar_falso(falla=()):
    llamadas = []

    def correr(argv):
        llamadas.append(argv)
        if argv[0] in falla:
            return 1, (PRIMERA if argv[0] == 'verificar' else f'{argv[0]} vencido') + '\n  ✗ x: y'
        return 0, 'bien'
    correr.llamadas = llamadas
    return correr


class PuertaVerificar(unittest.TestCase):
    # --- pv1: la puerta corre verificar y lo nombra -----------------------------------------------------------------------
    def test_pv1_verificar_se_corre_junto_a_las_otras_aunque_una_falle_y_sin_el_flag_verificar(self):
        v = verificar_falso(falla=('agentes',))
        puerta.verificaciones(v)
        self.assertEqual([a[0] for a in v.llamadas], ['agentes', 'kb', 'resumen', 'verificar'])
        self.assertIn(['verificar'], v.llamadas)  # `verificar --verificar` no existe: sin el flag

    def test_pv1_un_cambio_inconsistente_se_nombra_con_su_primera_linea_y_el_comando(self):
        codigo, texto = puerta.correr(LIMPIO, [['HEAD']], verificar_falso(falla=('verificar',)))
        self.assertEqual(codigo, 0)
        self.assertIn('verificar: ' + PRIMERA, texto)
        self.assertIn('oracle-factory verificar', texto)

    def test_pv1_todo_consistente_figura_al_dia(self):
        codigo, texto = puerta.correr(LIMPIO, [['HEAD']], verificar_falso())
        self.assertEqual(codigo, 0)
        self.assertIn('agentes, kb, resumen, verificar al día', texto)

    def test_pv1_el_verificar_de_verdad_acepta_el_argumento_que_le_pasa_la_puerta(self):
        guardado = cli.ROOT, cli.CHANGES  # otras pruebas de la suite dejan su carpeta temporal en el módulo: se apunta a este proyecto
        cli.ROOT, cli.CHANGES = SOURCE, SOURCE / 'openspec' / 'changes'
        try:
            codigo, salida = cli.verificar_en_proceso(['verificar'])
        finally:
            cli.ROOT, cli.CHANGES = guardado
        self.assertIn(codigo, (0, 1))
        self.assertIn('Miré ', salida)

    # --- pv2: avisa y no bloquea --------------------------------------------------------------------------------------------
    def test_pv2_un_cambio_inconsistente_pasa_y_no_sugiere_no_verify(self):
        codigo, texto = puerta.correr(LIMPIO, [['HEAD']], verificar_falso(falla=('verificar',)))
        self.assertEqual(codigo, 0)
        self.assertIn('! vencidos, no bloquean', texto)
        self.assertNotIn('--no-verify', texto)
        self.assertNotIn('✗ verificaciones', texto)

    def test_pv2_un_secreto_sigue_bloqueando_y_el_aviso_se_muestra(self):
        ghp = 'ghp' + '_' + 'a1B2c3D4e5F6g7H8i9J0k1L2m3N4o5P6q7R8'
        con_secreto = lambda argv: SimpleNamespace(  # noqa: E731
            returncode=0, stdout=f'commit:abc1234\n\ndiff --git a/a.py b/a.py\n--- a/a.py\n+++ b/a.py\n@@ -0,0 +1,1 @@\n+x = "{ghp}"\n')
        codigo, texto = puerta.correr(con_secreto, [['HEAD']], verificar_falso(falla=('verificar',)))
        self.assertEqual(codigo, puerta.CODIGO_BLOQUEO)
        self.assertIn('✗ secretos', texto)
        self.assertIn('verificar: ' + PRIMERA, texto)

    def test_pv2_verificar_no_es_de_los_que_bloquean(self):
        self.assertEqual({n: b for n, _, b in puerta.VERIFICACIONES}['verificar'], False)

    # --- pv3: sin registro de Factory se omite ------------------------------------------------------------------------------
    def test_pv3_sin_config_json_se_omite_se_dice_y_no_se_corre(self):
        v = verificar_falso(falla=('verificar',))
        codigo, texto = puerta.correr(LIMPIO, [['HEAD']], v, existe=lambda archivo: archivo != '.factory/config.json')
        self.assertEqual(codigo, 0)
        self.assertIn('se omiten verificar', texto)
        self.assertNotIn(['verificar'], v.llamadas)

    def test_pv3_la_puerta_de_verdad_decide_por_config_json(self):
        self.assertIn(('verificar', '.factory/config.json', False), puerta.VERIFICACIONES)

    # --- pv4: la guía y el hook cuentan la política real --------------------------------------------------------------------
    def test_pv4_la_guia_nombra_verificar_dice_que_avisa_y_remite_a_ci(self):
        doc = (SOURCE / 'docs/puerta.md').read_text(encoding='utf-8')
        self.assertIn('`verificar`', doc)
        self.assertIn('docs/ci.md', doc)
        self.assertIn('sin bloquear', doc[doc.index('`verificar`'):])

    def test_pv4_el_hook_dice_que_un_cambio_inconsistente_solo_avisa(self):
        with tempfile.TemporaryDirectory() as t:
            texto = cli.instalar_pre_push(Path(t))
        self.assertIn('un cambio inconsistente', texto)
        self.assertIn('sólo avisan', texto)


if __name__ == '__main__':
    unittest.main()
