"""Registros fuera del repo del producto, etapa 4a: escenarios ac1–ac2 de la spec (Factory commitea en el almacén).

Se corre la CLI en el mismo proceso (`f.main`). El producto y el almacén son repos Git temporales; HOME y XDG_CONFIG_HOME
apuntan a un directorio temporal, y GIT_CONFIG_GLOBAL y GIT_CONFIG_SYSTEM a archivos temporales: ninguna prueba lee ni
escribe el HOME real ni el ~/.gitconfig real. La identidad «ya configurada» es la del archivo global temporal.
"""
import contextlib
import io
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import test_archivo as _archivo  # noqa: E402

f = _archivo.f
GIT = _archivo.GIT  # sólo para lo que arma la fixture: Factory commitea con la identidad configurada, no con ésta
NOMBRE, CORREO = 'Persona Almacen', 'almacen@example.invalid'


class AlmacenCommits(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        base = Path(self.tmp.name).resolve()
        self.base = base
        self.producto, self.almacen, self.casa = base / 'producto', base / 'almacen', base / 'casa'
        for carpeta in (self.producto, self.almacen, self.casa):
            carpeta.mkdir()
        self.git_global, self.git_vacio = base / 'gitconfig-global', base / 'gitconfig-vacio'
        self.git_global.write_text(f'[user]\n\tname = {NOMBRE}\n\temail = {CORREO}\n', encoding='utf-8')
        self.git_vacio.write_text('', encoding='utf-8')
        limpio = {k: v for k, v in os.environ.items() if not k.startswith('GIT_') and k not in ('EMAIL', 'FACTORY_AGENTE')}
        entorno = patch.dict(os.environ, {**limpio, 'HOME': str(self.casa), 'XDG_CONFIG_HOME': str(self.casa / '.config'),
                                          'GIT_CONFIG_GLOBAL': str(self.git_global), 'GIT_CONFIG_SYSTEM': str(self.git_vacio)}, clear=True)
        entorno.start(); self.addCleanup(entorno.stop)
        self.addCleanup(os.chdir, os.getcwd())
        for nombre, valor in [('ROOT', self.producto), ('CHANGES', self.producto / 'openspec/changes'), ('AGENTE', None),
                              ('REGISTROS', self.producto)]:
            p = patch.object(f, nombre, valor, create=True); p.start(); self.addCleanup(p.stop)
        p = patch.object(f, 'terminal_interactiva', return_value=True); p.start(); self.addCleanup(p.stop)
        self.git_en(self.producto, 'init', '-q', '-b', 'main')
        (self.producto / 'README.md').write_text('producto\n', encoding='utf-8')
        self.git_en(self.producto, 'add', '-A')
        self.git_en(self.producto, 'commit', '-q', '-m', 'producto inicial')
        self.git_en(self.almacen, 'init', '-q', '-b', 'main')
        (self.almacen / 'notas.md').write_text('notas del equipo\n', encoding='utf-8')
        self.git_en(self.almacen, 'add', '-A')
        self.git_en(self.almacen, 'commit', '-q', '-m', 'almacén inicial')

    # --- ayudantes -----------------------------------------------------------------
    def git_en(self, carpeta, *args):
        return subprocess.run([*GIT, '-c', 'core.quotepath=false', *args], cwd=carpeta, check=True, capture_output=True, text=True).stdout.strip()

    def corre(self, *args, agente=None):
        out, err = io.StringIO(), io.StringIO()
        base = (['--agente', agente] if agente else []) + ['--proyecto', str(self.producto)]
        with patch('builtins.input', side_effect=['1'] * 8), contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            codigo = f.main([*base, *args])
        return codigo, out.getvalue(), err.getvalue()

    def bien(self, *args, **kw):
        codigo, salida, error = self.corre(*args, **kw)
        self.assertEqual(codigo, 0, (args, error))
        return salida + error

    def arbol(self, raiz):
        return {p.relative_to(raiz).as_posix(): p.read_bytes() for p in sorted(raiz.rglob('*'))
                if p.is_file() and '.git' not in p.relative_to(raiz).parts}

    def commits(self, repo=None):
        return int(self.git_en(repo or self.almacen, 'rev-list', '--count', 'HEAD'))

    def estado_git(self, repo=None):
        return self.git_en(repo or self.almacen, 'status', '--porcelain', '--untracked-files=all')

    def archivos_del_ultimo(self):
        return set(self.git_en(self.almacen, 'show', '--name-only', '--format=', 'HEAD').splitlines())

    def mensaje_del_ultimo(self):
        return self.git_en(self.almacen, 'log', '-1', '--format=%B').strip().splitlines()

    def configuraciones(self):
        """Toda configuración de Git a la vista: la de cada repo y las dos de usuario/sistema (temporales)."""
        return {str(p): p.read_bytes() for p in (self.producto / '.git/config', self.almacen / '.git/config', self.git_global, self.git_vacio)}

    def comando_que_escribe(self, *args, **kw):
        """Corre el comando y devuelve (rutas del almacén que creó, modificó o borró; lo que imprimió)."""
        antes = self.arbol(self.almacen)
        impreso = self.bien(*args, **kw)
        despues = self.arbol(self.almacen)
        return {n for n in antes.keys() | despues.keys() if antes.get(n) != despues.get(n)}, impreso

    def conectado_con_un_cambio(self):
        self.bien('conectar', str(self.almacen))
        self.bien('nuevo', 'Notas', '--capacidad', 'notas', '--sufijo', 'ac', agente='claude-code')
        return next(p.name for p in (self.almacen / 'openspec/changes').iterdir() if p.is_dir())

    def registro(self, ident):
        return (self.almacen / f'.factory/cambios/{ident}/factory.json').read_text(encoding='utf-8')

    # --- ac1: con almacén aparte, cada comando que escribe deja su commit ----------------------------------------------
    def test_ac1_un_comando_que_escribe_deja_un_commit_con_sus_archivos_y_su_mensaje(self):
        self.bien('conectar', str(self.almacen))
        self.assertEqual(self.estado_git(), '')  # conectar también escribe en el almacén: lo suyo queda commiteado
        cuenta = self.commits()
        tocados, _ = self.comando_que_escribe('nuevo', 'Notas', '--capacidad', 'notas', '--sufijo', 'ac', agente='claude-code')
        ident = next(p.name for p in (self.almacen / 'openspec/changes').iterdir() if p.is_dir())
        self.assertTrue(tocados)
        self.assertEqual(self.commits(), cuenta + 1)
        self.assertEqual(self.archivos_del_ultimo(), tocados)
        lineas = self.mensaje_del_ultimo()
        self.assertIn('nuevo', lineas[0])
        self.assertEqual(lineas[-3:], [f'Cambio: {ident}', 'Comando: nuevo', 'Actor: claude-code (agente)'])
        self.assertEqual(self.estado_git(), '')

        tocados, _ = self.comando_que_escribe('mensaje', ident, 'hola equipo', agente='claude-code')
        self.assertTrue(tocados)
        self.assertEqual(self.commits(), cuenta + 2)
        self.assertEqual(self.archivos_del_ultimo(), tocados)
        lineas = self.mensaje_del_ultimo()
        self.assertIn('mensaje', lineas[0])
        self.assertIn(ident, '\n'.join(lineas))
        self.assertEqual(lineas[-3:], [f'Cambio: {ident}', 'Comando: mensaje', 'Actor: claude-code (agente)'])
        self.assertEqual(self.estado_git(), '')
        self.assertEqual(self.estado_git(self.producto), '')  # y en el producto no se commitea ni se escribe nada
        self.assertEqual(self.commits(self.producto), 1)

    def test_ac1_una_persona_queda_como_actor_y_un_comando_sin_cambio_no_lleva_la_linea_cambio(self):
        cuenta = self.commits()
        self.bien('conectar', str(self.almacen))
        self.assertEqual(self.commits(), cuenta + 1)
        lineas = self.mensaje_del_ultimo()
        self.assertIn('conectar', lineas[0])
        self.assertEqual(lineas[-2:], ['Comando: conectar', f'Actor: {NOMBRE} (persona)'])
        self.assertFalse([linea for linea in lineas if linea.startswith('Cambio:')])
        self.bien('nuevo', 'Notas', '--capacidad', 'notas', '--sufijo', 'ac')
        ident = next(p.name for p in (self.almacen / 'openspec/changes').iterdir() if p.is_dir())
        self.bien('tomar', ident)
        self.assertEqual(self.mensaje_del_ultimo()[-3:], [f'Cambio: {ident}', 'Comando: tomar', f'Actor: {NOMBRE} (persona)'])

    def test_ac1_con_registros_explicito_tambien_se_commitea(self):
        self.bien('--registros', str(self.almacen), 'init')
        self.assertEqual(self.estado_git(), '')
        cuenta = self.commits()
        tocados, _ = self.comando_que_escribe('--registros', str(self.almacen), 'nuevo', 'Notas', '--capacidad', 'notas', '--sufijo', 'ac')
        self.assertEqual(self.commits(), cuenta + 1)
        self.assertEqual(self.archivos_del_ultimo(), tocados)
        self.assertEqual(self.estado_git(), '')

    def test_ac1_lo_que_ya_estaba_cambiado_no_entra(self):
        ident = self.conectado_con_un_cambio()
        self.assertEqual(self.estado_git(), '')
        (self.almacen / 'notas.md').write_text('notas a medio escribir\n', encoding='utf-8')  # versionado y modificado a mano
        (self.almacen / 'suelto.txt').write_text('sin versionar\n', encoding='utf-8')  # nuevo y sin versionar
        (self.almacen / 'preparado.txt').write_text('ya en el índice\n', encoding='utf-8')  # agregado al índice a mano
        self.git_en(self.almacen, 'add', 'preparado.txt')
        pendiente = self.estado_git()
        cuenta = self.commits()
        tocados, _ = self.comando_que_escribe('mensaje', ident, 'hola', agente='claude-code')
        self.assertEqual(self.commits(), cuenta + 1)
        self.assertEqual(self.archivos_del_ultimo(), tocados)
        self.assertFalse(self.archivos_del_ultimo() & {'notas.md', 'suelto.txt', 'preparado.txt'})
        self.assertEqual(self.estado_git(), pendiente)  # siguen como estaban: modificado, sin versionar y en el índice
        self.assertEqual((self.almacen / 'notas.md').read_text(encoding='utf-8'), 'notas a medio escribir\n')

    def test_ac1_un_comando_que_solo_lee_no_commitea(self):
        ident = self.conectado_con_un_cambio()
        cuenta, cabeza = self.commits(), self.git_en(self.almacen, 'rev-parse', 'HEAD')
        for comando in (('estado', ident), ('listar',), ('estado', ident, '--json'), ('conectar',)):
            with self.subTest(comando=comando):
                tocados, _ = self.comando_que_escribe(*comando)
                self.assertEqual(tocados, set())
                self.assertEqual((self.commits(), self.git_en(self.almacen, 'rev-parse', 'HEAD')), (cuenta, cabeza))
                self.assertEqual(self.estado_git(), '')

    def test_ac1_sin_almacen_aparte_no_se_commitea_nada(self):
        self.bien('init')
        self.bien('nuevo', 'Notas', '--capacidad', 'notas', '--sufijo', 'ac', agente='claude-code')
        ident = next(p.name for p in (self.producto / 'openspec/changes').iterdir() if p.is_dir())
        self.bien('mensaje', ident, 'hola', agente='claude-code')
        self.assertEqual(self.commits(self.producto), 1)  # sólo el inicial de la fixture
        self.assertNotEqual(self.estado_git(self.producto), '')  # los registros quedan escritos y sin commitear, como hoy
        self.assertEqual(self.commits(), 1)
        self.assertEqual(self.estado_git(), '')

    # --- ac2: el commit no escribe configuración, no sube nada y no hace fallar al comando --------------------------------
    def test_ac2_commitea_con_la_identidad_configurada_sin_escribir_configuracion(self):
        antes = self.configuraciones()
        ident = self.conectado_con_un_cambio()
        self.bien('mensaje', ident, 'hola', agente='claude-code')
        for formato in ('%an <%ae>', '%cn <%ce>'):  # autor y quien commitea, también cuando el actor es un agente
            self.assertEqual(set(self.git_en(self.almacen, 'log', '-3', f'--format={formato}').splitlines()), {f'{NOMBRE} <{CORREO}>'})
        self.assertEqual(self.configuraciones(), antes)
        self.git_en(self.almacen, 'config', 'user.name', 'Persona Local')  # la identidad propia del almacén manda, como en Git
        self.git_en(self.almacen, 'config', 'user.email', 'local@example.invalid')
        antes = self.configuraciones()
        self.bien('mensaje', ident, 'otra vez', agente='claude-code')
        self.assertEqual(self.git_en(self.almacen, 'log', '-1', '--format=%an <%ae>'), 'Persona Local <local@example.invalid>')
        self.assertEqual(self.configuraciones(), antes)

    def test_ac2_sin_identidad_de_git_el_comando_termina_bien_y_avisa(self):
        ident = self.conectado_con_un_cambio()
        cuenta, antes = self.commits(), self.configuraciones()
        # Sin identidad: usuario y sistema apuntan a archivos vacíos, y `useConfigOnly` (por el entorno, sin escribir ningún archivo)
        # le impide a Git inventar una con el nombre de la cuenta y el de la máquina, que depende de dónde corra la prueba.
        sin_identidad = {'GIT_CONFIG_GLOBAL': str(self.git_vacio), 'GIT_CONFIG_SYSTEM': str(self.git_vacio),
                         'GIT_CONFIG_COUNT': '1', 'GIT_CONFIG_KEY_0': 'user.useConfigOnly', 'GIT_CONFIG_VALUE_0': 'true'}
        with patch.dict(os.environ, sin_identidad):
            tocados, impreso = self.comando_que_escribe('mensaje', ident, 'hola sin identidad', agente='claude-code')
        self.assertTrue(tocados)
        self.assertIn('hola sin identidad', self.registro(ident))  # los registros quedaron en el disco
        self.assertEqual(self.commits(), cuenta)
        self.assertNotEqual(self.estado_git(), '')
        self.assertRegex(impreso.casefold(), r'no (se )?pudo commitear')
        self.assertRegex(impreso.casefold(), r'identidad|identity|user\.name')  # y por qué
        self.assertNotIn('Traceback', impreso)
        self.assertEqual(self.configuraciones(), antes)
        self.assertEqual(self.git_vacio.read_bytes(), b'')

    def test_ac2_un_hook_que_rechaza_no_hace_fallar_al_comando(self):
        ident = self.conectado_con_un_cambio()
        hook = self.almacen / '.git/hooks/pre-commit'
        hook.parent.mkdir(exist_ok=True)
        hook.write_text('#!/bin/sh\necho RECHAZADO-POR-EL-HOOK >&2\nexit 1\n', encoding='utf-8')
        hook.chmod(0o755)
        cuenta, antes = self.commits(), self.configuraciones()
        tocados, impreso = self.comando_que_escribe('mensaje', ident, 'hola con hook', agente='claude-code')
        self.assertTrue(tocados)
        self.assertIn('hola con hook', self.registro(ident))
        self.assertEqual(self.commits(), cuenta)  # el hook se respeta: no se saltea con --no-verify
        self.assertRegex(impreso.casefold(), r'no (se )?pudo commitear')
        self.assertIn('RECHAZADO-POR-EL-HOOK', impreso)
        self.assertNotIn('Traceback', impreso)
        self.assertEqual(self.configuraciones(), antes)

    def test_ac2_no_sube_nada_al_remoto(self):
        remoto = self.base / 'remoto.git'
        self.git_en(self.base, 'init', '-q', '--bare', '-b', 'main', str(remoto))
        self.git_en(self.almacen, 'remote', 'add', 'origin', str(remoto))
        ident = self.conectado_con_un_cambio()
        self.git_en(self.almacen, 'push', '-q', '-u', 'origin', 'main')  # con rama de seguimiento: un `git push` pelado subiría
        refs = self.git_en(remoto, 'for-each-ref')
        self.assertTrue(refs)
        cuenta = self.commits()
        self.bien('mensaje', ident, 'hola', agente='claude-code')
        self.assertEqual(self.commits(), cuenta + 1)
        self.assertEqual(self.git_en(remoto, 'for-each-ref'), refs)
        self.assertEqual(self.git_en(self.almacen, 'rev-list', '--count', 'origin/main..main'), '1')  # quedó sólo en el almacén local


if __name__ == '__main__':
    unittest.main()
