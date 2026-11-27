"""ct1–ct2: la extensión de VS Code en una carpeta que no es de confianza avisa sin correr nada (ct1), y con confianza encuentra los
registros con `oracle-factory proyecto --json` y nombra una CLI que no la entiende (ct2). El 27/11, Jam abierto con `factory-code .`
en modo restringido no mostró nada de Factory. Corre la extensión en node con los `vscode` falsos de tests/*_en_node.cjs."""
import json
import os
from pathlib import Path
import subprocess
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import test_almacen_vscode as _vscode  # noqa: E402

SOURCE, EXTENSION, NODE = _vscode.SOURCE, _vscode.EXTENSION, _vscode.NODE
RESTRINGIDO = 'confiá en la carpeta'


class Base(_vscode.AlmacenVscode):
    def tablero(self, proyecto, mensajes=(), cli=None, **entorno):
        r = subprocess.run([NODE, str(SOURCE / 'tests/tablero_en_node.cjs'), str(EXTENSION), str(proyecto), json.dumps(list(mensajes)),
                            str(cli or self.cli)], capture_output=True, text=True, timeout=180, env={**os.environ, **entorno})
        self.assertEqual(r.returncode, 0, r.stderr)
        return json.loads(r.stdout)

    def proyecto_real(self):
        """Un producto conectado a su almacén, con un cambio abierto. El almacén temporal no tiene origin, así que `conectar` no
        escribe la marca que tiene un producto real: se escribe acá."""
        self.bien('conectar', str(self.almacen))
        (self.producto / '.oracle-factory-almacen').write_text('git@ejemplo:equipo/registros.git\n', encoding='utf-8')
        self.bien('nuevo', 'Notas compartidas', '--capacidad', 'notas', '--sufijo', 'vs')

    def cli_falsa(self, respuesta_proyecto):
        """Una CLI que contesta `--version` y, a `proyecto --json`, lo que se le pida (None: no conoce el comando, como una vieja)."""
        falsa = self.base / 'oracle-factory-falsa'
        proyecto = (f"echo '{json.dumps(respuesta_proyecto)}'" if respuesta_proyecto is not None
                    else "echo \"oracle-factory: error: argument comando: invalid choice: 'proyecto'\" >&2; exit 2")
        falsa.write_text('#!/bin/sh\ncase "$1" in\n  --version) echo "oracle-factory 0.1.0a9";;\n'
                         f'  proyecto) {proyecto};;\n  *) echo "{{}}";;\nesac\n', encoding='utf-8')
        falsa.chmod(0o755)
        return falsa


for _nombre in [n for n in dir(_vscode.AlmacenVscode) if n.startswith('test_')]:
    setattr(Base, _nombre, None)
del _nombre


