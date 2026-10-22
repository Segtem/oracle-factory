"""Preguntar desde un agente y desde el editor: escenarios mc1 (oracle-factory mcp, en un proyecto temporal y con la
CLI de verdad) y mc2 (la extensión de VS Code en node, con un `vscode` falso)."""
import contextlib
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import test_archivo as _archivo  # noqa: E402
import test_tablero as _tablero  # noqa: E402

f = _archivo.f
SOURCE = Path(__file__).resolve().parents[1]


class Mcp(unittest.TestCase):
    setUp_archivo, escribe, git = _archivo.Archivo.setUp, _archivo.Archivo.escribe, _archivo.Archivo.git

    def setUp(self):
        self.setUp_archivo()
        f.AGENTE = 'claude-code'
        try:
            self.ident = f.nuevo('Una tortuga que cruza el camino', capacidad='otra', sufijo='tortuga')
        finally:
            f.AGENTE = None
        ruta = self.root / '.factory/config.json'
        datos = json.loads(ruta.read_text()) if ruta.is_file() else {}
        ruta.write_text(json.dumps({**datos, 'rag': {'embeddings': {'proveedor': 'ninguno'}}}))
        with contextlib.redirect_stdout(io.StringIO()):
            f.main(['--proyecto', str(self.root), 'kb'])
        self.git('add', '-A')
        self.git('commit', '-qm', 'el proyecto')

    def cli(self, *args):
        r = subprocess.run([sys.executable, '-c', 'import sys; from oracle_factory.cli import main; sys.exit(main())',
                            '--proyecto', str(self.root), *args], capture_output=True, text=True, stdin=subprocess.DEVNULL,
                           env={**os.environ, 'PYTHONPATH': str(SOURCE)})
        return r.stdout

    def servidor(self, *mensajes):
        entrada = ''.join(json.dumps(m) + '\n' if isinstance(m, dict) else m for m in mensajes)
        r = subprocess.run([sys.executable, '-c', 'import sys; from oracle_factory.cli import main; sys.exit(main())',
                            '--proyecto', str(self.root), 'mcp'], input=entrada, capture_output=True, text=True,
                           env={**os.environ, 'PYTHONPATH': str(SOURCE)}, timeout=300)
        self.assertEqual(r.returncode, 0, r.stderr)
        return {x.get('id'): x for x in map(json.loads, r.stdout.splitlines())}

    @staticmethod
    def llamar(n, nombre, **argumentos):
        return {'jsonrpc': '2.0', 'id': n, 'method': 'tools/call', 'params': {'name': nombre, 'arguments': argumentos}}

    def test_mc1_un_agente_pregunta_y_consulta_un_cambio(self):
        r = self.servidor({'jsonrpc': '2.0', 'id': 1, 'method': 'initialize', 'params': {}},
                          {'jsonrpc': '2.0', 'method': 'notifications/initialized'},
                          {'jsonrpc': '2.0', 'id': 2, 'method': 'tools/list'},
                          self.llamar(3, 'preguntar', texto='¿Cómo cruza el camino la tortuga?'),
                          self.llamar(4, 'estado', id=self.ident),
                          self.llamar(5, 'estado', id='20990101-000000-no-existe'),
                          self.llamar(6, 'buscar', texto='--json'),
                          self.llamar(7, 'estado', id='--json'),
                          self.llamar(8, 'preguntar', texto='tortuga', extra=1),
                          self.llamar(13, 'preguntar'),
                          'esto no es JSON\n',
                          {'jsonrpc': '2.0', 'id': 9, 'method': 'resources/list'},
                          self.llamar(10, 'borrar', id=self.ident),
                          self.llamar(11, 'log', id=self.ident),
                          {'jsonrpc': '2.0', 'id': 12, 'method': 'ping'},
                          {'jsonrpc': '2.0', 'id': 14, 'method': 'tools/call', 'params': {'name': [], 'arguments': {}}},
                          self.llamar(15, 'buscar', texto='nulo\0'),
                          self.llamar(16, 'por_que', linea=1),
                          self.llamar(17, 'por_que', archivo=f'openspec/changes/{self.ident}/proposal.md', linea=1),
                          self.llamar(18, 'resumen'),
                          self.llamar(19, 'listar'),
                          {'jsonrpc': '2.0', 'id': 20, 'method': 'ping'})
        self.assertEqual(r[1]['result']['serverInfo']['name'], 'oracle-factory')
        herramientas = {h['name']: h for h in r[2]['result']['tools']}
        self.assertEqual(set(herramientas), {'preguntar', 'estado', 'buscar', 'por_que', 'resumen', 'log', 'listar'})
        self.assertTrue(all(h['annotations']['readOnlyHint'] for h in herramientas.values()))
        # Lo mismo que la CLI.
        self.assertEqual(json.loads(r[3]['result']['content'][0]['text']),
                         json.loads(self.cli('preguntar', '--json', '--', '¿Cómo cruza el camino la tortuga?')))
        self.assertEqual(json.loads(r[4]['result']['content'][0]['text']), json.loads(self.cli('estado', self.ident, '--json')))
        self.assertEqual(r[11]['result']['content'][0]['text'], self.cli('log', self.ident, '--json'))
        self.assertEqual(r[17]['result']['content'][0]['text'],
                         self.cli('por-que', '--json', '--', f'openspec/changes/{self.ident}/proposal.md:1'))
        self.assertEqual(r[18]['result']['content'][0]['text'], self.cli('resumen', '--json'))
        self.assertEqual(r[19]['result']['content'][0]['text'], self.cli('listar'))
        self.assertIn(self.ident, r[19]['result']['content'][0]['text'])
        # Un nombre que no es texto, un byte nulo o un argumento obligatorio que falta: error, y el servidor sigue.
        self.assertEqual(r[14]['error']['code'], -32602)
        for n in (15, 16):
            self.assertTrue(r[n]['result']['isError'])
            self.assertIn('argumentos inválidos', r[n]['result']['content'][0]['text'])
        # Si la CLI no se puede correr (un plazo vencido), también es un error de la herramienta.
        from oracle_factory import mcp
        with patch.object(mcp.subprocess, 'run', side_effect=mcp.subprocess.TimeoutExpired('oracle-factory', 600)):
            vencido = mcp.llamar(self.root, 'listar', {})
        self.assertTrue(vencido['isError'] and 'no se pudo correr' in vencido['content'][0]['text'])
        self.assertEqual(r[20]['result'], {})
        # Un error es un resultado de error, y el servidor sigue atendiendo.
        self.assertTrue(r[5]['result']['isError'])
        self.assertEqual(r[12]['result'], {})
        # Un texto que empieza con guiones es un texto: se busca tal cual, y un id que no es un id se rechaza.
        self.assertFalse(r[6]['result']['isError'])
        self.assertEqual(r[6]['result']['content'][0]['text'], self.cli('buscar', '--', '--json'))
        self.assertTrue(r[7]['result']['isError'] and 'argumentos inválidos' in r[7]['result']['content'][0]['text'])
        self.assertTrue(r[8]['result']['isError'] and r[13]['result']['isError'])
        self.assertEqual(r[None]['error']['code'], -32700)
        self.assertEqual(r[9]['error']['code'], -32601)
        self.assertEqual(r[10]['error']['code'], -32602)
        # Nada del proyecto cambió (el índice de preguntar vive en .factory/local/, que Git ignora).
        self.assertEqual(self.git('status', '--porcelain'), '')

    @unittest.skipUnless(_tablero.NODE, 'hace falta node')
    def test_mc2_una_pregunta_desde_el_editor(self):
        cli = Path(self.tmp.name) / 'oracle-factory'
        cli.write_text(f'#!/bin/sh\nPYTHONPATH={SOURCE} exec {sys.executable} -c "import sys; '
                       f'from oracle_factory.cli import main; sys.exit(main())" "$@"\n')
        cli.chmod(0o755)

        def tablero(pregunta):
            r = subprocess.run([_tablero.NODE, str(SOURCE / 'tests/tablero_en_node.cjs'), str(_tablero.EXTENSION), str(self.root),
                                json.dumps([{'tipo': 'preguntar'}]), str(cli)], capture_output=True, text=True, timeout=120,
                               env={**os.environ, 'PREGUNTA': pregunta})
            self.assertEqual(r.returncode, 0, r.stderr)
            return json.loads(r.stdout)
        datos = tablero('--json')  # un texto que parece una opción llega como texto
        self.assertIn('data-preguntar="1"', datos['html'])
        self.assertIn("if (b.dataset.preguntar) vscode.postMessage({tipo: 'preguntar'});", datos['html'])
        [doc] = datos['diffs']
        self.assertEqual((doc['lenguaje'], doc['primera']), ('markdown', '# --json'))
        self.assertFalse(datos['documentos'][0].split('\n', 2)[2].startswith('Factory:'))  # no es un error de la CLI
        self.assertEqual(tablero('')['diffs'], [])  # cancelar no hace nada
        # Desde la paleta: el comando está registrado y hace lo mismo.
        r = subprocess.run([_tablero.NODE, str(SOURCE / 'tests/tablero_en_node.cjs'), str(_tablero.EXTENSION), str(self.root),
                            '[]', str(cli)], capture_output=True, text=True, timeout=120,
                           env={**os.environ, 'PREGUNTA': 'tortuga', 'COMANDO': 'factory.preguntar'})
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual([d['primera'] for d in json.loads(r.stdout)['diffs']], ['# tortuga'])
        paquete = json.loads((_tablero.EXTENSION / 'package.json').read_text())
        self.assertIn('factory.preguntar', [c['command'] for c in paquete['contributes']['commands']])
        self.assertEqual(self.git('status', '--porcelain'), '')


if __name__ == '__main__':
    unittest.main()
