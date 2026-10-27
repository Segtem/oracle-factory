"""El tablero dice quién hace cada pendiente y cuándo no te toca nada: escenarios tbq1–tbq2."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import test_archivo as _archivo  # noqa: E402
import test_tablero as _tablero  # noqa: E402
from oracle_factory import tablero  # noqa: E402

f = _archivo.f
SOURCE = Path(__file__).resolve().parents[1]
NODE = shutil.which('node')
JS = """
const t = require(process.argv[1] + '/editores/vscode/tablero.js');
const {faltan, pendientes, proximo, responsable, yo} = JSON.parse(process.argv[2]);
const metricas = {fases: [], vueltas_de_revision: 0, riesgos_aceptados: 0, hallazgos_por_severidad: {},
                  decisiones_por_actor: {persona: 0, agente: 0, sin_identificar: 0}, requisitos: {total: 0, medidos: 0}};
const c = {id: 'c1', titulo: 'Un cambio', fase: 'spec_aprobada', modo: 'confirmacion', candidato: null, metricas, pendientes,
           proximo_paso: proximo, alternativas: [], avisos: [], hallazgos: [], requisitos: [], commits: [], linea_de_tiempo: [],
           quien: {responsable: responsable ? {persona: responsable, desde: null} : null, agentes: [], revisores_en_curso: []}};
