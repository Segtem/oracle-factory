"""Un clon sin conectar se niega a trabajar: el producto marca dónde está su almacén (mk1–mk3).

Mismo entorno que tests/test_almacen_commits.py: producto y almacén como repos Git temporales, con HOME, XDG y la configuración
global de Git temporales. El almacén tiene un remoto `origin` (un repo desnudo temporal) cuando la prueba lo necesita."""
import json
from pathlib import Path
import shutil
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import test_almacen_migrar as _migrar  # noqa: E402
import test_preparar_migracion as _pm  # noqa: E402

MARCA = '.oracle-factory-almacen'


def sin_heredados(clase, base):
    """Las pruebas de `base` no se repiten en `clase`: acá sólo interesa su entorno (setUp y ayudantes)."""
    for nombre in dir(base):
        if nombre.startswith('test_') and nombre not in vars(clase):
            setattr(clase, nombre, None)
    return clase


class ConOrigen(_pm.Conectado):
    def setUp(self):
        super().setUp()
        self.remoto = self.base / 'registros.git'
        self.git_en(self.base, 'init', '-q', '--bare', str(self.remoto))
        self.url = self.remoto.as_uri()
        self.git_en(self.almacen, 'remote', 'add', 'origin', self.url)

    def marca(self, raiz=None):
        ruta = (raiz or self.producto) / MARCA
        return ruta.read_text(encoding='utf-8') if ruta.exists() else None

    def marcado_y_commiteado(self):
        self.bien('conectar', str(self.almacen))
        self.git_en(self.producto, 'add', MARCA)
        self.git_en(self.producto, 'commit', '-q', '-m', 'marca del almacén')

    def todo(self, raiz):
        return self.arbol(raiz), self.git_en(raiz, 'status', '--porcelain', '--untracked-files=all'), self.arbol(self.casa)


# --- mk1: el producto marca su almacén ------------------------------------------------------------------------------------
class MigrarMarca(_migrar.AlmacenMigrar):
    def test_mk1_migrar_marca_el_producto(self):
        remoto = self.base / 'registros.git'
        self.git_en(self.base, 'init', '-q', '--bare', str(remoto))
        self.git_en(self.almacen, 'remote', 'add', 'origin', remoto.as_uri())
        self.assertIn(MARCA, self.bien('migrar', '--almacen', str(self.almacen), '--verificar'))
        self.assertFalse((self.producto / MARCA).exists())  # verificar no escribe
        self.bien('migrar', '--almacen', str(self.almacen))
        self.assertEqual((self.producto / MARCA).read_text(encoding='utf-8'), remoto.as_uri() + '\n')
        indice = self.git_en(self.producto, 'diff', '--cached', '--name-status').splitlines()
        self.assertIn(f'A\t{MARCA}', indice)
        self.assertEqual(self.git_en(self.producto, 'log', '-1', '--format=%s'), 'registros adentro')  # sin commitear

    def test_mk1_migrar_a_un_almacen_sin_remoto_no_marca(self):
        salida = self.bien('migrar', '--almacen', str(self.almacen))
        self.assertFalse((self.producto / MARCA).exists())
        self.assertIn('origin', salida)


sin_heredados(MigrarMarca, _migrar.AlmacenMigrar)


class ConectarMarca(ConOrigen):
    def test_mk1_conectar_marca_un_producto_ya_conectado(self):
        self.bien('conectar', str(self.almacen))
        (self.producto / MARCA).unlink()
        salida = self.bien('conectar', str(self.almacen))  # ya conectado: igual marca
        self.assertEqual(self.marca(), self.url + '\n')
        self.assertIn(f'?? {MARCA}', self.git_en(self.producto, 'status', '--porcelain'))
        self.assertIn('commit', salida.casefold())

    def test_mk1_conectar_un_almacen_sin_remoto_no_marca(self):
        self.git_en(self.almacen, 'remote', 'remove', 'origin')
        salida = self.bien('conectar', str(self.almacen))
        self.assertIsNone(self.marca())
        self.assertIn('origin', salida)

    def test_mk1_un_agente_no_marca(self):
        self.bien('conectar', str(self.almacen))
        (self.producto / MARCA).unlink()
        self.mal('--agente', 'claude-code', 'conectar', str(self.almacen))
        self.assertIsNone(self.marca())


# --- mk2: sin conexión, el producto marcado se niega ----------------------------------------------------------------------
class SinConexion(ConOrigen):
    def setUp(self):
        super().setUp()
        self.marcado_y_commiteado()
        self.clon = self.base / 'clon'
        self.git_en(self.base, 'clone', '-q', str(self.producto), str(self.clon))

    def test_mk2_un_clon_limpio_se_niega(self):
        for comando in (['listar'], ['nuevo', '--capacidad', 'x', '--sufijo', 'pr', 'Prueba'], ['init']):
            antes = self.todo(self.clon)
            error = self.mal(*comando, raiz=self.clon)
            self.assertIn(self.url, error, comando)
            self.assertIn('oracle-factory conectar', error, comando)
            self.assertEqual(self.todo(self.clon), antes, comando)
            self.assertFalse((self.clon / '.factory').exists(), comando)

    def test_mk2_una_copia_movida_se_niega(self):
        copia = self.base / 'copia'
        shutil.copytree(self.producto, copia, symlinks=True)
        antes = self.todo(copia)
        self.assertIn(self.url, self.mal('estado', 'x', raiz=copia))
        self.assertEqual(self.todo(copia), antes)

    def test_mk2_conectar_sigue_funcionando(self):
        self.bien('conectar', str(self.almacen), raiz=self.clon)
        self.bien('listar', raiz=self.clon)
        self.assertEqual(json.loads(self.bien('conectar', '--json', raiz=self.clon).split('\n')[0])['almacen'], str(self.almacen))


# --- mk3: una marca que no coincide se avisa ------------------------------------------------------------------------------
class OtraMarca(ConOrigen):
    def test_mk3_conectado_a_otro_almacen_avisa_y_sigue(self):
        self.marcado_y_commiteado()
        self.git_en(self.almacen, 'remote', 'set-url', 'origin', 'git@example.invalid:otro/registros.git')
        salida = self.bien('listar')
        self.assertIn('no coincide', salida)
        self.assertIn(self.url, salida)


sin_heredados(ConOrigen, _pm.Conectado)
sin_heredados(ConectarMarca, _pm.Conectado)
sin_heredados(SinConexion, _pm.Conectado)
sin_heredados(OtraMarca, _pm.Conectado)


if __name__ == '__main__':
    unittest.main()
