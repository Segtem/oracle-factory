"""Registros fuera del repo del producto: preparar la migración real de Factory (pm1–pm4).

Mismo entorno que tests/test_almacen_commits.py: producto y almacén como repos Git temporales; HOME, XDG y la configuración
global de Git temporales. pm2 parte del producto con registros adentro de tests/test_almacen_migrar.py."""
import json
import os
from pathlib import Path
import subprocess
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import test_almacen_commits as _commits  # noqa: E402
import test_almacen_guia as _guia  # noqa: E402
import test_almacen_migrar as _migrar  # noqa: E402
import test_verificador_generico as _vg  # noqa: E402
from oracle_factory import agentes as agentes_mod  # noqa: E402

f = _commits.f
SOURCE = Path(__file__).resolve().parents[1]
DEL_TRAILER = ('commit-msg', 'prepare-commit-msg', 'post-commit', 'post-merge')
AJENO = '#!/bin/sh\n# un hook del equipo, no de Factory\nexit 0\n'


def prestados(clase, *nombres):
    """Los ayudantes de otra clase de pruebas sin heredarla: heredarla correría también sus pruebas en este módulo."""
    return {n: getattr(clase, n) for n in nombres}


class Conectado(unittest.TestCase):
    """Producto y almacén temporales (el setUp de AlmacenCommits), con los ayudantes en/bien/mal de AlmacenGuia."""
    locals().update(prestados(_guia.AlmacenGuia, 'git_en', 'arbol', 'configuraciones', 'setUp', 'en', 'bien', 'mal',
                              'exclusiones', 'estado'))

    def escribir(self, raiz, ruta, texto):
        (raiz / ruta).parent.mkdir(parents=True, exist_ok=True)
        (raiz / ruta).write_text(texto, encoding='utf-8')

    def commitear(self, raiz, mensaje):
        self.git_en(raiz, 'add', '-A')
        self.git_en(raiz, 'commit', '-q', '-m', mensaje)


# --- pm1: las pruebas y las herramientas leen los registros del almacén -------------------------------------------------
class Registros(Conectado):
    def con_demo(self, registros):
        """El cambio de demo de test_verificador_generico: la spec y el registro en `registros`, las pruebas en el producto."""
        self.escribir(self.producto, 'tests/test_demo.py', _vg.MODULO)
        self.escribir(self.producto, '.gitignore', '__pycache__/\nevidencia/\n')
        self.escribir(registros, f'openspec/changes/{_vg.CAMBIO}/specs/demo/spec.md', _vg.SPEC)
        self.escribir(registros, f'.factory/cambios/{_vg.CAMBIO}/factory.json',
                      json.dumps({'requisitos': ['demo_h.el_segundo', 'demo_h.el_primero']}))
        self.commitear(self.producto, 'pruebas')

    def verificar_cambio(self, *args):
        return subprocess.run([sys.executable, str(SOURCE / 'tools/verificar_cambio.py'), _vg.CAMBIO, '--pruebas', 'test_demo',
                               '--raiz', str(self.producto), *args], env=dict(os.environ), capture_output=True, text=True,
                              stdin=subprocess.DEVNULL, timeout=300)

    def test_pm1_registros_de_dice_el_almacen_si_el_producto_esta_conectado(self):
        self.assertEqual(f.almacenes.registros_de(self.producto), self.producto)
        self.bien('conectar', str(self.almacen))
        self.assertEqual(f.almacenes.registros_de(self.producto), self.almacen)
        sub = self.producto / 'sub'
        sub.mkdir()
        self.assertEqual(f.almacenes.registros_de(sub), self.almacen)  # desde una carpeta del producto, lo mismo

    def test_pm1_verificar_cambio_con_el_producto_conectado_lee_y_escribe_en_el_almacen(self):
        self.bien('conectar', str(self.almacen))
        self.con_demo(self.almacen)
        r = self.verificar_cambio('--catalogos', '--salida', str(self.producto / 'evidencia'))
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertEqual(sorted(p.name for p in (self.almacen / 'catalogos').glob('*.oracle')),
                         ['factory_demo.corrida_completa.oracle', 'factory_demo.el_primero.oracle', 'factory_demo.el_segundo.oracle'])
        self.assertTrue(json.loads((self.producto / 'evidencia/resultado.json').read_text(encoding='utf-8'))['exitoso'])
        for registro in ('catalogos', 'openspec', '.factory'):
            self.assertFalse((self.producto / registro).exists(), registro)

    def test_pm1_sin_conexion_lee_y_escribe_en_el_producto(self):
        self.con_demo(self.producto)
        r = self.verificar_cambio('--catalogos')
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertTrue((self.producto / 'catalogos/factory_demo.corrida_completa.oracle').is_file())
        self.assertFalse((self.almacen / 'catalogos').exists())


