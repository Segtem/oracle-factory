"""pc1–pc2: `oracle-factory proyecto --json` dice a una interfaz si la carpeta es de Factory y dónde están sus registros (pc1), y quién
contesta, sin escribir nada (pc2). Producto, almacén y casa son los repos temporales de tests/test_almacen_commits.py."""
import contextlib
import io
import json
import os
import shutil
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import test_almacen_vscode as _vscode  # noqa: E402

f = _vscode.f


class Base(_vscode.AlmacenVscode):
    def proyecto(self, carpeta, *antes):
        """`proyecto --json` corrido desde `carpeta`, sin --proyecto: como lo corre una interfaz en la carpeta que abrió."""
        os.chdir(carpeta)
        out = io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(io.StringIO()):
            codigo = f.main([*antes, 'proyecto', '--json'])
        self.assertEqual(codigo, 0)
        return json.loads(out.getvalue())

    def conectado(self):
        (self.almacen / '.factory').mkdir()
        self.bien('conectar', str(self.almacen))


for _nombre in [n for n in dir(_vscode.AlmacenVscode) if n.startswith('test_')]:
    setattr(Base, _nombre, None)
del _nombre


class CarpetaPc1(Base):
    def test_pc1_los_registros_en_el_repo(self):
        (self.producto / '.factory').mkdir()
        (self.producto / 'src').mkdir()
        for carpeta in (self.producto, self.producto / 'src'):
            with self.subTest(carpeta=carpeta.name):
                datos = self.proyecto(carpeta)
                self.assertEqual(datos['esquema'], 'oracle-factory.proyecto/1')
                self.assertEqual({k: datos[k] for k in ('factory', 'producto', 'registros', 'almacen', 'problema')},
                                 {'factory': True, 'producto': str(self.producto), 'registros': str(self.producto), 'almacen': None,
                                  'problema': None})

    def test_pc1_un_producto_conectado_a_un_almacen(self):
        self.conectado()
        datos = self.proyecto(self.producto)
        self.assertEqual({k: datos[k] for k in ('factory', 'producto', 'registros', 'almacen', 'problema')},
                         {'factory': True, 'producto': str(self.producto), 'registros': str(self.almacen),
                          'almacen': str(self.almacen), 'problema': None})

    def test_pc1_una_carpeta_sin_factory(self):
        suelta = self.base / 'suelta'
        suelta.mkdir()
        for carpeta, producto in ((self.producto, str(self.producto)), (suelta, None)):
            with self.subTest(carpeta=carpeta.name):
                datos = self.proyecto(carpeta)
                self.assertEqual((datos['factory'], datos['producto'], datos['registros'], datos['almacen']), (False, producto, None, None))

    def test_pc1_un_almacen_que_no_esta(self):
        self.conectado()
        shutil.rmtree(self.almacen / '.factory')
        datos = self.proyecto(self.producto)
        self.assertEqual((datos['factory'], datos['registros'], datos['almacen']), (False, None, str(self.almacen)))
        self.assertIn(str(self.almacen), datos['problema'])
        destino = self.base / 'otro'
        self.almacen.rename(destino)
        datos = self.proyecto(self.producto)
        self.assertFalse(datos['factory'])
        self.assertIn(str(self.almacen), datos['problema'])

    def test_pc1_un_producto_marcado_sin_conectar(self):
        (self.producto / '.oracle-factory-almacen').write_text('git@ejemplo:equipo/registros.git\n', encoding='utf-8')
        datos = self.proyecto(self.producto)
        self.assertEqual((datos['factory'], datos['registros'], datos['almacen']), (False, None, None))
        self.assertIn('git@ejemplo:equipo/registros.git', datos['problema'])


class QuienContestaPc2(Base):
    def test_pc2_la_version_y_los_contratos(self):
        self.conectado()
        datos = self.proyecto(self.producto)
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            with self.assertRaises(SystemExit):
                f.main(['--version'])
        self.assertEqual(f'oracle-factory {datos["version"]}', out.getvalue().strip())
        self.assertEqual(datos['contratos']['proyecto'], datos['esquema'])
        from oracle_factory import resumen, tablero
        self.assertEqual(datos['contratos']['tablero'], tablero.ESQUEMA)
        self.assertEqual(datos['contratos']['resumen'], resumen.ESQUEMA)

    def test_pc2_no_escribe(self):
        self.conectado()
        antes = self.todo()
        self.proyecto(self.producto)
        self.proyecto(self.producto, '--agente', 'robot')
        self.assertEqual(self.todo(), antes)


if __name__ == '__main__':
    unittest.main()
