"""La versión identifica el código (vh1), las notas dicen lo sin publicar (vh2), el CI deja Node 20 (vh3) y el pedido de revisión
avisa lo que escribe Factory (vh4)."""
import contextlib
import io
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from oracle_factory import __version__, parser as parser_mod, revisores, version as version_mod  # noqa: E402

SOURCE = Path(__file__).resolve().parents[1]
GIT = ['git', '-c', 'user.name=Prueba', '-c', 'user.email=prueba@example.invalid', '-c', 'core.hooksPath=/dev/null']


class Version(unittest.TestCase):
    def checkout(self, tmp, commits_despues_del_tag):
        raiz = Path(tmp) / 'factory'
        raiz.mkdir()
        entorno = {k: v for k, v in os.environ.items() if not k.startswith('GIT_')}
        (raiz / 'pyproject.toml').write_text('[project]\nname = "oracle-factory"\n', encoding='utf-8')
        for orden in (['init', '-q', '-b', 'main'], ['add', '-A'], ['commit', '-q', '-m', 'versión'], ['tag', f'v{__version__}']):
            subprocess.run([*GIT, *orden], cwd=raiz, check=True, capture_output=True, env=entorno)
        for i in range(commits_despues_del_tag):
            subprocess.run([*GIT, 'commit', '-q', '--allow-empty', '-m', f'después {i}'], cwd=raiz, check=True, capture_output=True,
                           env=entorno)
        cabeza = subprocess.run(['git', 'rev-parse', 'HEAD'], cwd=raiz, check=True, capture_output=True, text=True,
                                env=entorno).stdout.strip()
        return raiz, cabeza

    # --- vh1: la versión identifica el código --------------------------------------------------------------------------
    def test_vh1_un_checkout_que_no_es_una_version_publicada(self):
        with tempfile.TemporaryDirectory() as tmp:
            raiz, cabeza = self.checkout(tmp, 2)
            self.assertEqual(version_mod.version_completa(raiz), f'{__version__}+{cabeza[:7]} (checkout, sin publicar)')

    def test_vh1_el_commit_del_tag_dice_solo_la_version(self):
        with tempfile.TemporaryDirectory() as tmp:
            raiz, _ = self.checkout(tmp, 0)
            self.assertEqual(version_mod.version_completa(raiz), __version__)

    def test_vh1_un_paquete_instalado_dice_solo_la_version(self):
        with tempfile.TemporaryDirectory() as tmp:  # sin .git: como site-packages
            self.assertEqual(version_mod.version_completa(Path(tmp)), __version__)
        with tempfile.TemporaryDirectory() as tmp:  # el paquete en un .venv adentro de OTRO proyecto con Git: no es su commit
            otro, _ = self.checkout(tmp, 1)
            paquete = otro / '.venv/lib/python3/site-packages'
            paquete.mkdir(parents=True)
            self.assertEqual(version_mod.version_completa(paquete), __version__)
        with patch.object(version_mod.subprocess, 'run', side_effect=OSError('sin git')):  # sin git a mano, tampoco falla
            self.assertEqual(version_mod.version_completa(SOURCE), __version__)

    def test_vh1_version_de_la_cli_y_ningun_otro_comando_corre_git_por_ella(self):
        salida = io.StringIO()
        with contextlib.redirect_stdout(salida), self.assertRaises(SystemExit):
            parser_mod.construir_parser().parse_args(['--version'])
        self.assertTrue(salida.getvalue().startswith(f'oracle-factory {__version__}'), salida.getvalue())
        with patch.object(version_mod, 'version_completa', side_effect=AssertionError('no se pidió --version')):
            args = parser_mod.construir_parser().parse_args(['listar'])
        self.assertEqual(args.comando, 'listar')


# --- vh2: las notas dicen lo sin publicar ---------------------------------------------------------------------------------
class Notas(unittest.TestCase):
    def test_vh2_la_primera_seccion_es_sin_publicar_y_nombra_lo_nuevo(self):
        texto = (SOURCE / 'NOTAS-DE-RELEASE.md').read_text(encoding='utf-8')
        titulos = re.findall(r'(?m)^# (.+)$', texto)
        self.assertEqual(titulos[0], 'Sin publicar')
        self.assertTrue(titulos[1].startswith('Oracle Factory '), titulos[:2])
        seccion = texto.split('\n# ', 2)[0]
        for novedad in ('conectar', 'sincronizar', 'migrar --almacen', '.oracle-factory-almacen', 'verificar-almacen.yml',
                        'pendientes_de_union', "'.[dev]'"):
            with self.subTest(novedad=novedad):
                self.assertIn(novedad, seccion)


# --- vh3: el CI deja Node 20 ----------------------------------------------------------------------------------------------
class AccionDeUv(unittest.TestCase):
    def test_vh3_setup_uv_esta_en_v7_o_posterior_en_los_workflows_y_las_plantillas(self):
        archivos = sorted([*(SOURCE / '.github/workflows').glob('*.y*ml'), *(SOURCE / 'docs/plantillas').glob('*.y*ml')])
        usos = []
        for archivo in archivos:
            for trabajo in (yaml.safe_load(archivo.read_text(encoding='utf-8')).get('jobs') or {}).values():
                usos += [(archivo.name, p['uses']) for p in trabajo.get('steps', []) if 'setup-uv' in str(p.get('uses', ''))]
        self.assertTrue(usos)
        viejos = [(n, u) for n, u in usos if int(re.search(r'@v(\d+)', u).group(1)) < 7]
        self.assertEqual(viejos, [])


# --- vh4: el pedido avisa lo que escribe Factory --------------------------------------------------------------------------
class Pedido(unittest.TestCase):
    def test_vh4_el_pedido_avisa_que_factory_escribe_los_eventos_de_la_revision(self):
        with tempfile.TemporaryDirectory() as tmp:
            texto = revisores.pedido(revisores.plantilla(Path(tmp)), {'id': 'ID'}, None)
        self.assertIn('revision_lanzada', texto)
        self.assertIn('revision_pedida', texto)
        self.assertIn('factory.json', texto)
        self.assertRegex(texto, r'no son (cambios )?de las pruebas')


if __name__ == '__main__':
    unittest.main()
