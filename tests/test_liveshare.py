"""El tablero en pair programming: escenarios ls1–ls3, con la CLI de verdad y dos VS Code falsos conectados por un
Live Share falso en node."""
import json
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import test_tablero as _tablero  # noqa: E402

f = _tablero.f
from oracle_factory import tablero as tablero_mod  # noqa: E402
SOURCE = Path(__file__).resolve().parents[1]


class LiveShare(unittest.TestCase):
    """Con el proyecto de los tests del tablero: un cambio abierto con hallazgos de dos revisores."""
    T = _tablero.Tablero
    escribe, git, salida, cambio_cerrado = T.escribe, T.git, T.salida, T.cambio_cerrado
    candidato_nuevo, pedir, con_dos_revisores = T.candidato_nuevo, T.pedir, T.con_dos_revisores

    def setUp(self):
        _tablero.Tablero.setUp(self)
        # git no sale del temporal: un test nunca toca el repositorio que lo contiene.
        self.assertEqual(Path(self.git('rev-parse', '--show-toplevel')).resolve(), self.root.resolve())

    def cli_falsa(self):
        cli = Path(self.tmp.name) / 'oracle-factory'
        cli.write_text(f'#!/bin/sh\nPYTHONPATH={SOURCE} exec {sys.executable} -c "import sys; '
                       f'from oracle_factory.cli import main; sys.exit(main())" "$@"\n')
        cli.chmod(0o755)
        return cli

    def sesion(self):
        self.con_dos_revisores()
        return self.sesion_sobre_lo_que_hay()

    # --- ls1: el tablero muestra quién está en la sesión -----------------------------------------------------------
    @unittest.skipUnless(_tablero.NODE, 'hace falta node')
    def test_ls1_una_sesion_con_un_invitado_que_entra_y_sale(self):
        salida, _ = self.sesion()
        v = salida['vistas']
        self.assertIn('<b>Ana Anfitriona</b> (vos, anfitrión)', v['anaSola'])
        self.assertNotIn('Iván Invitado', v['anaSola'])
        self.assertIn('<b>Iván Invitado</b> (invitado)', v['anaConIvan'])
        self.assertIn('<b>Iván Invitado</b> (vos, invitado)', v['ivan'])
        self.assertIn('<b>Ana Anfitriona</b> (anfitrión)', v['ivan'])
        self.assertNotIn('<b>Iván Invitado</b> (invitado)', v['anaSinIvan'])

    @unittest.skipUnless(_tablero.NODE, 'hace falta node')
    def test_ls1_sin_live_share(self):
        self.con_dos_revisores()
        r = subprocess.run([_tablero.NODE, str(SOURCE / 'tests/tablero_en_node.cjs'), str(_tablero.EXTENSION), str(self.root),
                            '[]', str(self.cli_falsa())], capture_output=True, text=True, timeout=120)
        self.assertEqual(r.returncode, 0, r.stderr)
        html = json.loads(r.stdout)['html']
        self.assertIn('Sin Live Share: para trabajar de a dos', html)
        self.assertIn('<h3>Hallazgos</h3>', html)  # el resto del tablero, como siempre
        self.assertNotIn('<form class="escribir"', html)

    # --- ls2: el invitado ve el tablero de quien comparte ----------------------------------------------------------
    @unittest.skipUnless(_tablero.NODE, 'hace falta node')
    def test_ls2_un_invitado_sin_factory(self):
        salida, hallazgo = self.sesion()
        v, ivan, ana = salida['vistas'], salida['ivan'], salida['ana']
        self.assertIn(self.ident, v['ivan'])
        self.assertIn('Ves el tablero de quien comparte', v['ivan'])
        self.assertIn('Un título que cambió en la sesión', v['ivanConMensaje'])
        # El hallazgo abre el archivo compartido en su línea; el camino que sube no se abre.
        self.assertEqual(ivan['abiertos'], [{'uri': '/' + hallazgo['archivo'], 'esquema': 'vsls', 'linea': hallazgo['linea']}])
        # El comando se escribe sin Enter en la terminal de la anfitriona; el de dos líneas no se escribe.
        self.assertEqual([(t['texto'].split()[-2:], t['enter']) for t in ana['terminal']], [(['estado', self.ident], False)])
        self.assertEqual(ivan['terminal'], [])
        self.assertEqual(f.leer(self.ident)[1].get('revision'), None)  # el tablero no decidió nada
        # Un invitado que entra antes de que esté el servicio espera, sin buscar el proyecto en su disco ni escribir nada.
        self.assertIn('Esperando el tablero de quien comparte', v['tina'])
        self.assertEqual((salida['tina']['terminal'], salida['tina']['errores']), ([], []))

    # --- ls3: el chat queda en el cambio ---------------------------------------------------------------------------
    @unittest.skipUnless(_tablero.NODE, 'hace falta node')
    def test_ls3_un_mensaje_desde_la_terminal_y_uno_desde_el_chat(self):
        self.con_dos_revisores()
        antes = f.datos_estado(self.ident)
        with patch.object(f, 'terminal_interactiva', return_value=True):
            f.mensaje(self.ident, 'hola')
        f.AGENTE = 'claude-code'
        try:
            f.mensaje(self.ident, 'terminé las pruebas')
        finally:
            f.AGENTE = None
        self.git('add', '.')
        self.git('commit', '-qm', 'mensajes')
        salida, _ = self.sesion_sobre_lo_que_hay()
        mensajes = [e for e in f.leer(self.ident)[1]['eventos'] if e['accion'] == 'mensaje']
        self.assertEqual([(e['actor'], e['tipo_actor'], e['texto'], e.get('via')) for e in mensajes], [
            (mensajes[0]['actor'], 'persona', 'hola', None), ('claude-code', 'agente', 'terminé las pruebas', None),
            ('Iván Invitado', 'persona', 'revisá el hook <b>ya</b>', 'live-share')])
        self.assertEqual(mensajes[-1]['guardado_por'], f.subprocess.run(['git', 'config', 'user.name'], cwd=self.root,
                                                                         capture_output=True, text=True).stdout.strip() or f.getpass.getuser())
        # Con un nombre que no es el de un invitado conectado (la anfitriona, o alguien que no está), no se guarda.
        self.assertEqual(salida['falsos'], [False, False, False, False])
        self.assertNotIn('soy Ana', json.dumps(f.leer(self.ident)[1]['eventos']))
        for vista in ('ivanConMensaje', 'anaConMensaje'):
            html = salida['vistas'][vista]
            self.assertIn('<b>Iván Invitado</b> <small>(live-share, guardado por ', html)
            self.assertIn(': revisá el hook &lt;b&gt;ya&lt;/b&gt;', html)
            self.assertIn('<b>claude-code</b>: terminé las pruebas', html)
            self.assertIn(f'<form class="escribir" data-cambio="{self.ident}">', html)
        # Los mensajes no son decisiones.
        self.assertEqual(f.datos_estado(self.ident)['quien']['responsable'], antes['quien']['responsable'])
        [cambio] = _tablero.cli_json(self.root, 'tablero', '--json')['cambios']
        self.assertEqual(cambio['metricas']['decisiones_por_actor'],
                         tablero_mod.metricas_del_cambio({'eventos': [e for e in f.leer(self.ident)[1]['eventos']
                                                                               if e['accion'] != 'mensaje']}, [], None)['decisiones_por_actor'])

    def sesion_sobre_lo_que_hay(self):
        [cambio] = _tablero.cli_json(self.root, 'tablero', '--json')['cambios']
        hallazgo = next(h for h in cambio['hallazgos'] if h['archivo'])
        r = subprocess.run([_tablero.NODE, str(SOURCE / 'tests/liveshare_en_node.cjs'), str(_tablero.EXTENSION), str(self.root),
                            str(self.cli_falsa()), json.dumps({'archivo': hallazgo['archivo'], 'linea': hallazgo['linea']}),
                            self.ident], capture_output=True, text=True, timeout=180)
        self.assertEqual(r.returncode, 0, r.stderr)
        return json.loads(r.stdout), hallazgo

    def test_ls3_un_mensaje_sin_autor(self):
        self.con_dos_revisores()
        registro = (self.root / '.factory/cambios' / self.ident / 'factory.json').read_text()
        with patch.object(f, 'terminal_interactiva', return_value=False), \
                self.assertRaisesRegex(f.FactoryError, 'una persona desde su terminal o un agente'):
            f.mensaje(self.ident, 'x')
        f.AGENTE = 'claude-code'
        try:
            with self.assertRaisesRegex(f.FactoryError, 'no se combina con --agente'):
                f.mensaje(self.ident, 'x', de='Alguien')
        finally:
            f.AGENTE = None
        with self.assertRaisesRegex(f.FactoryError, 'hasta 2000 caracteres'):
            f.mensaje(self.ident, '   ')
        self.assertEqual((self.root / '.factory/cambios' / self.ident / 'factory.json').read_text(), registro)


if __name__ == '__main__':
    unittest.main()
