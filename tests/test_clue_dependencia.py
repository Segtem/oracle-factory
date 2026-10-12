"""Oracle Clue como dependencia fija: escenarios k1–k3 de la spec (clue viene con Factory, siempre se valida, REMOVED no se importa)."""
import contextlib
import io
import json
import os
from pathlib import Path
import sys
import tomllib
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import test_autoproduccion as _ap  # noqa: E402
import test_archivo as _archivo  # noqa: E402
import test_revisores as _revisores  # noqa: E402

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
    preparar, configurar, pedir = _revisores.Revisores.preparar, _revisores.Revisores.configurar, _revisores.Revisores.pedir

    # --- k1: oracle-clue viene con Factory -----------------------------------------------------------------------------------
    def test_k1_clue_es_dependencia_y_se_usa_el_del_entorno(self):
        dependencias = tomllib.loads((RAIZ / 'pyproject.toml').read_text())['project']['dependencies']
        self.assertTrue(any(d.startswith('oracle-clue==') for d in dependencias), dependencias)
        with patch.dict(os.environ, {'PATH': ''}):  # sin nada en el PATH: sólo funciona si usa el Clue del entorno
            p = f.ejecutar(['oracle-clue', '--help'])
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertIn('preparar', p.stdout)
        real = f.metadata.distribution
        falta = lambda nombre: (_ for _ in ()).throw(f.metadata.PackageNotFoundError(nombre)) if nombre == 'oracle-clue' else real(nombre)  # noqa: E731
        with patch.object(f.metadata, 'distribution', side_effect=falta), self.assertRaisesRegex(f.FactoryError, 'falta oracle-clue'):
            f.ejecutar(['oracle-clue', '--help'])  # sin la distribución no cae a un oracle-clue del PATH

    def test_k1_pedir_revision_sin_clue_en_el_path(self):
        self.preparar('hallazgo')
        sin_clue = os.pathsep.join(d for d in os.environ.get('PATH', '').split(os.pathsep) if not (Path(d) / 'oracle-clue').exists())
        with patch.dict(os.environ, {'PATH': sin_clue}):
            destino = self.pedir()  # prepara el paquete y valida el informe con el Clue del entorno
        self.assertEqual(len(json.loads(destino.read_text())['findings']), 1)

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

    def candidato_con(self, *informes):
        """Un candidato con evidencia, un paquete y los informes dados ({nombre: (estado, hallazgos)})."""
        ident = self.cambio_medido()
        sha = self.head()
        carpeta = self.carpeta(ident)
        self.producir_evidencia(ident)
        (carpeta / 'revision').mkdir(parents=True)
        for nombre, estado_rev, hallazgos in informes:
            (carpeta / 'revision' / nombre).write_text(json.dumps(_ap.informe_clue(sha, hallazgos, estado=estado_rev)))
        (carpeta / 'clue').mkdir()
        (carpeta / 'clue' / 'paquete.json').write_text(json.dumps({
            'schema_version': 'oracle-clue.bundle/v1', 'repo': str(self.root), 'diff_sha256': 'd' * 64, 'context_sha256': 'c' * 64,
            'files': [{'file': 'examples/notas/notas.py'}]}))
        self.git('add', '.')
        self.git('commit', '-qm', 'evidencia e informes')
        return ident

    # --- k4: el informe más nuevo de cada revisor reemplaza a los anteriores ---------------------------------------------------
    def test_k4_incompleta_seguida_de_completa(self):
        ident = self.candidato_con(('codex-1.json', 'incompleto', ['R-01']), ('codex-2.json', 'completo', []))
        with _ap.clue_acepta(), contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            ruta, _ = f.preparar_revision(ident)
        informe = json.loads(ruta.read_text())
        self.assertEqual(informe['hallazgos'], [])  # los de codex-1 no se deciden otra vez
        revisiones = [c for c in informe['comprobaciones'] if c['descripcion'].startswith('Revisión de ')]
        self.assertEqual([(c['resultado'], c['evidencia'].rsplit('/', 1)[-1].split(' ')[0]) for c in revisiones], [('cumple', 'codex-2.json')])
        anteriores = [c for c in informe['comprobaciones'] if c['descripcion'].startswith('Vuelta anterior')]
        self.assertEqual([c['evidencia'].rsplit('/', 1)[-1].split(' ')[0] for c in anteriores], ['codex-1.json'])

    def test_k4_el_mas_nuevo_invalido_no_revive_el_anterior(self):
        ident = self.candidato_con(('codex-1.json', 'completo', ['R-01']))
        otro = _ap.informe_clue('f' * 40, [])  # de otro candidato: no se puede usar
        (self.carpeta(ident, self.git('rev-parse', 'HEAD~1')[:7]) / 'revision' / 'codex-2.json').write_text(json.dumps(otro))
        errores = io.StringIO()
        with _ap.clue_acepta(), contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(errores):
            ruta, _ = f.preparar_revision(ident)
        informe = json.loads(ruta.read_text())
        self.assertEqual(informe['hallazgos'], [])  # codex-1 no vuelve: lo reemplazó codex-2, que no se usa
        self.assertFalse([c for c in informe['comprobaciones'] if c['descripcion'].startswith('Revisión de ')])
        self.assertIn('codex-2.json es de otro candidato', errores.getvalue())

    # --- k5: el menú de la decisión no corre sus números -------------------------------------------------------------------------
    def test_k5_aprobar_no_disponible(self):
        ident = self.candidato_con(('codex-1.json', 'incompleto', []))
        antes = f.ruta_registro(f.leer(ident)[0]).read_bytes()
        salida = io.StringIO()
        with _ap.clue_acepta(), patch('builtins.input', side_effect=['1', '1']), contextlib.redirect_stdout(salida), \
                contextlib.redirect_stderr(io.StringIO()), self.assertRaisesRegex(f.FactoryError, 'no se puede aprobar'):
            f.revisar_paso_a_paso(ident)  # completa; «1» sigue siendo Aprobar, y no está disponible
        self.assertIn('1) Aprobar — NO DISPONIBLE', salida.getvalue())
        self.assertIn('2) Pedir cambios', salida.getvalue())
        self.assertEqual(f.ruta_registro(f.leer(ident)[0]).read_bytes(), antes)

    # --- k3: importar no trae lo que la spec retira ---------------------------------------------------------------------------
    def test_k3_retirados_sin_tipo_con_tipos_obligatorios(self):
        config = self.root / '.factory/config.json'
        config.write_text(json.dumps({**json.loads(config.read_text()), 'tipos_obligatorios': True}))
        with contextlib.redirect_stdout(io.StringIO()):
            ident = self.cambio_importado('Notas', 'notas', SPEC)  # el retirado no declara tipo y no hace falta
        self.assertEqual([r.split('.', 1)[1] for r in f.leer(ident)[1]['requisitos']], ['una_nota_nueva'])

    def test_k3_spec_que_retira_un_requisito(self):
        with contextlib.redirect_stdout(io.StringIO()):
            ident = self.cambio_importado('Notas', 'notas', SPEC)
        requisitos = f.leer(ident)[1]['requisitos']
        self.assertEqual([r.split('.', 1)[1] for r in requisitos], ['una_nota_nueva'])
        self.assertFalse(list((self.root / 'requisitos').glob('*.una_nota_vieja.requisito')))


if __name__ == '__main__':
    unittest.main()
