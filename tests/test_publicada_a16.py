"""La 0.1.0a16 figura publicada en las notas y los textos, y se detecta lo que la siga llamando candidata: escenarios pa1–pa2."""
from pathlib import Path
import re
import shutil
import tempfile
import unittest

from tools import docs_al_dia

ROOT = Path(__file__).resolve().parents[1]
V = "0.1.0a16"
ARCHIVOS = ("README.md", "docs/colaboracion.md", "site/desde-cero.html", "site/index.html", "site/colaboracion.html", "site/modos.html")
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


class PublicadaA16(unittest.TestCase):
    # --- pa1: los textos declaran publicada la versión publicada ---------------------------------------------------------
    def test_pa1_las_notas_declaran_la_version_publicada_con_su_tag_y_su_release(self):
        notas = (ROOT / "NOTAS-DE-RELEASE.md").read_text(encoding="utf-8")
        self.assertIn(f"\n# Oracle Factory {V}\n", "\n" + notas)
        self.assertNotIn(f"{V} (en preparación)", notas)
        self.assertRegex(notas, rf"\*\*Publicada\.\*\* En PyPI como `oracle-factory=={re.escape(V)}` y en GitHub con su tag `v{re.escape(V)}`")

    def test_pa1_ningun_texto_llama_candidata_a_la_version_publicada(self):
        for nombre in ARCHIVOS:
            texto = (ROOT / nombre).read_text(encoding="utf-8")
            self.assertIsNone(docs_al_dia.patron_preparacion(V).search(texto), nombre)
        self.assertEqual(divergencias(ROOT), [])

    def test_pa1_el_readme_y_la_guia_dicen_que_esta_publicada(self):
        self.assertIn(f"Versión publicada en PyPI: `oracle-factory=={V}`", (ROOT / "README.md").read_text(encoding="utf-8"))
        guia = (ROOT / "site/desde-cero.html").read_text(encoding="utf-8")
        self.assertIn(f"Esta guía describe Factory {V}, publicada en PyPI y en GitHub.", guia)
        self.assertIn(f"oracle-factory=={V}", guia)

    def test_pa1_la_historia_anterior_se_conserva(self):
        notas = (ROOT / "NOTAS-DE-RELEASE.md").read_text(encoding="utf-8")
        for v in ("0.1.0a15", "0.1.0a14", "0.1.0a13", "0.1.0a12"):
            self.assertIn(f"\n# Oracle Factory {v}\n", "\n" + notas, v)
            self.assertNotIn(f"{v} (en preparación)", notas, v)
        # el orden: la más nueva arriba
        orden = [notas.index(f"# Oracle Factory {v}") for v in (V, "0.1.0a15", "0.1.0a14", "0.1.0a13")]
        self.assertEqual(orden, sorted(orden))

    # --- pa2: se detecta lo que la siga llamando candidata ---------------------------------------------------------------
    def test_pa2_un_texto_candidata_con_las_notas_publicadas_se_detecta(self):
        frases = ("Candidato en preparación `oracle-factory==0.1.0a16`, y su wheel.", "La 0.1.0a16 (en preparación) trae el tablero.",
                  "La 0.1.0a16 en preparación trae el tablero.", "La 0.1.0a16 está en preparación.", "La 0.1.0a16 sigue en preparación.",
                  "Los comandos de instalación se podrán usar cuando se publique esta versión.", "Versión 0.1.0a16 y estado de preparación.",
                  "PREPARACIÓN 0.1.0a16", "Esta guía describe el candidato Factory 0.1.0a16.", "Esta guía describe el candidato 0.1.0a16.",
                  "La versión 0.1.0a16 es la candidata a publicar.", "La 0.1.0a16 es una versión candidata.",
                  "Estado: en preparación: 0.1.0a16.", "Se instala cuando se publique la 0.1.0a16.", "La 0.1.0a16 se publicará pronto.", "Versión 0.1.0a16 en preparación.",
                  "Esta guía describe Factory 0.1.0a16 en preparación para entrega.")
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

    def test_pa2_el_candidato_de_una_revision_y_otros_estados_de_preparacion_no_son_divergencia(self):
        legitimas = ("El candidato ca6a267 de la versión 0.1.0a16 fue aprobado.", "El candidato de la revisión de la 0.1.0a16 se prepara aparte.",
                     "El estado de preparación de un cambio se consulta con oracle-factory estado.", "Un cambio en preparación para entrega no se integra.",
                     "La 0.1.0a15 estuvo en preparación y hoy está publicada, igual que la 0.1.0a16.", "Cada candidato lleva su evidencia.",
                     "La 0.1.0a16 corrige el candidato anterior de la guía.", "Preparación de la revisión de la 0.1.0a16.",
                     "La 0.1.0a16 está publicada. El estado de preparación de un cambio se consulta con estado.",
                     "Los cambios se integran cuando se publique un cambio de la rama.", "En preparación: la revisión del cambio, no una versión.",
                     "La 0.1.0a16 trae muchas cosas nuevas del tablero, del idioma y de los bloqueos, y también cambia el estado de preparación de cada cambio.")
        with tempfile.TemporaryDirectory() as tmp:
            repo = copia(Path(tmp))
            for archivo in ("README.md", "docs/colaboracion.md", "site/desde-cero.html"):
                original = (repo / archivo).read_text(encoding="utf-8")
                for frase in legitimas:
                    (repo / archivo).write_text(original + f"\n<p>{frase}</p>\n", encoding="utf-8")
                    self.assertEqual(divergencias(repo), [], (archivo, frase))
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

    def test_pa2_la_palabra_candidato_junto_a_otra_version_no_cuenta(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = copia(Path(tmp))
            readme = repo / "README.md"
            for frase in ("La 0.1.0a15 fue candidata a publicar antes de la 0.1.0a16.", "Candidato en preparación `oracle-factory==0.1.0a15`.",
                          "El candidato de la 0.1.0a15 pasó la revisión."):
                readme.write_text(readme.read_text(encoding="utf-8") + f"\n{frase}\n", encoding="utf-8")
                self.assertFalse(any("describe la versión" in p for p in docs_al_dia.problemas(repo)), frase)


if __name__ == "__main__":
    unittest.main()
