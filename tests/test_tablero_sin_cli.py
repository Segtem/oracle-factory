"""sc1: en una carpeta sin indicios de Factory, una CLI que falla no se muestra como error (el CI de main, sin la CLI instalada,
dio rojo en test_vs1 después de confianza-del-tablero); con un indicio, la falla se sigue nombrando."""
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import test_confianza_del_tablero as _ct  # noqa: E402

NO_ES = {'etiqueta': 'Esta carpeta no es un proyecto de Factory (no tiene .factory/)', 'icono': 'info'}


class Base(_ct.Base):
    def rota(self):
        rota = self.base / 'rota.sh'
        rota.write_text('#!/bin/sh\necho "la CLI se rompió" >&2\nexit 3\n')
        rota.chmod(0o755)
        return rota

    def vista_con(self, cli):
        self.cli = cli
        return self.vista(self.producto)


for _nombre in [n for n in dir(_ct.Base) if n.startswith('test_')]:
    setattr(Base, _nombre, None)
del _nombre


@unittest.skipUnless(_ct.NODE, 'hace falta node')
class CarpetaAjenaSc1(Base):
    def test_sc1_sin_la_cli_instalada(self):
        ausente = self.base / 'no-existe' / 'oracle-factory'
        self.assertEqual(self.vista_con(ausente)['arbol'], [NO_ES])
        html = self.tablero(self.producto, cli=ausente)['html']
        self.assertIn('no es un proyecto de Factory', html)
        self.assertNotIn('ENOENT', html)

    def test_sc1_una_cli_que_se_rompe_en_una_carpeta_ajena(self):
        self.assertEqual(self.vista_con(self.rota())['arbol'], [NO_ES])

    def test_sc1_con_un_indicio_la_falla_se_nombra(self):
        (self.producto / '.factory').mkdir()
        [fila] = self.vista_con(self.base / 'no-existe' / 'oracle-factory')['arbol']
        self.assertEqual(fila['icono'], 'error')
        self.assertIn('ENOENT', fila['etiqueta'])
        [fila] = self.vista_con(self.rota())['arbol']
        self.assertIn('la CLI se rompió', fila['etiqueta'])


if __name__ == '__main__':
    unittest.main()
