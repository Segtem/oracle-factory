"""Registros fuera del repo del producto, etapa 2: escenarios ra1–ra4 de la spec (el almacén y `conectar`).

Se corre la CLI en el mismo proceso (`f.main`). La conexión vive en la configuración personal del usuario
(`$XDG_CONFIG_HOME/oracle-factory/almacenes.json`: {directorio común de Git del producto: ruta del almacén}); aquí HOME y
XDG_CONFIG_HOME apuntan a un directorio temporal: ninguna prueba lee ni escribe el HOME real.
"""
import contextlib
import io
import json
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
from oracle_factory import autopilot  # noqa: E402

f = _archivo.f
GIT = _archivo.GIT


class RegistrosAlmacen(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        base = Path(self.tmp.name).resolve()
        self.base = base
        self.producto, self.almacen, self.casa = base / 'producto', base / 'almacen', base / 'casa'
        for carpeta in (self.producto, self.almacen, self.casa):
            carpeta.mkdir()
        self.config = self.casa / '.config/oracle-factory/almacenes.json'
        entorno = patch.dict(os.environ, {'HOME': str(self.casa), 'XDG_CONFIG_HOME': str(self.casa / '.config')})
        entorno.start(); self.addCleanup(entorno.stop)
        self.addCleanup(os.chdir, os.getcwd())
        for nombre, valor in [('ROOT', self.producto), ('CHANGES', self.producto / 'openspec/changes'), ('AGENTE', None),
                              ('REGISTROS', self.producto)]:
            p = patch.object(f, nombre, valor, create=True); p.start(); self.addCleanup(p.stop)
        p = patch.object(f, 'terminal_interactiva', return_value=True); p.start(); self.addCleanup(p.stop)
        self.git_en(self.producto, 'init', '-q', '-b', 'main')
        (self.producto / 'README.md').write_text('producto\n', encoding='utf-8')
        (self.producto / 'src').mkdir()
        (self.producto / 'src/app.py').write_text('print("hola")\n', encoding='utf-8')
        self.git_en(self.producto, 'add', '-A')
        self.git_en(self.producto, 'commit', '-q', '-m', 'producto inicial')
        self.git_en(self.almacen, 'init', '-q', '-b', 'main')
        self.clave = str((self.producto / '.git').resolve())

    # --- ayudantes -----------------------------------------------------------------
    def git_en(self, carpeta, *args):
        return subprocess.run([*GIT, *args], cwd=carpeta, check=True, capture_output=True, text=True).stdout.strip()

    def corre(self, *args, agente=None, desde=None, proyecto=True):
        """(código, salida, error) de `oracle-factory [--agente A] [--proyecto PRODUCTO] ARGS`; con `desde`, corre desde esa carpeta y sin --proyecto."""
        out, err = io.StringIO(), io.StringIO()
        base = (['--agente', agente] if agente else []) + (['--proyecto', str(self.producto)] if proyecto and desde is None else [])
        if desde is not None:
            os.chdir(desde)
        with patch('builtins.input', side_effect=['1'] * 8), contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            codigo = f.main([*base, *args])
        return codigo, out.getvalue(), err.getvalue()

    def arbol(self, raiz):
        return {str(p.relative_to(raiz)): p.read_bytes() for p in sorted(raiz.rglob('*'))
                if p.is_file() and '.git' not in p.relative_to(raiz).parts}

    def conexiones(self):
        return json.loads(self.config.read_text(encoding='utf-8'))

    def conecta(self, almacen=None, **kw):
        codigo, salida, error = self.corre('conectar', str(almacen or self.almacen), **kw)
        self.assertEqual(codigo, 0, error)
        return salida

    def escribe_conexion(self, almacen=None):
        self.config.parent.mkdir(parents=True, exist_ok=True)
        self.config.write_text(json.dumps({self.clave: str(almacen or self.almacen)}), encoding='utf-8')

    def todo(self):
        """Lo que no debe moverse cuando algo se rechaza: producto, almacén y configuración personal."""
        return (self.arbol(self.producto), self.arbol(self.almacen), self.arbol(self.casa))

    def nuevo_cambio(self):
        self.assertEqual(self.corre('nuevo', 'Notas', '--capacidad', 'notas', '--sufijo', 'ra')[0], 0)
        return next(p.name for p in (self.almacen / 'openspec/changes').iterdir() if p.is_dir())

    # --- ra1: conectar guarda el almacén por usuario sin tocar el producto ----------------------------------------
    def test_ra1_conectar_un_almacen_nuevo(self):
        antes = self.arbol(self.producto)
        self.conecta()
        self.assertEqual(self.conexiones(), {self.clave: str(self.almacen)})
        for ruta in ('.factory/config.json', 'tareas', 'openspec/changes', 'requisitos'):
            self.assertTrue((self.almacen / ruta).exists(), ruta)
        self.assertEqual(self.arbol(self.producto), antes)
        self.assertEqual(self.git_en(self.producto, 'status', '--porcelain', '--untracked-files=all'), '')
        self.assertFalse((self.producto / '.factory').exists())
        self.assertEqual(sorted(p.name for p in self.config.parent.iterdir()), ['almacenes.json'])  # sin residuos temporales
        # dónde vive la configuración personal: XDG_CONFIG_HOME si está puesto, y si no HOME/.config
        otra = self.base / 'otra-config'
        with patch.dict(os.environ, {'XDG_CONFIG_HOME': str(otra)}):
            self.assertEqual(f.almacenes.archivo(), otra / 'oracle-factory' / 'almacenes.json')
        sin_xdg = {k: v for k, v in os.environ.items() if k != 'XDG_CONFIG_HOME'}
        with patch.dict(os.environ, sin_xdg, clear=True):
            self.assertEqual(f.almacenes.archivo(), self.casa / '.config' / 'oracle-factory' / 'almacenes.json')

    def test_ra1_conectar_desde_una_subcarpeta_del_producto_usa_la_clave_del_producto(self):
        codigo, _, error = self.corre('conectar', str(self.almacen), desde=self.producto / 'src')
        self.assertEqual(codigo, 0, error)
        self.assertEqual(self.conexiones(), {self.clave: str(self.almacen)})
        # con una ruta relativa, y sin dejar movido ni el directorio actual ni las raíces ni lo de Git del producto
        self.assertEqual(self.corre('desconectar')[0], 0)
        git_antes = {n: (self.producto / '.git' / n).read_bytes() for n in ('config', 'HEAD')}
        ganchos = sorted(p.name for p in (self.producto / '.git/hooks').iterdir())
        codigo, _, error = self.corre('conectar', os.path.relpath(self.almacen, self.producto), desde=self.producto)
        self.assertEqual(codigo, 0, error)
        self.assertEqual(self.conexiones(), {self.clave: str(self.almacen)})
        self.assertEqual(Path(os.getcwd()).resolve(), self.producto)
        self.assertEqual((f.ROOT, f.CHANGES), (self.producto, self.producto / 'openspec' / 'changes'))
        self.assertEqual({n: (self.producto / '.git' / n).read_bytes() for n in ('config', 'HEAD')}, git_antes)
        self.assertEqual(sorted(p.name for p in (self.producto / '.git/hooks').iterdir()), ganchos)

    def test_ra1_conectar_respeta_la_configuracion_del_usuario_y_agrega_sin_pisar(self):
        self.config.parent.mkdir(parents=True)
        self.config.write_text(json.dumps({'/otro/.git': '/otro/almacen'}), encoding='utf-8')
        self.conecta()
        self.assertEqual(self.conexiones(), {'/otro/.git': '/otro/almacen', self.clave: str(self.almacen)})

    def test_ra1_una_ruta_que_no_sirve_falla_sin_cambiar_nada(self):
        no_git = self.base / 'sin-git'
        no_git.mkdir()
        adentro = self.producto / 'hijo'
        adentro.mkdir()
        self.git_en(adentro, 'init', '-q', '-b', 'main')
        padre = self.base  # contiene al producto
        self.git_en(padre, 'init', '-q', '-b', 'main')
        archivo = self.base / 'archivo.txt'
        archivo.write_text('x\n', encoding='utf-8')
        for ruta in (self.base / 'no-existe', no_git, adentro, padre, archivo, self.producto):
            with self.subTest(ruta=str(ruta)):
                antes = self.todo()
                codigo, _, error = self.corre('conectar', str(ruta))
                self.assertNotEqual(codigo, 0)
                self.assertIn('FACTORY BLOQUEADA', error)
                self.assertNotIn('Traceback', error)
                self.assertEqual(self.todo(), antes)
                self.assertFalse(self.config.exists())

    def test_ra1_conectar_desde_algo_que_no_es_un_repo_git_falla(self):
        suelto = self.base / 'suelto'
        suelto.mkdir()
        antes = self.todo()
        codigo, _, error = self.corre('conectar', str(self.almacen), proyecto=False, desde=suelto)
        self.assertNotEqual(codigo, 0)
        self.assertIn('FACTORY BLOQUEADA', error)
        self.assertEqual(self.todo(), antes)

    def test_ra1_una_configuracion_personal_ilegible_no_se_sobrescribe(self):
        self.config.parent.mkdir(parents=True)
        for contenido in ('esto no es json {', '["una", "lista"]', '{"clave": 3}'):
            with self.subTest(contenido=contenido):
                self.config.write_text(contenido, encoding='utf-8')
                antes = self.todo()
                codigo, _, error = self.corre('conectar', str(self.almacen))
                self.assertNotEqual(codigo, 0)
                self.assertIn('almacenes.json', error)
                self.assertEqual(self.todo(), antes)
                self.assertEqual(self.config.read_text(encoding='utf-8'), contenido)
                self.assertFalse((self.almacen / '.factory').exists())

    def test_ra1_conectar_dos_veces_no_cambia_nada_y_lo_dice(self):
        self.conecta()
        antes = self.todo()
        codigo, salida, error = self.corre('conectar', str(self.almacen))
        self.assertEqual(codigo, 0, error)
        self.assertIn('ya está conectado', salida)
        self.assertEqual(self.todo(), antes)
        self.assertEqual(self.conexiones(), {self.clave: str(self.almacen)})

    # --- ra2: con el producto conectado los comandos usan el almacén ----------------------------------------------
    def test_ra2_desde_una_subcarpeta_y_desde_un_worktree(self):
        self.conecta()
        ident = self.nuevo_cambio()
        trabajo = self.base / 'producto-wt'
        self.git_en(self.producto, 'worktree', 'add', '-q', '-b', 'otra', str(trabajo))
        antes_producto, antes_trabajo = self.arbol(self.producto), self.arbol(trabajo)
        explicito = self.corre('--registros', str(self.almacen), 'listar')
        for desde in (self.producto, self.producto / 'src', trabajo):
            with self.subTest(desde=str(desde)):
                codigo, salida, error = self.corre('listar', desde=desde)
                self.assertEqual(codigo, 0, error)
                self.assertIn(ident, salida)
                self.assertEqual((codigo, salida), explicito[:2])  # el mismo comportamiento que --registros ALMACEN
                visto = {}
                with patch.object(f, 'listar', side_effect=lambda *a, **k: visto.update(producto=f.PRODUCTO, root=f.ROOT)):
                    self.corre('listar', desde=desde)
                self.assertEqual(visto, {'producto': Path(self.git_en(desde, 'rev-parse', '--show-toplevel')).resolve(), 'root': self.almacen})
        self.assertEqual((self.arbol(self.producto), self.arbol(trabajo)), (antes_producto, antes_trabajo))
        self.assertEqual(self.git_en(trabajo, 'status', '--porcelain', '--untracked-files=all'), '')
        self.assertFalse((trabajo / '.factory').exists() or (self.producto / '.factory').exists())

    def test_ra2_los_comandos_que_escriben_tambien_van_al_almacen(self):
        self.conecta()
        ident = self.nuevo_cambio()
        antes = self.arbol(self.producto)
        for comando in (('mensaje', ident, 'hola'), ('tomar', ident), ('soltar', ident), ('estado', ident)):
            codigo, _, error = self.corre(*comando, desde=self.producto / 'src')
            self.assertEqual(codigo, 0, (comando, error))
        self.assertEqual(self.arbol(self.producto), antes)
        self.assertIn('hola', (self.almacen / f'.factory/cambios/{ident}/factory.json').read_text(encoding='utf-8'))

    def test_ra2_la_opcion_explicita_manda_sobre_la_conexion(self):
        self.conecta()
        ident = self.nuevo_cambio()
        otro = self.base / 'otro'
        otro.mkdir()
        self.git_en(otro, 'init', '-q', '-b', 'main')
        self.assertEqual(self.corre('--registros', str(otro), 'init')[0], 0)
        codigo, salida, error = self.corre('--registros', str(otro), 'listar')
        self.assertEqual(codigo, 0, error)
        self.assertNotIn(ident, salida)
        self.assertIn(str(otro), salida)
        self.assertEqual(self.conexiones(), {self.clave: str(self.almacen)})

    def test_ra2_sin_conexion_se_comporta_como_siempre(self):
        self.assertEqual(self.corre('init')[0], 0)
        self.assertEqual(self.corre('nuevo', 'Notas', '--capacidad', 'notas', '--sufijo', 'ra')[0], 0)
        self.config.parent.mkdir(parents=True)
        self.config.write_text(json.dumps({'/otro/.git': str(self.almacen)}), encoding='utf-8')  # la conexión de otro producto no cuenta
        configuracion = self.config.read_bytes()
        codigo, salida, error = self.corre('listar')
        self.assertEqual(codigo, 0, error)
        self.assertIn('ra', salida)
        self.assertIn(str(self.producto), salida)
        self.assertEqual(self.arbol(self.almacen), {})
        self.assertEqual(self.config.read_bytes(), configuracion)

    def test_ra2_sin_ninguna_configuracion_personal_no_se_crea_una(self):
        self.assertEqual(self.corre('init')[0], 0)
        self.assertEqual(self.corre('listar')[0], 0)
        self.assertFalse(self.config.exists())

    def test_ra2_una_configuracion_personal_ilegible_se_avisa_y_es_no_conectado(self):
        self.assertEqual(self.corre('init')[0], 0)
        self.config.parent.mkdir(parents=True)
        self.config.write_text('esto no es json {', encoding='utf-8')
        codigo, salida, error = self.corre('listar')
        self.assertEqual(codigo, 0, error)
        self.assertIn('almacenes.json', error)  # el aviso
        self.assertNotIn('Traceback', error)
        self.assertIn(str(self.producto), salida)  # trabajó sobre el producto, como no conectado
        self.assertEqual(self.config.read_text(encoding='utf-8'), 'esto no es json {')

    # --- ra3: conectar sin argumentos y desconectar ---------------------------------------------------------------
    def test_ra3_ver_y_quitar_la_conexion(self):
        self.config.parent.mkdir(parents=True)
        self.config.write_text(json.dumps({'/otro/.git': '/otro/almacen'}), encoding='utf-8')
        codigo, salida, _ = self.corre('conectar')
        self.assertEqual(codigo, 0)
        self.assertIn('no está conectado', salida)
        self.conecta()
        antes_producto, antes_almacen = self.arbol(self.producto), self.arbol(self.almacen)
        codigo, salida, error = self.corre('conectar')
        self.assertEqual(codigo, 0, error)
        self.assertIn(str(self.almacen), salida)
        codigo, salida, error = self.corre('desconectar')
        self.assertEqual(codigo, 0, error)
        self.assertEqual(self.conexiones(), {'/otro/.git': '/otro/almacen'})  # sólo se quita la de este producto
        self.assertIn('el almacén y el producto siguen como estaban', salida)
        self.assertEqual((self.arbol(self.producto), self.arbol(self.almacen)), (antes_producto, antes_almacen))
        codigo, salida, error = self.corre('desconectar')
        self.assertEqual(codigo, 0, error)
        self.assertIn('no estaba conectado', salida)
        self.assertEqual(self.conexiones(), {'/otro/.git': '/otro/almacen'})

    def test_ra3_desconectar_con_la_configuracion_ilegible_no_la_sobrescribe(self):
        self.config.parent.mkdir(parents=True)
        self.config.write_text('esto no es json {', encoding='utf-8')
        codigo, _, error = self.corre('desconectar')
        self.assertNotEqual(codigo, 0)
        self.assertIn('almacenes.json', error)
        self.assertEqual(self.config.read_text(encoding='utf-8'), 'esto no es json {')

    def test_ra3_un_agente_no_conecta_ni_desconecta(self):
        for comando in (('conectar', str(self.almacen)), ('desconectar',)):
            with self.subTest(comando=comando[0]):
                antes = self.todo()
                codigo, _, error = self.corre(*comando, agente='claude-code')
                self.assertNotEqual(codigo, 0)
                self.assertIn('persona', error)
                self.assertEqual(self.todo(), antes)
        self.assertFalse(self.config.exists())
        self.conecta()  # y con la conexión puesta, desconectar con --agente tampoco la quita
        antes = self.todo()
        self.assertNotEqual(self.corre('desconectar', agente='claude-code')[0], 0)
        self.assertEqual(self.todo(), antes)

    def test_ra3_el_conductor_las_trata_como_decisiones_de_una_persona(self):
        for paso in (f'oracle-factory conectar {self.almacen}', 'oracle-factory desconectar',
                     f'oracle-factory --agente codex conectar {self.almacen}', 'oracle-factory --agente codex desconectar'):
            with self.subTest(paso=paso):
                d = autopilot.decidir({'fase': 'requisitos_importados', 'proximo_paso': paso, 'frenos': [], 'candidato': None})
                self.assertEqual((d['accion'], d['quien'], d['comando']), ('pedir_a_persona', 'persona', paso))
        solo = autopilot.decidir({'fase': 'requisitos_importados', 'proximo_paso': 'oracle-factory', 'frenos': [], 'candidato': None})
        self.assertEqual(solo['accion'], 'frenar')  # el programa sin subcomando no es un paso que se conozca

    # --- ra4: un producto con su propio Factory conectado se niega ---------------------------------------------------
    def test_ra4_los_dos_a_la_vez_se_niega_sin_escribir(self):
        self.assertEqual(self.corre('init')[0], 0)
        self.assertEqual(self.corre('nuevo', 'Notas', '--capacidad', 'notas', '--sufijo', 'ra')[0], 0)
        ident = next(p.name for p in (self.producto / 'openspec/changes').iterdir() if p.is_dir())
        self.escribe_conexion()
        for comando in (('estado', ident), ('listar',), ('nuevo', 'Otro', '--capacidad', 'otra', '--sufijo', 'rb')):
            with self.subTest(comando=comando[0]):
                antes = self.todo()
                codigo, _, error = self.corre(*comando)
                self.assertNotEqual(codigo, 0)
                self.assertIn('desconectar', error)
                self.assertIn('migrar', error)
                self.assertNotIn('Traceback', error)
                self.assertEqual(self.todo(), antes)

    def test_ra4_con_registros_explicito_no_se_niega_ni_con_los_dos(self):
        self.assertEqual(self.corre('init')[0], 0)
        self.escribe_conexion()
        codigo, _, error = self.corre('--registros', str(self.almacen), 'init')
        self.assertEqual(codigo, 0, error)

    def test_ra4_desconectar_y_conectar_siguen_funcionando_con_los_dos(self):
        self.assertEqual(self.corre('init')[0], 0)
        self.escribe_conexion()
        codigo, _, error = self.corre('desconectar')  # la salida que el mensaje de la negativa propone
        self.assertEqual(codigo, 0, error)
        self.assertEqual(self.conexiones(), {})
        self.assertEqual(self.corre('listar')[0], 0)


if __name__ == '__main__':
    unittest.main()
