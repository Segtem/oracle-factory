"""Registros fuera del repo del producto, etapa 5b: la extensión de VS Code reconoce un producto conectado (av1–av2).

Producto y almacén como repos Git temporales con el entorno de tests/test_almacen_commits.py; la extensión corre en node
con el `vscode` falso de tests/vscode_en_node.cjs y la CLI de verdad."""
import contextlib
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import test_almacen_commits as _commits  # noqa: E402

f = _commits.f
SOURCE = Path(__file__).resolve().parents[1]
EXTENSION = SOURCE / 'editores/vscode'
NODE = shutil.which('node')


class AlmacenVscode(unittest.TestCase):
    git_en, arbol = _commits.AlmacenCommits.git_en, _commits.AlmacenCommits.arbol

    def setUp(self):
        _commits.AlmacenCommits.setUp(self)
        self.cli = self.base / 'oracle-factory'
        self.cli.write_text(f'#!/bin/sh\nexec {sys.executable} -c "import sys; from oracle_factory.cli import main; sys.exit(main())" "$@"\n')
        self.cli.chmod(0o755)

    def en(self, *args):
        out, err = io.StringIO(), io.StringIO()
        with patch('builtins.input', side_effect=['1'] * 8), contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            codigo = f.main(['--proyecto', str(self.producto), *args])
        return codigo, out.getvalue(), err.getvalue()

    def bien(self, *args):
        codigo, salida, error = self.en(*args)
        self.assertEqual(codigo, 0, (args, error))
        return salida

    def todo(self):
        return self.arbol(self.producto), self.arbol(self.almacen), self.arbol(self.casa)

    def vista(self, proyecto, **entorno):
        r = subprocess.run([NODE, str(SOURCE / 'tests/vscode_en_node.cjs'), str(EXTENSION), str(proyecto), str(self.cli)],
                           capture_output=True, text=True, timeout=180, env={**os.environ, **entorno})
        self.assertEqual(r.returncode, 0, r.stderr)
        return json.loads(r.stdout)

    # --- av1: conectar --json -----------------------------------------------------------------------------------------
    def test_av1_conectar_json_dice_la_conexion_sin_escribir_nada(self):
        antes = self.todo()
        datos = json.loads(self.bien('conectar', '--json'))
        self.assertEqual(datos, {'conectado': False, 'almacen': None, 'producto': str(self.producto)})
        self.assertEqual(self.todo(), antes)
        self.bien('conectar', str(self.almacen))
        antes = self.todo()
        datos = json.loads(self.bien('conectar', '--json'))
        self.assertEqual(datos, {'conectado': True, 'almacen': str(self.almacen), 'producto': str(self.producto)})
        self.assertEqual(self.todo(), antes)
        # desde una carpeta que no es un repo Git: sin producto
        suelta = self.base / 'suelta'
        suelta.mkdir()
        out = io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(io.StringIO()):
            codigo = f.main(['--proyecto', str(suelta), 'conectar', '--json'])
        self.assertEqual((codigo, json.loads(out.getvalue())), (0, {'conectado': False, 'almacen': None, 'producto': None}))

    def test_av1_json_con_una_ruta_se_rechaza(self):
        antes = self.todo()
        codigo, _, error = self.en('conectar', '--json', str(self.almacen))
        self.assertNotEqual(codigo, 0)
        self.assertIn('--json', error)
        self.assertEqual(self.todo(), antes)

    # --- av2: la extensión reconoce y vigila un producto conectado --------------------------------------------------------
    @unittest.skipUnless(NODE, 'hace falta node')
    def test_av2_un_producto_conectado_muestra_su_cambio_y_vigila_el_almacen(self):
        self.bien('conectar', str(self.almacen))
        self.bien('nuevo', 'Notas compartidas', '--capacidad', 'notas', '--sufijo', 'vs')
        vista = self.vista(self.producto)
        [cambio] = vista['arbol']
        self.assertEqual(cambio['etiqueta'], 'Notas compartidas')
        self.assertEqual(cambio['hijos'][0]['descripcion'], 'próximo paso')
        bases = {(v['base'], v['patron']) for v in vista['vigias'] if isinstance(v, dict)}
        self.assertIn((str(self.almacen), '.factory/cambios/**/factory.json'), bases)
        self.assertIn((str(self.almacen), '.factory/despliegues/**/registro.json'), bases)
        self.assertFalse((self.producto / '.factory').exists())

    @unittest.skipUnless(NODE, 'hace falta node')
    def test_av2_si_no_se_puede_vigilar_el_almacen_la_vista_sigue(self):  # lo encontró el ensayo de la etapa 6
        self.bien('conectar', str(self.almacen))
        self.bien('nuevo', 'Notas compartidas', '--capacidad', 'notas', '--sufijo', 'vs')
        vista = self.vista(self.producto, SIN_RELATIVE_PATTERN='1')
        self.assertEqual([c['etiqueta'] for c in vista['arbol']], ['Notas compartidas'])
        self.assertFalse([v for v in vista['vigias'] if isinstance(v, dict)])

    @unittest.skipUnless(NODE, 'hace falta node')
    def test_av2_una_carpeta_sin_factory_sigue_igual_y_no_vigila_otra_cosa(self):
        vista = self.vista(self.producto)
        self.assertEqual(vista['arbol'], [{'etiqueta': 'Esta carpeta no es un proyecto de Factory (no tiene .factory/)', 'icono': 'info'}])
        self.assertFalse([v for v in vista['vigias'] if isinstance(v, dict)])

    def test_av2_se_activa_tambien_al_arrancar(self):
        eventos = json.loads((EXTENSION / 'package.json').read_text(encoding='utf-8'))['activationEvents']
        self.assertIn('onStartupFinished', eventos)
        self.assertIn('workspaceContains:.factory', eventos)


if __name__ == '__main__':
    unittest.main()
