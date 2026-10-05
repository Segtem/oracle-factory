"""No aceptar evidencia incompleta o alterada como demostración de colaboración."""
import tempfile
from pathlib import Path
import unittest

from tools.verify_collaboration import CASES, GUIDE_MARKERS, digest, missing_guide_markers, render_template, validate_artifacts, validate_results


class EvidenciaColaboracion(unittest.TestCase):
    def test_guia_sin_seccion_exigida_falla_su_caso(self):
        for case, markers in GUIDE_MARKERS.items():
            self.assertEqual(missing_guide_markers(case), [], case)
            with self.subTest(case=case):
                self.assertEqual(missing_guide_markers(case, 'guía vacía'), list(markers))

    def test_verdes_duplicados_no_reemplazan_un_caso_omitido(self):
        rows = [{'caso': case, 'codigo': 0} for case in CASES]
        validate_results(rows)
        rows[-1] = dict(rows[0])
        with self.assertRaises(ValueError):
            validate_results(rows)

    def test_falla_o_caso_desconocido_no_se_convierte_en_exito(self):
        for last in ({'caso': 'C9', 'codigo': 1}, {'caso': 'C9', 'codigo': None},
                     {'caso': 'C9', 'codigo': False}, {'caso': 'otro', 'codigo': 0}):
            rows = [{'caso': case, 'codigo': 0} for case in CASES if case != 'C9'] + [last]
            with self.subTest(last=last), self.assertRaises(ValueError):
                validate_results(rows)

    def test_artefacto_omitido_o_alterado_invalida_su_evidencia(self):
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp)
            path = output / 'informe.json'
            path.write_text('original')
            hashes = {'informe.json': digest(path)}
            validate_artifacts(output, hashes)
            path.write_text('alterado')
            with self.assertRaises(ValueError):
                validate_artifacts(output, hashes)
            path.unlink()
            with self.assertRaises(ValueError):
                validate_artifacts(output, hashes)
            with self.assertRaises(ValueError):
                validate_artifacts(output, {})

    def test_archivo_externo_no_se_presenta_como_adjunto_preservado(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            output = root / 'salida'
            output.mkdir()
            external = root / 'externo'
            external.write_text('fuera')
            with self.assertRaises(ValueError):
                validate_artifacts(output, {'../externo': digest(external)})

    def test_relevo_incompleto_no_se_presenta_como_plantilla_completada(self):
        with self.assertRaises(ValueError):
            render_template('relevo.md', {'tarea': 'un-id'})


if __name__ == '__main__':
    unittest.main()
