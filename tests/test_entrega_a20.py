"""ea1–ea3: versión candidata a20, wheel instalado con firmas y hashes de la entrega."""
import importlib
import io
import json
from contextlib import redirect_stdout
from pathlib import Path
import tempfile
import tomllib
import unittest
from unittest.mock import patch
from types import SimpleNamespace

from tools import docs_al_dia

ROOT = Path(__file__).resolve().parents[1]
VERSION = "0.1.0a20"


def probador():
    return importlib.import_module("tools.probar_entrega_a20")


class EntregaA20(unittest.TestCase):
    _entrega = None

    @classmethod
    def entrega(cls):
        if cls._entrega is None:
            temporal = tempfile.TemporaryDirectory(prefix="test-entrega-a20-")
            def limpiar():
                cls._entrega = None
                temporal.cleanup()
            cls.addClassCleanup(limpiar)
            salida = Path(temporal.name) / "entrega"
            cls._entrega = salida
            if probador().main(["--salida", str(salida)]) != 0:
                raise AssertionError("el probador de la entrega a20 falló")
        return cls._entrega

    # ea1: el candidato dice su propia versión sin presentarse como publicado.
    def test_ea1_version_metadatos_cli_lock_y_textos(self):
        import oracle_factory
        self.assertEqual(tomllib.loads((ROOT / "pyproject.toml").read_text())["project"]["version"], VERSION)
        self.assertEqual(oracle_factory.__version__, VERSION)
        [propio] = [p for p in tomllib.loads((ROOT / "uv.lock").read_text())["package"] if p["name"] == "oracle-factory"]
        self.assertEqual(propio["version"], VERSION)
        notas = (ROOT / "NOTAS-DE-RELEASE.md").read_text(encoding="utf-8")
        self.assertTrue(notas.startswith(f"# Oracle Factory {VERSION} (en preparación)\n"))
        self.assertLess(notas.index(f"# Oracle Factory {VERSION}"), notas.index("# Oracle Factory 0.1.0a19"))
        self.assertNotIn(f"**Publicada.** En PyPI como `oracle-factory=={VERSION}`", notas)
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("Versión publicada en PyPI: `oracle-factory==0.1.0a19`", readme)
        self.assertIn(f"{VERSION}", readme)
        self.assertEqual(docs_al_dia.problemas(ROOT), [])

    def test_ea1_publicacion_prematura_nombra_el_archivo(self):
        with tempfile.TemporaryDirectory() as tmp:
            raiz = Path(tmp)
            (raiz / "NOTAS-DE-RELEASE.md").write_text(f"# Oracle Factory {VERSION} (en preparación)\n")
            problemas = docs_al_dia.publicacion_prematura(
                raiz, VERSION, {"README.md": f"La {VERSION} ya está publicada en PyPI."})
        self.assertTrue(any("README.md:" in p and VERSION in p for p in problemas), problemas)
        with tempfile.TemporaryDirectory() as tmp:
            raiz = Path(tmp)
            (raiz / "pyproject.toml").write_text(f'[project]\nversion = "{VERSION}"\n')
            (raiz / "NOTAS-DE-RELEASE.md").write_text(
                f"# Oracle Factory {VERSION} (en preparación)\n\nLa {VERSION} ya está publicada en PyPI.\n")
            with patch.object(docs_al_dia, "textos", return_value={}), \
                    patch.object(docs_al_dia, "subcomandos", return_value=set()):
                problemas = docs_al_dia.problemas(raiz)
        self.assertTrue(any("NOTAS-DE-RELEASE.md:" in p and VERSION in p for p in problemas), problemas)
        with tempfile.TemporaryDirectory() as tmp:
            raiz = Path(tmp)
            (raiz / "pyproject.toml").write_text(f'[project]\nversion = "{VERSION}"\n')
            (raiz / "NOTAS-DE-RELEASE.md").write_text(
                f"# Oracle Factory {VERSION} (en preparación)\n\n"
                f"- **Publicada.** En PyPI como `oracle-factory=={VERSION}`.\n")
            with patch.object(docs_al_dia, "textos", return_value={}), \
                    patch.object(docs_al_dia, "subcomandos", return_value=set()):
                problemas = docs_al_dia.problemas(raiz)
        self.assertTrue(any("NOTAS-DE-RELEASE.md:" in p and VERSION in p for p in problemas), problemas)

        with tempfile.TemporaryDirectory() as tmp:
            raiz = Path(tmp)
            (raiz / "pyproject.toml").write_text(f'[project]\nversion = "{VERSION}"\n')
            (raiz / "NOTAS-DE-RELEASE.md").write_text(
                f"# Oracle Factory {VERSION} (en preparación)\n\n"
                "# Oracle Factory 0.1.0a19\n\n- **Publicada.** En PyPI como `oracle-factory==0.1.0a19`.\n")
            for instruccion in (f"uv tool install oracle-factory=={VERSION}",
                                f"Instalá la versión publicada con uv tool install oracle-factory=={VERSION}",
                                f"Instalá oracle-factory=={VERSION}"):
                with self.subTest(instruccion=instruccion), \
                        patch.object(docs_al_dia, "textos", return_value={"README.md": instruccion}), \
                        patch.object(docs_al_dia, "subcomandos", return_value=set()):
                    problemas = docs_al_dia.problemas(raiz)
                self.assertTrue(any("README.md:" in p and "instal" in p for p in problemas), problemas)
            notas = raiz / "NOTAS-DE-RELEASE.md"
            notas.write_text(notas.read_text() + f"\nuv tool install oracle-factory=={VERSION}\n")
            with patch.object(docs_al_dia, "textos", return_value={}), \
                    patch.object(docs_al_dia, "subcomandos", return_value=set()):
                problemas = docs_al_dia.problemas(raiz)
            self.assertTrue(any("NOTAS-DE-RELEASE.md:" in p and "instal" in p for p in problemas), problemas)
            notas.write_text(
                f"# Oracle Factory {VERSION} (en preparación)\n\n"
                "# Oracle Factory 0.1.0a19\n\n- **Publicada.** En PyPI como `oracle-factory==0.1.0a19`.\n"
                "La 0.1.0a19 está en preparación.\n")
            with patch.object(docs_al_dia, "textos", return_value={}), \
                    patch.object(docs_al_dia, "subcomandos", return_value=set()):
                problemas = docs_al_dia.problemas(raiz)
            self.assertTrue(any("NOTAS-DE-RELEASE.md:" in p and "candidata" in p for p in problemas), problemas)

    def test_ea1_una_version_mas_vieja_que_la_publicada_se_nombra(self):
        with tempfile.TemporaryDirectory() as tmp:
            raiz = Path(tmp)
            (raiz / "pyproject.toml").write_text(f'[project]\nversion = "{VERSION}"\n')
            (raiz / "NOTAS-DE-RELEASE.md").write_text(
                f"# Oracle Factory {VERSION} (en preparación)\n\n# Oracle Factory 0.1.0a19\n"
                "\n- **Publicada.** En PyPI como `oracle-factory==0.1.0a19`.\n")
            with patch.object(docs_al_dia, "textos", return_value={"README.md": "Instalá oracle-factory==0.1.0a18"}), \
                    patch.object(docs_al_dia, "subcomandos", return_value=set()):
                problemas = docs_al_dia.problemas(raiz)
        self.assertTrue(any("README.md:" in p and "0.1.0a18" in p for p in problemas), problemas)

    # ea2: lo que se instala desde el wheel trae las firmas y funciona fuera del checkout.
    def test_ea2_wheel_real_instalado_contiene_firmas(self):
        salida = self.entrega()
        registro = json.loads((salida / "registro.json").read_text(encoding="utf-8"))
        obs = registro["observaciones"]
        self.assertTrue(registro["ok"])
        self.assertEqual(obs["importacion"]["version"], VERSION)
        self.assertFalse(obs["importacion"]["desde_el_checkout"])
        self.assertTrue(obs["importacion"]["en_el_entorno"])
        self.assertEqual(obs["cli_version"], {"rc": 0, "salida": f"oracle-factory {VERSION}"})
        self.assertTrue(obs["firma_importada"]["en_el_entorno"])
        self.assertEqual(obs["firma_importada"]["rc"], 0)
        self.assertIn(probador().FIRMAS_EN_EL_WHEEL, registro["archivos_obligatorios"])

    def test_ea2_wheel_sin_firmas_se_rechaza(self):
        herramienta = probador()
        salida = self.entrega()
        registro = json.loads((salida / "registro.json").read_text(encoding="utf-8"))
        obs = dict(registro["observaciones"])
        obs["archivos_del_wheel"] = [p for p in registro["archivos_obligatorios"] if p != herramienta.FIRMAS_EN_EL_WHEEL]
        self.assertTrue(any(herramienta.FIRMAS_EN_EL_WHEEL in p for p in herramienta.validar(obs)))

    def test_ea2_firmas_importadas_fuera_del_entorno_se_rechazan(self):
        herramienta = probador()
        with tempfile.TemporaryDirectory() as tmp:
            python = Path(tmp) / "venv/bin/python"
            with patch.object(herramienta.anterior, "observar", return_value={}), \
                    patch.object(herramienta.anterior, "correr", return_value=SimpleNamespace(
                        stdout="/tmp/otro/oracle_factory/firmas.py\n", returncode=0)):
                obs = herramienta.observar(Path("wheel.whl"), Path("factory"), python, Path(tmp))
        self.assertFalse(obs["firma_importada"]["en_el_entorno"])

    def test_ea2_importacion_fallida_o_ajena_se_rechaza(self):
        herramienta = probador()
        obs = json.loads((self.entrega() / "registro.json").read_text(encoding="utf-8"))["observaciones"]
        obs["archivos_del_wheel"] = list(herramienta.OBLIGATORIOS)
        for firma in ({"rc": 1, "en_el_entorno": True}, {"rc": 0, "en_el_entorno": False}):
            with self.subTest(firma=firma):
                obs["firma_importada"] = firma
                self.assertIn("oracle_factory.firmas no se importa desde el entorno nuevo", herramienta.validar(obs))

    # ea3: el registro permite identificar los bytes probados y no afirma una subida remota.
    def test_ea3_registro_con_hashes_limites_y_sin_sobrescribir(self):
        herramienta = probador()
        salida = self.entrega()
        registro = json.loads((salida / "registro.json").read_text(encoding="utf-8"))
        self.assertEqual(registro["version"], VERSION)
        self.assertIs(registro["publicada"], False)
        self.assertEqual(herramienta.problemas_del_registro(registro), [])
        for tipo in ("wheel", "sdist"):
            self.assertEqual(registro["hashes"][tipo], herramienta.sha256(salida / "dist" / registro["archivos"][tipo]))
        self.assertTrue(registro["limites"])
        with self.assertRaises(FileExistsError):
            herramienta.main(["--salida", str(salida)])
        with tempfile.TemporaryDirectory() as tmp:
            destino = Path(tmp) / "entrega"
            destino.mkdir()
            previo = destino / "registro.json"
            previo.write_bytes(b'{"registro":"previo"}\n')
            with patch.object(herramienta.anterior, "construir", side_effect=AssertionError("no debe construir")):
                with self.assertRaises(FileExistsError):
                    herramienta.main(["--salida", str(destino)])
            self.assertEqual(previo.read_bytes(), b'{"registro":"previo"}\n')
            self.assertFalse((destino / "dist").exists())
            previo.unlink()
            previo.symlink_to(destino / "ausente")
            with patch.object(herramienta.anterior, "construir", side_effect=AssertionError("no debe construir")):
                with self.assertRaises(FileExistsError):
                    herramienta.main(["--salida", str(destino)])
            self.assertTrue(previo.is_symlink())

    def test_ea3_registro_incompleto_se_rechaza(self):
        herramienta = probador()
        registro = {"hashes": {"wheel": "a" * 64}, "versiones": {"python": "3.13", "uv": "uv"},
                    "observaciones": {"x": 1}, "limites": [], "publicada": False}
        problemas = herramienta.problemas_del_registro(registro)
        self.assertTrue(any("sdist" in p for p in problemas))
        self.assertTrue(any("límites" in p for p in problemas))

    def test_ea3_una_entrega_fallida_sale_con_codigo_y_resumen_verificables(self):
        herramienta = probador()
        hashes = {"wheel": "a" * 64, "sdist": "b" * 64}
        registro = {"hashes": hashes, "archivos": {"wheel": "w.whl", "sdist": "s.tar.gz"},
                    "limites": ["límites"], "version": VERSION, "publicada": False,
                    "observaciones": {}, "problemas": []}
        with tempfile.TemporaryDirectory() as tmp:
            salida = Path(tmp) / "entrega"
            salida.mkdir()
            stdout = io.StringIO()
            with patch.object(herramienta.anterior, "construir", return_value={"wheel": Path("w.whl")}), \
                    patch.object(herramienta.anterior, "instalar", return_value=(Path("factory"), Path("python"))), \
                    patch.object(herramienta, "observar", return_value={"archivos_del_wheel": list(herramienta.OBLIGATORIOS)}), \
                    patch.object(herramienta, "validar", return_value=["falló la comprobación"]), \
                    patch.object(herramienta.anterior, "registro", return_value=registro), \
                    patch.object(herramienta, "problemas_del_registro", return_value=[]), redirect_stdout(stdout):
                codigo = herramienta.main(["--salida", str(salida)])
            texto = (salida / "registro.json").read_text(encoding="utf-8")
        self.assertEqual(codigo, 1)
        self.assertIn('"límites"', texto)
        self.assertIn("Entrega 0.1.0a20: CON PROBLEMAS; wheel aaaaaaaaaaaa, sdist bbbbbbbbbbbb;", stdout.getvalue())
        self.assertIn("falló la comprobación", stdout.getvalue())


if __name__ == "__main__":
    unittest.main()
