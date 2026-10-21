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
        self.assertEqual(salida['llamadas'], ['share', 'end', f'join {ENLACE}', 'end', 'join https://vscode.dev/liveshare/XYZ', 'end'])
        # La sesión que vino después no muestra el enlace de la anterior, y copiarlo usa el comando de Live Share.
        self.assertNotIn('SESION1', salida['vistas']['otraSesion'])
        self.assertEqual(salida['ejecutados'], [['liveshare.collaboration.copyLink']])
        # El invitado que espera el tablero de quien comparte puede salir de la sesión.
        self.assertIn('Esperando el tablero de quien comparte', salida['vistas']['invitado'])
        self.assertIn('data-sesion="terminar">Salir de la sesión', salida['vistas']['invitado'])
        # El enlace de la sesión: se ve en el tablero, se copia y se avisa.
        sesion1 = 'https://prod.liveshare.vsengsaas.visualstudio.com/join?SESION1'
        self.assertIn(f'<code>{sesion1}</code>', salida['vistas']['conEnlace'])
        self.assertIn('data-sesion="copiar">Copiar enlace', salida['vistas']['compartida'])
        self.assertEqual(salida['portapapeles'], [sesion1, sesion1])
        self.assertEqual(salida['avisos'], [f'Enlace de la sesión copiado: {sesion1}'] * 2)
        # Una sesión que ya se compartió desde la paleta, con el rol como texto: a Live Share no se le pide compartir otra
        # vez (lo rechaza con «command '…' already exists» y deja la sesión a medias).
        # El rol, como número o como texto; Role.None (0) es sin sesión aunque quede un id.
        r = subprocess.run([_tablero.NODE, '-e', 'const {rolDe} = require(process.argv[1]); console.log(JSON.stringify(['
                            '[0, "s"], ["None", "s"], ["0", "s"], [1, null], ["Host", null], [2, null], ["Guest", null], '
                            '[undefined, "s"], [undefined, null], ["raro", "s"]].map(([x, id]) => rolDe(x, id))))',
                            str(_tablero.EXTENSION / 'liveshare.js')], capture_output=True, text=True, timeout=60)
        self.assertEqual(json.loads(r.stdout), [0, 0, 0, 1, 1, 2, 2, 1, 0, 0])
        ya = self.correr('ya-compartida')
        self.assertIn('<b>Ana</b> (vos, anfitrión)', ya['vistas']['inicio'])
        self.assertIn('data-sesion="copiar">Copiar enlace', ya['vistas']['inicio'])
        # Sin enlace propio, «Copiar enlace» usa el comando de Live Share que lo copia; a share() no se le pide nada.
        self.assertEqual((ya['llamadas'], ya['portapapeles']), ([], []))
        self.assertEqual(ya['ejecutados'], [['liveshare.collaboration.copyLink']])
        self.assertEqual(salida['errores'], ['Factory: ese no es un enlace de una sesión de Live Share.'] * len(otros))
        self.assertEqual(salida['llamadas'].count('share'), 1)  # compartir con la sesión abierta no comparte otra vez

    @unittest.skipUnless(_tablero.NODE, 'hace falta node')
    def test_se1_sin_live_share(self):
        salida = self.correr('sin')
        self.assertIn('data-sesion="instalar">Instalar Live Share', salida['vistas']['inicio'])
        self.assertEqual(salida['ejecutados'], [['extension.open', 'ms-vsliveshare.vsliveshare']])
        self.assertEqual(salida['llamadas'], [])


if __name__ == '__main__':
    unittest.main()
