"""Verificar con almacén (ci1–ci4): la suite pasa en un clon limpio, el CI del producto corre la suite, el almacén se verifica
en su propio CI y el MCP sirve sobre el producto."""
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import test_ci_activar as _ci  # noqa: E402
import test_marca_almacen as _marca  # noqa: E402

f = _marca._pm._commits.f
SOURCE = Path(__file__).resolve().parents[1]
WORKFLOW_ALMACEN = SOURCE / 'docs/plantillas/verificar-almacen.yml'
LAS_CUATRO = ['test_portabilidad.Portabilidad.test_p6_los_requisitos_de_este_repositorio_no_llevan_rutas_privadas',
              'test_verificador_generico.Catalogos.test_vg3_los_catalogos_escritos_tienen_la_misma_forma_que_los_que_ya_usa_factory',
              'test_puerta_verificar.PuertaVerificar.test_pv1_el_verificar_de_verdad_acepta_el_argumento_que_le_pasa_la_puerta',
              'test_kb.Conocimiento.test_kb1_un_proyecto_con_un_cambio_cerrado_y_otro_abierto']


def entorno_vacio(casa: Path) -> dict:
    """Sin la configuración de quien corre la suite: HOME, XDG y Git en una carpeta temporal, sin identidad ni conexión."""
    (casa / 'gitconfig').write_text('', encoding='utf-8')
    limpio = {k: v for k, v in os.environ.items() if not k.startswith(('GIT_', 'XDG_')) and k not in ('EMAIL', 'FACTORY_AGENTE')}
    return {**limpio, 'HOME': str(casa), 'XDG_CONFIG_HOME': str(casa / '.config'), 'XDG_DATA_HOME': str(casa / '.local/share'),
            'GIT_CONFIG_GLOBAL': str(casa / 'gitconfig'), 'GIT_CONFIG_SYSTEM': str(casa / 'gitconfig')}


# --- ci1: la suite pasa en un clon limpio ---------------------------------------------------------------------------------
class ClonLimpio(unittest.TestCase):
    def test_ci1_las_pruebas_que_dependian_de_la_maquina_pasan_en_una_copia_limpia(self):
        with tempfile.TemporaryDirectory() as tmp:
            copia, casa = Path(tmp) / 'copia', Path(tmp) / 'casa'
            casa.mkdir()
            archivos = subprocess.run(['git', 'ls-files', '-z', '--cached', '--others', '--exclude-standard'], cwd=SOURCE,
                                      capture_output=True, check=True).stdout.decode().split('\0')
            for nombre in filter(None, archivos):
                if (SOURCE / nombre).is_file():
                    (copia / nombre).parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(SOURCE / nombre, copia / nombre, follow_symlinks=False)
            entorno = entorno_vacio(casa)
            git = ['git', '-c', 'user.name=Copia', '-c', 'user.email=copia@example.invalid']
            for orden in (['init', '-q', '-b', 'main'], ['add', '-A'], ['commit', '-q', '-m', 'copia']):
                subprocess.run([*git, *orden], cwd=copia, env=entorno, check=True, capture_output=True)
            self.assertTrue((copia / '.oracle-factory-almacen').is_file())  # marcada y sin conexión, como un clon en el CI
            r = subprocess.run([sys.executable, '-m', 'unittest', *LAS_CUATRO], cwd=copia / 'tests', env=entorno,
                               capture_output=True, text=True, stdin=subprocess.DEVNULL, timeout=600)
            self.assertEqual(r.returncode, 0, r.stderr[-3000:])
            self.assertIn('Ran 4 tests', r.stderr)

    def test_ci1_con_los_registros_a_mano_p6_y_vg3_no_se_omiten(self):
        if f.almacenes.registros_de(SOURCE) == SOURCE:
            self.skipTest('este checkout no está conectado a su almacén: no hay registros a mano para leer')
        r = subprocess.run([sys.executable, '-m', 'unittest', '-v', *LAS_CUATRO[:2]], cwd=SOURCE / 'tests', capture_output=True,
                           text=True, stdin=subprocess.DEVNULL, timeout=600)
        self.assertEqual(r.returncode, 0, r.stderr[-3000:])
        self.assertNotIn('skipped', r.stderr)


# --- ci2: el CI del producto corre la suite -------------------------------------------------------------------------------
class WorkflowDelProducto(unittest.TestCase):
    def texto(self):
        return _ci.WORKFLOW.read_text(encoding='utf-8')

    def test_ci2_hay_un_trabajo_que_corre_la_suite_con_el_checkout(self):
        texto = self.texto()
        self.assertIn('python -m unittest discover -s tests', texto)
        self.assertIn('uv pip install -p .venv -e .', texto)

    def test_ci2_un_producto_marcado_avisa_que_los_registros_se_verifican_en_el_almacen(self):
        paso = _ci.paso_de_verificacion(self.texto())
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / '.oracle-factory-almacen').write_text('git@example.invalid:equipo/registros.git\n', encoding='utf-8')
            r = _ci.correr_paso(paso, 1, 'refs/heads/main', carpeta=Path(tmp))
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn('::notice', r.stdout)
        self.assertIn('git@example.invalid:equipo/registros.git', r.stdout)
        self.assertNotIn('Miré', r.stdout)  # no corre verificar: sin el almacén no hay nada que mirar

    def test_ci2_sin_marca_falla_en_main_y_avisa_en_otra_rama(self):
        paso = _ci.paso_de_verificacion(self.texto())
        self.assertEqual(_ci.correr_paso(paso, 1, 'refs/heads/main').returncode, 1)
        r = _ci.correr_paso(paso, 1, 'refs/heads/tarea/x')
        self.assertEqual(r.returncode, 0)
        self.assertIn('::warning', r.stdout)


