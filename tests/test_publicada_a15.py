"""La 0.1.0a15 figura publicada en las notas y los textos, y se detecta lo que la siga llamando candidata: escenarios pa1–pa2."""
from pathlib import Path
import re
import shutil
import tempfile
import unittest

from tools import docs_al_dia

ROOT = Path(__file__).resolve().parents[1]
V = "0.1.0a15"
ARCHIVOS = ("README.md", "docs/colaboracion.md", "site/desde-cero.html", "site/index.html", "site/colaboracion.html", "site/modos.html")
CANDIDATA = re.compile(rf"(?i){re.escape(V)}\s*\(en preparaci[oó]n\)|preparaci[oó]n\s+{re.escape(V)}|candidat[oa][^\n]{{0,60}}{re.escape(V)}"
                       rf"|{re.escape(V)}[^\n]{{0,60}}candidat[oa]|cuando se publique esta versi[oó]n|estado de preparaci[oó]n|en preparaci[oó]n para entrega")


def copia(tmp: Path) -> Path:
    dest = tmp / "repo"
    dest.mkdir()
    for n in ("pyproject.toml", "README.md", "NOTAS-DE-RELEASE.md"):
        shutil.copy2(ROOT / n, dest / n)
    shutil.copytree(ROOT / "docs", dest / "docs")
    shutil.copytree(ROOT / "site", dest / "site")
    return dest


def divergencias(raiz: Path) -> list[str]:
    return [p for p in docs_al_dia.problemas(raiz) if "describe la versión" in p or "afirma que la versión" in p]


class PublicadaA15(unittest.TestCase):
    # --- pa1: los textos declaran publicada la versión publicada ---------------------------------------------------------
    def test_pa1_las_notas_declaran_la_version_publicada_con_su_tag_y_su_release(self):
        notas = (ROOT / "NOTAS-DE-RELEASE.md").read_text(encoding="utf-8")
        self.assertIn(f"\n# Oracle Factory {V}\n", "\n" + notas)
        self.assertNotIn(f"{V} (en preparación)", notas)
        self.assertRegex(notas, rf"\*\*Publicada\.\*\* En PyPI como `oracle-factory=={re.escape(V)}` y en GitHub con su tag `v{re.escape(V)}`")

    def test_pa1_ningun_texto_llama_candidata_a_la_version_publicada(self):
        for nombre in ARCHIVOS:
            texto = (ROOT / nombre).read_text(encoding="utf-8")
            self.assertIsNone(CANDIDATA.search(texto), f"{nombre}: {CANDIDATA.search(texto)}")
        self.assertEqual(divergencias(ROOT), [])

    def test_pa1_el_readme_y_la_guia_dicen_que_esta_publicada(self):
        self.assertIn(f"Versión publicada en PyPI: `oracle-factory=={V}`", (ROOT / "README.md").read_text(encoding="utf-8"))
        guia = (ROOT / "site/desde-cero.html").read_text(encoding="utf-8")
        self.assertIn(f"Esta guía describe Factory {V}, publicada en PyPI y en GitHub.", guia)
        self.assertIn(f"oracle-factory=={V}", guia)

    def test_pa1_la_historia_anterior_se_conserva(self):
        notas = (ROOT / "NOTAS-DE-RELEASE.md").read_text(encoding="utf-8")
        for v in ("0.1.0a14", "0.1.0a13", "0.1.0a12", "0.1.0a11"):
            self.assertIn(f"\n# Oracle Factory {v}\n", "\n" + notas, v)
            self.assertNotIn(f"{v} (en preparación)", notas, v)
        # el orden: la más nueva arriba
        orden = [notas.index(f"# Oracle Factory {v}") for v in (V, "0.1.0a14", "0.1.0a13", "0.1.0a12")]
        self.assertEqual(orden, sorted(orden))

    # --- pa2: se detecta lo que la siga llamando candidata ---------------------------------------------------------------
    def test_pa2_un_texto_candidata_con_las_notas_publicadas_se_detecta(self):
        frases = ("Candidato en preparación `oracle-factory==0.1.0a15`, y su wheel.", "La 0.1.0a15 (en preparación) trae el tablero.",
                  "Los comandos de instalación se podrán usar cuando se publique esta versión.", "Versión y estado de preparación.",
                  "PREPARACIÓN 0.1.0a15", "Esta guía describe el candidato Factory 0.1.0a15.", "La versión 0.1.0a15 es la candidata a publicar.", "Esta guía está en preparación para entrega.")
        with tempfile.TemporaryDirectory() as tmp:
            repo = copia(Path(tmp))
            self.assertEqual(divergencias(repo), [])
            for archivo in ("README.md", "docs/colaboracion.md", "site/desde-cero.html"):
                original = (repo / archivo).read_text(encoding="utf-8")
                for frase in frases:
                    (repo / archivo).write_text(original + f"\n<p>{frase}</p>\n", encoding="utf-8")
                    self.assertTrue(any(p.startswith(f"{archivo}: describe la versión {V} como candidata o en preparación") for p in divergencias(repo)),
                                    (archivo, frase))
                (repo / archivo).write_text(original, encoding="utf-8")

    def test_pa2_una_version_en_preparacion_no_es_divergencia(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = copia(Path(tmp))
            notas = repo / "NOTAS-DE-RELEASE.md"
            texto = notas.read_text(encoding="utf-8")
            notas.write_text(texto.replace(f"# Oracle Factory {V}\n", f"# Oracle Factory {V} (en preparación)\n", 1), encoding="utf-8")
            readme = repo / "README.md"
            readme.write_text(f"{readme.read_text(encoding='utf-8')}\nCandidato en preparación `oracle-factory=={V}`.\n", encoding="utf-8")
            self.assertFalse(any("describe la versión" in p for p in docs_al_dia.problemas(repo)))

    def test_pa2_sin_notas_la_regla_no_inventa_divergencias(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = copia(Path(tmp))
            (repo / "NOTAS-DE-RELEASE.md").unlink()
            self.assertEqual(divergencias(repo), [])

    def test_pa2_otra_version_con_la_palabra_candidato_no_cuenta(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = copia(Path(tmp))
            readme = repo / "README.md"
            readme.write_text(readme.read_text(encoding="utf-8") + "\nEl candidato de la revisión se prepara aparte.\n", encoding="utf-8")
            self.assertEqual(divergencias(repo), [])


if __name__ == "__main__":
    unittest.main()
