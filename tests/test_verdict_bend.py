"""Las leyes de quién decide también valen para el núcleo de Bend probado en Lean (vb1): `bend PROOF.bend --verdict`.

Sin `bend`, `lean` o `leanc` en el PATH, la prueba se omite y dice cuál falta.
"""
import os
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


def veredicto(bend: str, carpeta: Path) -> tuple[int, str]:
    r = subprocess.run([bend, "PROOF.bend", "--verdict"], cwd=carpeta, env=ENTORNO, capture_output=True, text=True, timeout=PLAZO)
    return r.returncode, r.stdout + r.stderr


def nucleo() -> Path:
    """El núcleo de Bend compilado (BendTT, con su prueba en Lean), en la caché que deja --verdict."""
    hogar = Path(os.environ.get("BEND_HOME") or Path.home() / ".bend")
    encontrados = sorted(hogar.glob("bendtt/*/bendtt"))
    if len(encontrados) != 1:
        raise AssertionError(f"esperaba un núcleo compilado en {hogar}/bendtt/, hay {len(encontrados)}")
    return encontrados[0]


def traduccion(bend: str, tmp: str) -> Path:
    """Lo que lee el núcleo: PROOF.bend traducido con `bend PROOF.bend -o PROOF.bendtt`, en una copia del modelo."""
    copia = Path(tmp) / "q"
    shutil.copytree(MODELO, copia)
    subprocess.run([bend, "PROOF.bend", "-o", "PROOF.bendtt"], cwd=copia, env=ENTORNO, check=True, capture_output=True, timeout=PLAZO)
    return copia / "PROOF.bendtt"


def juzga_el_nucleo(archivo: Path) -> tuple[int, str]:
    r = subprocess.run([str(nucleo()), archivo.name], cwd=archivo.parent, capture_output=True, text=True, timeout=PLAZO)
    return r.returncode, r.stdout + r.stderr


class Verdict(unittest.TestCase):
    # --- vb1: las leyes valen para el núcleo probado ----------------------------------------------------------------------
    def test_vb1_el_nucleo_acepta_las_pruebas(self):
        bend = herramientas()
        codigo, salida = veredicto(bend, MODELO)
        self.assertEqual(codigo, 0, salida)
        self.assertIn("ALL PROOFS CHECK", salida)
        # El núcleo solo, sin bend en el medio (hallazgo BEND-VERDICT-001 de codex): acepta la traducción.
        with tempfile.TemporaryDirectory() as tmp:
            codigo, salida = juzga_el_nucleo(traduccion(bend, tmp))
        self.assertEqual(codigo, 0, salida)
        self.assertIn("ALL PROOFS CHECK", salida)

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
            codigo, salida = veredicto(bend, copia)
        self.assertNotEqual(codigo, 0, salida)
        self.assertNotIn("ALL PROOFS CHECK", salida)

    def test_vb1_el_nucleo_solo_rechaza_una_traduccion_alterada(self):
        # El verificador de bend rechaza el mutante antes de llegar al núcleo; acá el que rechaza es el núcleo mismo.
        bend = herramientas()
        with tempfile.TemporaryDirectory() as tmp:
            archivo = traduccion(bend, tmp)
            texto = archivo.read_text(encoding="utf-8")
            propone_no_es_decidir = "λ{.quien_3a_Propone: λ{(): (.False, ()); λ{}}"
            self.assertEqual(texto.count(propone_no_es_decidir), 1)
            archivo.write_text(texto.replace(propone_no_es_decidir, "λ{.quien_3a_Propone: λ{(): (.True, ()); λ{}}"), encoding="utf-8")
            codigo, salida = juzga_el_nucleo(archivo)
        self.assertNotEqual(codigo, 0, salida)
        self.assertNotIn("ALL PROOFS CHECK", salida)
        self.assertIn("confirmacion__el__agente__no__decide", salida)

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
