"""Pruebas de la preparación de la distribución 0.1.0a14.

Cubre los contratos de distribucion:
- ea1: la versión de entrega es coherente y declara su estado (metadatos, docs, web y detección de divergencias)
- ea2: la distribución instalada ofrece las consultas del proyecto (origen venv, conteos, elaboración fixture con rechazo de escrituras)
- ea3: la entrega registra sus pruebas y sus límites (arneses, hashes, estabilidad y detección de fallas)
"""
from __future__ import annotations

import json
from pathlib import Path
import shutil
import sys
import tempfile
import tomllib
import unittest

ROOT = Path(__file__).resolve().parents[1]
from tools import docs_al_dia, probar_entrega_a14
import oracle_factory


class EntregaA14(unittest.TestCase):
    def copia_repo_minima(self, tmp: Path) -> Path:
        """Copia archivos relevantes de documentación y metadatos a un directorio temporal."""
        dest = tmp / "repo"
        dest.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / "pyproject.toml", dest / "pyproject.toml")
        shutil.copy2(ROOT / "README.md", dest / "README.md")
        shutil.copy2(ROOT / "NOTAS-DE-RELEASE.md", dest / "NOTAS-DE-RELEASE.md")
        shutil.copytree(ROOT / "docs", dest / "docs")
        shutil.copytree(ROOT / "site", dest / "site")
        return dest

    # --- ea1: la versión de entrega es coherente y declara su estado ----------------------
    def test_ea1_version_coherente_y_estado_declarado(self):
        # 1. Metadatos y paquete coinciden en 0.1.0a14
        datos_pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
        version_pyproject = datos_pyproject["project"]["version"]
        self.assertEqual(version_pyproject, "0.1.0a14")
        self.assertEqual(oracle_factory.__version__, "0.1.0a14")

        # 2. Documentación y web actuales están al día con la CLI y 0.1.0a14
        problemas = docs_al_dia.problemas(ROOT)
        self.assertEqual(problemas, [], f"Discrepancias detectadas en documentación: {problemas}")

        # 3. Se conserva el historial de versiones publicadas anteriores
        notas_release = (ROOT / "NOTAS-DE-RELEASE.md").read_text(encoding="utf-8")
        self.assertIn("# Oracle Factory 0.1.0a14 (en preparación)", notas_release)
        self.assertIn("# Oracle Factory 0.1.0a13", notas_release)
        self.assertIn("# Oracle Factory 0.1.0a12", notas_release)
        self.assertIn("0.1.0a13", (ROOT / "README.md").read_text(encoding="utf-8"))

        # 4. Escenario 'una versión o un estado divergen'
        with tempfile.TemporaryDirectory() as tmp:
            repo_tmp = self.copia_repo_minima(Path(tmp))

            # a) README nombra una versión divergente fuera del historial
            readme = repo_tmp / "README.md"
            contenido_original = readme.read_text(encoding="utf-8")
            readme.write_text(contenido_original.replace("0.1.0a14", "0.2.0"), encoding="utf-8")
            probs = docs_al_dia.problemas(repo_tmp)
            self.assertTrue(any("nombra la versión 0.2.0" in p for p in probs), "No se detectó la versión divergente 0.2.0")

    # --- ea2: la distribución instalada ofrece las consultas del proyecto ------------------
    def test_ea2_distribucion_instalada_consultas_registro_y_elaboracion(self):
        # 2. Proyecto fixture: conteos de registro sin modelo y elaboración fixture con servidor HTTP
        with tempfile.TemporaryDirectory(prefix="test-ea2-") as tmp:
            tmp_path = Path(tmp)
            venv_dir = tmp_path / "venv"
            factory_bin, python_bin = probar_entrega_a14.crear_entorno_aislado(venv_dir, probar_entrega_a14.construir_artefactos(tmp_path / 'dist')['wheel'])

            # Verificación real del módulo instalado en el nuevo venv
            verif = probar_entrega_a14.verificar_origen_y_version(python_bin, factory_bin, venv_dir, "0.1.0a14", ROOT)
            self.assertIn(str(venv_dir), verif["archivo_modulo"])
            self.assertNotIn(str(ROOT), verif["archivo_modulo"])

            # Los casos negativos usan este entorno temporal; no dependen del editable
            # del Python que ejecuta unittest (que puede pertenecer a otro checkout).
            pth = Path(verif['archivo_modulo']).parent.parent / 'origen_sonda.pth'
            try:
                pth.write_text('import sys; sys.path.insert(0, ' + repr(str(ROOT)) + ')\n')
                with self.assertRaisesRegex(AssertionError, 'Importación accidental desde el checkout'):
                    probar_entrega_a14.verificar_origen_y_version(
                        python_bin, factory_bin, venv_dir, '0.1.0a14', ROOT)
            finally:
                pth.unlink(missing_ok=True)
            modulo = Path(verif['archivo_modulo'])
            original = modulo.read_bytes()
            try:
                self.assertEqual(original.count(b'__version__ = "0.1.0a14"'), 1)
                modulo.write_bytes(original.replace(b'__version__ = "0.1.0a14"', b'__version__ = "0.1.0a13"'))
                with self.assertRaisesRegex(AssertionError, 'Versión incorrecta instalada'):
                    probar_entrega_a14.verificar_origen_y_version(
                        python_bin, factory_bin, venv_dir, '0.1.0a14', ROOT)
            finally:
                modulo.write_bytes(original)
            probar_entrega_a14.verificar_origen_y_version(python_bin, factory_bin, venv_dir, '0.1.0a14', ROOT)

            # Proyecto fixture con 2 cerrados archivados, 1 abierto, 1 abandonado
            proyecto_dir = probar_entrega_a14.crear_proyecto_fixture_registro(tmp_path, factory_bin)

            # Escenario: contar sin depender del checkout ni del modelo
            res_conteo = probar_entrega_a14.probar_conteo_registro(factory_bin, proyecto_dir)
            self.assertTrue(res_conteo["exitoso"])
            self.assertEqual(len(res_conteo["casos"]), 4)
            # Confirmar cerrados == 2, abiertos == 1, abandonados == 1, todos == 4
            conteo_map = {c["filtro"]: c["observado"] for c in res_conteo["casos"]}
            self.assertEqual(conteo_map["cerrados"], 2)
            self.assertEqual(conteo_map["abiertos"], 1)
            self.assertEqual(conteo_map["abandonados"], 1)
            self.assertEqual(conteo_map["todos"], 4)

            # Escenario: elaborar con un proveedor fixture explícito y rechazo de escrituras
            res_elab = probar_entrega_a14.probar_elaboracion_servidor_fixture(factory_bin, proyecto_dir)
            self.assertTrue(res_elab["exitoso"])
            self.assertTrue(res_elab["simulado"])
            self.assertTrue(res_elab["rechazo_escritura"])
            # Trazas: 'escribir' rechazada con exitoso False
            trazas = res_elab["trazas"]
            self.assertTrue(any(t["herramienta"] == "escribir" and t["exitoso"] is False for t in trazas))
            # No se creó archivo en disco ni se alteró registro
            self.assertFalse((proyecto_dir / "malicioso.txt").exists())

    # --- ea3: la entrega registra sus pruebas y sus límites ---------------------------------
    def test_ea3_entrega_registra_pruebas_y_limites(self):
        # 1. Comprobación de que los arneses de instalación y guía corren exitosamente
        with tempfile.TemporaryDirectory(prefix="test-ea3-") as tmp:
            tmp_path = Path(tmp)
            venv_dir = tmp_path / "venv"
            factory_bin, python_bin = probar_entrega_a14.crear_entorno_aislado(venv_dir, probar_entrega_a14.construir_artefactos(tmp_path / 'dist')['wheel'])
            res_arneses = probar_entrega_a14.probar_arneses(factory_bin, python_bin)
            self.assertTrue(res_arneses["exitoso"])
            self.assertEqual(res_arneses["verify_installed"]["returncode"], 0)
            self.assertEqual(res_arneses["verify_guide"]["returncode"], 0)



if __name__ == "__main__":
    unittest.main()
