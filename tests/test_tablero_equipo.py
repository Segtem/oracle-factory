"""El tablero dice a quién necesita cada cambio y qué pasó hace poco: escenarios tbe1–tbe2."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import test_archivo as _archivo  # noqa: E402
import test_tablero as _tablero  # noqa: E402

f = _archivo.f
SOURCE = Path(__file__).resolve().parents[1]
NODE = shutil.which('node')
JS = """
const t = require(process.argv[1] + '/editores/vscode/tablero.js');
const {yo, responsable, proximo, alternativas, actividad} = JSON.parse(process.argv[2]);
const metricas = {fases: [], vueltas_de_revision: 0, riesgos_aceptados: 0, hallazgos_por_severidad: {},
                  decisiones_por_actor: {persona: 0, agente: 0, sin_identificar: 0}, requisitos: {total: 0, medidos: 0}};
const c = {id: 'c1', titulo: 'Un cambio', fase: 'spec_aprobada', modo: 'confirmacion', candidato: null, metricas, pendientes: [],
           proximo_paso: proximo, alternativas, avisos: [], hallazgos: [], requisitos: [], commits: [], linea_de_tiempo: [],
           quien: {responsable: responsable ? {persona: responsable, desde: null} : null, agentes: [], revisores_en_curso: []}};
const proyecto = {cambios: {abiertos: 1, cerrados: 0, abandonados: 0}, mediana_horas_hasta_cierre: null,
                  primera_vuelta: {proporcion: null}, hallazgos_por_revisor: {}, por_responsable: {}, sin_responsable: [], actividad};
