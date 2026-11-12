"""Registros fuera del repo del producto, etapa 6: migrar los registros de un proyecto a un almacén (mg1–mg4).

Producto y almacén son repos Git temporales con el entorno aislado de tests/test_almacen_commits.py (HOME, XDG y la
configuración global de Git temporales). El producto empieza con sus registros adentro, como Factory mismo."""
import json
from pathlib import Path
import subprocess
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import test_almacen_commits as _commits  # noqa: E402

f = _commits.f
SOURCE = Path(__file__).resolve().parents[1]
REGISTROS = ('.factory', 'openspec', 'requisitos', 'catalogos', 'tareas', 'kb', 'oracle.json')


class AlmacenMigrar(unittest.TestCase):
    _c = _commits.AlmacenCommits
    git_en, corre, bien, arbol, commits, estado_git = _c.git_en, _c.corre, _c.bien, _c.arbol, _c.commits, _c.estado_git

    def setUp(self):
        _commits.AlmacenCommits.setUp(self)
        p = _commits.patch.dict(_commits.os.environ, {'XDG_DATA_HOME': str(self.casa / '.local/share')}); p.start(); self.addCleanup(p.stop)
        self.bien('init')
        self.bien('nuevo', 'Notas compartidas', '--capacidad', 'notas', '--sufijo', 'mg')
        self.git_en(self.producto, 'add', '-A')
        self.git_en(self.producto, 'commit', '-q', '-m', 'registros adentro')
        (self.producto / '.factory/local').mkdir(exist_ok=True)
        (self.producto / '.factory/local/nota.txt').write_text('mía, no versionada\n', encoding='utf-8')

    def registros_versionados(self):
        salida = self.git_en(self.producto, 'ls-files', '-z', '--', *REGISTROS)
        return {n: (self.producto / n).read_bytes() for n in salida.split('\0') if n}

    def todo(self):
        repos = [r for r in (self.producto, self.almacen) if (r / '.git').exists()]
        return ({str(r): (self.arbol(r), self.git_en(r, 'rev-parse', 'HEAD'), self.estado_git(r),
                          self.git_en(r, 'diff', '--cached', '--name-status')) for r in repos},
                self.arbol(self.casa))

    def listado(self):  # sin la línea «Acuerdos: RUTA», que dice dónde están los registros (cambia a propósito)
        return [l for l in self.bien('listar').splitlines() if not l.startswith('Acuerdos:')]

    # --- mg1: migrar copia, conecta y deja la baja ---------------------------------------------------------------------------
    def test_mg1_migrar_copia_conecta_y_deja_la_baja_sin_commitear(self):
        antes, cabeza, listado = self.registros_versionados(), self.git_en(self.producto, 'rev-parse', 'HEAD'), self.listado()
        self.assertTrue(any(n.startswith('.factory/cambios/') for n in antes))
        commits = self.commits()
        self.bien('migrar', '--almacen', str(self.almacen))
        for nombre, contenido in antes.items():
            self.assertEqual((self.almacen / nombre).read_bytes(), contenido, nombre)
        self.assertEqual(self.commits(), commits + 1)
        mensaje = self.git_en(self.almacen, 'log', '-1', '--format=%B')
        self.assertIn(cabeza, mensaje)
        self.assertEqual(self.estado_git(), '')  # todo lo copiado quedó en el commit
        self.assertEqual((self.almacen / 'notas.md').read_text(encoding='utf-8'), 'notas del equipo\n')
        self.assertEqual((self.almacen / '.factory/local/nota.txt').read_text(encoding='utf-8'), 'mía, no versionada\n')
        self.assertFalse((self.producto / '.factory').exists())
        self.assertEqual(self.git_en(self.producto, 'rev-parse', 'HEAD'), cabeza)  # Factory no commitea en el producto
        baja = self.git_en(self.producto, 'diff', '--cached', '--name-status').splitlines()
        self.assertEqual(sorted(baja), sorted(f'D\t{n}' for n in antes))
        self.assertTrue(all(not (self.producto / n).exists() for n in antes))
        self.assertEqual(json.loads(self.bien('conectar', '--json').split('\n')[0])['almacen'], str(self.almacen))
        self.assertEqual(self.listado(), listado)

    def test_mg1_migrar_a_una_url_clona_y_migra_ahi(self):
        remoto = self.base / 'remoto.git'
        self.git_en(self.base, 'init', '-q', '--bare', str(remoto))
        antes = self.registros_versionados()
        self.bien('migrar', '--almacen', remoto.as_uri())
        clon = self.casa / '.local/share/oracle-factory/almacenes/remoto'
        for nombre, contenido in antes.items():
            self.assertEqual((clon / nombre).read_bytes(), contenido, nombre)
        self.assertEqual(self.estado_git(clon), '')
        self.assertEqual(json.loads(self.bien('conectar', '--json').split('\n')[0])['almacen'], str(clon))
        self.assertFalse((self.producto / '.factory').exists())

    # --- mg2: --verificar no escribe ----------------------------------------------------------------------------------------
    def test_mg2_verificar_dice_lo_que_haria_y_no_escribe(self):
        antes = self.todo()
        salida = self.bien('migrar', '--almacen', str(self.almacen), '--verificar')
        self.assertIn(f'{len(self.registros_versionados())} archivos versionados', salida)
        self.assertIn('.factory/local/nota.txt', salida)
        self.assertEqual(self.todo(), antes)

    def test_mg2_verificar_falla_si_migrar_se_negaria(self):
        (self.almacen / '.factory').mkdir()
        (self.almacen / '.factory/config.json').write_text('{}\n', encoding='utf-8')
        antes = self.todo()
        codigo, _, _ = self.corre('migrar', '--almacen', str(self.almacen), '--verificar')
        self.assertNotEqual(codigo, 0)
        self.assertEqual(self.todo(), antes)

    # --- mg3: se niega sin tocar nada ---------------------------------------------------------------------------------------
    def negado(self, *args, agente=None, destino=None):
        antes = self.todo()
        codigo, salida, error = self.corre('migrar', '--almacen', str(destino or self.almacen), *args, agente=agente)
        self.assertNotEqual(codigo, 0, salida + error)
        self.assertEqual(self.todo(), antes)
        return error

    def test_mg3_un_agente_no_migra(self):
        self.assertIn('persona', self.negado(agente='claude-code'))

    def test_mg3_un_producto_ya_conectado_no_migra(self):
        config = self.casa / '.config/oracle-factory/almacenes.json'
        config.parent.mkdir(parents=True)
        clave = str(Path(self.git_en(self.producto, 'rev-parse', '--path-format=absolute', '--git-common-dir')).resolve())
        config.write_text(json.dumps({clave: str(self.base / 'otro')}), encoding='utf-8')
        self.negado()

    def test_mg3_registros_sin_commitear_no_migran(self):
        tarea = next((self.producto / 'tareas').rglob('TAREA.md'))
        tarea.write_text(tarea.read_text(encoding='utf-8') + 'a mano\n', encoding='utf-8')
        self.assertIn('sin commitear', self.negado())

    def test_mg3_un_archivo_sin_versionar_en_los_registros_no_migra(self):
        (self.producto / 'openspec/suelto.md').write_text('suelto\n', encoding='utf-8')
        self.assertIn('openspec/suelto.md', self.negado())

    def test_mg3_el_formato_anterior_no_migra(self):
        (self.producto / 'factory.json').write_text('{"revisores": {}}\n', encoding='utf-8')
        self.git_en(self.producto, 'add', 'factory.json')
        self.git_en(self.producto, 'commit', '-q', '-m', 'config vieja')
        self.assertIn('migrar', self.negado())

    def test_mg3_un_almacen_que_no_es_un_repo_no_sirve(self):
        suelta = self.base / 'suelta'
        suelta.mkdir()
        self.negado(destino=suelta)

    def test_mg3_un_almacen_con_registros_no_sirve(self):
        (self.almacen / 'requisitos').mkdir()
        (self.almacen / 'requisitos/x.requisito').write_text('x\n', encoding='utf-8')
        self.git_en(self.almacen, 'add', '-A')
        self.git_en(self.almacen, 'commit', '-q', '-m', 'con registros')
        self.negado()

    def test_mg3_almacen_y_producto_uno_dentro_del_otro(self):
        adentro = self.producto / 'sub'
        adentro.mkdir()
        self.git_en(adentro, 'init', '-q')
        self.negado(destino=adentro)

    # --- mg4: el ensayo sobre una copia -------------------------------------------------------------------------------------
    def ensayo(self, *args):
        informe = self.base / 'informe.json'
        r = subprocess.run([sys.executable, str(SOURCE / 'tools/ensayar_migracion.py'), str(self.producto), '--informe', str(informe), *args],
                           capture_output=True, text=True, timeout=600, stdin=subprocess.DEVNULL)
        self.assertEqual(r.returncode, 0, r.stderr)
        return json.loads(informe.read_text(encoding='utf-8'))

    def test_mg4_el_ensayo_migra_una_copia_y_no_toca_el_original(self):
        antes = self.todo()
        datos = self.ensayo()
        self.assertTrue(datos['coinciden'])
        self.assertEqual(datos['antes'], datos['despues'])
        self.assertIn('mg', datos['antes'])
        self.assertEqual(self.todo(), antes)

    def test_mg4_con_pruebas_dice_cuales_fallan_con_los_registros_afuera(self):
        (self.producto / 'tests').mkdir()
        (self.producto / 'tests/test_registros.py').write_text(
            'import pathlib, unittest\n'
            'class R(unittest.TestCase):\n'
            '    def test_hay_factory(self):\n'
            '        self.assertTrue((pathlib.Path(__file__).parents[1] / ".factory").is_dir())\n'
            '    def test_otra(self):\n'
            '        pass\n'
            '    def test_siempre_falla(self):\n'
            '        self.fail("ya fallaba")\n', encoding='utf-8')
        self.git_en(self.producto, 'add', 'tests')
        self.git_en(self.producto, 'commit', '-q', '-m', 'pruebas')
        datos = self.ensayo('--pruebas')
        self.assertNotEqual(datos['pruebas']['codigo'], 0)
        self.assertEqual([n for n in datos['pruebas']['fallan'] if 'test_hay_factory' in n], datos['pruebas']['fallan'])
        self.assertEqual(len(datos['pruebas']['fallan']), 1)
        self.assertEqual([n for n in datos['pruebas']['antes']['fallan'] if 'test_siempre_falla' in n], datos['pruebas']['antes']['fallan'])
        self.assertEqual(len(datos['pruebas']['antes']['fallan']), 1)  # la que ya fallaba antes no cuenta como de la migración

    def test_mg4_si_los_cambios_no_coinciden_lo_dice_y_sale_con_1(self):
        sys.path.insert(0, str(SOURCE / 'tools'))
        self.addCleanup(sys.path.remove, str(SOURCE / 'tools'))
        import ensayar_migracion
        vistas = iter(['cambio A', 'cambio A y otro'])
        informe = self.base / 'informe.json'
        with _commits.patch.object(ensayar_migracion, 'listado', lambda copia, entorno: next(vistas)):
            codigo = ensayar_migracion.main([str(self.producto), '--informe', str(informe)])
        datos = json.loads(informe.read_text(encoding='utf-8'))
        self.assertEqual((codigo, datos['coinciden']), (1, False))


if __name__ == '__main__':
    unittest.main()
