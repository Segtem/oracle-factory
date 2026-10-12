"""Oracle Clue como dependencia fija: escenarios k1–k3 de la spec (clue viene con Factory, siempre se valida, REMOVED no se importa)."""
import contextlib
import io
import json
from pathlib import Path
import sys
import tomllib
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import test_autoproduccion as _ap  # noqa: E402
import test_archivo as _archivo  # noqa: E402

f = _ap.f
RAIZ = Path(__file__).resolve().parents[1]
SPEC = '''# Capability: notas

## ADDED Requirements

### Requirement: una nota nueva
Tipo: funcional
El sistema SHALL guardar una nota nueva.

#### Scenario: guardar
- GIVEN una nota
- WHEN se guarda
- THEN queda guardada

## REMOVED Requirements

### Requirement: una nota vieja
'''


class ClueDependencia(_ap.Base):
    cambio_medido = _ap.Autoproduccion.cambio_medido
    carpeta = _ap.Autoproduccion.carpeta
    producir_evidencia = _ap.Autoproduccion.producir_evidencia
    head = _ap.Autoproduccion.head
    cambio_importado = _archivo.Archivo.cambio_importado

    # --- k1: oracle-clue viene con Factory -----------------------------------------------------------------------------------
    def test_k1_clue_es_dependencia_y_se_usa_el_del_entorno(self):
        dependencias = tomllib.loads((RAIZ / 'pyproject.toml').read_text())['project']['dependencies']
        self.assertTrue(any(d.startswith('oracle-clue==') for d in dependencias), dependencias)
        with patch.object(f.shutil, 'which', return_value=None):  # sin oracle-clue en el PATH
            p = f.ejecutar(['oracle-clue', '--help'])
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertIn('preparar', p.stdout)

    # --- k2: los informes de revisores siempre se validan ----------------------------------------------------------------------
    def test_k2_informe_sin_paquete_no_se_usa(self):
        ident = self.cambio_medido()
        carpeta = self.carpeta(ident)
        self.producir_evidencia(ident)
        (carpeta / 'revision').mkdir(parents=True)
        (carpeta / 'revision' / 'codex-1.json').write_text(json.dumps(_ap.informe_clue(self.head(), ['R-01'])))
        errores = io.StringIO()
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(errores):
            informe, _ = f.preparar_revision(ident)
        self.assertEqual(json.loads(informe.read_text())['hallazgos'], [])
        self.assertIn('no se puede validar', errores.getvalue())
        self.assertNotIn('sin validar', errores.getvalue())

    # --- k3: importar no trae lo que la spec retira ---------------------------------------------------------------------------
    def test_k3_spec_que_retira_un_requisito(self):
        with contextlib.redirect_stdout(io.StringIO()):
            ident = self.cambio_importado('Notas', 'notas', SPEC)
        requisitos = f.leer(ident)[1]['requisitos']
        self.assertEqual([r.split('.', 1)[1] for r in requisitos], ['una_nota_nueva'])
        self.assertFalse(list((self.root / 'requisitos').glob('*.una_nota_vieja.requisito')))


if __name__ == '__main__':
    unittest.main()
