"""Migrar se niega ante un repo anidado (ma1) y la guía dice si está en el repo (ma2).

Mismo entorno que tests/test_almacen_migrar.py y tests/test_preparar_migracion.py: producto y almacén como repos Git temporales,
HOME, XDG y la configuración global de Git temporales."""
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import test_almacen_migrar as _migrar  # noqa: E402
import test_preparar_migracion as _pm  # noqa: E402
from oracle_factory import agentes as agentes_mod  # noqa: E402

EXCLUIDA = 'excluidas de Git'


def sin_heredados(clase, base):
    """Las pruebas de `base` no se repiten en `clase`: acá sólo interesa su entorno (setUp y ayudantes)."""
    for nombre in dir(base):
        if nombre.startswith('test_') and nombre not in vars(clase):
            setattr(clase, nombre, None)
    return clase


# --- ma1: migrar se niega ante un repo anidado ------------------------------------------------------------------------------
class Anidados(_migrar.AlmacenMigrar):
    def setUp(self):
        super().setUp()
        self.anidado = self.producto / '.factory/local/revision/checkout'
        self.anidado.mkdir(parents=True)
        self.git_en(self.anidado, 'init', '-q')
        (self.anidado / 'x.txt').write_text('x\n', encoding='utf-8')

    def test_ma1_un_repo_anidado_en_lo_local_no_migra(self):
        error = self.negado()
        self.assertIn('.factory/local/revision/checkout', error)
        self.assertIn('sac', error.casefold())

    def test_ma1_verificar_lo_anuncia_y_no_escribe(self):
        self.assertIn('.factory/local/revision/checkout', self.negado('--verificar'))

    def test_ma1_si_git_lista_los_archivos_del_repo_anidado_tambien_lo_ve(self):  # MA1-001: según la versión de Git
        from oracle_factory import almacenes
        nombres = ['.factory/local/nota.txt', '.factory/local/revision/checkout/x.txt', '.factory/local/revision/checkout/sub/y.txt']
        self.assertEqual(almacenes._anidados(self.producto, nombres), ['.factory/local/revision/checkout'])
        self.assertEqual(almacenes._anidados(self.producto, ['.factory/local/nota.txt']), [])

    def test_ma1_un_worktree_de_otro_repo_sigue_registrado(self):
        import shutil
        shutil.rmtree(self.anidado)
        otro = self.base / 'otro'
        self.git_en(self.base, 'init', '-q', str(otro))
        (otro / 'a.txt').write_text('a\n', encoding='utf-8')
        self.git_en(otro, 'add', 'a.txt')
        self.git_en(otro, 'commit', '-q', '-m', 'a')
        self.git_en(otro, 'worktree', 'add', '-q', '--detach', str(self.anidado))
        self.assertIn('.factory/local/revision/checkout', self.negado())
        self.assertIn(str(self.anidado), self.git_en(otro, 'worktree', 'list'))
        self.assertEqual(self.git_en(self.anidado, 'status', '--porcelain'), '')


# --- ma2: la guía dice si está en el repo -----------------------------------------------------------------------------------
class GuiaVersionada(_pm.GuiaVersionada):
    def test_ma2_una_guia_versionada_dice_que_es_parte_del_producto(self):
        self.bien('agentes', '--en-el-repo')
        guia = (self.producto / 'AGENTS.md').read_text(encoding='utf-8')
        self.assertIn('almacén aparte', guia)
        self.assertIn('agentes --en-el-repo', guia)
        self.assertIn('parte del producto', guia)
        self.assertNotIn(EXCLUIDA, guia)
        self.bien('agentes', '--verificar')


class GuiaExcluida(_pm.Conectado):
    def setUp(self):
        super().setUp()
        self.bien('conectar', str(self.almacen))

    def test_ma2_una_guia_no_versionada_dice_que_esta_excluida(self):
        self.bien('agentes')
        guia = (self.producto / 'AGENTS.md').read_text(encoding='utf-8')
        self.assertIn(EXCLUIDA, guia)
        self.assertNotIn('parte del producto', guia)
        self.bien('agentes', '--verificar')

    def test_ma2_los_dos_textos_son_distintos(self):
        self.assertNotEqual(agentes_mod.bloque('confirmacion', con_almacen=True),
                            agentes_mod.bloque('confirmacion', con_almacen=True, versionada=True))


sin_heredados(Anidados, _migrar.AlmacenMigrar)  # el repo anidado haría negarse a mg1–mg4 a propósito
sin_heredados(GuiaVersionada, _pm.GuiaVersionada)
sin_heredados(GuiaExcluida, _pm.Conectado)


if __name__ == '__main__':
    unittest.main()
