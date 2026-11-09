"""Registros fuera del repo del producto, etapa 1: escenarios rr1–rr3 de la spec (dos raíces: producto y registros).

Se corre la CLI en el mismo proceso (`f.main`) con `--proyecto` (el producto) y, cuando hace falta, `--registros` (el almacén).
La implementación guarda la raíz de los registros en `f.REGISTROS`; `main` la fija en cada invocación (sin `--registros`, es ROOT).
"""
import contextlib
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import test_archivo as _archivo  # noqa: E402

f = _archivo.f
GIT = _archivo.GIT
SPEC = '''# Capability: notas

## ADDED Requirements

### Requirement: titulo valido
Tipo: funcional
El sistema SHALL validar el título.

#### Scenario: titulo vacio
- GIVEN un título vacío
- WHEN se guarda
- THEN se rechaza
'''
ETAPA_3 = 'etapa 3 de 6'


class RegistrosRaiz(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        base = Path(self.tmp.name)
        self.producto, self.almacen = base / 'producto', base / 'almacen'
        self.producto.mkdir()
        self.almacen.mkdir()
        # Lo que main reasigna en cada corrida se restaura al terminar, para no contaminar a los demás tests.
        for nombre, valor in [('ROOT', self.producto), ('CHANGES', self.producto / 'openspec/changes'), ('AGENTE', None),
                              ('REGISTROS', self.producto)]:
            p = patch.object(f, nombre, valor, create=True); p.start(); self.addCleanup(p.stop)
        p = patch.object(f, 'terminal_interactiva', return_value=True); p.start(); self.addCleanup(p.stop)

    # --- ayudantes -----------------------------------------------------------------
    def git(self, *args):
        return subprocess.run([*GIT, *args], cwd=self.producto, check=True, capture_output=True, text=True).stdout.strip()

    def producto_con_git(self):
        self.git('init', '-q', '-b', 'main')
        (self.producto / 'README.md').write_text('producto\n', encoding='utf-8')
        (self.producto / 'src').mkdir()
        (self.producto / 'src/app.py').write_text('print("hola")\n', encoding='utf-8')
        self.git('add', '-A')
        self.git('commit', '-q', '-m', 'producto inicial')

    def corre(self, *args, registros=True, respuestas=('1',)):
        """(código, salida, error) de `oracle-factory --proyecto PRODUCTO [--registros ALMACEN] ARGS` en este proceso."""
        out, err = io.StringIO(), io.StringIO()
        base = ['--proyecto', str(self.producto)] + (['--registros', str(self.almacen)] if registros else [])
        with patch('builtins.input', side_effect=list(respuestas) + ['1'] * 5), contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            codigo = f.main([*base, *args])
        return codigo, out.getvalue(), err.getvalue()

    def arbol(self, raiz):
        return {str(p.relative_to(raiz)): p.read_bytes() for p in sorted(raiz.rglob('*'))
                if p.is_file() and '.git' not in p.relative_to(raiz).parts}

    def identificador(self):
        return next(p.name for p in (self.almacen / 'openspec/changes').iterdir() if p.is_dir())

    def cambio_en_el_almacen(self, hasta='importar'):
        """init, nuevo, spec escrita, aprobar-spec e importar, todo con --registros; devuelve el id."""
        self.assertEqual(self.corre('init')[0], 0)
        self.assertEqual(self.corre('nuevo', 'Notas', '--capacidad', 'notas', '--sufijo', 'rr')[0], 0)
        ident = self.identificador()
        estado = json.loads((self.almacen / '.factory/cambios' / ident / 'factory.json').read_text(encoding='utf-8'))
        (self.almacen / estado['spec']).write_text(SPEC, encoding='utf-8')
        (self.almacen / 'openspec/changes' / ident / 'proposal.md').write_text('# Notas\n\nFixture.\n', encoding='utf-8')
        if hasta == 'nuevo':
            return ident
        self.assertEqual(self.corre('aprobar-spec', ident)[0], 0)
        self.assertEqual(self.corre('importar', ident)[0], 0)
        return ident

    # --- rr1: sin --registros nada cambia -------------------------------------------------------------------------
    def test_rr1_sin_la_opcion_los_registros_son_los_del_producto(self):
        self.producto_con_git()
        self.assertEqual(self.corre('init', registros=False)[0], 0)
        self.assertEqual(self.corre('nuevo', 'Notas', '--capacidad', 'notas', '--sufijo', 'rr', registros=False)[0], 0)
        self.assertEqual(f.REGISTROS, self.producto)
        for ruta in ('.factory/config.json', 'tareas', 'openspec/changes'):
            self.assertTrue((self.producto / ruta).exists(), ruta)
        self.assertEqual(list(self.almacen.iterdir()), [])
        codigo, salida, _ = self.corre('listar', registros=False)
        self.assertEqual(codigo, 0)
        self.assertIn('rr', salida)

    def test_rr1_registros_igual_al_producto_es_lo_mismo_que_no_darlo(self):
        self.producto_con_git()
        self.assertEqual(self.corre('init', registros=False)[0], 0)
        sin = self.corre('listar', registros=False)
        with patch.object(self, 'almacen', self.producto):
            con = self.corre('listar')
        self.assertEqual(sin, con)
        (self.producto / 'sub').mkdir()
        for ruta in (self.producto, self.producto / '..' / 'producto', self.producto / 'sub' / '..'):  # el mismo lugar, escrito de otra manera
            with patch.object(self, 'almacen', ruta):
                self.assertNotIn(ETAPA_3, self.corre('juzgar', 'x')[2], ruta)  # no cuenta como registros aparte
        self.assertNotIn(ETAPA_3, self.corre('juzgar', 'x', registros=False)[2])  # sin la opción, un comando de candidato sigue siendo el de siempre

    # --- rr2: con --registros el producto queda limpio -------------------------------------------------------------
    def test_rr2_un_cambio_completo_hasta_las_medidas(self):
        self.producto_con_git()
        antes = self.arbol(self.producto)
        ident = self.cambio_en_el_almacen()
        for ruta in ('.factory/config.json', f'.factory/cambios/{ident}/factory.json', f'tareas/{ident}/TAREA.md',
                     f'openspec/changes/{ident}/proposal.md', 'requisitos'):
            self.assertTrue((self.almacen / ruta).exists(), ruta)
        self.assertEqual(self.corre('medir', ident, '--listar')[0], 0)
        self.assertEqual(self.corre('mensaje', ident, 'hola')[0], 0)
        self.assertEqual(self.corre('tomar', ident)[0], 0)
        self.assertEqual(self.corre('soltar', ident)[0], 0)
        self.assertEqual(self.corre('listar')[0], 0)
        self.assertEqual(self.corre('estado', ident)[0], 0)
        self.assertEqual(self.git('status', '--porcelain', '--untracked-files=all'), '')
        self.assertEqual(self.arbol(self.producto), antes)  # ni un archivo nuevo ni modificado, tampoco ignorado
        # lo que ve el código por dentro: la raíz de los registros, la del producto, y que se suelta al terminar
        visto = {}
        with patch.object(f, 'listar', side_effect=lambda *a, **k: visto.update(registros=f.REGISTROS, root=f.ROOT, producto=f.PRODUCTO)):
            self.corre('listar')
        self.assertEqual(visto, {'registros': self.almacen.resolve(), 'root': self.almacen.resolve(), 'producto': self.producto.resolve()})
        with patch.object(self, 'almacen', self.almacen / '..' / 'almacen'):  # el almacén escrito con «..»: la raíz queda resuelta
            visto.clear()
            with patch.object(f, 'listar', side_effect=lambda *a, **k: visto.update(root=f.ROOT)):
                self.corre('listar')
            self.assertEqual(visto, {'root': self.almacen.resolve()})
        self.assertIsNone(f.PRODUCTO)
        self.assertEqual(f.argumentos_de_raiz(), ['--proyecto', str(f.ROOT)])
        with patch.object(f, 'PRODUCTO', self.producto):
            self.assertEqual(f.argumentos_de_raiz(), ['--proyecto', str(self.producto), '--registros', str(f.ROOT)])
        # verificar_en_proceso corre sobre las dos raíces y las deja como estaban
        with patch.object(f, 'PRODUCTO', self.producto), patch.object(f, 'ROOT', self.almacen), patch.object(f, 'REGISTROS', Path('/otra')):
            original, adentro = f.listar, {}

            def espiar(*a, **k):
                adentro.update(producto=f.PRODUCTO, root=f.ROOT)
                return original(*a, **k)
            with patch.object(f, 'listar', side_effect=espiar):
                codigo, salida = f.verificar_en_proceso(['listar'])
            self.assertEqual(adentro, {'producto': self.producto.resolve(), 'root': self.almacen.resolve()})  # adentro también están las dos raíces
            self.assertEqual((codigo, f.ROOT, f.PRODUCTO, f.REGISTROS), (0, self.almacen, self.producto, Path('/otra')))
            self.assertIn(ident, salida)
        # el menú «¿Seguís?» vuelve a llamar con las dos raíces
        class Tty(io.StringIO):
            def isatty(self):
                return True
        with patch.object(f, 'PRODUCTO', self.producto), patch.object(f, 'AGENTE', None), patch.object(f, 'elegir', return_value=0), \
                patch.object(f, 'pasos', return_value=['oracle-factory estado ID']), patch.object(f, 'main') as principal, contextlib.redirect_stdout(Tty()):
            f.ofrecer_siguiente(ident)
        principal.assert_called_once_with(['--proyecto', str(self.producto), '--registros', str(f.ROOT), 'estado', 'ID'])

    def test_rr2_el_producto_con_su_propio_git_no_cambia(self):
        self.producto_con_git()
        (self.producto / '.gitignore').write_text('*.tmp\n', encoding='utf-8')
        self.git('add', '-A')
        self.git('commit', '-q', '-m', 'ignora')
        cabeza, ramas, indice = self.git('rev-parse', 'HEAD'), self.git('branch', '--list'), self.git('ls-files', '-s')
        gitignore = (self.producto / '.gitignore').read_bytes()
        self.cambio_en_el_almacen()
        self.assertEqual((self.git('rev-parse', 'HEAD'), self.git('branch', '--list'), self.git('ls-files', '-s')), (cabeza, ramas, indice))
        self.assertEqual((self.producto / '.gitignore').read_bytes(), gitignore)  # init tampoco toca el .gitignore del producto
        self.assertEqual(self.git('status', '--porcelain', '--untracked-files=all'), '')

    # --- rr3: lo que necesita candidato no inventa uno --------------------------------------------------------------
    def test_rr3_un_comando_de_candidato_falla_con_el_mensaje_de_la_etapa_3(self):
        self.producto_con_git()
        ident = self.cambio_en_el_almacen()
        comandos = [('pedir-revision', ident, '--a', 'codex'), ('revision-preparar', ident),
                    ('revision', ident, '--informe', 'x.json', '--revisor', 'R', '--decision', 'aprobar', '--hallazgos-abiertos', '0'),
                    ('revisar', ident), ('juzgar', ident), ('cerrar', ident)]
        for comando in comandos:
            with self.subTest(comando=comando[0]):
                almacen, producto = self.arbol(self.almacen), self.arbol(self.producto)
                codigo, _, error = self.corre(*comando)
                self.assertNotEqual(codigo, 0)
                self.assertIn(ETAPA_3, error)
                self.assertIn('registros aparte', error)
                self.assertEqual((self.arbol(self.almacen), self.arbol(self.producto)), (almacen, producto))

    def test_rr3_estado_muestra_el_cambio_sin_candidato_vigente_y_no_escribe(self):
        self.producto_con_git()
        ident = self.cambio_en_el_almacen()
        almacen, producto = self.arbol(self.almacen), self.arbol(self.producto)
        codigo, salida, error = self.corre('estado', ident)
        self.assertEqual(codigo, 0, error)
        self.assertIn(ident, salida)
        self.assertNotIn('Traceback', error)
        self.assertEqual((self.arbol(self.almacen), self.arbol(self.producto)), (almacen, producto))


if __name__ == '__main__':
    unittest.main()
