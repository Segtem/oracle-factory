"""El workflow `verificar` de este repositorio: escenarios ca1–ca3. El paso de verificación se ejecuta de verdad con un `oracle-factory` falso."""
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import textwrap
import unittest

SOURCE = Path(__file__).resolve().parents[1]
WORKFLOW = SOURCE / '.github/workflows/verificar.yml'
PLANTILLA = SOURCE / 'docs/plantillas/verificar.yml'


def paso_de_verificacion(texto: str) -> str:
    """El bloque `run: |` del paso cuyo nombre empieza con «Verificar»: el shell tal cual, sin la sangría del YAML."""
    m = re.search(r'^( *)- name: Verificar[^\n]*\n\1  run: \|\n((?:\1    [^\n]*\n|\n)+)', texto, re.MULTILINE)
    assert m, 'no hay un paso «Verificar…» con run: |'
    return textwrap.dedent(m.group(2))


def correr_paso(paso: str, salida_de_verificar: int, ref: str) -> subprocess.CompletedProcess:
    with tempfile.TemporaryDirectory() as tmp:
        falso = Path(tmp) / 'oracle-factory'
        falso.write_text(f'#!/bin/sh\necho "Miré 3 cambios: 1 con problemas."\nexit {salida_de_verificar}\n')
        falso.chmod(0o755)
        env = {**os.environ, 'PATH': f'{tmp}:{os.environ["PATH"]}', 'GITHUB_REF': ref}
        return subprocess.run(['bash', '-e', '-o', 'pipefail', '-c', paso], capture_output=True, text=True, env=env, timeout=30)


class Workflow(unittest.TestCase):
    # --- ca1: el repositorio corre verificar en su CI ---------------------------------------------------------------------
    def test_ca1_el_workflow_se_dispara_con_push_y_pull_request_y_corre_verificar(self):
        texto = WORKFLOW.read_text(encoding='utf-8')
        self.assertRegex(texto, r'(?m)^on:\n  push:\n  pull_request:')
        self.assertIn('oracle-factory verificar', texto)

    def test_ca1_solo_lee_y_no_usa_secretos(self):
        texto = WORKFLOW.read_text(encoding='utf-8')
        self.assertIn('contents: read', texto)
        for prohibido in ('secrets.', 'contents: write', 'pull-requests: write', 'id-token', 'pages:'):
            self.assertNotIn(prohibido, texto)

    def test_ca1_instala_factory_desde_el_checkout_y_no_desde_pypi(self):
        texto = WORKFLOW.read_text(encoding='utf-8')
        self.assertIn('uv tool install .', texto)
        self.assertNotIn('uv tool install oracle-factory', texto)
        self.assertIn('actions/checkout', texto)

    # --- ca2: falla en main y avisa en las demás ----------------------------------------------------------------------------
    def test_ca2_un_cambio_inconsistente_en_main_falla(self):
        r = correr_paso(paso_de_verificacion(WORKFLOW.read_text(encoding='utf-8')), 1, 'refs/heads/main')
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertNotIn('::warning', r.stdout)

    def test_ca2_en_otra_rama_o_en_un_pull_request_avisa_y_no_falla(self):
        paso = paso_de_verificacion(WORKFLOW.read_text(encoding='utf-8'))
        for ref in ('refs/heads/tarea/x', 'refs/pull/3/merge', 'refs/heads/mainstream', 'refs/tags/v1'):
            with self.subTest(ref=ref):
                r = correr_paso(paso, 1, ref)
                self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
                self.assertIn('::warning', r.stdout)

    def test_ca2_todo_consistente_no_falla_ni_avisa_en_ninguna_referencia(self):
        paso = paso_de_verificacion(WORKFLOW.read_text(encoding='utf-8'))
        for ref in ('refs/heads/main', 'refs/heads/tarea/x', 'refs/pull/3/merge'):
            with self.subTest(ref=ref):
                r = correr_paso(paso, 0, ref)
                self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
                self.assertNotIn('::warning', r.stdout)

    def test_ca2_el_aviso_trae_el_detalle_de_verificar(self):
        r = correr_paso(paso_de_verificacion(WORKFLOW.read_text(encoding='utf-8')), 1, 'refs/heads/tarea/x')
        self.assertIn('Miré 3 cambios: 1 con problemas.', r.stdout)  # la salida de verificar queda en el registro del job

    # --- ca3: la plantilla y la guía cuentan la política ----------------------------------------------------------------------
    def test_ca3_la_plantilla_aplica_la_misma_politica(self):
        paso = paso_de_verificacion(PLANTILLA.read_text(encoding='utf-8'))
        self.assertEqual(correr_paso(paso, 1, 'refs/heads/main').returncode, 1)
        r = correr_paso(paso, 1, 'refs/heads/otra')
        self.assertEqual(r.returncode, 0)
        self.assertIn('::warning', r.stdout)
        self.assertEqual(paso, paso_de_verificacion(WORKFLOW.read_text(encoding='utf-8')))  # el mismo paso: una sola política

    def test_ca3_la_guia_explica_la_politica_y_nombra_el_workflow_del_repositorio(self):
        guia = (SOURCE / 'docs/ci.md').read_text(encoding='utf-8')
        for marca in ('.github/workflows/verificar.yml', 'main', '::warning', 'avisa'):
            with self.subTest(marca=marca):
                self.assertIn(marca, guia)


if __name__ == '__main__':
    unittest.main()
