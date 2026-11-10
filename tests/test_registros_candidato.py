"""Registros fuera del repo del producto, etapa 3: escenarios rc1–rc4 de la spec (el candidato y la huella con dos fuentes).

Se corre la CLI en el mismo proceso (`f.main`). El producto y el almacén son repos Git temporales; la conexión vive en la
configuración personal, con HOME y XDG_CONFIG_HOME en un directorio temporal: ninguna prueba lee ni escribe el HOME real.
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
import test_revisores as _revisores  # noqa: E402
from oracle_factory import trazabilidad as trazabilidad_mod  # noqa: E402

f = _archivo.f
GIT = _archivo.GIT
SPEC = '''# Capability: {capacidad}

## ADDED Requirements

### Requirement: titulo valido
Tipo: funcional
El sistema SHALL validar el título.

#### Scenario: titulo vacio
- GIVEN un título vacío
- WHEN se guarda
- THEN se rechaza
'''
MEDIDA = '''medida {id}:
    de rc_caso c
    donde c.codigo == 0
    resumen contar(1)
    umbral == 1 segun contrato porque "la fixture observa un caso"
    requiere rc_caso
    ambito universal
    alcance "fixture de prueba"
'''
APP = 'def saludo():\n    return "hola"\n'
PRUEBA = 'def test_saludo():\n    assert True\n    assert 1\n'


class RegistrosCandidato(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        base = Path(self.tmp.name).resolve()
        self.base = base
        self.producto, self.almacen, self.casa = base / 'producto', base / 'almacen', base / 'casa'
        for carpeta in (self.producto, self.almacen, self.casa):
            carpeta.mkdir()
        entorno = patch.dict(os.environ, {'HOME': str(self.casa), 'XDG_CONFIG_HOME': str(self.casa / '.config')})
        entorno.start(); self.addCleanup(entorno.stop)
        os.environ.pop('FACTORY_AGENTE', None)  # el --agente por omisión: aquí decide una persona salvo que se pida otra cosa
        self.addCleanup(os.chdir, os.getcwd())
        for nombre, valor in [('ROOT', self.producto), ('CHANGES', self.producto / 'openspec/changes'), ('AGENTE', None),
                              ('REGISTROS', self.producto)]:
            p = patch.object(f, nombre, valor, create=True); p.start(); self.addCleanup(p.stop)
        p = patch.object(f, 'terminal_interactiva', return_value=True); p.start(); self.addCleanup(p.stop)
        self.git_en(self.producto, 'init', '-q', '-b', 'main')
        (self.producto / '.gitignore').write_text('*.tmp\n', encoding='utf-8')
        (self.producto / 'README.md').write_text('producto\n', encoding='utf-8')
        (self.producto / 'src').mkdir()
        (self.producto / 'src/app.py').write_text(APP, encoding='utf-8')
        (self.producto / 'tests').mkdir()
        (self.producto / 'tests/test_app.py').write_text(PRUEBA, encoding='utf-8')
        self.git_en(self.producto, 'add', '-A')
        self.git_en(self.producto, 'commit', '-q', '-m', 'producto inicial')
        self.git_en(self.almacen, 'init', '-q', '-b', 'main')
        self.registros = self.almacen  # dónde están los registros: el almacén, o el producto en las pruebas sin almacén

    # --- ayudantes -----------------------------------------------------------------
    def git_en(self, carpeta, *args):
        return subprocess.run([*GIT, *args], cwd=carpeta, check=True, capture_output=True, text=True).stdout.strip()

    def corre(self, *args, agente=None):
        """(código, salida, error) de `oracle-factory [--agente A] --proyecto PRODUCTO ARGS` en este proceso."""
        out, err = io.StringIO(), io.StringIO()
        base = (['--agente', agente] if agente else []) + ['--proyecto', str(self.producto)]
        with patch('builtins.input', side_effect=['1'] * 12), contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            codigo = f.main([*base, *args])
        return codigo, out.getvalue(), err.getvalue()

    def ok(self, *args, agente=None):
        codigo, salida, error = self.corre(*args, agente=agente)
        self.assertEqual(codigo, 0, (args, salida[-2000:], error[-2000:]))
        return salida

    def arbol(self, raiz, con_git=False):
        return {str(p.relative_to(raiz)): p.read_bytes() for p in sorted(raiz.rglob('*'))
                if p.is_file() and (con_git or '.git' not in p.relative_to(raiz).parts)}

    def producto_entero(self):
        """El árbol de trabajo y el .git del producto, byte a byte (índice, refs, hooks, configuración y objetos)."""
        return self.arbol(self.producto, con_git=True)

    def conecta(self):
        self.ok('conectar', str(self.almacen))

    def sin_almacen(self):
        """Factory dentro del producto, como siempre: los registros son del producto."""
        self.registros = self.producto
        self.ok('init')

    def head(self):
        return self.git_en(self.producto, 'rev-parse', 'HEAD')[:7]

    def commit_producto(self, ruta='src/app.py', texto=None, mensaje='producto'):
        destino = self.producto / ruta
        destino.parent.mkdir(parents=True, exist_ok=True)
        destino.write_text(texto if texto is not None else destino.read_text(encoding='utf-8') + '# más\n', encoding='utf-8')
        self.git_en(self.producto, 'add', '-A')
        self.git_en(self.producto, 'commit', '-q', '-m', mensaje)
        return self.head()

    def cambio(self, sufijo='rc', capacidad='notas'):
        """nuevo, spec escrita, aprobar-spec e importar; devuelve el id."""
        antes = {p.name for p in (self.registros / 'openspec/changes').iterdir()} if (self.registros / 'openspec/changes').is_dir() else set()
        self.ok('nuevo', 'Notas', '--capacidad', capacidad, '--sufijo', sufijo)
        [ident] = {p.name for p in (self.registros / 'openspec/changes').iterdir() if p.is_dir()} - antes
        estado = self.registro(ident)
        (self.registros / estado['spec']).write_text(SPEC.format(capacidad=capacidad), encoding='utf-8')
        (self.registros / 'openspec/changes' / ident / 'proposal.md').write_text('# Notas\n\nFixture.\n', encoding='utf-8')
        self.ok('aprobar-spec', ident)
        self.ok('importar', ident)
        return ident

    def registro(self, ident):
        return json.loads((self.registros / '.factory/cambios' / ident / 'factory.json').read_text(encoding='utf-8'))

    def requisito(self, ident):
        return self.registro(ident)['requisitos'][0]

    def archivo_requisito(self, ident):
        return self.registros / 'requisitos' / f'{self.requisito(ident)}.requisito'

    def catalogo(self, medida):
        return self.registros / 'catalogos' / f'{medida}.oracle'

    def medir(self, ident, medida):
        """Escribe el catálogo de `medida` y una persona la elige para el requisito del cambio."""
        self.catalogo(medida).parent.mkdir(parents=True, exist_ok=True)
        self.catalogo(medida).write_text(MEDIDA.format(id=medida), encoding='utf-8')
        self.ok('medir', ident, '--requisito', self.requisito(ident), '--medida', medida, '--quitar-sin-medir')

    def evidencia(self, ident, sha=None):
        """La carpeta de evidencia del cambio para `sha` (por omisión, el HEAD del producto), con hechos y trazabilidad."""
        carpeta = self.registros / '.factory/cambios' / ident / 'candidatos' / (sha or self.head()) / 'evidencia'
        carpeta.mkdir(parents=True)
        (carpeta / 'hechos.json').write_text(json.dumps({'rc_caso': [{'codigo': 0}]}), encoding='utf-8')
        (carpeta / 'trazabilidad.json').write_text(json.dumps({'esquema': trazabilidad_mod.ESQUEMA_CASOS, 'requisitos': {}, 'casos': {}}),
                                                   encoding='utf-8')
        return carpeta

    def estado(self, ident):
        return json.loads(self.ok('estado', ident, '--json'))

    def candidato(self, ident):
        return self.estado(ident)['candidato']

    def vigentes(self, ident):
        e = self.estado(ident)
        return ((e.get('revision') or {}).get('vigente'), (e.get('oracle') or {}).get('vigente'))

    def informe(self, ident):
        destino = self.registros / 'tareas' / ident / 'revision.md'
        destino.write_text('Fixture de revisión; no es una revisión real.\n', encoding='utf-8')
        return destino

    def registrar_revision(self, ident):
        self.ok('revision', ident, '--informe', str(self.informe(ident)), '--revisor', 'Persona fixture', '--decision', 'aprobar',
                '--hallazgos-abiertos', '0')

    def revisor_de_prueba(self):
        script = self.base / 'revisor.py'
        script.write_text(_revisores.REVISOR, encoding='utf-8')
        config_ruta = self.registros / '.factory/config.json'
        config = json.loads(config_ruta.read_text(encoding='utf-8'))
        config['revisores'] = {'prueba': {'comando': [sys.executable, str(script), 'ok', '{paquete}', '{informe}'],
                                          'proveedor': 'revisor de prueba', 'modelo': 'fixture', 'tope_minutos': 1}}
        config_ruta.write_text(json.dumps(config), encoding='utf-8')

    def preparar_ciclo(self):
        """Un cambio con spec aprobada, su medida elegida, un revisor de prueba y, en la rama `tarea`, un commit de producto
        con su evidencia que cambia src/app.py y quita una aserción de una prueba existente.

        Devuelve (id, base del paquete = main, candidato). Sin almacén, lo de Factory se commitea con el producto (como siempre)."""
        ident = self.cambio()
        self.medir(ident, 'rc.casos')
        self.revisor_de_prueba()
        if self.registros == self.producto:
            self.git_en(self.producto, 'add', '-A')
            self.git_en(self.producto, 'commit', '-q', '-m', 'registros')
        base = self.git_en(self.producto, 'rev-parse', 'HEAD')
        self.git_en(self.producto, 'checkout', '-q', '-b', 'tarea')
        (self.producto / 'tests/test_app.py').write_text(PRUEBA.replace('    assert 1\n', ''), encoding='utf-8')
        sha = self.commit_producto(texto='def saludo():\n    return "hola, mundo"\n')
        self.evidencia(ident, sha)
        return ident, base, sha

    def ciclo(self, ident, base):
        """pedir-revision, revision-preparar, revisar (propuesta del agente), revision, juzgar y cerrar."""
        self.ok('pedir-revision', ident, '--a', 'prueba', '--base', base, agente='claude-code')
        self.ok('revision-preparar', ident, agente='claude-code')
        self.ok('revisar', ident, '--decision', 'aprobar', '--motivo', 'fixture: sin hallazgos', agente='claude-code')
        self.registrar_revision(ident)
        self.ok('juzgar', ident, agente='claude-code')
        self.ok('cerrar', ident)

    # --- rc1: con almacén aparte el candidato es el ancestro con evidencia -------------------------------------------
    def test_rc1_el_commit_con_evidencia_es_head(self):
        self.conecta()
        ident = self.cambio()
        self.evidencia(ident)
        self.assertEqual(self.candidato(ident), self.head())
        self.assertEqual(self.git_en(self.producto, 'status', '--porcelain', '--untracked-files=all'), '')
        # una carpeta de candidato sin su evidencia (sólo una revisión, o una evidencia que es un enlace) no es candidato (RCAND-1 de codex)
        otro_cambio = self.cambio(sufijo='rs', capacidad='sueltas')
        carpeta = self.registros / '.factory/cambios' / otro_cambio / 'candidatos' / self.head()
        (carpeta / 'revision').mkdir(parents=True)
        self.assertIsNone(self.candidato(otro_cambio))
        (carpeta / 'evidencia').symlink_to(carpeta / 'revision', target_is_directory=True)
        self.assertIsNone(self.candidato(otro_cambio))
        # la evidencia de otro cambio no hace candidato a este
        otro = self.cambio(sufijo='rd', capacidad='otras')
        self.assertIsNone(self.candidato(otro))

    def test_rc1_commits_sin_cambios_de_archivos_despues(self):
        self.conecta()
        ident = self.cambio()
        sha = self.head()
        self.evidencia(ident)
        self.git_en(self.producto, 'commit', '-q', '--allow-empty', '-m', 'vacío')
        self.git_en(self.producto, 'commit', '-q', '--allow-empty', '-m', 'otro vacío')
        self.assertNotEqual(self.head(), sha)
        self.assertEqual(self.candidato(ident), sha)
        (self.producto / 'algo.tmp').write_text('ignorado\n', encoding='utf-8')  # un archivo ignorado no es un cambio local
        self.assertEqual(self.candidato(ident), sha)
        # con dos commits con evidencia, el más cercano a HEAD
        nuevo = self.commit_producto()
        self.evidencia(ident, nuevo)
        self.assertEqual(self.candidato(ident), nuevo)

    def test_rc1_el_producto_cambio(self):
        self.conecta()
        ident = self.cambio()
        sha = self.head()
        self.evidencia(ident)
        app = self.producto / 'src/app.py'
        casos = {'modificado sin commit': lambda: app.write_text(APP + '# local\n', encoding='utf-8'),
                 'en el índice': lambda: ((self.producto / 'nuevo.py').write_text('x = 1\n', encoding='utf-8'),
                                          self.git_en(self.producto, 'add', 'nuevo.py')),
                 'nuevo no ignorado': lambda: (self.producto / 'suelto.txt').write_text('x\n', encoding='utf-8'),
                 # con almacén, todo el producto es producto: también sus carpetas que se llaman como las de Factory
                 'en una carpeta tareas/ del producto': lambda: ((self.producto / 'tareas').mkdir(exist_ok=True),
                                                                 (self.producto / 'tareas/lista.md').write_text('x\n', encoding='utf-8'))}
        for nombre, ensuciar in casos.items():
            with self.subTest(caso=nombre):
                ensuciar()
                self.assertIsNone(self.candidato(ident))
                self.git_en(self.producto, 'reset', '-q', '--hard')
                self.git_en(self.producto, 'clean', '-q', '-fd')
                self.assertEqual(self.candidato(ident), sha)
        self.commit_producto()  # un commit que cambia un archivo
        self.assertIsNone(self.candidato(ident))
        # evidencia de un commit que no es ancestro de HEAD (otra rama) tampoco cuenta
        self.git_en(self.producto, 'checkout', '-q', '-b', 'otra', sha)
        lejos = self.commit_producto(mensaje='en otra rama')
        self.git_en(self.producto, 'checkout', '-q', 'main')
        self.git_en(self.producto, 'reset', '-q', '--hard', sha)
        self.evidencia(ident, lejos)
        self.assertEqual(self.candidato(ident), sha)
        self.git_en(self.producto, 'commit', '-q', '--allow-empty', '-m', 'vacío')
        (self.registros / '.factory/cambios' / ident / 'candidatos' / sha / 'evidencia' / 'hechos.json').unlink()
        (self.registros / '.factory/cambios' / ident / 'candidatos' / sha / 'evidencia' / 'trazabilidad.json').unlink()
        (self.registros / '.factory/cambios' / ident / 'candidatos' / sha / 'evidencia').rmdir()
        (self.registros / '.factory/cambios' / ident / 'candidatos' / sha).rmdir()
        self.assertIsNone(self.candidato(ident))

    def test_rc1_sin_almacen_el_candidato_es_el_de_siempre(self):
        self.sin_almacen()
        ident = self.cambio()
        self.git_en(self.producto, 'add', '-A')
        self.git_en(self.producto, 'commit', '-q', '-m', 'registros')
        sha = self.head()
        self.evidencia(ident)
        self.assertEqual(self.candidato(ident), sha)
        self.git_en(self.producto, 'add', '-A')
        self.git_en(self.producto, 'commit', '-q', '-m', 'guarda la evidencia')  # sólo .factory/: el producto es el mismo
        self.assertEqual(self.candidato(ident), sha)
        (self.producto / 'tareas/lista.md').write_text('x\n', encoding='utf-8')  # sin almacén, tareas/ es de Factory
        self.assertEqual(self.candidato(ident), sha)

    # --- rc2: con almacén aparte la huella es el producto y este cambio ----------------------------------------------
    def dos_cambios_con_revision(self):
        """A con revisión y juicio vigentes, B al lado en el mismo almacén; cada uno con su medida."""
        self.conecta()
        a, b = self.cambio('ra', 'notas'), self.cambio('rb', 'otras')
        self.medir(a, 'rc.a')
        self.medir(b, 'rc.b')
        self.registrar_revision(a)
        self.evidencia(a)
        self.ok('juzgar', a, agente='claude-code')
        self.assertEqual(self.vigentes(a), (True, True))
        return a, b

    def test_rc2_otro_cambio_del_almacen(self):
        a, b = self.dos_cambios_con_revision()
        estado_b = self.registro(b)
        for nombre, ruta in (('la spec de B', self.almacen / estado_b['spec']),
                             ('la propuesta de B', self.almacen / 'openspec/changes' / b / 'proposal.md'),
                             ('el requisito de B', self.archivo_requisito(b)),
                             ('el catálogo de la medida de B', self.catalogo('rc.b'))):
            with self.subTest(edita=nombre):
                ruta.write_text(ruta.read_text(encoding='utf-8') + '\n# editado\n', encoding='utf-8')
                self.assertEqual(self.vigentes(a), (True, True))
        self.ok('mensaje', b, 'un mensaje en B', agente='claude-code')
        self.ok('mensaje', a, 'un mensaje en A', agente='claude-code')  # lo que Factory genera en el registro de A tampoco cuenta
        (self.almacen / 'tareas' / a / 'notas.md').write_text('una nota\n', encoding='utf-8')
        self.assertEqual(self.vigentes(a), (True, True))

    def test_rc2_la_spec_o_el_producto_de_este_cambio(self):
        a, _ = self.dos_cambios_con_revision()
        estado_a = self.registro(a)
        for nombre, ruta in (('su spec', self.almacen / estado_a['spec']),
                             ('su propuesta', self.almacen / 'openspec/changes' / a / 'proposal.md'),
                             ('su requisito', self.archivo_requisito(a)),
                             ('el catálogo de su medida', self.catalogo('rc.a')),
                             ('un archivo del producto', self.producto / 'src/app.py'),
                             ('un archivo nuevo del producto', self.producto / 'nuevo.py'),
                             ('una carpeta tareas/ del producto', self.producto / 'tareas/lista.md')):
            with self.subTest(edita=nombre):
                original = ruta.read_bytes() if ruta.exists() else None
                ruta.parent.mkdir(parents=True, exist_ok=True)
                ruta.write_bytes((original or b'') + b'\n# editado\n')
                self.assertEqual(self.vigentes(a), (False, False))
                paso = self.estado(a)['proximo_paso'] or ''  # el próximo paso usa la misma huella: no ofrece juzgar ni cerrar
                self.assertFalse(paso.startswith('oracle-factory cerrar') or 'juzgar' in paso, paso)
                if original is None:
                    ruta.unlink()
                else:
                    ruta.write_bytes(original)
                self.assertEqual(self.vigentes(a), (True, True))  # la vigencia es por contenido
                self.assertTrue((self.estado(a)['proximo_paso'] or '').startswith('oracle-factory cerrar'), self.estado(a)['proximo_paso'])

    def test_rc2_sin_almacen_la_huella_es_la_de_siempre(self):
        self.sin_almacen()
        a, b = self.cambio('ra', 'notas'), self.cambio('rb', 'otras')
        self.registrar_revision(a)
        self.assertEqual(self.vigentes(a)[0], True)
        spec_b = self.producto / self.registro(b)['spec']
        spec_b.write_text(spec_b.read_text(encoding='utf-8') + '\n# editado\n', encoding='utf-8')
        self.assertEqual(self.vigentes(a)[0], False)  # sin almacén, la spec de otro cambio es parte del producto

    # --- rc3: con almacén aparte el ciclo completo funciona sin tocar el producto -------------------------------------
    def test_rc3_de_punta_a_punta(self):
        self.conecta()
        ident, base, sha = self.preparar_ciclo()
        antes = self.producto_entero()
        self.ciclo(ident, base)
        self.assertEqual(self.registro(ident)['fase'], 'cerrada')
        self.assertEqual(self.producto_entero(), antes)
        candidato = self.almacen / '.factory/cambios' / ident / 'candidatos' / sha
        self.assertTrue((candidato / 'revision/prueba-1.json').is_file())
        self.assertTrue((candidato / 'clue/paquete-prueba-1.json').is_file())
        paquete = json.loads((candidato / 'clue/paquete-prueba-1.json').read_text(encoding='utf-8'))
        self.assertEqual((paquete['base'], paquete['head']), (base, self.git_en(self.producto, 'rev-parse', sha)))
        self.assertEqual(sorted(a['file'] for a in paquete['files']), ['src/app.py', 'tests/test_app.py'])  # el diff es el del producto
        self.assertFalse((self.producto / '.factory').exists())

    def test_rc3_sin_almacen_el_mismo_ciclo_funciona_como_siempre(self):
        self.sin_almacen()
        ident, base, _ = self.preparar_ciclo()
        self.ciclo(ident, base)
        self.assertEqual(self.registro(ident)['fase'], 'cerrada')

    def test_rc3_lo_que_mira_el_producto(self):
        self.conecta()
        ident, base, sha = self.preparar_ciclo()
        completo = self.git_en(self.producto, 'rev-parse', sha)
        antes = self.producto_entero()
        # la base del candidato (merge-base con main) y su diff son los del producto
        traza = json.loads(self.ok('trazabilidad', ident, '--json'))
        self.assertEqual((traza['candidato'], traza['base']), (sha, base))
        self.assertIn('src/app.py', traza['sin_respaldo'])
        self.assertEqual(sorted(traza['sin_respaldo']), ['src/app.py'])  # la prueba sólo pierde una línea: no tiene líneas agregadas que cubrir
        # las alarmas: la prueba existente a la que el candidato le quitó una aserción
        texto = self.ok('estado', ident)
        self.assertIn('test existente editado: tests/test_app.py', texto)
        # por-que, log y ruta
        por_que = json.loads(self.ok('por-que', f'{self.producto / "src/app.py"}:2', '--json'))
        self.assertEqual(por_que['commit']['sha'], completo)
        self.assertEqual(por_que['cambio']['id'], ident)
        log = json.loads(self.ok('log', ident, '--json'))
        self.assertIn(completo, [c['sha'] for c in log['commits']])
        self.assertEqual(self.ok('ruta', ident, 'evidencia').strip(),
                         str(self.almacen / '.factory/cambios' / ident / 'candidatos' / sha / 'evidencia'))
        # procedencia guarda el inventario en el candidato del producto, en el almacén
        self.ok('procedencia', ident, '--python', sys.executable)
        self.assertTrue((self.almacen / '.factory/cambios' / ident / 'candidatos' / sha / 'procedencia/cyclonedx.json').is_file())
        self.assertEqual(self.producto_entero(), antes)
        self.assertFalse((self.producto / '.factory').exists())
        # una revisión con la base vacía (todo el producto) no escribe objetos en el .git del producto: la base se crea en el clon
        self.ok('pedir-revision', ident, '--a', 'prueba', '--base', 'vacio', agente='claude-code')
        self.assertEqual(self.producto_entero(), antes)
        paquete = json.loads((self.almacen / '.factory/cambios' / ident / 'candidatos' / sha / 'clue/paquete-prueba-1.json').read_text(encoding='utf-8'))
        self.assertNotEqual(paquete['base'], base)
        self.assertIn('README.md', [a['file'] for a in paquete['files']])  # con la base vacía entra todo el producto
        # una segunda vuelta sobre otro candidato nombra la anterior: los candidatos anteriores salen de la historia del producto
        sha2 = self.commit_producto(texto='def saludo():\n    return "hola, otra vez"\n')
        self.evidencia(ident, sha2)
        self.ok('pedir-revision', ident, '--a', 'prueba', '--base', base, agente='claude-code')
        pedido = (self.almacen / '.factory/cambios' / ident / 'candidatos' / sha2 / 'revision/prueba-1.pedido.md').read_text(encoding='utf-8')
        self.assertIn(sha, pedido)

    # --- rc4: con almacén aparte no hay hook en el producto -------------------------------------------------------------
    def test_rc4_hooks_con_almacen_aparte(self):
        self.conecta()
        antes = (self.producto_entero(), self.arbol(self.almacen), self.arbol(self.casa))
        codigo, salida, error = self.corre('hooks')
        self.assertNotEqual(codigo, 0)
        self.assertIn('candidatos', salida + error)
        self.assertNotIn('Traceback', error)
        self.assertEqual((self.producto_entero(), self.arbol(self.almacen), self.arbol(self.casa)), antes)
        # con --registros explícito, igual
        self.ok('desconectar')
        antes = (self.producto_entero(), self.arbol(self.almacen))
        codigo, salida, error = self.corre('--registros', str(self.almacen), 'hooks')
        self.assertNotEqual(codigo, 0)
        self.assertIn('candidatos', salida + error)
        self.assertEqual((self.producto_entero(), self.arbol(self.almacen)), antes)

    def test_rc4_log_sin_trailer(self):
        self.conecta()
        ident = self.cambio()
        sha = self.commit_producto(mensaje='un commit sin trailer')
        self.assertNotIn('Cambio:', self.git_en(self.producto, 'log', '-1', '--format=%B'))
        self.evidencia(ident, sha)
        log = json.loads(self.ok('log', ident, '--json'))
        [commit] = [c for c in log['commits'] if c['corto'] == sha]
        self.assertEqual((commit['union'], commit['candidato'], commit['evidencia']), ('deducido', True, True))
        self.assertIn(sha, self.ok('log', ident))


if __name__ == '__main__':
    unittest.main()