@unittest.skipUnless(NODE, 'hace falta node')
class RestringidoCt1(Base):
    def sin_confianza(self, proyecto):
        vista = self.vista(proyecto, SIN_CONFIANZA='1')
        self.assertEqual(vista['procesos'], [])
        [fila] = vista['arbol']
        tablero = self.tablero(proyecto, [{'tipo': 'confiar'}, {'tipo': 'terminal', 'comando': 'oracle-factory listar'}], SIN_CONFIANZA='1')
        self.assertEqual(tablero['procesos'], [])
        self.assertEqual(tablero['terminal'], [])  # sin confianza tampoco escribe en una terminal
        return fila, tablero

    def test_ct1_jam_sin_confianza(self):
        (self.producto / '.factory').mkdir()
        fila, tablero = self.sin_confianza(self.producto)
        self.assertIn(RESTRINGIDO, fila['etiqueta'])
        self.assertEqual(fila['ejecuta'], 'workbench.trust.manage')
        self.assertIn(RESTRINGIDO, tablero['html'])
        self.assertEqual(tablero['ejecutados'], ['workbench.trust.manage'])

    def test_ct1_un_producto_con_almacen_sin_confianza(self):
        (self.producto / '.oracle-factory-almacen').write_text('git@ejemplo:equipo/registros.git\n', encoding='utf-8')
        fila, tablero = self.sin_confianza(self.producto)
        self.assertIn(RESTRINGIDO, fila['etiqueta'])
        self.assertIn(RESTRINGIDO, tablero['html'])

    def test_ct1_una_carpeta_ajena_sin_confianza(self):
        fila, tablero = self.sin_confianza(self.producto)
        self.assertEqual(fila, {'etiqueta': 'Esta carpeta no es un proyecto de Factory (no tiene .factory/)', 'icono': 'info'})
        self.assertNotIn(RESTRINGIDO, tablero['html'])

    def test_ct1_al_confiar(self):
        self.proyecto_real()
        vista = self.vista(self.producto, SIN_CONFIANZA='1', CONFIAR='1')
        self.assertEqual(vista['procesosAntesDeConfiar'], 0)
        self.assertIn(RESTRINGIDO, vista['arbol'][0]['etiqueta'])
        self.assertEqual([c['etiqueta'] for c in vista['arbolDespues']], ['Notas compartidas'])
        tablero = self.tablero(self.producto, SIN_CONFIANZA='1', CONFIAR='1')
        self.assertEqual(tablero['procesosAntesDeConfiar'], 0)
        self.assertIn('Notas compartidas', tablero['htmlConfiado'])

    def test_ct1_la_extension_declara_el_modo_limitado(self):
        paquete = json.loads((EXTENSION / 'package.json').read_text(encoding='utf-8'))
        confianza = paquete['capabilities']['untrustedWorkspaces']
        self.assertEqual(confianza['supported'], 'limited')
        self.assertIn('factory.comando', confianza['restrictedConfigurations'])


@unittest.skipUnless(NODE, 'hace falta node')
class NucleoCt2(Base):
    def test_ct2_un_producto_con_almacen(self):
        self.proyecto_real()
        vista = self.vista(self.producto)
        self.assertIn(f'{self.cli} proyecto --json', vista['procesos'])
        self.assertNotIn(f'{self.cli} conectar --json', vista['procesos'])
        self.assertEqual([c['etiqueta'] for c in vista['arbol']], ['Notas compartidas'])
        self.assertIn('Notas compartidas', self.tablero(self.producto)['html'])

    def test_ct2_se_activa_con_los_dos_marcadores(self):
        eventos = json.loads((EXTENSION / 'package.json').read_text(encoding='utf-8'))['activationEvents']
        self.assertIn('workspaceContains:.factory', eventos)
        self.assertIn('workspaceContains:.oracle-factory-almacen', eventos)

    def test_ct2_una_cli_vieja(self):
        (self.producto / '.factory').mkdir()
        falsa = self.cli_falsa(None)
        r = subprocess.run([NODE, str(SOURCE / 'tests/vscode_en_node.cjs'), str(EXTENSION), str(self.producto), str(falsa)],
                           capture_output=True, text=True, timeout=180)
        self.assertEqual(r.returncode, 0, r.stderr)
        [fila] = json.loads(r.stdout)['arbol']
        self.assertIn('0.1.0a9', fila['etiqueta'])
        self.assertIn('proyecto', fila['etiqueta'])
        self.assertIn('actualiz', fila['etiqueta'])
        html = self.tablero(self.producto, cli=falsa)['html']
        self.assertIn('0.1.0a9', html)

    def test_ct2_otro_contrato(self):
        falsa = self.cli_falsa({'esquema': 'oracle-factory.proyecto/1', 'factory': True, 'producto': str(self.producto),
                                'registros': str(self.producto), 'almacen': None, 'problema': None, 'version': '9.9.9',
                                'contratos': {'proyecto': 'oracle-factory.proyecto/1', 'tablero': 'oracle-factory.tablero/2'}})
        html = self.tablero(self.producto, cli=falsa)['html']
        self.assertIn('oracle-factory.tablero/2', html)
        self.assertIn('oracle-factory.tablero/1', html)
        self.assertIn('9.9.9', html)
        self.assertNotIn('<section', html)  # no pinta datos que no entiende


if __name__ == '__main__':
    unittest.main()
