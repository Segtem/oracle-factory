"""La sesión de Live Share desde el tablero: escenarios se1, con la CLI de verdad y el panel en node con un Live Share
falso (o sin él)."""
import json
from pathlib import Path
import subprocess
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import test_tablero as _tablero  # noqa: E402

f = _tablero.f
SOURCE = Path(__file__).resolve().parents[1]
ENLACE = 'https://prod.liveshare.vsengsaas.visualstudio.com/join?ABC123'


class Sesion(unittest.TestCase):
    T = _tablero.Tablero
    escribe, git, salida, cambio_cerrado = T.escribe, T.git, T.salida, T.cambio_cerrado
    candidato_nuevo, pedir, con_dos_revisores = T.candidato_nuevo, T.pedir, T.con_dos_revisores

    def setUp(self):
        _tablero.Tablero.setUp(self)
        self.assertEqual(Path(self.git('rev-parse', '--show-toplevel')).resolve(), self.root.resolve())
        self.con_dos_revisores()
        self.antes = (self.root / '.factory/cambios' / self.ident / 'factory.json').read_text()

    def correr(self, con, enlaces=()):
        cli = Path(self.tmp.name) / 'oracle-factory'
        cli.write_text(f'#!/bin/sh\nPYTHONPATH={SOURCE} exec {sys.executable} -c "import sys; '
                       f'from oracle_factory.cli import main; sys.exit(main())" "$@"\n')
        cli.chmod(0o755)
        r = subprocess.run([_tablero.NODE, str(SOURCE / 'tests/sesion_en_node.cjs'), str(_tablero.EXTENSION), str(self.root),
                            str(cli), con, json.dumps(list(enlaces))], capture_output=True, text=True, timeout=120)
        self.assertEqual(r.returncode, 0, r.stderr)
        # Ningún botón de la sesión toca un registro de Factory.
        self.assertEqual((self.root / '.factory/cambios' / self.ident / 'factory.json').read_text(), self.antes)
        return json.loads(r.stdout)

    # --- se1: la sesión de Live Share se maneja desde el tablero ---------------------------------------------------
    @unittest.skipUnless(_tablero.NODE, 'hace falta node')
    def test_se1_compartir_terminar_y_unirse(self):
        otros = ['http://prod.liveshare.vsengsaas.visualstudio.com/join?X', 'https://evil.example/join?x', 'https://evil.com/join?x',
                 'https://vscode.dev/otra-cosa', 'no es un enlace']
        salida = self.correr('con', [ENLACE, *otros, 'https://vscode.dev/liveshare/XYZ'])
        self.assertIn('data-sesion="compartir">Compartir sesión', salida['vistas']['inicio'])
        self.assertIn('data-sesion="unirse">Unirse a una sesión', salida['vistas']['inicio'])
        self.assertIn('data-sesion="terminar">Terminar sesión', salida['vistas']['compartida'])
        self.assertEqual(salida['llamadas'], ['share', 'end', f'join {ENLACE}', 'join https://vscode.dev/liveshare/XYZ'])
        self.assertEqual(salida['errores'], ['Factory: ese no es un enlace de una sesión de Live Share.'] * len(otros))

    @unittest.skipUnless(_tablero.NODE, 'hace falta node')
    def test_se1_sin_live_share(self):
        salida = self.correr('sin')
        self.assertIn('data-sesion="instalar">Instalar Live Share', salida['vistas']['inicio'])
        self.assertEqual(salida['ejecutados'], [['extension.open', 'ms-vsliveshare.vsliveshare']])
        self.assertEqual(salida['llamadas'], [])


if __name__ == '__main__':
    unittest.main()
