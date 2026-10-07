import contextlib
import io
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from oracle_factory import cli as f


class SeleccionProyecto(unittest.TestCase):
    def test_init_preserva_configuracion_y_no_escribe_en_instalacion(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)/'proyecto';root.mkdir()
            (root/'oracle.json').write_text('{"catalogo_base": false, "perfiles": []}\n')
            (root/'.gitignore').write_text('mis-salidas/\n')
            module=Path(f.__file__);original=module.read_bytes()
            with patch.object(f,'ROOT',root),patch.object(f,'CHANGES',root/'openspec/changes'),contextlib.redirect_stdout(io.StringIO()):
                f.inicializar();f.inicializar()
            self.assertIn('false',(root/'oracle.json').read_text())
            self.assertEqual((root/'.gitignore').read_text(),'mis-salidas/\n.factory-demo/\n.factory/local/\n.factory/cambios/*/candidatos/*/clue/\n__pycache__/\n*.py[cod]\n')
            self.assertEqual(original,module.read_bytes())
            self.assertTrue((root/'tareas').is_dir())

    def test_ejemplo_distribuido_completo_y_sin_sobrescribir(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)
            with patch.object(f,'ROOT',root),contextlib.redirect_stdout(io.StringIO()):
                f.copiar_ejemplo(Path('notas'))
                with self.assertRaises(f.FactoryError):f.copiar_ejemplo(Path('notas'))
            source=Path(__file__).resolve().parents[1]/'examples/notas'
            for file in source.rglob('*'):
                if file.is_file() and '__pycache__' not in file.parts:
                    self.assertEqual(file.read_bytes(),(root/'notas'/file.relative_to(source)).read_bytes())
