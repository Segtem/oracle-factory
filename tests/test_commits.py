"""Los commits unidos a su cambio: escenarios cm1–cm2, con git de verdad (el hook corre en cada commit) y la CLI."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

SOURCE = Path(__file__).resolve().parents[1]
PYTHON_CLI = [sys.executable, '-c', 'import sys; from oracle_factory.cli import main; sys.exit(main())']
NODE = shutil.which('node')
ENTORNO = {**os.environ, 'PYTHONPATH': str(SOURCE), 'GIT_AUTHOR_NAME': 'Persona fixture', 'GIT_AUTHOR_EMAIL': 'p@example.invalid',
           'GIT_COMMITTER_NAME': 'Persona fixture', 'GIT_COMMITTER_EMAIL': 'p@example.invalid'}
CON_AUTOR = 'Co-Authored-By: Agente fixture <agente@example.invalid>'


class Commits(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / 'producto'
        self.root.mkdir()
        self.git('init', '-q', '-b', 'main')
        self.instalado = self.cli('init')
        self.git('add', '.')
        self.git('commit', '-qm', 'init')

    def git(self, *args):
        r = subprocess.run(['git', *args], cwd=self.root, env=ENTORNO, capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr)
        return r.stdout.strip()

    def cli(self, *args):
        r = subprocess.run([*PYTHON_CLI, '--agente', 'claude-code', *args], cwd=self.root, env=ENTORNO, capture_output=True,
                           text=True, stdin=subprocess.DEVNULL)
        self.assertEqual(r.returncode, 0, r.stderr)
        return r.stdout

    def nuevo(self, sufijo):
        self.cli('nuevo', '--capacidad', 'otra', '--sufijo', sufijo, f'Cambio {sufijo}')
        return next(p.name for p in (self.root / 'openspec/changes').iterdir() if p.name.endswith(sufijo))

    def commit(self, archivo, mensaje):
        """Un commit con fecha propia (un minuto después del anterior): el orden de log no depende de la velocidad."""
        (self.root / archivo).write_text(mensaje + '\n')
        self.git('add', '.')
        self.minuto = getattr(self, 'minuto', 0) + 1
        ENTORNO['GIT_AUTHOR_DATE'] = f'2026-10-19T10:{self.minuto:02d}:00-03:00'
        try:
            self.git('commit', '-q', '-m', mensaje, '-m', CON_AUTOR)
        finally:
            del ENTORNO['GIT_AUTHOR_DATE']
        return self.git('log', '-1', '--format=%B')

    def cerrar_a_mano(self, ident):
        registro = self.root / '.factory/cambios' / ident / 'factory.json'
        datos = json.loads(registro.read_text())
        datos['fase'] = 'cerrada'
        registro.write_text(json.dumps(datos))

    # --- cm1: cada commit nuevo dice de qué cambio es ---------------------------------------------------------------
    def test_cm1_un_commit_con_un_cambio_abierto(self):
        self.assertIn('Hook de commits en', self.instalado)
        ident = self.nuevo('uno')
        mensaje = self.commit('a.txt', 'producto: algo')
        self.assertEqual(mensaje.splitlines()[-2:], [CON_AUTOR, f'Cambio: {ident}'])
        # Rehacer el commit (amend) no lo repite, y un Cambio: que ya está se respeta.
        self.git('commit', '-q', '--amend', '--no-edit')
        self.assertEqual(self.git('log', '-1', '--format=%B').count('Cambio:'), 1)
        self.git('commit', '-q', '--allow-empty', '-m', 'otro', '-m', 'Cambio: 20200101-000000-elegido')
        self.assertEqual(self.git('log', '-1', '--format=%(trailers:key=Cambio,valueonly)'), '20200101-000000-elegido')

    def test_cm1_sin_un_unico_cambio_abierto_o_con_un_hook_ajeno(self):
        self.assertNotIn('Cambio:', self.commit('a.txt', 'sin cambios abiertos'))
        uno, dos = self.nuevo('uno'), self.nuevo('dos')
        self.assertNotIn('Cambio:', self.commit('b.txt', 'con dos abiertos'))
        self.cerrar_a_mano(dos)
        self.assertIn(f'Cambio: {uno}', self.commit('c.txt', 'con uno abierto'))
        # Sin el intérprete de Factory, el commit se hace igual (sin trailer).
        hook = Path(self.git('rev-parse', '--git-path', 'hooks'))
        hook = (self.root / hook / 'prepare-commit-msg')
        hook.write_text(hook.read_text().replace(sys.executable, '/no/existe/python'))
        self.assertNotIn('Cambio:', self.commit('d.txt', 'sin intérprete'))
        # Un hook ajeno no se pisa: hooks avisa cómo encadenarlo.
        hook.write_text('#!/bin/sh\necho ajeno >/dev/null\n')
        salida = self.cli('hooks')
        self.assertIn('no es de Factory; no lo toqué', salida)
        self.assertIn('trailer "$@"', salida)
        self.assertEqual(hook.read_text(), '#!/bin/sh\necho ajeno >/dev/null\n')
        # El de Factory se reinstala sobre sí mismo.
        hook.write_text('#!/bin/sh\n# oracle-factory: une cada commit con su cambio (viejo)\nexit 0\n')
        self.assertIn('Hook de commits en', self.cli('hooks'))
        self.assertIn(f'Cambio: {uno}', self.commit('e.txt', 'otra vez con hook'))

    # --- cm2: los commits de un cambio se ven en log, estado y el tablero ------------------------------------------
    def test_cm2_un_cambio_cerrado_de_antes_del_trailer(self):
        hook = self.root / self.git('rev-parse', '--git-path', 'hooks') / 'prepare-commit-msg'
        hook.unlink()  # como antes del trailer
        self.git('checkout', '-q', '-b', 'tarea/viejo')
        ident = self.nuevo('viejo')
        self.commit('a.txt', 'viejo: primero')
        candidato = self.git('rev-parse', '--short=7', 'HEAD')
        revision = self.root / '.factory/cambios' / ident / 'candidatos' / candidato / 'revision'
        revision.mkdir(parents=True)
        (revision / 'codex-1.json').write_text('{"findings": []}')
        self.git('checkout', '-q', 'main')
        self.commit('m.txt', 'main: algo de otro')
        # main entra a la rama antes de integrarla: ese merge no es el que integró el cambio.
        self.git('checkout', '-q', 'tarea/viejo')
        self.git('merge', '-q', '--no-ff', 'main', '-m', 'Traer main')
        self.commit('b.txt', 'viejo: registros')
        self.git('checkout', '-q', 'main')
        self.git('merge', '-q', '--no-ff', 'tarea/viejo', '-m', 'Integrar viejo')
        self.cerrar_a_mano(ident)
        datos = json.loads(self.cli('log', ident, '--json'))
        self.assertEqual(datos['esquema'], 'oracle-factory.log/1')
        asuntos = {c['asunto']: c for c in datos['commits']}
        self.assertEqual(set(asuntos), {'viejo: primero', 'Traer main', 'viejo: registros'})  # ni el de main ni el init
        self.assertEqual({c['union'] for c in datos['commits']}, {'deducido'})
        primero = asuntos['viejo: primero']
        self.assertEqual((primero['corto'], primero['candidato'], primero['revisado']), (candidato, True, True))
        self.assertFalse(asuntos['viejo: registros']['candidato'])
        self.assertIn(f'{candidato}  ', self.cli('log', ident))

    def test_cm2_un_cambio_abierto_con_trailer_en_estado_y_en_el_tablero(self):
        ident = self.nuevo('abierto')
        self.assertIn('Commits: ninguno unido todavía', self.cli('estado', ident))
        self.commit('a.txt', 'abierto: primero')
        self.commit('b.txt', 'abierto: segundo')
        ultimo = self.git('rev-parse', 'HEAD')
        self.assertIn(f'Commits: 2; el último {ultimo[:7]} «abierto: segundo»', self.cli('estado', ident))
        commits = json.loads(self.cli('estado', ident, '--json'))['commits']
        self.assertEqual([(c['asunto'], c['union']) for c in commits], [('abierto: segundo', 'trailer'), ('abierto: primero', 'trailer')])
        if not NODE:
            self.skipTest('hace falta node')
        cli = Path(self.tmp.name) / 'oracle-factory'
        cli.write_text(f'#!/bin/sh\nPYTHONPATH={SOURCE} exec {sys.executable} -c "import sys; '
                       f'from oracle_factory.cli import main; sys.exit(main())" "$@"\n')
        cli.chmod(0o755)
        mensajes = [{'tipo': 'commit', 'sha': ultimo}, {'tipo': 'commit', 'sha': '--output=/tmp/x'},
                    {'tipo': 'commit', 'sha': 'f' * 40}]
        r = subprocess.run([NODE, str(SOURCE / 'tests/tablero_en_node.cjs'), str(SOURCE / 'editores/vscode'), str(self.root),
                            json.dumps(mensajes), str(cli)], capture_output=True, text=True, timeout=120, env=ENTORNO)
        self.assertEqual(r.returncode, 0, r.stderr)
        salida = json.loads(r.stdout)
        self.assertIn('<h3>Commits (2)</h3>', salida['html'])
        self.assertIn(f'data-commit="{ultimo}"', salida['html'])
        self.assertIn('abierto: primero', salida['html'])
        # El diff del commit elegido, de sólo lectura; un sha que no es hex no llega a git, y uno que no existe avisa.
        self.assertEqual(salida['diffs'], [{'lenguaje': 'diff', 'primera': f'commit {ultimo}'}])
        self.assertEqual(salida['errores'], [f'Factory: git no encontró el commit {"f" * 40}.'])
        self.assertEqual(salida['abiertos'], [])


if __name__ == '__main__':
    unittest.main()
