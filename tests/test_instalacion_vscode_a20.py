"""iv1–iv3: instalación publicada del kit y del complemento de VS Code."""

import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
import zipfile

from tools import docs_al_dia


ROOT = Path(__file__).resolve().parents[1]
VERSION = "0.1.0a20"
VSIX = "oracle-factory-0.5.0.vsix"
ASSET = f"https://github.com/Segtem/oracle-factory/releases/download/v{VERSION}/{VSIX}"


class InstalacionVscodeA20(unittest.TestCase):
    def test_iv1_guia_instala_kit_y_cli_sin_pisar_comandos(self):
        guia = (ROOT / "docs/instalacion.md").read_text(encoding="utf-8")
        self.assertIn(f"uv tool install --python 3.13 oracle-factory=={VERSION}", guia)
        self.assertIn(
            "uv tool install --python 3.13 --with-executables-from "
            f"oracle-metalenguaje,oracle-task,oracle-clue oracle-factory=={VERSION}", guia)
        for command in ("oracle-factory --version", "oracle --version", "tasks --version", "oracle-clue --version"):
            self.assertIn(command, guia)
        for version in (VERSION, "0.39.0", "0.2.0", "0.1.0a2"):
            self.assertIn(version, guia)
        self.assertIn("conflicto", guia.lower())
        self.assertIn("sin sobrescribir", guia.lower())
        self.assertIn("uv tool upgrade", guia)
        self.assertIn("uv tool install --python 3.13 oracle-factory==VERSION_NUEVA", guia)

    def test_iv2_vsix_construido_tiene_identidad_y_archivos(self):
        with tempfile.TemporaryDirectory() as tmp:
            salida = Path(tmp) / VSIX
            subprocess.run([sys.executable, "editores/vscode/empaquetar.py", "--salida", str(salida)],
                           cwd=ROOT, check=True, capture_output=True, text=True)
            package = json.loads((ROOT / "editores/vscode/package.json").read_text(encoding="utf-8"))
            with zipfile.ZipFile(salida) as z:
                self.assertEqual(package["publisher"], "cs50-taller")
                self.assertEqual(package["name"], "oracle-factory")
                self.assertEqual(package["version"], "0.5.0")
                self.assertEqual(json.loads(z.read("extension/package.json")), package)
                for name in ("extension.js", "modelo.js", "tablero.js", "liveshare.js"):
                    self.assertEqual(z.read(f"extension/{name}"), (ROOT / "editores/vscode" / name).read_bytes())
                manifest = z.read("extension.vsixmanifest").decode()
                self.assertIn('Id="oracle-factory" Version="0.5.0" Publisher="cs50-taller"', manifest)

    def test_iv2_guia_descarga_comprueba_e_instala_el_vsix(self):
        guia = (ROOT / "docs/instalacion.md").read_text(encoding="utf-8")
        self.assertIn(ASSET, guia)
        self.assertIn("sha256sum", guia)
        self.assertIn(VSIX, guia)
        self.assertIn("code --install-extension", guia)
        self.assertIn("code --list-extensions --show-versions", guia)
        self.assertIn("cs50-taller.oracle-factory@0.5.0", guia)
        self.assertIn("factory.comando", guia)
        self.assertIn(".venv/bin/oracle-factory", guia)

    def test_iv2_vs_code_lista_el_paquete_en_un_perfil_aislado(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            vsix = base / VSIX
            subprocess.run([sys.executable, "editores/vscode/empaquetar.py", "--salida", str(vsix)],
                           cwd=ROOT, check=True, capture_output=True, text=True)
            self.assertTrue(zipfile.is_zipfile(vsix))
            code = shutil.which("code")
            if code is None:
                return  # VS Code no es dependencia de la suite; la evidencia local sí lo ejercita.
            perfil = ["--extensions-dir", str(base / "extensions"), "--user-data-dir", str(base / "user")]
            subprocess.run([code, "--install-extension", str(vsix), *perfil, "--force"],
                           check=True, capture_output=True, text=True, timeout=60)
            lista = subprocess.run([code, "--list-extensions", "--show-versions", *perfil],
                                   check=True, capture_output=True, text=True, timeout=60).stdout.splitlines()
            self.assertIn("cs50-taller.oracle-factory@0.5.0", lista)

    def test_iv3_entradas_conducen_a_las_dos_instalaciones(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        tablero = (ROOT / "docs/tablero.md").read_text(encoding="utf-8")
        web = (ROOT / "site/desde-cero.html").read_text(encoding="utf-8")
        self.assertIn("docs/instalacion.md", readme)
        self.assertIn("instalacion.md", tablero)
        self.assertIn("docs/instalacion.md", web)
        self.assertIn(ASSET, tablero)
        self.assertIn(ASSET, web)
        self.assertIn("sin instalar", web.lower())

    def test_iv3_auditoria_de_versiones_distingue_vsix_de_factory(self):
        for nombre in ("docs/instalacion.md", "docs/tablero.md", "site/desde-cero.html"):
            texto = (ROOT / nombre).read_text(encoding="utf-8")
            self.assertNotIn("0.5.0", docs_al_dia.versiones_factory(texto, nombre), nombre)


if __name__ == "__main__":
    unittest.main()
