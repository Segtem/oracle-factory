"""pb1–pb2: los textos presentan a20 publicada y detectan un estado de publicación viejo."""
from pathlib import Path
import tempfile
import unittest

from tools import docs_al_dia


ROOT = Path(__file__).resolve().parents[1]
VERSION = "0.1.0a20"
WHEEL_SHA256 = "f2a9aa64c77788a9a33f64b08c798dd8420edb66b87a680eef6131fdb60bfb60"
SDIST_SHA256 = "0fa02fff24dc7b166682ccff68449ac46052c06fb4b711ca5dc20f86944e9b7a"
ENTRADAS = ("README.md", "docs/colaboracion.md", "site/index.html", "site/desde-cero.html",
            "site/colaboracion.html", "site/modos.html")


class PublicadaA20(unittest.TestCase):
    # pb1: la publicación aparece en los textos y el historial sigue completo.
    def test_pb1_notas_nominan_publicacion_y_artefactos_verificados(self):
        notas = (ROOT / "NOTAS-DE-RELEASE.md").read_text(encoding="utf-8")
        self.assertTrue(notas.startswith("# Sin publicar\n"))
        self.assertIn(f"\n# Oracle Factory {VERSION}\n", notas)
        self.assertNotIn(f"{VERSION} (en preparación)", notas)
        a20 = notas.split(f"\n# Oracle Factory {VERSION}\n", 1)[1].split("\n# Oracle Factory ", 1)[0]
        self.assertIn(f"**Publicada.** En PyPI como `oracle-factory=={VERSION}`", a20)
        self.assertIn(f"`v{VERSION}`", a20)
        self.assertIn(f"https://github.com/Segtem/oracle-factory/releases/tag/v{VERSION}", a20)
        self.assertIn(WHEEL_SHA256, a20)
        self.assertIn(SDIST_SHA256, a20)

    def test_pb1_readme_guias_y_web_instalan_a20_sin_llamarla_candidata(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertTrue(readme.startswith(f"# Oracle Factory — {VERSION} (alpha)\n"))
        self.assertIn(f"Versión publicada en PyPI: `oracle-factory=={VERSION}`", readme)
        self.assertIn(f"uv tool install --python 3.13 oracle-factory=={VERSION}", readme)
        guia = (ROOT / "site/desde-cero.html").read_text(encoding="utf-8")
        self.assertIn(f"Esta guía describe Factory {VERSION}, publicada en PyPI y en GitHub.", guia)
        self.assertIn(f"oracle-factory=={VERSION}", guia)
        for nombre in ENTRADAS:
            texto = (ROOT / nombre).read_text(encoding="utf-8")
            self.assertIsNone(docs_al_dia.patron_preparacion(VERSION).search(texto), nombre)
            if nombre == "README.md":
                texto = texto.split("## Historial de versiones", 1)[0]
            self.assertNotIn("oracle-factory==0.1.0a19", texto, nombre)
        self.assertEqual(docs_al_dia.problemas(ROOT), [])

    def test_pb1_historial_anterior_se_conserva_en_orden(self):
        notas = (ROOT / "NOTAS-DE-RELEASE.md").read_text(encoding="utf-8")
        versiones = (VERSION, "0.1.0a19", "0.1.0a18", "0.1.0a17", "0.1.0a16")
        posiciones = [notas.index(f"# Oracle Factory {version}\n") for version in versiones]
        self.assertEqual(posiciones, sorted(posiciones))
        for version in versiones[1:]:
            self.assertIn(f"**Publicada.** En PyPI como `oracle-factory=={version}`", notas)

    def test_pb1_web_y_readme_describen_el_alcance_actual_de_las_firmas(self):
        for nombre in ("site/index.html", "site/modos.html", "site/colaboracion.html"):
            texto = (ROOT / nombre).read_text(encoding="utf-8")
            self.assertIn("firmas", texto, nombre)
            self.assertNotIn("Factory no autentica", texto, nombre)
            self.assertNotIn("El registro no está firmado", texto, nombre)
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertNotIn("ni ese archivo ni el registro están firmados", readme)

    # pb2: el chequeo nombra textos obsoletos y conserva los usos legítimos de «candidato».
    def test_pb2_un_texto_obsoleto_se_detecta_con_su_archivo(self):
        with tempfile.TemporaryDirectory() as tmp:
            raiz = Path(tmp)
            (raiz / "NOTAS-DE-RELEASE.md").write_text(f"# Oracle Factory {VERSION}\n", encoding="utf-8")
            for nombre in ("README.md", "site/desde-cero.html"):
                for texto in (f"La {VERSION} está en preparación.",
                              f"Candidato en preparación `oracle-factory=={VERSION}`.",
                              f"La {VERSION} se publicará pronto."):
                    with self.subTest(nombre=nombre, texto=texto):
                        problemas = docs_al_dia.preparacion_olvidada(raiz, VERSION, {nombre: texto})
                        self.assertTrue(any(p.startswith(f"{nombre}:") for p in problemas), problemas)

    def test_pb2_candidato_de_revision_y_estado_de_cambio_no_son_divergencias(self):
        with tempfile.TemporaryDirectory() as tmp:
            raiz = Path(tmp)
            (raiz / "NOTAS-DE-RELEASE.md").write_text(f"# Oracle Factory {VERSION}\n", encoding="utf-8")
            textos = {"README.md": (f"El candidato abc123 de la versión {VERSION} pasó la revisión. "
                                     "El estado de preparación de un cambio se consulta con estado.")}
            self.assertEqual(docs_al_dia.preparacion_olvidada(raiz, VERSION, textos), [])


if __name__ == "__main__":
    unittest.main()
