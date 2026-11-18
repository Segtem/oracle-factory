"""Las leyes de quién decide también valen para el núcleo de Bend probado en Lean (vb1): `bend PROOF.bend --verdict`.

Sin `bend`, `lean` o `leanc` en el PATH, la prueba se omite y dice cuál falta.
"""
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_leyes_bend import ENTORNO, MODELO, MUTANTES, requiere  # noqa: E402

PLAZO = 600  # la primera vez compila el núcleo (unos 12 s); después lo reusa de ~/.bend/bendtt/


def herramientas(path: str | None = None) -> str:
    """La ruta de bend, después de comprobar que también están lean y leanc; SkipTest nombrando el que falta."""
    bend = requiere("bend", path)
    for programa in ("lean", "leanc"):
        requiere(programa, path)
    return bend


def veredicto(bend: str, carpeta: Path) -> str:
    r = subprocess.run([bend, "PROOF.bend", "--verdict"], cwd=carpeta, env=ENTORNO, capture_output=True, text=True, timeout=PLAZO)
    return r.stdout + r.stderr


class Verdict(unittest.TestCase):
    # --- vb1: las leyes valen para el núcleo probado ----------------------------------------------------------------------
    def test_vb1_el_nucleo_acepta_las_pruebas(self):
        salida = veredicto(herramientas(), MODELO)
        self.assertIn("ALL PROOFS CHECK", salida)
        self.assertNotIn("BendTT infrastructure", salida)

    def test_vb1_el_nucleo_rechaza_un_mutante(self):
        bend = herramientas()
        viejo, nuevo = MUTANTES["confirmación: un agente decide la revisión"]
        with tempfile.TemporaryDirectory() as tmp:
            copia = Path(tmp) / "q"
            shutil.copytree(MODELO, copia)
            modelo = copia / "quien.bend"
            texto = modelo.read_text(encoding="utf-8")
            self.assertEqual(texto.count(viejo), 1)
            modelo.write_text(texto.replace(viejo, nuevo), encoding="utf-8")
            self.assertNotIn("ALL PROOFS CHECK", veredicto(bend, copia))

    def test_vb1_sin_lean_o_sin_leanc_se_omite_nombrando_el_que_falta(self):
        with tempfile.TemporaryDirectory() as tmp:
            solo = Path(tmp)
            (solo / "bend").write_text("#!/bin/sh\n", encoding="utf-8")
            (solo / "bend").chmod(0o755)
            with self.assertRaises(unittest.SkipTest) as omitida:
                herramientas(str(solo))
            self.assertIn("falta lean ", str(omitida.exception))
            (solo / "lean").write_text("#!/bin/sh\n", encoding="utf-8")
            (solo / "lean").chmod(0o755)
            with self.assertRaises(unittest.SkipTest) as omitida:
                herramientas(str(solo))
            self.assertIn("falta leanc ", str(omitida.exception))


if __name__ == "__main__":
    unittest.main()
