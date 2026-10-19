"""Las guías con la fábrica viva: escenarios wg1–wg2 en Chromium con Playwright (tests/test_web_guias.cjs).
Hace falta node, Chromium y Playwright: npm install --no-save --package-lock=false playwright@1.62.1"""
from pathlib import Path
import os
import shutil
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]
NODE = shutil.which('node')
HAY = bool(NODE) and (ROOT / 'node_modules/playwright').is_dir() and Path(os.environ.get('CHROMIUM', '/usr/bin/chromium')).exists()


@unittest.skipUnless(HAY, 'hace falta node, Chromium y Playwright en node_modules')
class WebGuias(unittest.TestCase):
    def escenario(self, nombre):
        r = subprocess.run([NODE, 'tests/test_web_guias.cjs', nombre], cwd=ROOT, capture_output=True, text=True, timeout=300)
        self.assertEqual(r.returncode, 0, (r.stdout + r.stderr)[-3000:])

    def test_wg1_recorrer_cada_guia(self):
        self.escenario('recorrer_cada_guia')

    def test_wg1_movimiento_reducido_y_pantalla_chica(self):
        self.escenario('movimiento_reducido_y_pantalla_chica')

    def test_wg2_comparar_con_la_version_anterior(self):
        self.escenario('comparar_con_la_version_anterior')


if __name__ == '__main__':
    unittest.main()
