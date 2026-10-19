"""Lo que la prueba del ajedrez dejó a la vista: escenarios hg1–hg3, en repositorios temporales con revisores de prueba."""
import contextlib
import io
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import tempfile
import time
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import test_vueltas as _vueltas  # noqa: E402

f = _vueltas.f
PYTHON_CLI = [sys.executable, '-c', 'import sys; from oracle_factory.cli import main; sys.exit(main())']
SOURCE = Path(__file__).resolve().parents[1]


def entorno():
    return {**os.environ, 'PYTHONPATH': str(SOURCE)}


class Higiene(_vueltas.Base):
    preparar, candidato_nuevo = _vueltas.Vueltas.preparar, _vueltas.Vueltas.candidato_nuevo
    pedir = _vueltas.Vueltas.pedir

    def eventos(self):
        return f.leer(self.ident)[1]['eventos']

    def avisos(self, texto):
        return [a for a in f.datos_estado(self.ident)['avisos'] if texto in a]

    def estado_texto(self):
        salida = io.StringIO()
        with contextlib.redirect_stdout(salida), contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(f.main(['--proyecto', str(self.root), 'estado', self.ident]), 0)
        return salida.getvalue()

    def revisor(self, nombre, comando):
        config = json.loads((self.root / '.factory/config.json').read_text())
        config['revisores'] = {nombre: {'comando': comando, 'proveedor': 'revisor de prueba', 'modelo': 'fixture',
                                        'tope_minutos': 1}}
        (self.root / '.factory/config.json').write_text(json.dumps(config))

    # --- hg1: un pedido de revisión cortado queda a la vista -------------------------------------------------------
    def test_hg1_un_revisor_que_se_corta_sin_terminar(self):
        self.preparar()
        self.revisor('lento', [sys.executable, '-c', 'import time; time.sleep(60)'])
        self.git('add', '.')
        self.git('commit', '-qm', 'revisor lento', '--allow-empty')
        sha = f.candidato_vigente(self.ident) or self.git('rev-parse', '--short=7', 'HEAD')
        # pedir-revision por la CLI de verdad, y se lo mata a mitad (como una sesión que se cierra).
        proc = subprocess.Popen([*PYTHON_CLI, '--agente', 'claude-code', 'pedir-revision', self.ident, '--a', 'lento',
                                 '--base', self.base], cwd=self.root, env=entorno(), stdout=subprocess.DEVNULL,
                                stderr=subprocess.DEVNULL, start_new_session=True)
        limite = time.monotonic() + 30
        while not any(e['accion'] == 'revision_lanzada' for e in self.eventos()) and time.monotonic() < limite:
            time.sleep(0.1)
        os.killpg(proc.pid, signal.SIGKILL)
        proc.wait(timeout=10)
        [lanzada] = [e for e in self.eventos() if e['accion'] == 'revision_lanzada']
        self.assertEqual((lanzada['revisor'], lanzada['candidato']), ('lento', sha))
        self.assertNotIn('revision_pedida', [e['accion'] for e in self.eventos()])
        [aviso] = self.avisos('no dejó resultado')
        self.assertIn(f"el revisor lento se lanzó ({lanzada['cuando'][:16].replace('T', ' ')}) sobre el candidato {sha}", aviso)
        self.assertIn(f'Aviso: {aviso}.', self.estado_texto())
        self.lanzamientos_solapados_y_candidatos_que_quedan_atras()

    def test_hg1_un_revisor_que_termina_o_se_interrumpe(self):
        self.preparar()
        self.pedir('codex', ['baja', 'Un nombre poco claro'])
        acciones = [e['accion'] for e in self.eventos()]
        self.assertEqual(acciones[-2:], ['revision_lanzada', 'revision_pedida'])
        lanzada, pedida = self.eventos()[-2:]
        self.assertTrue(lanzada['lanzamiento'])
        self.assertEqual(pedida['lanzamiento'], lanzada['lanzamiento'])
        self.assertEqual(self.avisos('no dejó resultado'), [])
        # Ctrl-C a mitad del revisor: queda «interrumpido» y no avisa de un lanzamiento sin resultado.
        with patch.object(f.revisores_mod, 'ejecutar_revisor', side_effect=KeyboardInterrupt), \
                contextlib.redirect_stdout(io.StringIO()), self.assertRaises(KeyboardInterrupt):
            f.pedir_revision(self.ident, 'codex', base=self.base)
        ultimo = self.eventos()[-1]
        self.assertEqual((ultimo['accion'], ultimo['resultado']), ('revision_pedida', 'interrumpido'))
        self.assertEqual(self.avisos('no dejó resultado'), [])
        # Ctrl-C cuando el revisor ya terminó y Clue valida su informe: también queda «interrumpido».
        ejecutar = f.ejecutar

        def clue_cortado(argv, *a, **k):
            if argv[:2] == ['oracle-clue', 'validar']:
                raise KeyboardInterrupt
            return ejecutar(argv, *a, **k)
        with patch.object(f, 'ejecutar', side_effect=clue_cortado), \
                contextlib.redirect_stdout(io.StringIO()), self.assertRaises(KeyboardInterrupt):
            f.pedir_revision(self.ident, 'codex', base=self.base)
        ultimo = self.eventos()[-1]
        self.assertEqual((ultimo['accion'], ultimo['resultado']), ('revision_pedida', 'interrumpido'))
        self.assertEqual(self.avisos('no dejó resultado'), [])

    def lanzamientos_solapados_y_candidatos_que_quedan_atras(self):
        def ev(accion, revisor, candidato, minuto, lanzamiento=None):
            return {'accion': accion, 'revisor': revisor, 'candidato': candidato,
                    'cuando': f'2026-10-19T10:{minuto:02d}', **({'lanzamiento': lanzamiento} if lanzamiento else {})}
        avisos = lambda *eventos: f.aviso_lanzamientos({'id': 'X', 'eventos': list(eventos)})
        # Cortado y pedido otra vez, como indica el aviso, hasta el final: no queda nada que avisar.
        self.assertEqual(avisos(ev('revision_lanzada', 'codex', 'c1', 0, 'a'), ev('revision_lanzada', 'codex', 'c1', 1, 'b'),
                                ev('revision_pedida', 'codex', 'c1', 2, 'b')), [])
        # Dos lanzamientos solapados: termina el primero y el segundo se corta; el segundo sigue a la vista.
        [aviso] = avisos(ev('revision_lanzada', 'codex', 'c1', 0, 'a'), ev('revision_lanzada', 'codex', 'c1', 1, 'b'),
                         ev('revision_pedida', 'codex', 'c1', 2, 'a'))
        self.assertIn('el revisor codex se lanzó (2026-10-19 10:01) sobre el candidato c1', aviso)
        # Registros de antes del lanzamiento con nombre: el resultado cierra los de su revisor y candidato.
        self.assertEqual(avisos(ev('revision_lanzada', 'codex', 'c1', 0), ev('revision_lanzada', 'codex', 'c1', 1),
                                ev('revision_pedida', 'codex', 'c1', 2)), [])
        # Cortado sobre c1 y lanzado otra vez sobre c2: el de c1 quedó atrás (pedirlo de nuevo ya no lo cerraría).
        self.assertEqual(avisos(ev('revision_lanzada', 'codex', 'c1', 0, 'a'), ev('revision_lanzada', 'codex', 'c2', 1, 'b'),
                                ev('revision_pedida', 'codex', 'c2', 2, 'b')), [])
        [aviso] = avisos(ev('revision_lanzada', 'codex', 'c1', 0, 'a'), ev('revision_lanzada', 'codex', 'c2', 1, 'b'))
        self.assertIn('(2026-10-19 10:01) sobre el candidato c2', aviso)
        # Otro revisor sobre otro candidato no deja atrás a éste.
        [aviso] = avisos(ev('revision_lanzada', 'codex', 'c1', 0, 'a'), ev('revision_lanzada', 'agy', 'c2', 1, 'b'),
                         ev('revision_pedida', 'agy', 'c2', 2, 'b'))
        self.assertIn('el revisor codex se lanzó (2026-10-19 10:00) sobre el candidato c1', aviso)

    # --- hg2: las acciones sin autor se avisan --------------------------------------------------------------------
    def test_hg2_un_agente_que_se_olvido_de_agente(self):
        # nuevo, sin --agente y sin terminal (como lo corre un agente): la acción queda sin autor.
        r = subprocess.run([*PYTHON_CLI, 'nuevo', '--capacidad', 'otra', '--sufijo', 'sinautor', 'Sin autor'],
                           cwd=self.root, env=entorno(), capture_output=True, text=True, stdin=subprocess.DEVNULL)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.ident = next(p.name for p in (self.root / '.factory/cambios').iterdir() if p.name.endswith('sinautor'))
        self.assertEqual(self.eventos()[0]['tipo_actor'], 'sin_identificar')
        [aviso] = self.avisos('sin autor')
        self.assertIn('1 acción quedó sin autor (cambio_creado)', aviso)
        self.assertIn('--agente NOMBRE', aviso)
        self.assertIn(f'Aviso: {aviso}.', self.estado_texto())
        # Un cambio hecho con --agente no avisa.
        f.AGENTE = 'claude-code'
        try:
            otro = f.nuevo('Con autor', capacidad='otra', sufijo='conautor')
        finally:
            f.AGENTE = None
        self.ident = otro
        self.assertEqual(self.avisos('sin autor'), [])


