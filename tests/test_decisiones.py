"""Decisiones guiadas: escenarios d1–d5 de la spec (menú en vez de frase, revisar, motivo elegido, medidas, sin terminal)."""
import contextlib
import io
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import test_autoproduccion as _ap  # noqa: E402

f = _ap.f


class Decisiones(_ap.Base):
    def setUp(self):
        super().setUp()
        # Sin Clue: los informes de prueba se usan marcados «sin validar», como en autoproducción.
        p = patch.object(f.shutil, 'which', return_value=None); p.start(); self.addCleanup(p.stop)

    cambio_medido = _ap.Autoproduccion.cambio_medido
    head = _ap.Autoproduccion.head
    carpeta = _ap.Autoproduccion.carpeta
    producir_evidencia = _ap.Autoproduccion.producir_evidencia
    cambio_cerrado = _ap._archivo.Archivo.cambio_cerrado

    def responde(self, *respuestas):
        return patch('builtins.input', side_effect=list(respuestas))

    def candidato(self, hallazgos=()):
        """Un cambio medido con evidencia y un informe de revisor en su candidato vigente."""
        self.ident = self.cambio_medido()
        self.sha = self.head()[:7]  # el candidato: el commit de producto, no el que guarda la evidencia
        carpeta = self.carpeta(self.ident)
        self.producir_evidencia(self.ident)
        (carpeta / 'revision').mkdir(parents=True)
        (carpeta / 'revision' / 'codex-1.json').write_text(json.dumps(_ap.informe_clue(self.head(), list(hallazgos))))
        (carpeta / 'clue').mkdir()
        (carpeta / 'clue' / 'paquete.json').write_text(json.dumps({
            'schema_version': 'oracle-clue.bundle/v1', 'repo': '/no/existe', 'diff_sha256': 'd' * 64, 'context_sha256': 'c' * 64,
            'files': [{'file': 'examples/notas/notas.py'}]}))
        self.git('add', '.')
        self.git('commit', '-qm', 'evidencia e informe')

    def revisar(self, *respuestas):
        salida = io.StringIO()
        with self.responde(*respuestas), contextlib.redirect_stdout(salida), contextlib.redirect_stderr(io.StringIO()):
            f.revisar_paso_a_paso(self.ident)
        return salida.getvalue()

    def registro(self):
        return f.ruta_registro(f.leer(self.ident)[0]).read_bytes()

    def revision(self):
        return f.leer(self.ident)[1]['revision']

    # --- d1: las confirmaciones son un menú ------------------------------------------------------------------------------
    def test_d1_cerrar_con_el_menu(self):
        salida = io.StringIO()
        with contextlib.redirect_stdout(salida):
            ident = self.cambio_cerrado()  # aprobar, revisar y cerrar respondiendo «1»
        self.assertEqual(f.leer(ident)[1]['fase'], 'cerrada')
        self.assertIn(f'Cerrar {ident}', salida.getvalue())
        self.assertIn('1) Cerrar el cambio', salida.getvalue())
        self.assertNotIn('Escribí', salida.getvalue())

    def test_d1_cancelar(self):
        self.ident = f.nuevo('Nota', con_ejemplo='notas')
        antes = self.registro()
        for respuesta in ('2', '', f'APROBAR ESPECIFICACION {self.ident}', '9'):  # Enter solo tampoco elige
            with self.subTest(respuesta=respuesta), self.responde(respuesta), self.assertRaises(f.FactoryError), \
                    contextlib.redirect_stdout(io.StringIO()):
                f.aprobar_spec(self.ident)
            self.assertEqual(self.registro(), antes)

    # --- d2: revisar guía la revisión de punta a punta --------------------------------------------------------------------
    def test_d2_revision_sin_hallazgos(self):
        self.candidato()
        salida = self.revisar('1', '1')  # aprobar; motivo armado
        revision = self.revision()
        self.assertEqual((revision['decision'], revision['revisor']), ('aprobar', f.actor()['actor']))
        self.assertTrue(revision['motivo'].startswith(f'Apruebo el candidato {self.sha}'))
        self.assertIn('Evidencia del candidato', salida)  # lo que se decide se muestra en texto

    def test_d2_un_hallazgo_abierto(self):
        self.candidato(['R-01'])
        salida = self.revisar('3', '1', '1')  # dejar abierto; la única decisión posible es pedir cambios
        self.assertIn('Hallazgo R-01', salida)
        self.assertNotIn('Aprobar —', salida)
        self.assertEqual(self.revision()['decision'], 'cambios')

    def test_d2_un_hallazgo_decidido(self):
        self.candidato(['R-01'])
        self.revisar('1', '1', '1', '1')  # aceptar el riesgo con su motivo armado; aprobar; motivo armado
        revision = self.revision()
        self.assertEqual((revision['decision'], revision['hallazgos_abiertos']), ('aprobar', 0))
        decisiones = json.loads((self.root / revision['decisiones']).read_text())
        self.assertEqual([(d['hallazgo_id'], d['estado']) for d in decisiones['decisiones']], [('R-01', 'riesgo_aceptado')])

    # --- d3: el motivo se elige -------------------------------------------------------------------------------------------
    def test_d3_motivo_propuesto_por_el_agente(self):
        self.candidato()
        with patch.object(f, 'AGENTE', 'claude-code'), contextlib.redirect_stdout(io.StringIO()):
            f.proponer_revision(self.ident, 'aprobar', 'Sin hallazgos; acepto el límite X.')
        salida = self.revisar('1', '1')  # aprobar; el motivo del agente (primera opción)
        self.assertIn('«Sin hallazgos; acepto el límite X.»', salida)  # el texto completo, antes de elegir
        revision = self.revision()
        self.assertEqual((revision['motivo'], revision['origen_motivo'], revision['forma']),
                         ('Sin hallazgos; acepto el límite X.', 'agente', 'confirmo'))
        self.assertNotIn('revisar', f.leer(self.ident)[1].get('propuestas') or {})

    def test_d3_motivo_escrito(self):
        self.candidato()
        self.revisar('1', '2', 'Lo miré yo.')  # aprobar; Otro (sin propuesta del agente: armado y Otro)
        self.assertEqual((self.revision()['motivo'], self.revision()['origen_motivo']), ('Lo miré yo.', 'persona'))

    # --- d4: confirmar las medidas propuestas de una vez -------------------------------------------------------------------
    def proponer_medidas(self):
        self.ident = f.nuevo('Nota', con_ejemplo='notas')
        with self.escribe('1'), contextlib.redirect_stdout(io.StringIO()):
            f.aprobar_spec(self.ident)
            f.importar(self.ident)
        rid = f.leer(self.ident)[1]['requisitos'][0]
        with patch.object(f, 'AGENTE', 'claude-code'), contextlib.redirect_stdout(io.StringIO()):
            f.medir(self.ident, requisito_id=rid, medidas=['notas.casos_ejecutados', 'notas.resultados'], quitar_sin_medir=True)
        return rid

    def test_d4_confirmar_todas(self):
        rid = self.proponer_medidas()
        salida = io.StringIO()
        with self.responde('1'), contextlib.redirect_stdout(salida):
            f.confirmar_medidas(self.ident)
        estado = f.leer(self.ident)[1]
        self.assertEqual(estado['medidas'][rid]['forma'], 'confirmo')
        self.assertFalse(estado.get('medidas_pendientes'))
        self.assertIn('Sin límite sin medir: queda cubierto', salida.getvalue())

    def test_d4_de_a_una_y_saltear(self):
        rid = self.proponer_medidas()
        with self.responde('2', '2'), contextlib.redirect_stdout(io.StringIO()):  # de a una; saltear
            f.confirmar_medidas(self.ident)
        estado = f.leer(self.ident)[1]
        self.assertIn(rid, estado['medidas_pendientes'])
        self.assertNotIn(rid, estado.get('medidas') or {})

    # --- d5: sin terminal no hay decisión de persona -------------------------------------------------------------------------
    def test_d5_entrada_por_pipe(self):
        self.candidato()
        antes = self.registro()
        with patch.object(f, 'terminal_interactiva', return_value=False), self.responde('1', '1', '1'):
            for decidir in (lambda: f.aprobar_spec(self.ident), lambda: f.revisar_paso_a_paso(self.ident),
                            lambda: f.confirmar_medidas(self.ident)):
                with self.assertRaisesRegex(f.FactoryError, 'terminal interactiva'), contextlib.redirect_stdout(io.StringIO()):
                    decidir()
        self.assertEqual(self.registro(), antes)


if __name__ == '__main__':
    unittest.main()