process.stdout.write(t.html({yo, cambios: [c], sesion: {estado: 'sin-live-share'}, proyecto}, {nonce: 'n', cspSource: 'x'}));
"""
DECIDE = {'texto': 'oracle-factory revisar c1', 'comando': 'oracle-factory revisar c1', 'decision_de_la_persona': True}


def pagina(yo=None, responsable=None, proximo=DECIDE, actividad=(), alternativas=()):
    if not NODE:
        raise unittest.SkipTest('hace falta node')
    r = subprocess.run([NODE, '-e', JS, '--', str(SOURCE), json.dumps(
        {'yo': yo, 'responsable': responsable, 'proximo': proximo, 'actividad': list(actividad), 'alternativas': list(alternativas)})],
        capture_output=True, text=True, timeout=60)
    assert r.returncode == 0, r.stderr
    return r.stdout


class TableroEquipo(unittest.TestCase):
    setUp, escribe, git, salida = (_archivo.Archivo.setUp, _archivo.Archivo.escribe, _archivo.Archivo.git,
                                   _archivo.Archivo.salida)
    cambio_cerrado = _archivo.Archivo.cambio_cerrado

    def nuevo(self, sufijo):
        f.AGENTE = 'claude-code'
        try:
            return f.nuevo(f'Cambio {sufijo}', capacidad='otra', sufijo=sufijo)
        finally:
            f.AGENTE = None

    def mensajes(self, ident, cuantos):
        f.AGENTE = 'claude-code'
        try:
            for i in range(cuantos):
                f.mensaje(ident, f'{ident[-3:]}-{i}')
        finally:
            f.AGENTE = None

    # --- tbe1: a quién necesita cada cambio ------------------------------------------------------------------------
    def test_tbe1_el_json_dice_quien_sos_sin_tocar_la_configuracion_de_git(self):
        self.git('config', 'user.name', 'Brian Hollweg')
        antes = self.git('config', '--local', '--list')
        self.assertEqual(_tablero.cli_json(self.root, 'tablero', '--json')['yo'], 'Brian Hollweg')
        self.assertEqual(self.git('config', '--local', '--list'), antes)

    def test_tbe1_sin_nombre_de_git_yo_es_nulo(self):
        # Sin configuración de Git alguna (ni del usuario ni del sistema ni del repositorio): no hay nombre.
        env_home = {'HOME': self.tmp.name, 'GIT_CONFIG_NOSYSTEM': '1', 'GIT_CONFIG_GLOBAL': '/dev/null'}
        r = subprocess.run([sys.executable, '-c', 'import sys; from oracle_factory.cli import main; sys.exit(main())', 'tablero', '--json'],
                           cwd=self.root, capture_output=True, text=True, stdin=subprocess.DEVNULL,
                           env={'PATH': '/usr/bin:/bin', 'PYTHONPATH': str(SOURCE), **env_home})
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIsNone(json.loads(r.stdout)['yo'])

    def test_tbe1_un_cambio_de_otra_persona_se_rotula_con_su_nombre(self):
        html = pagina(yo='Brian Hollweg', responsable='Ana')
        self.assertIn('LA DECIDE ANA', html)
        self.assertNotIn('TE NECESITA', html)
        self.assertNotIn('paso tuya', html)

    def test_tbe1_el_cambio_mio_o_sin_responsable_sigue_te_necesita(self):
        for responsable in ('Brian Hollweg', None):
            html = pagina(yo='Brian Hollweg', responsable=responsable)
            self.assertIn('TE NECESITA', html, responsable)
            self.assertIn('paso tuya', html)
            self.assertNotIn('LA DECIDE', html)

    def test_tbe1_lo_que_no_es_una_decision_no_cambia_de_rotulo(self):
        paso = {'texto': 'oracle-factory importar c1', 'comando': 'oracle-factory importar c1', 'decision_de_la_persona': False}
        self.assertIn('LO QUE SIGUE', pagina(yo='Brian Hollweg', responsable='Ana', proximo=paso))

    def test_tbe1_una_decision_alternativa_tambien_dice_quien_la_decide(self):
        html = pagina(yo='Brian Hollweg', responsable='Ana', proximo={**DECIDE, 'decision_de_la_persona': False},
                      alternativas=[{**DECIDE, 'texto': 'oracle-factory cerrar c1', 'comando': 'oracle-factory cerrar c1'}])
        self.assertIn('LA DECIDE ANA', html)
        self.assertNotIn('TE NECESITA', html)
        self.assertNotIn('TAMBIÉN', html)

    def test_tbe1_el_nombre_del_responsable_se_escapa(self):
        html = pagina(yo='Brian Hollweg', responsable='<b>Ana</b>')
        self.assertNotIn('<b>Ana</b>', html.split('LA DECIDE')[1].split('</p>')[0])
        self.assertIn('LA DECIDE &lt;B&gt;ANA&lt;/B&gt;', html)

    # --- tbe2: qué pasó hace poco ------------------------------------------------------------------------------------
    def test_tbe2_la_actividad_trae_los_diez_eventos_mas_nuevos_primero(self):
        a, b = self.nuevo('uno'), self.nuevo('dos')
        for _ in range(6):  # intercalados: lo más nuevo está repartido entre los dos cambios
            self.mensajes(a, 1)
            self.mensajes(b, 1)
        datos = _tablero.cli_json(self.root, 'tablero', '--json')
        todos = [{**e, 'cambio': c['id']} for c in datos['cambios'] for e in c['linea_de_tiempo']]
        self.assertGreater(len(todos), 12)
        actividad = datos['proyecto']['actividad']
        self.assertEqual(len(actividad), 10)
        cuando = [e['cuando'] for e in actividad]
        self.assertEqual(cuando, sorted(cuando, reverse=True))
        self.assertEqual(cuando, sorted((e['cuando'] for e in todos), reverse=True)[:10])
        self.assertEqual(set(actividad[0]), {'cambio', 'cuando', 'accion', 'actor', 'tipo_actor'})
        self.assertEqual((actividad[0]['cambio'], actividad[0]['accion'], actividad[0]['actor']), (b, 'mensaje', 'claude-code'))
        self.assertEqual({e['cambio'] for e in actividad}, {a, b})
        self.assertEqual([e['cambio'] for e in actividad[:4]], [b, a, b, a])  # la alternancia se conserva, del más nuevo al más viejo
        resto = [{k: e[k] for k in ('cambio', 'cuando', 'accion', 'actor', 'tipo_actor')} for e in sorted(todos, key=lambda e: e['cuando'], reverse=True)[:10]]
        self.assertEqual(actividad, resto)

    def test_tbe2_un_cambio_cerrado_no_entra(self):
        cerrado = self.cambio_cerrado()
        shutil.rmtree(self.root / 'examples/notas')
        for catalogo in (self.root / 'catalogos').glob('notas.*'):
            catalogo.unlink()
        abierto = self.nuevo('abierto')
        self.mensajes(abierto, 2)
        actividad = _tablero.cli_json(self.root, 'tablero', '--json')['proyecto']['actividad']
        self.assertTrue(actividad)
        self.assertEqual({e['cambio'] for e in actividad}, {abierto})
        self.assertNotIn(cerrado, {e['cambio'] for e in actividad})

    def test_tbe2_sin_cambios_la_actividad_es_una_lista_vacia(self):
        self.assertEqual(_tablero.cli_json(self.root, 'tablero', '--json')['proyecto']['actividad'], [])

    def test_tbe2_la_pagina_muestra_la_actividad_y_escapa_el_registro(self):
        evento = {'cambio': 'c<1>', 'cuando': '2026-10-27T10:00:00+00:00', 'accion': 'mensaje', 'actor': '<i>Ana</i>', 'tipo_actor': 'persona'}
        otro = {'cambio': 'c2', 'cuando': '2026-10-27T09:00:00+00:00', 'accion': 'cierre', 'actor': 'Beto', 'tipo_actor': 'sin_identificar'}
        html = pagina(actividad=[evento, otro])
        seccion = html[html.index('<h4>Actividad reciente</h4>'):]
        self.assertNotIn('<i>Ana</i>', seccion)
        self.assertIn('&lt;i&gt;Ana&lt;/i&gt;', seccion)
        self.assertIn('Mensaje <small>c&lt;1&gt;</small>', seccion)
        self.assertIn('Cerrado <small>c2</small>', seccion)
        self.assertLess(seccion.index('Ana'), seccion.index('Beto'))
        self.assertIn('Beto</b> ⚠', seccion)

    def test_tbe2_una_accion_desconocida_se_escapa(self):
        evento = {'cambio': 'c1', 'cuando': '2026-10-27T10:00:00+00:00', 'accion': '<u>rara</u>', 'actor': 'Ana', 'tipo_actor': 'persona'}
        seccion = pagina(actividad=[evento])
        seccion = seccion[seccion.index('<h4>Actividad reciente</h4>'):]
        self.assertNotIn('<u>rara</u>', seccion)
        self.assertIn('&lt;u&gt;rara&lt;/u&gt;', seccion)

    def test_tbe2_el_orden_es_por_instante_aunque_el_huso_difiera(self):
        # 10:30+02:00 es 08:30 UTC: más viejo que 09:00 UTC, aunque como texto sea mayor. Sin zona cuenta como UTC (08:45),
        # no como la hora local de la máquina, que acá es Buenos Aires (UTC-3).
        eventos = [('c1', '2026-10-27T10:30:00+02:00'), ('c2', '2026-10-27T09:00:00+00:00'), ('c3', '2026-10-27T08:45:00'),
                   ('c4', 'no es una hora')]
        raiz = self.nuevo('huso')
        for ident, cuando in eventos:
            ruta = self.root / '.factory/cambios' / raiz / 'factory.json'
            registro = json.loads(ruta.read_text())
            registro['eventos'].append({'cuando': cuando, 'accion': 'mensaje', 'actor': ident, 'tipo_actor': 'persona', 'texto': ident})
            ruta.write_text(json.dumps(registro, indent=2))
        with patch.dict(os.environ, {'TZ': 'America/Argentina/Buenos_Aires'}):
            actividad = _tablero.cli_json(self.root, 'tablero', '--json')['proyecto']['actividad']
        self.assertEqual([e['actor'] for e in actividad if e['actor'] in ('c1', 'c2', 'c3', 'c4')], ['c2', 'c3', 'c1', 'c4'])

    def test_tbe2_sin_actividad_la_pagina_lo_dice(self):
        self.assertIn('Sin actividad.', pagina())


if __name__ == '__main__':
    unittest.main()
