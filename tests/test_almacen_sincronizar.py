"""Registros fuera del repo del producto, etapa 4b2: escenarios as1–as3 de la spec (conectar desde una URL y sincronizar el
almacén entre personas).

Mismo entorno que tests/test_almacen_commits.py (de donde se toman setUp y los ayudantes): la CLI corre en el mismo proceso
(`f.main`); productos, almacenes y remotos son repos Git temporales, y el remoto del equipo es un repo bare local al que se
llega con una URL `file://` (sin red). HOME, XDG_CONFIG_HOME, XDG_DATA_HOME, GIT_CONFIG_GLOBAL y GIT_CONFIG_SYSTEM apuntan a
archivos y carpetas temporales; cada «persona» tiene los suyos. Ninguna prueba lee ni escribe el HOME real ni el
~/.gitconfig real.

La interfaz que se espera: `conectar URL` clona en `$XDG_DATA_HOME/oracle-factory/almacenes/NOMBRE` (o
`~/.local/share/...`); `sincronizar` trae, une con los drivers de Factory pasados con `git -c`, rehace lo generado, commitea y,
si es una persona, sube; con un problema sale con código distinto de cero y el almacén como estaba.
"""
import contextlib
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import test_almacen_bloqueo as _bloqueo  # noqa: E402
import test_almacen_commits as _commits  # noqa: E402

f = _commits.f
_Base = _commits.AlmacenCommits
GIT = _commits.GIT


