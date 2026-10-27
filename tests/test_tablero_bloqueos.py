"""El tablero muestra qué falta en cada cambio y distingue una explicación de un comando: escenarios tbb1–tbb3."""
import json
from pathlib import Path
import shutil
import subprocess
import unittest

SOURCE = Path(__file__).resolve().parents[1]
NODE = shutil.which('node')
JS = """
const t = require(process.argv[1] + '/editores/vscode/tablero.js');
const [pendientes, proximo, alternativas] = JSON.parse(process.argv[2]);
const metricas = {fases: [], vueltas_de_revision: 0, riesgos_aceptados: 0, hallazgos_por_severidad: {},
                  decisiones_por_actor: {persona: 0, agente: 0, sin_identificar: 0}, requisitos: {total: 0, medidos: 0}};
const c = {id: 'c1', titulo: 'Un cambio', fase: 'spec_aprobada', modo: 'confirmacion', candidato: null, metricas, pendientes,
           proximo_paso: proximo, alternativas, avisos: [], hallazgos: [], requisitos: [], commits: [], linea_de_tiempo: [], quien: null};
process.stdout.write(t.html({cambios: [c], sesion: {estado: 'sin-live-share'}, proyecto: null}, {nonce: 'n', cspSource: 'x'}));
"""


def pagina(pendientes, proximo, alternativas=()):
    if not NODE:
        raise unittest.SkipTest('hace falta node')
    r = subprocess.run([NODE, '-e', JS, '--', str(SOURCE), json.dumps([pendientes, proximo, list(alternativas)])],
                       capture_output=True, text=True, timeout=60)
    assert r.returncode == 0, r.stderr
    return r.stdout


def paso(texto, decide=False):
    comando = texto if texto.startswith('oracle-factory ') else None
    return {'texto': texto, 'comando': comando, 'decision_de_la_persona': decide}


class TableroBloqueos(unittest.TestCase):
    def test_tbb1_un_cambio_con_pendientes_los_lista_en_orden(self):
        html = pagina(['importar los requisitos', 'revisión humana aprobada', 'veredicto Oracle'], paso('oracle-factory importar c1'))
        seccion = html[html.index('<h3>Qué falta</h3>'):html.index('<h3>Hallazgos</h3>')]
        a, b, c = (seccion.index(f'<li>{x}</li>') for x in ('importar los requisitos', 'revisión humana aprobada', 'veredicto Oracle'))
        self.assertTrue(a < b < c)

    def test_tbb1_un_cambio_sin_pendientes_lo_dice(self):
        html = pagina([], paso('oracle-factory cerrar c1', True))
        self.assertIn('Nada falta', html)
        self.assertNotIn('<ul class="faltante">', html)

    def test_tbb2_una_explicacion_va_como_texto_sin_boton(self):
        texto = 'falta un revisor independiente: declaralo en .factory/config.json'
        html = pagina(['x'], paso(texto))
        bloque = html[html.index('<div class="paso'):html.index('</div>', html.index('<div class="paso'))]
        self.assertIn('QUÉ HACER', bloque)
        self.assertIn(f'<p>{texto}</p>', bloque)
        self.assertNotIn('<code>', bloque)
        self.assertNotIn('Escribir en la terminal', bloque)

    def test_tbb2_un_comando_sigue_con_su_boton(self):
        html = pagina(['x'], paso('oracle-factory importar c1'), [paso('oracle-factory mensaje c1 "hola"')])
        self.assertIn('LO QUE SIGUE', html)
        self.assertIn('TAMBIÉN', html)
        self.assertEqual(html.count('Escribir en la terminal</button>'), 2)
        self.assertIn('<code>oracle-factory importar c1</code>', html)

    def test_tbb2_la_decision_de_la_persona_se_marca_como_tuya(self):
        html = pagina(['x'], paso('oracle-factory revisar c1', True))
        self.assertIn('TE NECESITA', html)
        self.assertNotIn('QUÉ HACER', html)

    def test_tbb2_una_explicacion_alternativa_tambien_es_texto(self):
        html = pagina(['x'], paso('oracle-factory importar c1'), [paso('esperá a que termine el revisor')])
        self.assertEqual(html.count('Escribir en la terminal</button>'), 1)
        self.assertIn('<p>esperá a que termine el revisor</p>', html)

    def test_tbb3_el_texto_del_registro_se_escapa(self):
        html = pagina(['<script>alert(1)</script>'], paso('<img src=x onerror=1>'))
        self.assertNotIn('<script>alert(1)</script>', html)
        self.assertNotIn('<img src=x', html)
        self.assertIn('&lt;script&gt;alert(1)&lt;/script&gt;', html)
        self.assertIn('&lt;img src=x onerror=1&gt;', html)


if __name__ == '__main__':
    unittest.main()
