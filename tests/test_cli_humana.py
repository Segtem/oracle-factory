"""La CLI cómoda para la persona: escenarios c1–c5 de la spec (errores, entorno, resumen, próximo paso, sin ejecución sola)."""
import contextlib
import hashlib
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import test_autoproduccion as _ap  # noqa: E402

f = _ap.f
RAIZ = Path(__file__).resolve().parents[1]


class Terminal(io.StringIO):
    """Una salida capturada que se declara terminal, como la de una persona."""
    def isatty(self):
        return True


class CliHumana(_ap.Base):
    def setUp(self):
        super().setUp()
        p = patch.object(f.shutil, 'which', return_value=None); p.start(); self.addCleanup(p.stop)

    cambio_medido = _ap.Autoproduccion.cambio_medido
    head = _ap.Autoproduccion.head
    carpeta = _ap.Autoproduccion.carpeta
    producir_evidencia = _ap.Autoproduccion.producir_evidencia

    def errores(self, accion):
        salida, errores = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(salida), contextlib.redirect_stderr(errores):
            resultado = accion()
        return resultado, salida.getvalue(), errores.getvalue()

    def listo_para_cerrar(self):
        """Un cambio con revisión aprobada y Oracle en verde, como en el recorrido del ejemplo."""
        ident = self.cambio_medido()
        informe = self.root / 'tareas' / ident / 'revision.md'
        informe.write_text('Fixture de revisión; no es una revisión real.\n')
        hechos = self.root / 'tareas' / ident / 'hechos.json'
        subprocess.run([sys.executable, 'examples/notas/sensor.py', '--salida', hechos], cwd=self.root, check=True, capture_output=True)
        with self.escribe('1'), contextlib.redirect_stdout(io.StringIO()):
            f.revisar(ident, informe, 'Persona fixture', 'aprobar', 0)
            f.juzgar(ident, hechos)
        return ident

    # --- c1: los errores dicen qué pasó y cómo seguir --------------------------------------------------------------------
    def test_c1_aprobar_con_una_comprobacion_que_falla(self):
        ident = self.cambio_medido()
        self.producir_evidencia(ident)
        self.git('add', '.')
        self.git('commit', '-qm', 'evidencia')
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            ruta_informe, ruta_decisiones = f.preparar_revision(ident)
        informe = json.loads(ruta_informe.read_text())
        informe['comprobaciones'][0]['resultado'] = 'falla'
        informe.update(revisor='Persona fixture', completa=True, archivos_revisados=['examples/notas/notas.py'],
                       sin_hallazgos_motivo='fixture')
        ruta_informe.write_text(json.dumps(informe))
        decisiones = json.loads(ruta_decisiones.read_text())
        decisiones.update(informe_sha256=hashlib.sha256(ruta_informe.read_bytes()).hexdigest(), actor='Persona fixture',
                          motivo='fixture', decisiones=[])
        ruta_decisiones.write_text(json.dumps(decisiones))
        with self.escribe('1'), self.assertRaises(f.FactoryError) as error, contextlib.redirect_stdout(io.StringIO()):
            f.revisar_guiado(ident, ruta_informe, ruta_decisiones, 'Persona fixture', 'aprobar')
        self.assertIn('comprobación en falla: ' + informe['comprobaciones'][0]['descripcion'], str(error.exception))

    def test_c1_preparar_sin_candidato_avisa(self):
        ident = self.cambio_medido()  # sin evidencia ni informes: no hay carpeta de candidato
        _, _, errores = self.errores(lambda: f.preparar_revision(ident))
        self.assertIn('no hay candidato vigente', errores)
        self.assertIn(f'pedir-revision {ident}', errores)

    def test_c1_falta_oracle(self):
        ident = self.cambio_medido()
        falta = ModuleNotFoundError("No module named 'oracle_metalenguaje'", name='oracle_metalenguaje')
        with patch.object(f, 'medir', side_effect=falta):
            codigo, _, errores = self.errores(lambda: f.main(['--proyecto', str(self.root), 'medir', ident, '--listar']))
        self.assertEqual(codigo, 1)
        self.assertIn('falta oracle-metalenguaje', errores)
        self.assertNotIn('Traceback', errores)

    # --- c2: fabrica.py usa el entorno del proyecto ------------------------------------------------------------------------
    def test_c2_python_del_sistema(self):
        venv_real = Path(sys.prefix)  # el entorno con las dependencias con que corren estas pruebas
        if venv_real == Path(sys.base_prefix):
            self.skipTest('las pruebas no corren dentro de un venv')
        with tempfile.TemporaryDirectory() as tmp:
            clon = Path(tmp)
            shutil.copy(RAIZ / 'fabrica.py', clon / 'fabrica.py')
            (clon / '.venv').symlink_to(venv_real)  # su bin/python es, como en un venv real, un enlace al binario de base
            base = Path(sys.executable).resolve()  # el mismo binario, fuera del venv: sin oracle-metalenguaje
            entorno = {k: v for k, v in os.environ.items() if k not in ('VIRTUAL_ENV', 'PYTHONPATH', 'FACTORY_REEJECUTADO')}
            ident = self.cambio_medido()
            p = subprocess.run([str(base), '-s', str(clon / 'fabrica.py'), '--proyecto', str(self.root), 'estado', ident],
                               capture_output=True, text=True, timeout=60, env=entorno)
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertIn(f'Próximo paso: oracle-factory pedir-revision {ident}', p.stdout)  # el comando entero, con sus argumentos

    # --- c3: el resumen se ve con formato ------------------------------------------------------------------------------------
    def test_c3_sin_glow(self):
        self.cambio_medido()
        _, salida, _ = self.errores(lambda: f.comando_resumen(False, None, ver=True))
        self.assertEqual(salida, (self.root / '.factory/resumen.md').read_text())

    def test_c3_con_glow(self):
        self.cambio_medido()
        with patch.object(f.shutil, 'which', return_value='/usr/bin/glow'), patch.object(f.sys.stdout, 'isatty', return_value=True), \
                patch.object(f.subprocess, 'run') as run:
            f.comando_resumen(False, None, ver=True)
        run.assert_called_once_with(['glow', '-p', str(self.root / '.factory/resumen.md')], check=False)

    # --- c4: estado calcula y ofrece el próximo paso ---------------------------------------------------------------------------
    def test_c4_listo_para_cerrar(self):
        ident = self.listo_para_cerrar()
        self.assertEqual(f.proximo_paso(ident), f'oracle-factory cerrar {ident}')
        with self.escribe('1'), contextlib.redirect_stdout(Terminal()), contextlib.redirect_stderr(io.StringIO()):
            codigo = f.ofrecer_siguiente(ident)  # ejecutar el paso, que abre el menú de cierre: los dos con «1»
        self.assertEqual(codigo, 0)
        self.assertEqual(f.leer(ident)[1]['fase'], 'cerrada')

    def test_c4_medidas_propuestas(self):
        ident = f.nuevo('Nota', con_ejemplo='notas')
        with self.escribe('1'), contextlib.redirect_stdout(io.StringIO()):
            f.aprobar_spec(ident)
            f.importar(ident)
        rid = f.leer(ident)[1]['requisitos'][0]
        with patch.object(f, 'AGENTE', 'claude-code'), contextlib.redirect_stdout(io.StringIO()):
            f.medir(ident, requisito_id=rid, medidas=['notas.casos_ejecutados', 'notas.resultados'], quitar_sin_medir=True)
        self.assertEqual(f.proximo_paso(ident), f'oracle-factory medir {ident} --confirmar')

    def test_c4_candidato_sin_material(self):
        ident = self.cambio_medido()
        (self.carpeta(ident) / 'clue').mkdir(parents=True)  # un pedir-revision que falló: carpeta sin informes ni evidencia
        self.assertIsNotNone(f.candidato_vigente(ident))
        self.assertTrue(f.proximo_paso(ident).startswith(f'oracle-factory pedir-revision {ident}'))

    def test_c4_oracle_rojo_sin_cambios(self):
        ident = self.listo_para_cerrar()
        carpeta, estado = f.leer(ident)
        estado['fase'] = 'oracle_rojo'
        f.guardar(carpeta, estado)
        self.assertEqual(f.proximo_paso(ident), f'corregí la evidencia o el producto; después: oracle-factory juzgar {ident}')
        with patch('builtins.input', side_effect=AssertionError('no debía ofrecer un paso que no es un comando')), \
                contextlib.redirect_stdout(Terminal()):
            self.assertEqual(f.ofrecer_siguiente(ident), 0)

    def test_c4_recorrido_completo(self):
        """El paso calculado en cada punto del flujo, de la spec al cierre."""
        paso = lambda: f.proximo_paso(ident)  # noqa: E731
        ident = f.nuevo('Nota', con_ejemplo='notas')
        self.assertEqual(paso(), f'oracle-factory aprobar-spec {ident}')
        with self.escribe('1'), contextlib.redirect_stdout(io.StringIO()):
            f.aprobar_spec(ident)
        self.assertEqual(paso(), f'oracle-factory importar {ident}')
        with contextlib.redirect_stdout(io.StringIO()):
            f.importar(ident)
        self.assertEqual(paso(), f'oracle-factory medir {ident} --listar')
        rid = f.leer(ident)[1]['requisitos'][0]
        with contextlib.redirect_stdout(io.StringIO()):
            f.medir(ident, requisito_id=rid, medidas=['notas.casos_ejecutados', 'notas.resultados'], quitar_sin_medir=True)
        self.git('add', '.')
        self.git('commit', '-qm', 'producto')
        sha = self.head()[:7]
        self.assertTrue(paso().startswith(f'oracle-factory pedir-revision {ident} --a '))
        self.producir_evidencia(ident)
        self.assertTrue(paso().startswith(f'oracle-factory pedir-revision {ident} --a '))  # la evidencia sola no alcanza
        carpeta = self.carpeta(ident, sha)
        (carpeta / 'revision').mkdir(parents=True)
        (carpeta / 'revision' / 'codex-1.json').write_text(json.dumps(_ap.informe_clue(self.head(), [])))
        (carpeta / 'clue').mkdir()
        (carpeta / 'clue' / 'paquete.json').write_text(json.dumps({
            'schema_version': 'oracle-clue.bundle/v1', 'repo': '/no/existe', 'diff_sha256': 'd' * 64, 'context_sha256': 'c' * 64,
            'files': [{'file': 'examples/notas/notas.py'}]}))
        self.assertEqual(paso(), f'oracle-factory revisar {ident}')
        with patch('builtins.input', side_effect=['1', '2', '1']), contextlib.redirect_stdout(io.StringIO()), \
                contextlib.redirect_stderr(io.StringIO()):
            f.revisar_paso_a_paso(ident)  # completa; pedir cambios; motivo armado
        self.assertEqual(paso(), f'corregí lo que pidió la revisión y commitealo; después: oracle-factory pedir-revision {ident}')
        with patch('builtins.input', side_effect=['1', '1', '1']), contextlib.redirect_stdout(io.StringIO()), \
                contextlib.redirect_stderr(io.StringIO()):
            f.revisar_paso_a_paso(ident)  # completa; aprobar; motivo armado
        self.assertEqual(paso(), f'oracle-factory juzgar {ident}')  # los hechos están en el candidato
        with contextlib.redirect_stdout(io.StringIO()):
            f.juzgar(ident, f.hechos_del_candidato(ident))
        self.assertEqual(paso(), f'oracle-factory cerrar {ident}')

    def test_c4_salir_no_ejecuta(self):
        ident = self.listo_para_cerrar()
        with self.escribe('2'), patch.object(f, 'main', side_effect=AssertionError('no debía ejecutar')), \
                contextlib.redirect_stdout(Terminal()):
            self.assertEqual(f.ofrecer_siguiente(ident), 0)
        self.assertNotEqual(f.leer(ident)[1]['fase'], 'cerrada')

    # --- c5: el próximo paso no se ejecuta solo ------------------------------------------------------------------------------
    def test_c5_agente_sin_terminal_o_salida_redirigida(self):
        ident = self.listo_para_cerrar()
        nunca = patch('builtins.input', side_effect=AssertionError('no debía preguntar'))
        for nombre, argv, contexto, salida in (
                ('agente', ['--agente', 'x'], contextlib.nullcontext(), Terminal()),
                ('sin terminal', [], patch.object(f, 'terminal_interactiva', return_value=False), Terminal()),
                ('salida redirigida', [], contextlib.nullcontext(), io.StringIO())):
            with self.subTest(nombre), contexto, nunca, contextlib.redirect_stdout(salida):
                self.assertEqual(f.main([*argv, '--proyecto', str(self.root), 'estado', ident]), 0)
            self.assertIn(f'Próximo paso: oracle-factory cerrar {ident}', salida.getvalue())  # se imprime, no se ejecuta
        self.assertNotEqual(f.leer(ident)[1]['fase'], 'cerrada')


if __name__ == '__main__':
    unittest.main()