# --- pm2: migrar limpia lo de Factory del producto ----------------------------------------------------------------------
class Limpieza(unittest.TestCase):
    locals().update(prestados(_migrar.AlmacenMigrar, 'git_en', 'corre', 'bien', 'arbol', 'commits', 'estado_git',
                              'registros_versionados', 'todo', 'negado'))

    def setUp(self):
        _migrar.AlmacenMigrar.setUp(self)
        dice = subprocess.run(['git', 'rev-parse', '--git-path', 'hooks'], cwd=self.producto, capture_output=True, text=True,
                              check=True).stdout.strip()  # sin el core.hooksPath de GIT, como lo ve Factory
        self.hooks = self.producto / dice
        self.hooks.mkdir(parents=True, exist_ok=True)
        (self.hooks / 'post-merge').write_text(AJENO, encoding='utf-8')  # uno del equipo: hooks no lo pisa y migrar no lo saca
        self.bien('hooks')
        ignore = self.producto / '.gitignore'
        propio = ignore.read_text(encoding='utf-8') if ignore.exists() else ''
        lineas = propio.splitlines()
        for linea in (f.estructura.IGNORAR_LOCAL, f.estructura.IGNORAR_CLUE):
            if linea not in lineas:
                propio += linea + '\n'
        ignore.write_text('# del equipo\nsecretos.env\n' + propio, encoding='utf-8')
        atributos = self.producto / '.gitattributes'
        atributos.write_text('*.png binary\n' + (atributos.read_text(encoding='utf-8') if atributos.exists() else ''), encoding='utf-8')
        self.assertTrue(f.ATRIBUTOS_MARCA in atributos.read_text(encoding='utf-8'))
        self.git_en(self.producto, 'add', '.gitignore', '.gitattributes')
        self.git_en(self.producto, 'commit', '-q', '-m', 'líneas propias y de Factory')

    def hooks_de_factory(self):
        return {n for n in DEL_TRAILER if (self.hooks / n).is_file() and f.HOOK_MARCA in (self.hooks / n).read_text(encoding='utf-8')}

    def test_pm2_migrar_saca_las_lineas_y_los_hooks_de_factory(self):
        self.assertEqual(self.hooks_de_factory(), {'commit-msg', 'prepare-commit-msg', 'post-commit'})
        pre_push = (self.hooks / 'pre-push').read_bytes()
        self.bien('migrar', '--almacen', str(self.almacen))
        ignore = (self.producto / '.gitignore').read_text(encoding='utf-8').splitlines()
        self.assertIn('secretos.env', ignore)
        self.assertIn('# del equipo', ignore)
        self.assertNotIn(f.estructura.IGNORAR_LOCAL, ignore)
        self.assertNotIn(f.estructura.IGNORAR_CLUE, ignore)
        atributos = (self.producto / '.gitattributes').read_text(encoding='utf-8')
        self.assertEqual(atributos, '*.png binary\n')
        indice = self.git_en(self.producto, 'diff', '--cached', '--name-status').splitlines()
        self.assertIn('M\t.gitignore', indice)
        self.assertIn('M\t.gitattributes', indice)
        self.assertEqual(self.git_en(self.producto, 'diff', '--name-only'), '')  # todo quedó en el índice
        del_almacen = self.git_en(self.almacen, 'show', 'HEAD:.gitattributes').splitlines()
        for linea in (f.ATRIBUTOS_MARCA, *f.ATRIBUTOS):
            self.assertIn(linea, del_almacen)
        self.assertEqual(self.estado_git(), '')
        self.assertEqual(self.hooks_de_factory(), set())
        self.assertEqual((self.hooks / 'post-merge').read_text(encoding='utf-8'), AJENO)
        self.assertEqual((self.hooks / 'pre-push').read_bytes(), pre_push)

    def test_pm2_un_gitignore_que_solo_tiene_lineas_de_factory_se_borra(self):
        (self.producto / '.gitignore').write_text(f.estructura.IGNORAR_LOCAL + '\n' + f.estructura.IGNORAR_CLUE + '\n', encoding='utf-8')
        self.git_en(self.producto, 'commit', '-q', '-am', 'sólo Factory')
        self.bien('migrar', '--almacen', str(self.almacen))
        self.assertFalse((self.producto / '.gitignore').exists())
        self.assertIn('D\t.gitignore', self.git_en(self.producto, 'diff', '--cached', '--name-status').splitlines())

    def test_pm2_verificar_dice_que_sacaria_y_no_escribe(self):
        antes, hooks = self.todo(), {p.name: p.read_bytes() for p in self.hooks.iterdir()}
        salida = self.bien('migrar', '--almacen', str(self.almacen), '--verificar')
        for nombre in ('.gitignore', '.gitattributes', 'commit-msg', 'prepare-commit-msg', 'post-commit'):
            self.assertIn(nombre, salida)
        self.assertEqual(self.todo(), antes)
        self.assertEqual({p.name: p.read_bytes() for p in self.hooks.iterdir()}, hooks)

    def test_pm2_un_gitignore_sin_commitear_no_migra(self):
        with open(self.producto / '.gitignore', 'a', encoding='utf-8') as archivo:
            archivo.write('a-medias\n')
        hooks = {p.name: p.read_bytes() for p in self.hooks.iterdir()}
        self.assertIn('.gitignore', self.negado())
        self.assertEqual({p.name: p.read_bytes() for p in self.hooks.iterdir()}, hooks)