if (faltan) c.faltan = faltan;
process.stdout.write(t.html({yo, cambios: [c], sesion: {estado: 'sin-live-share'}, proyecto: null}, {nonce: 'n', cspSource: 'x'}));
"""


def paso(texto, humano=None, decide=False):
    comando = texto if texto.startswith('oracle-factory ') else None
    return {'texto': texto, 'comando': comando, 'decision_de_la_persona': decide, 'humano': humano or texto}


AGENTE = paso('oracle-factory importar c1', 'Importar los requisitos de la spec')
PERSONA = paso('oracle-factory revisar c1', 'Revisar el cambio y decidir', True)


def pagina(faltan=None, pendientes=(), proximo=AGENTE, responsable=None, yo='Brian Hollweg'):
    if not NODE:
        raise unittest.SkipTest('hace falta node')
    r = subprocess.run([NODE, '-e', JS, '--', str(SOURCE), json.dumps(
        {'faltan': faltan, 'pendientes': list(pendientes), 'proximo': proximo, 'responsable': responsable, 'yo': yo})],
        capture_output=True, text=True, timeout=60)
    assert r.returncode == 0, r.stderr
    return r.stdout


def seccion(html):
    return html[html.index('<h3>Qué falta</h3>'):html.index('<h3>Hallazgos</h3>')]


class TableroQuienHace(unittest.TestCase):
    setUp, escribe, git, salida = (_archivo.Archivo.setUp, _archivo.Archivo.escribe, _archivo.Archivo.git,
                                   _archivo.Archivo.salida)

    def cambio_aprobado(self):
        """El ejemplo de notas con la spec aprobada por una persona y nada más."""
        ident = f.nuevo('Nota abierta', con_ejemplo='notas')
        with self.escribe('1'):
            f.aprobar_spec(ident)
        return ident

    # --- tbq1: cada pendiente dice quién lo hace ------------------------------------------------------------------
    def test_tbq1_un_cambio_recien_aprobado_dice_quien_hace_cada_cosa(self):
        self.cambio_aprobado()
        [cambio] = _tablero.cli_json(self.root, 'tablero', '--json')['cambios']
        self.assertEqual([x['texto'] for x in cambio['faltan']], cambio['pendientes'])
        self.assertEqual([(x['humano'], x['quien']) for x in cambio['faltan']],
                         [('Importar los requisitos de la spec', 'agente'),
                          ('Revisar el cambio y decidir si se aprueba', 'persona'),
                          ('Correr Oracle sobre la evidencia', 'agente')])

    def test_tbq1_una_propuesta_de_medidas_sin_confirmar_es_de_una_persona(self):
        ident = self.cambio_aprobado()
        f.importar(ident)
        rid = f.leer(ident)[1]['requisitos'][0]
        f.AGENTE = 'claude-code'
        try:
            f.medir(ident, requisito_id=rid, medidas=['notas.casos_ejecutados', 'notas.resultados'])
        finally:
            f.AGENTE = None
        [cambio] = _tablero.cli_json(self.root, 'tablero', '--json')['cambios']
        propuestas = [x for x in cambio['faltan'] if 'sin confirmar' in x['texto']]
        self.assertEqual([(x['humano'], x['quien']) for x in propuestas],
                         [('Confirmar las medidas que propuso un agente', 'persona')])

    def test_tbq1_cada_patron_clasifica_su_pendiente(self):
        casos = {
            'aprobación humana de spec': ('Aprobar la propuesta y la spec', 'persona'),
            'aceptación de spec': ('Aceptar la spec', 'agente'),
            'importación OpenSpec → requisitos Oracle': ('Importar los requisitos de la spec', 'agente'),
            'revisión humana aprobada y sin hallazgos abiertos': ('Revisar el cambio y decidir si se aprueba', 'persona'),
            'revisión aprobada y sin hallazgos abiertos': ('Aprobar la revisión', 'agente'),
            'veredicto Oracle exitoso con evidencia': ('Correr Oracle sobre la evidencia', 'agente'),
            'medidas de r1 propuestas por claude-code, sin confirmar por una persona':
                ('Confirmar las medidas que propuso un agente', 'persona'),
            'medidas de r1 elegidas por el agente x; en modo confirmacion las decide una persona':
                ('Elegir las medidas (las decide una persona)', 'persona'),
            'la decisión de revisión propuesta por claude-code, sin confirmar por una persona':
                ('Confirmar lo que propuso un agente', 'persona'),
        }
        for texto, (humano, quien) in casos.items():
            self.assertEqual(tablero._faltan([texto]), [{'texto': texto, 'humano': humano, 'quien': quien}], texto)

    def test_tbq1_un_pendiente_desconocido_queda_con_su_texto_y_sin_responsable(self):
        self.assertEqual(tablero._faltan(['algo que nadie clasificó']),
                         [{'texto': 'algo que nadie clasificó', 'humano': 'algo que nadie clasificó', 'quien': None}])
        html = pagina([{'texto': 'algo raro', 'humano': 'algo raro', 'quien': None}])
        self.assertIn('<li>algo raro</li>', html)
        self.assertNotIn('tuyo', seccion(html))
        self.assertNotIn('de un agente</span>', seccion(html))

    def test_tbq1_la_pagina_marca_lo_tuyo_y_lo_del_agente_y_escapa(self):
        html = pagina([{'texto': 'a', 'humano': 'Importar <b>x</b>', 'quien': 'agente'},
                       {'texto': 'b', 'humano': 'Revisar', 'quien': 'persona'}])
        s = seccion(html)
        self.assertIn('<li>Importar &lt;b&gt;x&lt;/b&gt; <span class="quien-agente">de un agente</span></li>', s)
        self.assertIn('<li>Revisar <span class="quien-tuyo">tuyo</span></li>', s)
        self.assertNotIn('<b>x</b>', s)

    def test_tbq1_sin_faltan_la_pagina_cae_a_los_pendientes(self):
        s = seccion(pagina(None, pendientes=['uno', 'dos <i>']))
        self.assertIn('<li>uno</li>', s)
        self.assertIn('<li>dos &lt;i&gt;</li>', s)

    def test_tbq1_sin_pendientes_la_pagina_lo_dice(self):
        self.assertIn('Nada falta', seccion(pagina([])))

    def test_tbq1_cada_paso_trae_su_frase(self):
        frases = {'oracle-factory importar c1': 'Importar los requisitos de la spec',
                  'oracle-factory pedir-revision c1 --a agy': 'Pedir la revisión independiente',
                  'oracle-factory revision-preparar c1': 'Preparar el informe de la revisión',
                  'oracle-factory juzgar c1': 'Correr Oracle sobre la evidencia',
                  'oracle-factory medir c1 --confirmar': 'Confirmar las medidas',
                  'oracle-factory medir c1 --listar': 'Ver qué medidas elegir',
                  'oracle-factory aprobar-spec c1': 'Aprobar la propuesta y la spec',
                  'oracle-factory cerrar c1': 'Cerrar el cambio',
                  'oracle-factory mensaje c1 "hola"': 'oracle-factory mensaje c1 "hola"',
                  'corregí los hallazgos y commitealo': 'corregí los hallazgos y commitealo'}
        for texto, humano in frases.items():
            self.assertEqual(tablero._paso(texto)['humano'], humano, texto)

    # --- tbq2: ahora no te toca nada ---------------------------------------------------------------------------------
    def test_tbq2_si_lo_que_sigue_lo_hace_un_agente_dice_que_no_te_toca_nada(self):
        for responsable in (None, 'Brian Hollweg'):
            s = seccion(pagina([], proximo=AGENTE, responsable=responsable))
            self.assertIn('Ahora no te toca nada: sigue Importar los requisitos de la spec (lo hace un agente).', s, responsable)
            self.assertLess(s.index('Ahora no te toca nada'), s.index('Nada falta'))

    def test_tbq2_si_es_una_decision_tuya_o_una_explicacion_no_aparece(self):
        for proximo in (PERSONA, paso('falta un revisor independiente: declaralo en .factory/config.json'), None):
            self.assertNotIn('Ahora no te toca nada', pagina([], proximo=proximo))

    def test_tbq2_si_el_cambio_lo_tiene_otra_persona_no_aparece(self):
        self.assertNotIn('Ahora no te toca nada', pagina([], proximo=AGENTE, responsable='Ana'))

    def test_tbq2_la_frase_del_paso_se_escapa(self):
        html = pagina([], proximo=paso('oracle-factory importar c1', 'Importar <img src=x>'))
        self.assertIn('sigue Importar &lt;img src=x&gt; (lo hace', html)
        self.assertNotIn('<img src=x>', html)


if __name__ == '__main__':
    unittest.main()