# --- ci3: el almacén se verifica en su CI ---------------------------------------------------------------------------------
class WorkflowDelAlmacen(_marca.ConOrigen):
    def texto(self):
        return WORKFLOW_ALMACEN.read_text(encoding='utf-8')

    def test_ci3_la_plantilla_clona_los_dos_y_verifica_con_registros(self):
        texto = self.texto()
        self.assertRegex(texto, r'(?m)^on:\n  push:\n  pull_request:')
        self.assertIn('contents: read', texto)
        for prohibido in ('secrets.', 'contents: write', 'id-token'):
            self.assertNotIn(prohibido, texto)
        self.assertIn('path: almacen', texto)
        self.assertIn('path: producto', texto)
        self.assertIn('fetch-depth: 0', texto)
        self.assertIn('uv tool install ./producto', texto)
        paso = _ci.paso_de_verificacion(texto)
        self.assertIn('--proyecto producto --registros almacen verificar', paso)
        self.assertEqual(_ci.correr_paso(paso, 1, 'refs/heads/main').returncode, 1)
        r = _ci.correr_paso(paso, 1, 'refs/heads/otra')
        self.assertEqual(r.returncode, 0)
        self.assertIn('::warning', r.stdout)
        self.assertEqual(_ci.correr_paso(paso, 0, 'refs/heads/main').returncode, 0)

    def test_ci3_verificar_con_registros_sobre_un_clon_marcado_sin_conexion(self):
        self.marcado_y_commiteado()
        self.bien('--agente', 'claude-code', 'nuevo', '--capacidad', 'notas', '--sufijo', 'ci', 'Un cambio')
        clon = self.base / 'clon'
        self.git_en(self.base, 'clone', '-q', str(self.producto), str(clon))
        antes = self.todo(clon)
        salida = self.bien('--registros', str(self.almacen), 'verificar', raiz=clon)
        self.assertIn('Miré 1 cambio', salida)
        self.assertEqual(self.todo(clon), antes)


# --- ci4: el MCP sirve sobre el producto ----------------------------------------------------------------------------------
class McpConAlmacen(_marca.ConOrigen):
    CONSULTAS = ('listar', 'estado', 'log', 'resumen', 'buscar', 'por_que')

    def setUp(self):
        super().setUp()
        self.bien('conectar', str(self.almacen))
        self.bien('--agente', 'claude-code', 'nuevo', '--capacidad', 'notas', '--sufijo', 'mc', 'Un cambio')
        self.ident = next(p.name for p in (self.almacen / 'openspec/changes').iterdir() if p.name.endswith('-mc'))

    def pedir(self, *llamadas, raices=None):
        lineas = [json.dumps({'jsonrpc': '2.0', 'id': i, 'method': 'tools/call', 'params': {'name': n, 'arguments': a}})
                  for i, (n, a) in enumerate(llamadas, 1)]
        salida = io.StringIO()
        with patch('sys.stdin', io.StringIO('\n'.join(lineas) + '\n')), patch('sys.stdout', salida):
            self.assertEqual(f.main([*(raices or ['--proyecto', str(self.producto)]), 'mcp']), 0)
        return [json.loads(l)['result'] for l in salida.getvalue().splitlines() if l.strip()]

    def test_ci4_por_que_de_un_archivo_del_producto(self):
        [resultado] = self.pedir(('por_que', {'archivo': 'README.md', 'linea': 1}))
        self.assertFalse(resultado['isError'], resultado)
        self.assertIn('README.md', resultado['content'][0]['text'])

    def test_ci4_con_registros_explicito_las_herramientas_reciben_las_dos_raices(self):  # hallazgo bajo de codex
        self.bien('desconectar')  # sin conexión: sólo --registros dice dónde están los registros
        resultados = self.pedir(('estado', {'id': self.ident}), ('por_que', {'archivo': 'README.md', 'linea': 1}),
                                raices=['--proyecto', str(self.producto), '--registros', str(self.almacen)])
        for resultado in resultados:
            self.assertFalse(resultado['isError'], resultado)
        self.assertIn(self.ident, resultados[0]['content'][0]['text'])
        self.assertIn('README.md', resultados[1]['content'][0]['text'])

    def test_ci4_las_herramientas_de_consulta_contestan_sin_error(self):
        argumentos = {'listar': {}, 'estado': {'id': self.ident}, 'log': {'id': self.ident}, 'resumen': {},
                      'buscar': {'texto': 'cambio'}, 'por_que': {'archivo': 'README.md', 'linea': 1}}
        resultados = self.pedir(*[(n, argumentos[n]) for n in self.CONSULTAS])
        for nombre, resultado in zip(self.CONSULTAS, resultados):
            self.assertFalse(resultado['isError'], (nombre, resultado))


_marca.sin_heredados(WorkflowDelAlmacen, _marca._pm.Conectado)
_marca.sin_heredados(McpConAlmacen, _marca._pm.Conectado)


if __name__ == '__main__':
    unittest.main()