# --- pm3: la puerta funciona con el producto conectado ------------------------------------------------------------------
class Puerta(Conectado):
    def setUp(self):
        super().setUp()
        self.bien('conectar', str(self.almacen))
        codigo, impreso = self.en(self.producto, '--agente', 'claude-code', 'nuevo', 'Notas', '--capacidad', 'notas', '--sufijo', 'pt')
        self.assertEqual(codigo, 0, impreso)
        self.bien('agentes')  # la guía en el producto, sin versionar

    def puerta(self):
        return self.en(self.producto, 'puerta', 'HEAD~1..HEAD')

    def test_pm3_un_secreto_en_el_producto_bloquea(self):
        self.escribir(self.producto, 'config.py', f'clave = "{"AKIA" + "IOSFODNN7EXAMPLE"}"\n')
        self.commitear(self.producto, 'con un secreto')
        codigo, impreso = self.puerta()
        self.assertEqual(codigo, f.puerta_mod.CODIGO_BLOQUEO, impreso)
        self.assertIn('config.py', impreso)

    def test_pm3_sin_secretos_y_con_los_registros_al_dia_deja_pasar(self):
        self.escribir(self.producto, 'codigo.py', 'x = 1\n')
        self.commitear(self.producto, 'código')
        codigo, impreso = self.puerta()
        self.assertEqual(codigo, 0, impreso)
        self.assertIn('ninguno en los commits', impreso)
        self.assertIn('agentes', impreso.split('verificaciones:', 1)[1].split('\n', 1)[0])  # la guía del producto se verificó
        self.assertNotIn('se omiten agentes', impreso)

    def test_pm3_una_guia_vieja_en_el_producto_bloquea(self):
        guia = self.producto / 'AGENTS.md'
        guia.write_text(guia.read_text(encoding='utf-8').replace('Oracle Factory', 'Factory vieja', 1), encoding='utf-8')
        self.escribir(self.producto, 'codigo.py', 'x = 1\n')
        self.commitear(self.producto, 'código')
        codigo, impreso = self.puerta()
        self.assertEqual(codigo, f.puerta_mod.CODIGO_BLOQUEO, impreso)
        self.assertIn('agentes:', impreso)


# --- pm4: agentes --en-el-repo mantiene una guía versionada --------------------------------------------------------------
class GuiaVersionada(Conectado):
    PROPIO = '# Mi producto\n\nInstrucciones propias del equipo.\n'

    def setUp(self):
        super().setUp()
        viejo = f'{agentes_mod.INICIO}\nuna guía vieja\n{agentes_mod.FIN}\n'
        self.escribir(self.producto, 'AGENTS.md', self.PROPIO + '\n' + viejo)
        self.escribir(self.producto, 'CLAUDE.md', 'Notas propias.\n')
        self.commitear(self.producto, 'guía versionada')
        self.bien('conectar', str(self.almacen))

    def test_pm4_en_el_repo_actualiza_el_bloque_de_la_guia_versionada(self):
        self.bien('agentes', '--en-el-repo')
        guia = (self.producto / 'AGENTS.md').read_text(encoding='utf-8')
        self.assertTrue(guia.startswith(self.PROPIO))
        self.assertNotIn('una guía vieja', guia)
        self.assertIn(agentes_mod.bloque(f.config_proyecto()['modo_por_defecto'], con_almacen=True).strip(), guia)
        claude = (self.producto / 'CLAUDE.md').read_text(encoding='utf-8')
        self.assertIn('Notas propias.', claude)
        self.assertIn('@AGENTS.md', claude)
        self.assertNotIn('AGENTS.md', self.exclusiones())
        self.assertEqual(self.git_en(self.producto, 'diff', '--name-only').splitlines(), ['AGENTS.md', 'CLAUDE.md'])  # el repo ve el cambio
        self.bien('agentes', '--verificar')
        self.bien('agentes', '--en-el-repo')  # otra vez: nada cambia
        self.assertEqual((self.producto / 'AGENTS.md').read_text(encoding='utf-8'), guia)

    def test_pm4_sin_la_opcion_se_niega_y_no_escribe(self):
        antes = self.arbol(self.producto)
        self.assertIn('--en-el-repo', self.mal('agentes'))
        self.assertEqual(self.arbol(self.producto), antes)
        self.assertIn('al día', self.mal('agentes', '--verificar').replace('no está al día', 'al día'))

    def test_pm4_un_agente_no_usa_en_el_repo(self):
        antes = self.arbol(self.producto)
        self.assertIn('persona', self.mal('--agente', 'claude-code', 'agentes', '--en-el-repo'))
        self.assertEqual(self.arbol(self.producto), antes)


if __name__ == '__main__':
    unittest.main()
