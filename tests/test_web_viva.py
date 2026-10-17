"""La portada viva: escenarios de la spec en Chromium con Playwright (tests/test_web_viva.cjs) y la máquina del minijuego
(tests/test_juego.cjs). Hace falta node, Chromium y Playwright: npm install --no-save --package-lock=false playwright@1.62.1"""
from pathlib import Path
import os
import shutil
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]
NODE = shutil.which('node')
CHROMIUM = os.environ.get('CHROMIUM', '/usr/bin/chromium')
HAY = bool(NODE) and (ROOT / 'node_modules/playwright').is_dir() and Path(CHROMIUM).exists()


def correr(*args):
    r = subprocess.run([NODE, *args], cwd=ROOT, capture_output=True, text=True, timeout=300)
    return r.returncode, r.stdout + r.stderr


@unittest.skipUnless(HAY, 'hace falta node, Chromium y Playwright en node_modules')
class WebViva(unittest.TestCase):
    def escenario(self, nombre):
        codigo, salida = correr('tests/test_web_viva.cjs', nombre)
        self.assertEqual(codigo, 0, salida[-3000:])

    def test_wv1_recorrer_la_portada(self):
        self.escenario('recorrer_la_portada')

    def test_wv1_movimiento_reducido_y_pantalla_chica(self):
        self.escenario('movimiento_reducido_y_pantalla_chica')

    def test_wv2_una_partida_que_cierra_en_verde(self):
        codigo, salida = correr('tests/test_juego.cjs')  # las reglas, también sin navegador
        self.assertEqual(codigo, 0, salida)
        self.escenario('una_partida_que_cierra_en_verde')

    def test_wv2_aprobar_con_un_hallazgo_abierto_y_medidas_sin_acordar(self):
        self.escenario('aprobar_con_un_hallazgo_abierto_y_medidas_sin_acordar')

    def test_wv2_jugar_solo_con_teclado(self):
        self.escenario('jugar_solo_con_teclado')

    def test_wv3_encontrar_los_tres(self):
        self.escenario('encontrar_los_tres')

    def test_wv_el_sitio_entero_sigue_funcionando(self):
        codigo, salida = correr('tests/test_site.cjs')  # el recorrido, las guías, sin red y sin desbordes
        self.assertEqual(codigo, 0, salida[-3000:])


if __name__ == '__main__':
    unittest.main()
