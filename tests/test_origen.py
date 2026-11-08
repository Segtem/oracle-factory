"""La medición reparte los hallazgos de la primera ronda según se pudieran ver en la spec: escenarios or1–or3, con registros temporales."""
import contextlib
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools import medir_rondas  # noqa: E402

RUTAS = 'symlink escapa del proyecto'
PRUEBAS = 'un mutante sobrevive'
MIXTO = 'symlink y un mutante sobrevive'
NADA = 'otra cosa sin clase'


def hallazgo(severidad, titulo):
    return {'id': 'h', 'severity': severidad, 'title': titulo, 'explanation': 'Explicación.'}


class Origen(unittest.TestCase):
    def setUp(self):
        self._t = tempfile.TemporaryDirectory()
        self.addCleanup(self._t.cleanup)
        self.raiz = Path(self._t.name)

    def registro(self, ident, rondas, informes=True):
        """rondas: [[hallazgos de la ronda 1], …]; informes=False no escribe los informes, 'roto' los escribe con JSON inválido y cualquier otro valor se escribe tal cual como el contenido del informe."""
        carpeta = self.raiz / '.factory/cambios' / ident
        eventos = [{'accion': 'cambio_creado', 'cuando': '2026-10-25T00:00:00+00:00'}]
        for i, hallazgos in enumerate(rondas, 1):
            sha = f'c{i}{ident[-3:]}'
            eventos.append({'accion': 'revision_pedida', 'candidato': sha, 'cuando': f'2026-10-25T0{i}:00:00+00:00'})
            if informes is not False:
                informe = carpeta / 'candidatos' / sha / 'revision' / 'agy-1.json'
                informe.parent.mkdir(parents=True, exist_ok=True)
                informe.write_text('{ esto no es json' if informes == 'roto' else json.dumps({'findings': hallazgos} if informes is True else informes))
        eventos.append({'accion': 'cierre', 'cuando': '2026-10-26T00:00:00+00:00'})
        carpeta.mkdir(parents=True, exist_ok=True)
        (carpeta / 'factory.json').write_text(json.dumps({'id': ident, 'eventos': eventos}))

    def correr(self, *args):
        salida = io.StringIO()
        with contextlib.redirect_stdout(salida):
            codigo = medir_rondas.main(['--proyecto', str(self.raiz), *args])
        self.assertEqual(codigo, 0)
        return salida.getvalue()

    def foto(self):
        return {str(p.relative_to(self.raiz)): (p.read_bytes() if p.is_file() else None, p.stat().st_mtime_ns)
                for p in sorted(self.raiz.rglob('*'))}

    # --- or1: el reparto por origen ----------------------------------------------------------------------------------------
    def test_or1_un_hallazgo_por_grupo_y_cada_uno_se_cuenta_una_vez(self):
        self.registro('a', [[hallazgo('media', RUTAS), hallazgo('media', PRUEBAS), hallazgo('alta', MIXTO), hallazgo('media', NADA)]])
        origen = medir_rondas.analizar(self.raiz, origen=True)['origen']
        self.assertEqual(origen, {'atrapable al leer la spec': 1, 'solo con el código': 1, 'mixto': 1, 'sin clase': 1})
        self.assertIn('4', self.correr('--origen'))

    def test_or1_solo_cuentan_la_primera_ronda_y_los_altos_y_medios(self):
        self.registro('a', [[hallazgo('baja', RUTAS), hallazgo('informativa', PRUEBAS), hallazgo('media', RUTAS)],
                            [hallazgo('alta', RUTAS), hallazgo('alta', NADA)]])
        origen = medir_rondas.analizar(self.raiz, origen=True)['origen']
        self.assertEqual(origen, {'atrapable al leer la spec': 1, 'solo con el código': 0, 'mixto': 0, 'sin clase': 0})

    def test_or1_los_cambios_se_suman_y_cada_clase_cae_en_su_grupo(self):
        clases = {
            'atrapable al leer la spec': ['symlink escapa', 'AttributeError al leer', 'falso aviso del resumen', 'diverge del importador'],
            'solo con el código': ['mutante sobrevive', 'fuentes_estables cambia', 'docs/ promete otra cosa'],
        }
        self.registro('a', [[hallazgo('media', t) for t in clases['atrapable al leer la spec']]])
        self.registro('b', [[hallazgo('alta', t) for t in clases['solo con el código']]])
        origen = medir_rondas.analizar(self.raiz, origen=True)['origen']
        self.assertEqual((origen['atrapable al leer la spec'], origen['solo con el código'], origen['mixto'], origen['sin clase']), (4, 3, 0, 0))

    def test_or1_sin_la_opcion_la_salida_es_la_de_siempre(self):
        self.registro('a', [[hallazgo('media', RUTAS)]])
        self.assertNotIn('origen', medir_rondas.analizar(self.raiz))
        salida = self.correr()
        self.assertEqual(salida, medir_rondas.texto(medir_rondas.analizar(self.raiz)))
        self.assertNotIn('atrapable', salida)

    # --- or2: la regla y su límite a la vista ------------------------------------------------------------------------------
    def test_or2_la_salida_nombra_las_clases_de_cada_grupo_y_dice_que_es_una_aproximacion(self):
        self.registro('a', [[hallazgo('media', RUTAS)]])
        salida = self.correr('--origen')
        for clase in medir_rondas.ATRAPABLE + medir_rondas.SOLO_CODIGO:
            self.assertIn(clase, salida)
        self.assertIn('aproximación por el texto', salida)
        self.assertIn('no un juicio humano', salida)

    def test_or2_un_candidato_de_primera_ronda_sin_informe_se_dice_y_la_medicion_no_pasa_por_completa(self):
        self.registro('a', [[hallazgo('media', RUTAS)]], informes=False)
        salida = self.correr('--origen')
        self.assertIn('1 candidatos de primera ronda', salida)
        self.assertIn('1 sin informe legible', salida)
        self.assertIn('incompleta', salida)
        self.assertEqual(medir_rondas.analizar(self.raiz, origen=True)['cobertura'],
                         {'candidatos_primera_ronda': 1, 'sin_informe_legible': 1, 'informes_ilegibles': 0, 'registros_ilegibles': 0})

    def test_or2_un_informe_con_json_roto_se_cuenta_como_ilegible_y_tambien_avisa(self):
        self.registro('a', [[hallazgo('media', RUTAS)]], informes='roto')
        salida = self.correr('--origen')
        self.assertIn('1 informes ilegibles', salida)
        self.assertIn('incompleta', salida)
        self.assertEqual(medir_rondas.analizar(self.raiz, origen=True)['cobertura']['informes_ilegibles'], 1)

    def test_or2_un_informe_con_findings_que_no_es_una_lista_de_objetos_es_ilegible_y_no_rompe_la_medicion(self):
        for contenido in ({'findings': 'no es una lista'}, {'findings': [None]}, {'findings': ['x']}, {'findings': None}, {}, [], 3, None):
            with self.subTest(contenido=contenido):
                self.setUp()
                self.registro('a', [[hallazgo('media', RUTAS)]], informes=contenido)
                resultado = medir_rondas.analizar(self.raiz, origen=True)
                self.assertEqual(resultado['cobertura'], {'candidatos_primera_ronda': 1, 'sin_informe_legible': 1, 'informes_ilegibles': 1, 'registros_ilegibles': 0})
                self.assertEqual(sum(resultado['origen'].values()), 0)
                self.assertIn('incompleta', self.correr('--origen'))
                self.assertIn('1', self.correr())  # sin --origen tampoco se rompe

    def test_or2_un_hallazgo_con_severidad_o_titulo_que_no_son_texto_o_con_severidad_desconocida_hace_ilegible_el_informe(self):
        malos = ({'severity': ['media'], 'title': RUTAS}, {'severity': 7, 'title': RUTAS}, {'severity': None, 'title': RUTAS},
                 {'severity': 'critica', 'title': RUTAS}, {'title': RUTAS}, {'severity': 'media', 'title': 3}, {'severity': 'media'})
        for malo in malos:
            with self.subTest(hallazgo=malo):
                self.setUp()
                self.registro('a', [[]], informes={'findings': [malo]})
                resultado = medir_rondas.analizar(self.raiz, origen=True)
                self.assertEqual(resultado['cobertura']['informes_ilegibles'], 1)
                self.assertEqual(sum(resultado['origen'].values()), 0)
                self.assertIn('incompleta', self.correr('--origen'))
                self.correr()  # sin --origen tampoco se rompe

    def test_or2_un_registro_ilegible_o_con_eventos_malformados_se_cuenta_y_avisa_en_vez_de_desaparecer(self):
        evento = {'accion': 'revision_pedida', 'candidato': 'x', 'cuando': 'ayer'}
        creado, cierre = {'accion': 'cambio_creado', 'cuando': '2026-10-25T00:00:00+00:00'}, {'accion': 'cierre', 'cuando': '2026-10-26T00:00:00+00:00'}
        revision = {'accion': 'revision_pedida', 'candidato': 'x', 'cuando': '2026-10-25T01:00:00+00:00'}
        malos = ({'eventos': {'accion': 'cierre'}}, {'eventos': [{'accion': 'cierre'}, 'no es un evento']}, {'eventos': None}, {},
                 [], 'texto', {'eventos': [{'accion': 'cambio_creado', 'cuando': '2026-10-25T00:00:00+00:00'}, evento, {'accion': 'cierre'}]},
                 {'eventos': [creado, {**revision, 'accion': 7}, cierre]}, {'eventos': [creado, {**revision, 'accion': None}, cierre]},
                 {'eventos': [creado, {'candidato': 'x', 'cuando': revision['cuando']}, cierre]},  # sin accion
                 {'eventos': [creado, {**revision, 'candidato': 5}, cierre]}, {'eventos': [creado, {**revision, 'candidato': ['x']}, cierre]},
                 {'eventos': [creado, {k: v for k, v in revision.items() if k != 'candidato'}, cierre]},
                 {'eventos': [creado, {**revision, 'cuando': 7}, cierre]},
                 {'eventos': [{**creado, 'cuando': 7}, revision, cierre]},  # un evento cualquiera con el momento que no es texto
                 {'eventos': [creado, {**revision, 'candidato': ''}, cierre]},
                 {'eventos': [creado, {k: v for k, v in revision.items() if k != 'cuando'}, cierre]},
                 {'eventos': [creado, {**revision, 'accion': 'revision_lanzada', 'candidato': 5}, cierre]})
        for malo in malos:
            with self.subTest(registro=malo):
                self.setUp()
                self.registro('a', [[hallazgo('media', RUTAS)]])
                (self.raiz / '.factory/cambios/a/factory.json').write_text(json.dumps(malo))
                resultado = medir_rondas.analizar(self.raiz, origen=True)
                self.assertEqual(resultado['cobertura']['registros_ilegibles'], 1)
                self.assertIn('1 registros ilegibles', self.correr('--origen'))
                self.assertIn('incompleta', self.correr('--origen'))
        self.setUp()
        (self.raiz / '.factory/cambios/b').mkdir(parents=True)
        (self.raiz / '.factory/cambios/b/factory.json').write_text('{ roto')
        self.assertEqual(medir_rondas.analizar(self.raiz, origen=True)['cobertura']['registros_ilegibles'], 1)

    def test_or2_un_informe_sin_hallazgos_es_legible(self):
        self.registro('a', [[]], informes={'findings': []})
        self.assertEqual(medir_rondas.analizar(self.raiz, origen=True)['cobertura']['informes_ilegibles'], 0)
        self.assertNotIn('incompleta', self.correr('--origen'))

    def test_or2_con_todos_los_informes_legibles_la_cobertura_es_completa_y_no_avisa(self):
        self.registro('a', [[hallazgo('media', RUTAS)], [hallazgo('media', NADA)]])  # la segunda ronda no cuenta para la cobertura
        salida = self.correr('--origen')
        self.assertIn('0 sin informe legible', salida)
        self.assertIn('0 informes ilegibles', salida)
        self.assertNotIn('incompleta', salida)
        self.assertEqual(medir_rondas.analizar(self.raiz, origen=True)['cobertura'],
                         {'candidatos_primera_ronda': 1, 'sin_informe_legible': 0, 'informes_ilegibles': 0, 'registros_ilegibles': 0})

    def test_or2_los_informes_rotos_de_otra_ronda_no_ensucian_la_cobertura_de_la_primera(self):
        self.registro('a', [[hallazgo('media', RUTAS)]])
        carpeta = self.raiz / '.factory/cambios/a'
        eventos = json.loads((carpeta / 'factory.json').read_text())
        eventos['eventos'].insert(1, {'accion': 'revision_pedida', 'candidato': 'segunda', 'cuando': '2026-10-25T09:00:00+00:00'})
        (carpeta / 'factory.json').write_text(json.dumps(eventos))
        rota = carpeta / 'candidatos/segunda/revision/agy-1.json'
        rota.parent.mkdir(parents=True)
        rota.write_text('{ roto')
        self.assertEqual(medir_rondas.analizar(self.raiz, origen=True)['cobertura']['informes_ilegibles'], 0)

    def test_or2_los_dos_grupos_cubren_clases_distintas_y_existentes(self):
        self.assertFalse(set(medir_rondas.ATRAPABLE) & set(medir_rondas.SOLO_CODIGO))
        for clase in medir_rondas.ATRAPABLE + medir_rondas.SOLO_CODIGO:
            self.assertIn(clase, medir_rondas.CLASES)

    # --- or3: la muestra y la solo lectura -----------------------------------------------------------------------------------
    def test_or3_la_muestra_lista_los_mismos_n_ordenados_por_cambio_y_titulo(self):
        self.registro('b', [[hallazgo('media', f'symlink {i}') for i in (3, 1, 2)]])
        self.registro('a', [[hallazgo('media', f'symlink {i}') for i in (9, 8)]])
        primera = self.correr('--origen', '--muestra', '3')
        self.assertEqual(primera, self.correr('--origen', '--muestra', '3'))
        titulos = [linea.strip() for linea in primera.splitlines() if 'symlink' in linea and linea.lstrip().startswith('a ') or 'symlink' in linea and linea.lstrip().startswith('b ')]
        self.assertEqual(len(titulos), 3)
        self.assertTrue(titulos[0].startswith('a ') and titulos[1].startswith('a '), titulos)
        self.assertLess(titulos[0], titulos[1])
        self.assertIn('ronda 1', titulos[0])

    def test_or3_sin_muestra_no_se_lista_ningun_hallazgo_y_con_cero_tampoco(self):
        self.registro('a', [[hallazgo('media', RUTAS)]])
        self.assertNotIn(RUTAS, self.correr('--origen'))
        self.assertNotIn(RUTAS, self.correr('--origen', '--muestra', '0'))

    def test_or3_medir_con_muestra_no_modifica_ningun_archivo(self):
        self.registro('a', [[hallazgo('media', RUTAS), hallazgo('alta', PRUEBAS)]])
        antes = self.foto()
        self.correr('--origen', '--muestra', '3')
        self.assertEqual(self.foto(), antes)

    def test_or3_muestra_sin_origen_es_un_error_de_uso(self):
        with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as e:
            medir_rondas.main(['--proyecto', str(self.raiz), '--muestra', '2'])
        self.assertEqual(e.exception.code, 2)


if __name__ == '__main__':
    unittest.main()