class HigieneInit(unittest.TestCase):
    """init en carpetas temporales, con la CLI de verdad."""

    def init(self, raiz):
        subprocess.run(['git', 'init', '-q', '-b', 'main'], cwd=raiz, check=True)
        r = subprocess.run([*PYTHON_CLI, 'init'], cwd=raiz, env=entorno(), capture_output=True, text=True,
                           stdin=subprocess.DEVNULL)
        self.assertEqual(r.returncode, 0, r.stderr)

    # --- hg3: init no deja carpetas que Factory no usa -------------------------------------------------------------
    def test_hg3_un_proyecto_nuevo(self):
        with tempfile.TemporaryDirectory() as d:
            raiz = Path(d)
            self.init(raiz)
            for nombre in ('corpus', 'relaciones', 'diferencial'):
                self.assertFalse((raiz / nombre).exists(), nombre)
            self.assertTrue((raiz / 'catalogos').is_dir() and (raiz / 'oracle.json').is_file())
            self.assertNotIn('.factory-demo', (raiz / '.gitignore').read_text())
            # El bloqueo de medir se toma dentro de .factory/local/locks y no deja nada afuera.
            with patch.object(f, 'ROOT', raiz):
                with f.bloqueo_medidas('20260101-000000-x'):
                    self.assertEqual([p.relative_to(raiz).as_posix() for p in raiz.rglob('*.medir.lock')],
                                     ['.factory/local/locks/20260101-000000-x.medir.lock'])
            self.assertFalse((raiz / '.factory-demo').exists())
            self.assertEqual(list(raiz.rglob('*.medir.lock')), [])

    def test_hg3_un_proyecto_con_carpetas_de_oracle_propias(self):
        with tempfile.TemporaryDirectory() as d:
            raiz = Path(d)
            (raiz / 'corpus').mkdir()
            caso = raiz / 'corpus' / 'uno.caso'
            caso.write_text('caso uno:\n')
            (raiz / 'diferencial').mkdir()  # vacía, pero ya estaba: no se toca
            self.init(raiz)
            self.assertEqual(caso.read_text(), 'caso uno:\n')
            self.assertTrue((raiz / 'diferencial').is_dir())
            self.assertFalse((raiz / 'relaciones').exists())


if __name__ == '__main__':
    unittest.main()
