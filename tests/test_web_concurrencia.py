"""La simulación de concurrencia: motor, escena y comprobaciones del sitio. Escenarios wc1–wc4.
Las de navegador necesitan node, Chromium y Playwright (npm install --no-save --package-lock=false playwright@1.62.1)."""
from pathlib import Path
import os
import shutil
import subprocess
import tempfile
import unittest

from tools import sitio_concurrencia

ROOT = Path(__file__).resolve().parents[1]
NODE = shutil.which('node')
CHROMIUM = os.environ.get('CHROMIUM', '/usr/bin/chromium')
HAY_NODE = bool(NODE)
HAY = HAY_NODE and (ROOT / 'node_modules/playwright').is_dir() and Path(CHROMIUM).exists()


def node(*args):
    r = subprocess.run([NODE, *args], cwd=ROOT, capture_output=True, text=True, timeout=300)
    return r.returncode, r.stdout + r.stderr


def copia(tmp: Path) -> Path:
    dest = tmp / 'repo'
    (dest / 'docs').mkdir(parents=True)
    shutil.copytree(ROOT / 'site', dest / 'site')
    shutil.copy(ROOT / 'docs' / 'colaboracion.md', dest / 'docs' / 'colaboracion.md')
    return dest


class WebConcurrencia(unittest.TestCase):
    def setUp(self):
        self._t = tempfile.TemporaryDirectory()
        self.addCleanup(self._t.cleanup)
        self.tmp = Path(self._t.name)

    def navegador(self, nombre):
        codigo, salida = node('tests/test_web_concurrencia.cjs', nombre)
        self.assertEqual(codigo, 0, salida[-3000:])

    # --- wc1: el motor sigue las reglas ----------------------------------------------------------------------------------
    @unittest.skipUnless(HAY_NODE, 'hace falta node')
    def test_wc1_el_motor_sigue_las_reglas_y_es_determinista(self):
        codigo, salida = node('tests/test_concurrencia.cjs')
        self.assertEqual(codigo, 0, salida[-3000:])

    @unittest.skipUnless(HAY, 'hace falta node, Chromium y Playwright')
    def test_wc1_la_escena_muestra_que_el_agente_no_cierra(self):
        self.navegador('agente_no_cierra')

    # --- wc2: los escenarios ------------------------------------------------------------------------------------------------
    @unittest.skipUnless(HAY, 'hace falta node, Chromium y Playwright')
    def test_wc2_cada_escenario_llega_al_final_y_el_conflicto_lo_resuelve_una_persona(self):
        self.navegador('recorrer_cada_escenario')

    # --- wc3: controles y accesibilidad ---------------------------------------------------------------------------------------
    @unittest.skipUnless(HAY, 'hace falta node, Chromium y Playwright')
    def test_wc3_se_usa_con_teclado(self):
        self.navegador('usar_con_teclado')

    @unittest.skipUnless(HAY, 'hace falta node, Chromium y Playwright')
    def test_wc3_movimiento_reducido_y_pantalla_chica(self):
        self.navegador('movimiento_reducido_y_pantalla_chica')

    # --- wc4: dice que es una simulación y no inventa nada -----------------------------------------------------------------------
    def test_wc4_el_repositorio_cumple(self):
        self.assertEqual(sitio_concurrencia.problemas(ROOT), [])

    def test_wc4_una_cita_que_no_esta_en_la_guia_falla_nombrando_la_regla(self):
        dest = copia(self.tmp)
        guia = dest / 'docs' / 'colaboracion.md'
        guia.write_text(guia.read_text(encoding='utf-8').replace('no lo elige Factory', 'lo elige Factory'), encoding='utf-8')
        ps = sitio_concurrencia.problemas(dest)
        self.assertTrue(any('«distinto»' in p for p in ps), ps)

    def test_wc4_un_comando_inexistente_falla(self):
        dest = copia(self.tmp)
        js = dest / 'site' / 'concurrencia.js'
        js.write_text(js.read_text(encoding='utf-8').replace('oracle-factory decidir-union', 'oracle-factory decidir-todo'), encoding='utf-8')
        self.assertTrue(any('decidir-todo' in p for p in sitio_concurrencia.problemas(dest)))

    def test_wc4_sin_rotulo_o_sin_enlaces_falla(self):
        dest = copia(self.tmp)
        pag = dest / 'site' / 'concurrencia.html'
        pag.write_text(pag.read_text(encoding='utf-8').replace('Es una simulación', 'Es un juego'), encoding='utf-8')
        self.assertTrue(any('simulación' in p for p in sitio_concurrencia.problemas(dest)))
        dest = copia(self.tmp / 'otra')
        for origen in ('index.html', 'colaboracion.html'):
            p = dest / 'site' / origen
            p.write_text(p.read_text(encoding='utf-8').replace('./concurrencia.html', './nada.html'), encoding='utf-8')
        ps = sitio_concurrencia.problemas(dest)
        self.assertTrue(any('index.html' in p for p in ps) and any('colaboracion.html' in p for p in ps), ps)
        pag = dest / 'site' / 'concurrencia.html'
        pag.write_text(pag.read_text(encoding='utf-8').replace('./colaboracion.html', './x.html'), encoding='utf-8')
        self.assertTrue(any('guía en equipo' in p for p in sitio_concurrencia.problemas(dest)))


if __name__ == '__main__':
    unittest.main()