class AlmacenSincronizar(unittest.TestCase):
    git_en, arbol, commits, estado_git = _Base.git_en, _Base.arbol, _Base.commits, _Base.estado_git
    hijo, esperar_archivo = _bloqueo.AlmacenBloqueo.hijo, _bloqueo.AlmacenBloqueo.esperar_archivo

    def setUp(self):
        _commits.AlmacenCommits.setUp(self)  # producto, almacén «semilla» y el entorno temporal (por el módulo: `_Base` se borra abajo)
        self.remoto = self.base / 'remotos' / 'equipo.git'
        self.remoto.parent.mkdir()
        self.git_en(self.base, 'clone', '-q', '--bare', str(self.almacen), str(self.remoto))
        self.url = self.remoto.as_uri()  # file:///…/equipo.git
        self.datos = self.base / 'datos-uno'
        p = patch.dict(os.environ, {'XDG_DATA_HOME': str(self.datos)})
        p.start(); self.addCleanup(p.stop)
        self.casa_dos = self.base / 'casa-dos'
        self.casa_dos.mkdir()

    # --- ayudantes -----------------------------------------------------------------
    def en(self, producto, *args, agente=None):
        """Corre la CLI sobre `producto`; (código, todo lo impreso). Un SystemExit (orden desconocida) cuenta como código."""
        out, err = io.StringIO(), io.StringIO()
        base = (['--agente', agente] if agente else []) + ['--proyecto', str(producto)]
        with patch('builtins.input', side_effect=['1'] * 8), contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            try:
                codigo = f.main([*base, *args])
            except SystemExit as e:
                codigo = e.code if isinstance(e.code, int) else 1
        return codigo, out.getvalue() + err.getvalue()

    def bien(self, producto, *args, **kw):
        codigo, impreso = self.en(producto, *args, **kw)
        self.assertEqual(codigo, 0, (args, impreso))
        self.assertNotIn('Traceback', impreso)
        return impreso

    def mal(self, producto, *args, **kw):
        codigo, impreso = self.en(producto, *args, **kw)
        self.assertNotEqual(codigo, 0, (args, impreso))
        self.assertTrue(impreso.strip())
        self.assertNotIn('Traceback', impreso)
        return impreso

    def clon(self, datos=None, nombre='equipo'):
        return (datos or self.datos) / 'oracle-factory' / 'almacenes' / nombre

    @contextlib.contextmanager
    def como_dos(self):
        """La segunda persona: su propia casa, su configuración de Factory y su carpeta de datos."""
        with patch.dict(os.environ, {'HOME': str(self.casa_dos), 'XDG_CONFIG_HOME': str(self.casa_dos / '.config'),
                                     'XDG_DATA_HOME': str(self.base / 'datos-dos')}):
            yield

    def producto_nuevo(self, nombre):
        repo = self.base / nombre
        repo.mkdir()
        self.git_en(repo, 'init', '-q', '-b', 'main')
        (repo / 'README.md').write_text(f'{nombre}\n', encoding='utf-8')
        self.git_en(repo, 'add', '-A')
        self.git_en(repo, 'commit', '-q', '-m', 'inicial')
        return repo

    def conectado(self, producto):
        """El almacén al que quedó conectado `producto` según la configuración de Factory del usuario actual, o None."""
        return f.almacenes.leer().get(f.almacenes.clave(producto))

    def head(self, repo):
        return self.git_en(repo, 'rev-parse', 'HEAD')

    def refs(self):
        return self.git_en(self.remoto, 'for-each-ref')

    def tercero_sube(self, archivo='de-tercero.md', texto='un tercero sube algo\n'):
        """Alguien más (con Git a mano) sube un commit al remoto."""
        otro = self.base / f'tercero-{len(list(self.base.glob("tercero-*")))}'
        self.git_en(self.base, 'clone', '-q', self.url, str(otro))
        (otro / archivo).write_text(texto, encoding='utf-8')
        self.git_en(otro, 'add', '-A')
        self.git_en(otro, 'commit', '-q', '-m', f'tercero: {archivo}')
        self.git_en(otro, 'push', '-q', 'origin', 'HEAD:main')
        return self.head(otro)

    def uno_con_un_cambio(self):
        """La primera persona conecta desde la URL, arma el vault y crea un cambio; devuelve (clon, id)."""
        self.bien(self.producto, 'conectar', self.url)
        self.bien(self.producto, 'kb')
        self.bien(self.producto, 'nuevo', 'Compartido', '--capacidad', 'notas', '--sufijo', 'eq', agente='claude-code')
        clon = self.clon()
        return clon, next(p.name for p in (clon / 'openspec/changes').iterdir() if p.is_dir() and p.name.endswith('-eq'))

    def configuraciones(self, *repos):
        rutas = [r / '.git/config' for r in repos] + [self.remoto / 'config', self.git_global, self.git_vacio]
        return {str(p): p.read_bytes() for p in rutas}

    # --- as1: conectar URL clona el almacén en una carpeta del usuario -------------------------------------------------
    def test_as1_conectar_desde_una_url_clona_y_conecta(self):
        impreso = self.bien(self.producto, 'conectar', self.url)
        clon = self.clon()
        self.assertTrue((clon / '.git').exists(), impreso)
        self.assertEqual(self.git_en(clon, 'remote', 'get-url', 'origin'), self.url)
        self.assertEqual((clon / 'notas.md').read_text(encoding='utf-8'), 'notas del equipo\n')
        self.assertEqual(self.conectado(self.producto), str(clon.resolve()))
        self.assertTrue((clon / '.factory').is_dir())  # preparado como con `conectar RUTA`
        self.assertEqual(self.estado_git(clon), '')
        self.bien(self.producto, 'nuevo', 'Notas', '--capacidad', 'notas', '--sufijo', 'ur', agente='claude-code')
        self.assertTrue(any(p.name.endswith('-ur') for p in (clon / 'openspec/changes').iterdir()))
        self.assertEqual(self.estado_git(self.producto), '')  # el producto no recibe nada
        self.assertEqual(self.commits(self.producto), 1)

    def test_as1_sin_xdg_data_home_clona_en_la_carpeta_local_del_usuario(self):
        with patch.dict(os.environ):
            del os.environ['XDG_DATA_HOME']
            self.bien(self.producto, 'conectar', self.url)
            self.assertEqual(self.conectado(self.producto), str(self.clon(self.casa / '.local/share').resolve()))
        self.assertTrue((self.clon(self.casa / '.local/share') / '.git').exists())
        self.assertFalse(self.datos.exists())

    def test_as1_el_clon_ya_existe_y_se_reusa(self):
        self.bien(self.producto, 'conectar', self.url)
        clon = self.clon()
        (clon / 'local.md').write_text('trabajo local sin subir\n', encoding='utf-8')
        self.git_en(clon, 'add', 'local.md')
        self.git_en(clon, 'commit', '-q', '-m', 'commit local que un clon nuevo no tendría')
        cabeza, inodo = self.head(clon), (clon / '.git').stat().st_ino
        self.bien(self.producto, 'conectar', self.url)  # otra vez, desde el mismo producto
        self.assertEqual(self.conectado(self.producto), str(clon.resolve()))
        otro = self.producto_nuevo('otro-producto')
        self.bien(otro, 'conectar', self.url)  # y desde otro producto
        self.assertEqual(self.conectado(otro), str(clon.resolve()))
        self.assertEqual(self.conectado(self.producto), str(clon.resolve()))
        self.assertEqual((self.head(clon), (clon / '.git').stat().st_ino), (cabeza, inodo))
        self.assertEqual((clon / 'local.md').read_text(encoding='utf-8'), 'trabajo local sin subir\n')
        self.assertEqual(sorted(p.name for p in clon.parent.iterdir()), ['equipo'])  # ningún clon al lado

    def test_as1_la_carpeta_es_otra_cosa_y_se_niega_sin_tocar_nada(self):
        clon = self.clon()
        clon.mkdir(parents=True)
        (clon / 'mio.txt').write_text('no es un almacén\n', encoding='utf-8')
        antes = self.arbol(clon)
        self.mal(self.producto, 'conectar', self.url)
        self.assertEqual(self.arbol(clon), antes)
        self.assertFalse((clon / '.git').exists())
        self.assertIsNone(self.conectado(self.producto))
        # un clon de otra URL con el mismo nombre tampoco se reusa
        ajeno = self.base / 'ajenos' / 'equipo.git'
        ajeno.parent.mkdir()
        self.git_en(self.base, 'init', '-q', '--bare', '-b', 'main', str(ajeno))
        (clon / 'mio.txt').unlink()
        clon.rmdir()
        self.git_en(self.base, 'clone', '-q', str(self.almacen), str(clon))
        self.git_en(clon, 'remote', 'set-url', 'origin', ajeno.as_uri())
        antes, cabeza = self.arbol(clon), self.head(clon)
        impreso = self.mal(self.producto, 'conectar', self.url)
        self.assertIn(str(clon), impreso)
        self.assertEqual((self.arbol(clon), self.head(clon)), (antes, cabeza))
        self.assertEqual(self.git_en(clon, 'remote', 'get-url', 'origin'), ajeno.as_uri())
        self.assertIsNone(self.conectado(self.producto))

    def test_as1_un_clon_que_falla_no_conecta_ni_deja_carpetas(self):
        url = (self.base / 'remotos' / 'no-existe.git').as_uri()
        self.mal(self.producto, 'conectar', url)
        self.assertIsNone(self.conectado(self.producto))
        almacenes = self.clon().parent
        self.assertEqual(list(almacenes.iterdir()) if almacenes.exists() else [], [])  # ni no-existe/ ni temporales
        self.assertEqual(self.estado_git(self.producto), '')

    def test_as1_conectar_una_url_sigue_siendo_de_una_persona(self):
        impreso = self.mal(self.producto, 'conectar', self.url, agente='claude-code')
        self.assertIn('persona', impreso)
        self.assertFalse(self.clon().exists())
        self.assertIsNone(self.conectado(self.producto))

    # --- as2: sincronizar une los registros de todos sin escribir configuración ------------------------------------------
    def test_as2_dos_personas_en_el_mismo_cambio(self):
        clon_uno, ident = self.uno_con_un_cambio()
        self.bien(self.producto, 'sincronizar')  # la primera sube su cambio
        producto_dos = self.producto_nuevo('producto-dos')
        with self.como_dos():
            self.bien(producto_dos, 'conectar', self.url)
            clon_dos = self.clon(self.base / 'datos-dos')
            self.assertTrue((clon_dos / f'.factory/cambios/{ident}/factory.json').is_file())
        self.bien(self.producto, 'mensaje', ident, 'mensaje de la persona uno', agente='claude-code')
        self.bien(self.producto, 'sincronizar')  # la primera sube su mensaje
        with self.como_dos():
            self.bien(producto_dos, 'mensaje', ident, 'mensaje de la persona dos', agente='codex')
            antes = self.configuraciones(self.producto, producto_dos, clon_uno, clon_dos)
            self.bien(producto_dos, 'sincronizar')
        registro = json.loads((clon_dos / f'.factory/cambios/{ident}/factory.json').read_text(encoding='utf-8'))
        textos = [e.get('texto') for e in registro['eventos'] if e.get('accion') == 'mensaje']
        self.assertEqual(sorted(t for t in textos if t.startswith('mensaje de la persona')),
                         ['mensaje de la persona dos', 'mensaje de la persona uno'])
        nota = (clon_dos / f'kb/cambios/{ident}.md').read_text(encoding='utf-8')  # lo generado, rehecho con los dos
        self.assertIn('mensaje de la persona uno', nota)
        self.assertIn('mensaje de la persona dos', nota)
        self.assertNotIn('<<<<<<<', nota)
        self.assertEqual(self.estado_git(clon_dos), '')  # rehecho y commiteado
        self.assertFalse((clon_dos / '.git/MERGE_HEAD').exists())
        self.assertEqual(self.configuraciones(self.producto, producto_dos, clon_uno, clon_dos), antes)
        self.assertEqual(self.git_en(self.remoto, 'rev-parse', 'main'), self.head(clon_dos))

    def test_as2_sin_gitattributes_lo_escribe_y_lo_commitea_antes_de_unir(self):
        self.bien(self.producto, 'conectar', self.url)
        clon = self.clon()
        self.assertFalse((clon / '.gitattributes').exists())
        del_remoto = self.tercero_sube()  # el remoto avanzó: la unión es un merge de verdad
        self.bien(self.producto, 'sincronizar', agente='claude-code')
        atributos = (clon / '.gitattributes').read_text(encoding='utf-8')
        for linea in f.ATRIBUTOS:
            self.assertIn(linea, atributos)
        self.assertEqual(self.git_en(clon, 'ls-files', '.gitattributes'), '.gitattributes')
        self.assertEqual(self.estado_git(clon), '')
        agregado = self.git_en(clon, 'log', '--diff-filter=A', '--format=%H', '--', '.gitattributes').splitlines()
        union = self.git_en(clon, 'rev-list', '--merges', '-1', 'HEAD')
        self.assertTrue(union, 'no hubo un merge')
        self.assertEqual(len(agregado), 1)
        self.assertNotEqual(agregado[0], union)
        self.git_en(clon, 'merge-base', '--is-ancestor', agregado[0], f'{union}^1')  # del lado local, antes de unir
        self.git_en(clon, 'merge-base', '--is-ancestor', del_remoto, 'HEAD')

    def test_as2_sincronizar_toma_el_bloqueo_del_almacen(self):
        self.bien(self.producto, 'conectar', self.url)
        clon = self.clon()
        self.tercero_sube()
        sinc = self.base / 'sinc'
        sinc.mkdir()
        dueño = self.hijo('tiene-bloqueo', sinc, str(clon), esperar=False)
        self.addCleanup(lambda: dueño.poll() is None and dueño.kill())
        self.esperar_archivo(sinc / 'tomado', dueño)
        cabeza, refs = self.head(clon), self.refs()
        with patch.object(f.almacenes, 'PLAZO_DEL_BLOQUEO', 0.3):
            impreso = self.mal(self.producto, 'sincronizar')
        self.assertIn('bloqueo', impreso.casefold())
        self.assertEqual((self.head(clon), self.refs(), self.estado_git(clon)), (cabeza, refs, ''))
        (sinc / 'soltar').touch()
        dueño.communicate(timeout=60)
        self.bien(self.producto, 'sincronizar')
        self.assertEqual(self.git_en(self.remoto, 'rev-parse', 'main'), self.head(clon))

    # --- as3: sincronizar sube sólo si es una persona y no deja nada a medias ---------------------------------------------
    def divergidos(self):
        """Cambios nuevos en el remoto y en el almacén local; devuelve (clon, id, commit del remoto)."""
        clon, ident = self.uno_con_un_cambio()
        del_remoto = self.tercero_sube()
        self.bien(self.producto, 'mensaje', ident, 'mensaje local', agente='claude-code')
        return clon, ident, del_remoto

    def test_as3_un_agente_sincroniza_trae_y_une_pero_no_sube(self):
        clon, _, del_remoto = self.divergidos()
        refs, local = self.refs(), self.head(clon)
        impreso = self.bien(self.producto, 'sincronizar', agente='claude-code')
        self.assertEqual(self.refs(), refs)  # el remoto no recibió nada
        self.git_en(clon, 'merge-base', '--is-ancestor', del_remoto, 'HEAD')  # trajo y unió
        self.git_en(clon, 'merge-base', '--is-ancestor', local, 'HEAD')
        self.assertTrue((clon / 'de-tercero.md').is_file())
        self.assertEqual(self.estado_git(clon), '')
        self.assertRegex(impreso.casefold(), r'no (lo )?(se )?sub')  # y lo dice

    def test_as3_una_persona_sincroniza_y_el_remoto_queda_con_la_union(self):
        clon, ident, del_remoto = self.divergidos()
        self.bien(self.producto, 'sincronizar')
        self.assertEqual(self.git_en(self.remoto, 'rev-parse', 'main'), self.head(clon))
        self.git_en(self.remoto, 'merge-base', '--is-ancestor', del_remoto, 'main')
        self.assertIn('mensaje local', self.git_en(self.remoto, 'show', f'main:.factory/cambios/{ident}/factory.json'))
        self.assertEqual(self.estado_git(clon), '')

    def test_as3_con_cambios_sin_commitear_se_niega_sin_cambiar_nada(self):
        clon, _, _ = self.divergidos()
        (clon / 'notas.md').write_text('a medio escribir\n', encoding='utf-8')
        antes = (self.head(clon), self.refs(), self.estado_git(clon), self.arbol(clon))
        impreso = self.mal(self.producto, 'sincronizar')
        self.assertIn('notas.md', impreso)
        self.assertEqual((self.head(clon), self.refs(), self.estado_git(clon), self.arbol(clon)), antes)

    def test_as3_sin_remoto_se_niega_sin_cambiar_nada(self):
        clon, _ = self.uno_con_un_cambio()
        self.git_en(clon, 'remote', 'remove', 'origin')
        antes = (self.head(clon), self.estado_git(clon), self.arbol(clon))
        impreso = self.mal(self.producto, 'sincronizar')
        self.assertIn('remoto', impreso.casefold())
        self.assertEqual((self.head(clon), self.estado_git(clon), self.arbol(clon)), antes)

    def test_as3_un_conflicto_sin_driver_deshace_la_union_y_nombra_los_archivos(self):
        clon, _ = self.uno_con_un_cambio()  # sin .gitattributes todavía: sincronizar lo escribe, y al deshacer no queda
        self.tercero_sube('notas.md', 'notas del tercero\n')
        (clon / 'notas.md').write_text('notas de la persona uno\n', encoding='utf-8')
        self.git_en(clon, 'commit', '-q', '-am', 'la persona uno cambia las notas')
        antes, refs = (self.head(clon), self.arbol(clon)), self.refs()
        impreso = self.mal(self.producto, 'sincronizar')
        self.assertIn('notas.md', impreso)
        self.assertEqual((self.head(clon), self.arbol(clon)), antes)
        self.assertEqual(self.estado_git(clon), '')
        self.assertFalse((clon / '.git/MERGE_HEAD').exists())
        self.assertEqual(self.refs(), refs)
        self.assertEqual((clon / 'notas.md').read_text(encoding='utf-8'), 'notas de la persona uno\n')


del _Base  # que el cargador no vuelva a correr las pruebas de la etapa 4a desde este módulo


if __name__ == '__main__':
    unittest.main()
