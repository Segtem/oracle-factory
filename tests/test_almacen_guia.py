"""Registros fuera del repo del producto, etapa 5a: la guía de agentes y la skill van al producto sin versionar (ag1–ag2).

Mismo entorno que tests/test_almacen_commits.py (setUp y ayudantes): producto y almacén como repos Git temporales; HOME,
XDG_CONFIG_HOME, GIT_CONFIG_GLOBAL y GIT_CONFIG_SYSTEM en archivos y carpetas temporales."""
import contextlib
import io
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import test_almacen_commits as _commits  # noqa: E402
from oracle_factory import agentes as agentes_mod  # noqa: E402

f = _commits.f
SKILL = '.claude/skills/oracle-factory/SKILL.md'
RUTAS = ('AGENTS.md', 'CLAUDE.md', SKILL)


class AlmacenGuia(unittest.TestCase):
    git_en, arbol, configuraciones = _commits.AlmacenCommits.git_en, _commits.AlmacenCommits.arbol, _commits.AlmacenCommits.configuraciones

    def setUp(self):
        _commits.AlmacenCommits.setUp(self)

    def en(self, raiz, *args):
        out, err = io.StringIO(), io.StringIO()
        with patch('builtins.input', side_effect=['1'] * 8), contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            codigo = f.main(['--proyecto', str(raiz), *args])
        return codigo, out.getvalue() + err.getvalue()

    def bien(self, *args, raiz=None):
        codigo, impreso = self.en(raiz or self.producto, *args)
        self.assertEqual(codigo, 0, (args, impreso))
        return impreso

    def mal(self, *args, raiz=None):
        codigo, impreso = self.en(raiz or self.producto, *args)
        self.assertNotEqual(codigo, 0, (args, impreso))
        self.assertNotIn('Traceback', impreso)
        return impreso

    def exclusiones(self):
        ruta = self.producto / '.git/info/exclude'
        return ruta.read_text(encoding='utf-8') if ruta.exists() else ''

    def git_del_producto(self):
        """El .git del producto sin lo que Git reescribe solo al leer (el índice) ni el archivo de exclusiones."""
        return {n: v for n, v in self.arbol_git(self.producto).items() if n not in ('index', 'info/exclude')}

    def arbol_git(self, repo):
        git = repo / '.git'
        return {p.relative_to(git).as_posix(): p.read_bytes() for p in sorted(git.rglob('*')) if p.is_file()}

    def estado(self, repo=None):
        return self.git_en(repo or self.producto, 'status', '--porcelain', '--untracked-files=all')

    # --- ag1: con almacén, la guía y la skill van al producto sin versionar -------------------------------------------
    def test_ag1_la_guia_y_la_skill_quedan_en_el_producto_sin_versionar(self):
        self.bien('conectar', str(self.almacen))
        antes_git, antes_config = self.git_del_producto(), self.configuraciones()
        self.bien('agentes')
        self.bien('skill', '--instalar')
        for ruta in RUTAS:
            self.assertTrue((self.producto / ruta).is_file(), ruta)
        self.assertIn(agentes_mod.INICIO, (self.producto / 'AGENTS.md').read_text(encoding='utf-8'))
        self.assertIn('@AGENTS.md', (self.producto / 'CLAUDE.md').read_text(encoding='utf-8'))
        self.assertEqual(self.estado(), '')  # el repo no los ve
        lineas = self.exclusiones().splitlines()
        for ruta in RUTAS:
            self.assertIn(f'/{ruta}', lineas)
        self.assertEqual(self.configuraciones(), antes_config)
        self.assertEqual(self.git_del_producto(), antes_git)  # nada más en el .git del producto
        self.assertFalse((self.producto / '.gitignore').exists())
        for ruta in RUTAS:
            self.assertFalse((self.almacen / ruta).exists(), ruta)  # ya no van al almacén
        # otra vez: nada cambia y las exclusiones no se repiten
        excluido = self.exclusiones()
        self.bien('agentes')
        self.bien('skill', '--instalar')
        self.assertEqual(self.exclusiones(), excluido)
        self.assertEqual(self.exclusiones().count(f.almacenes.MARCA_EXCLUIR), 1)  # con su encabezado, una sola vez
        # lo que ya ignora el .gitignore del producto no se vuelve a excluir
        (self.producto / 'AGENTS.md').unlink()
        (self.producto / '.git/info/exclude').write_text('', encoding='utf-8')
        (self.producto / '.gitignore').write_text('AGENTS.md\n', encoding='utf-8')
        self.git_en(self.producto, 'add', '.gitignore')
        self.git_en(self.producto, 'commit', '-q', '-m', 'ignora AGENTS.md')
        self.bien('agentes')
        self.bien('skill', '--instalar')  # el archivo de exclusiones se vació arriba: vuelven la de CLAUDE.md y la de la skill
        self.assertNotIn('/AGENTS.md', self.exclusiones().splitlines())
        self.assertIn('/CLAUDE.md', self.exclusiones().splitlines())
        self.assertEqual(self.estado(), '')

    def test_ag1_desde_un_worktree_la_exclusion_es_la_comun(self):
        self.bien('conectar', str(self.almacen))
        trabajo = self.base / 'producto-wt'
        self.git_en(self.producto, 'worktree', 'add', '-q', '-b', 'otra', str(trabajo))
        self.bien('agentes', raiz=trabajo)
        self.assertTrue((trabajo / 'AGENTS.md').is_file())
        self.assertIn('/AGENTS.md', self.exclusiones().splitlines())  # el archivo común, en el .git del repo principal
        self.assertEqual(self.estado(trabajo), '')
        self.bien('agentes')  # y en el principal vale la misma exclusión
        self.assertEqual(self.estado(), '')

    def test_ag1_verificar_mira_la_guia_del_producto(self):
        self.bien('conectar', str(self.almacen))
        self.bien('agentes')
        self.assertIn('AGENTS.md', self.bien('agentes', '--verificar'))
        guia = self.producto / 'AGENTS.md'
        guia.write_text(guia.read_text(encoding='utf-8').replace('Trabajar con Oracle Factory', 'Trabajar con otra cosa'), encoding='utf-8')
        self.assertIn('AGENTS.md', self.mal('agentes', '--verificar'))
        self.bien('agentes')
        self.bien('agentes', '--verificar')

    def test_ag1_sin_almacen_aparte_escribe_donde_siempre(self):
        self.bien('init')
        self.bien('agentes')
        self.bien('skill', '--instalar')
        for ruta in RUTAS:
            self.assertTrue((self.producto / ruta).is_file(), ruta)
        self.assertNotIn('AGENTS.md', self.exclusiones())
        estado = self.estado()
        self.assertIn('AGENTS.md', estado)  # como siempre: quedan para versionar con el proyecto
        self.assertNotIn('almacén aparte', (self.producto / 'AGENTS.md').read_text(encoding='utf-8'))

    # --- ag2: no pisa lo que el producto versiona, y la guía dice del almacén --------------------------------------------
    def test_ag2_el_producto_ya_versiona_su_guia_o_su_skill(self):
        for ruta, comando in (('AGENTS.md', ('agentes',)), ('CLAUDE.md', ('agentes',)), (SKILL, ('skill', '--instalar')),
                              (SKILL, ('skill', '--instalar', '--forzar'))):  # ni con --forzar
            with self.subTest(ruta=ruta):
                archivo = self.producto / ruta
                archivo.parent.mkdir(parents=True, exist_ok=True)
                archivo.write_text('la del equipo\n', encoding='utf-8')
                self.git_en(self.producto, 'add', ruta)
                self.git_en(self.producto, 'commit', '-q', '-m', f'el equipo versiona {ruta}')
                if not f.almacenes.leer().get(f.almacenes.clave(self.producto)):
                    self.bien('conectar', str(self.almacen))
                antes, excluido = self.git_del_producto(), self.exclusiones()
                impreso = self.mal(*comando)
                self.assertIn(ruta, impreso)
                self.assertEqual(archivo.read_text(encoding='utf-8'), 'la del equipo\n')
                self.assertEqual((self.git_del_producto(), self.exclusiones()), (antes, excluido))
                self.git_en(self.producto, 'rm', '-q', ruta)
                self.git_en(self.producto, 'commit', '-q', '-m', f'saca {ruta}')

    def test_ag2_la_guia_dice_que_los_registros_viven_en_un_almacen_aparte(self):
        self.bien('conectar', str(self.almacen))
        self.bien('agentes')
        texto = (self.producto / 'AGENTS.md').read_text(encoding='utf-8')
        self.assertIn('almacén aparte', texto)
        self.assertIn('oracle-factory sincronizar', texto)
        self.assertNotIn('almacén aparte', agentes_mod.bloque('confirmacion'))  # sin almacén, la guía de siempre
        # un AGENTS.md que es un enlace simbólico no se sigue
        ajeno = self.base / 'ajeno.md'
        ajeno.write_text('de otro lado\n', encoding='utf-8')
        (self.producto / 'AGENTS.md').unlink()
        (self.producto / 'AGENTS.md').symlink_to(ajeno)
        self.assertIn('enlace', self.mal('agentes'))
        self.assertEqual(ajeno.read_text(encoding='utf-8'), 'de otro lado\n')


if __name__ == '__main__':
    unittest.main()
