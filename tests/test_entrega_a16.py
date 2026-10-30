"""Pruebas de la preparación de la distribución 0.1.0a16.

Cubre los contratos de distribucion:
- ea1: la versión de entrega es coherente y declara su estado (metadatos, docs, web y detección de divergencias)
- ea2: el wheel instalado ofrece lo nuevo (origen venv, versión, las novedades de esta entrega y las consultas de la anterior)
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
from tools import docs_al_dia, probar_entrega_a16
import oracle_factory


class EntregaA16(unittest.TestCase):
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
        # 1. Metadatos y paquete coinciden en 0.1.0a16
        datos_pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
        version_pyproject = datos_pyproject["project"]["version"]
        self.assertEqual(version_pyproject, "0.1.0a16")
        self.assertEqual(oracle_factory.__version__, "0.1.0a16")

        # 2. Documentación y web actuales están al día con la CLI y 0.1.0a16
        problemas = docs_al_dia.problemas(ROOT)
        self.assertEqual(problemas, [], f"Discrepancias detectadas en documentación: {problemas}")

        # 3. La 0.1.0a16 figura en preparación, la 0.1.0a15 publicada, y se conserva el historial
        notas_release = (ROOT / "NOTAS-DE-RELEASE.md").read_text(encoding="utf-8")
        self.assertTrue(notas_release.startswith("# Oracle Factory 0.1.0a16 (en preparación)\n"))
        self.assertIn("\n# Oracle Factory 0.1.0a15\n", "\n" + notas_release)
        self.assertNotIn("0.1.0a15 (en preparación)", notas_release)
        self.assertIn("**Publicada.** En PyPI como `oracle-factory==0.1.0a15`", notas_release)
        self.assertNotIn("**Publicada.** En PyPI como `oracle-factory==0.1.0a16`", notas_release)
        self.assertIn("\n# Oracle Factory 0.1.0a14\n", "\n" + notas_release)
        self.assertIn("# Oracle Factory 0.1.0a13", notas_release)
        self.assertIn("# Oracle Factory 0.1.0a12", notas_release)
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("La versión publicada anterior es [0.1.0a15]", readme)
        self.assertIn("Candidato en preparación `oracle-factory==0.1.0a16`", readme)
        self.assertNotRegex(readme + (ROOT / "site/index.html").read_text(encoding="utf-8"),
                            r"(?i)0\.1\.0a16[^\n]{0,40}(ya está|está)\s+publicada|Versión publicada en PyPI: `oracle-factory==0\.1\.0a16`")
        uvlock = tomllib.loads((ROOT / "uv.lock").read_text(encoding="utf-8"))
        [propio] = [p for p in uvlock["package"] if p["name"] == "oracle-factory"]
        self.assertEqual(propio["version"], "0.1.0a16")  # el lock viaja con la versión de la entrega

        # 4. Escenario 'una versión o un estado divergen'
        with tempfile.TemporaryDirectory() as tmp:
            repo_tmp = self.copia_repo_minima(Path(tmp))
            readme = repo_tmp / "README.md"
            notas = repo_tmp / "NOTAS-DE-RELEASE.md"
            contenido_original = readme.read_text(encoding="utf-8")
            notas_originales = notas.read_text(encoding="utf-8")
            publicada = notas_originales.replace("# Oracle Factory 0.1.0a16 (en preparación)\n", "# Oracle Factory 0.1.0a16\n", 1)
            self.assertNotEqual(publicada, notas_originales)

            # a) README nombra una versión divergente fuera del historial
            readme.write_text(contenido_original.replace("0.1.0a16", "0.2.0"), encoding="utf-8")
            probs = docs_al_dia.problemas(repo_tmp)
            self.assertTrue(any("nombra la versión 0.2.0" in p for p in probs), "No se detectó la versión divergente 0.2.0")

            # b) mientras las notas dicen «en preparación», un texto que afirma la publicación se detecta
            readme.write_text(contenido_original + "\nLa 0.1.0a16 ya está publicada en PyPI.\n", encoding="utf-8")
            probs = docs_al_dia.problemas(repo_tmp)
            self.assertTrue(any("afirma que la versión 0.1.0a16 está publicada" in p for p in probs), probs)
            for frase in ("Ya está en PyPI la 0.1.0a16.", "La versión 0.1.0a16, publicada en GitHub.", "0.1.0a16 disponible en PyPI"):
                readme.write_text(contenido_original + f"\n{frase}\n", encoding="utf-8")
                self.assertTrue(any("afirma que la versión" in p for p in docs_al_dia.problemas(repo_tmp)), frase)

            # c) los textos reales de la preparación no son una divergencia mientras las notas la tienen en preparación...
            readme.write_text(contenido_original, encoding="utf-8")
            self.assertEqual(docs_al_dia.problemas(repo_tmp), [])
            # ...pero con las notas ya publicadas esos mismos textos se señalan como de candidata, en el README y en la guía
            notas.write_text(publicada, encoding="utf-8")
            probs = [p for p in docs_al_dia.problemas(repo_tmp) if "describe la versión 0.1.0a16 como candidata o en preparación" in p]
            self.assertTrue(any(p.startswith("README.md:") for p in probs) and any(p.startswith("site/desde-cero.html:") for p in probs), probs)

            # d) con las notas publicadas y el README en su forma publicada, la afirmación de publicación no es un problema...
            preparacion = ("Candidato en preparación `oracle-factory==0.1.0a16`, y su wheel candidato verificable antes de la publicación remota.\n"
                           "Los comandos de instalación desde PyPI que siguen se podrán usar cuando se publique esta versión. Con `uv`:")
            self.assertIn(preparacion, contenido_original)
            publicado = contenido_original.replace(preparacion, "Versión publicada en PyPI: `oracle-factory==0.1.0a16`. Con `uv`:")
            readme.write_text(publicado + "\nLa 0.1.0a16 ya está publicada en PyPI.\n", encoding="utf-8")
            self.assertEqual([p for p in docs_al_dia.problemas(repo_tmp) if p.startswith("README.md:")], [])  # el README publicado no tiene problemas
            # e) ...pero un texto que la sigue llamando candidata o en preparación se detecta
            for frase in ("Candidato en preparación `oracle-factory==0.1.0a16`, y su wheel.", "La 0.1.0a16 (en preparación) trae la procedencia.",
                          "Los comandos de instalación se podrán usar cuando se publique esta versión.", "Versión 0.1.0a16 y estado de preparación.",
                          "PREPARACIÓN 0.1.0a16", "Esta guía describe el candidato Factory 0.1.0a16."):
                readme.write_text(publicado + f"\n{frase}\n", encoding="utf-8")  # sobre un README ya limpio: cada frase se detecta sola
                self.assertTrue(any(p.startswith("README.md:") and "describe la versión 0.1.0a16 como candidata o en preparación" in p
                                    for p in docs_al_dia.problemas(repo_tmp)), frase)
            # f) y mientras las notas la tienen en preparación, ese mismo texto no es una divergencia
            notas.write_text(notas_originales, encoding="utf-8")
            readme.write_text(contenido_original + "\nCandidato en preparación `oracle-factory==0.1.0a16`.\n", encoding="utf-8")
            self.assertFalse(any("describe la versión" in p for p in docs_al_dia.problemas(repo_tmp)))

    # --- ea2: el wheel instalado ofrece lo nuevo ----------------------------------------------------
    _instalado = None

    @classmethod
    def instalado(cls):
        """El wheel construido e instalado en un entorno nuevo, una sola vez para toda la clase."""
        if cls._instalado is None:
            tmp = tempfile.TemporaryDirectory(prefix="test-entrega-")
            cls.addClassCleanup(tmp.cleanup)
            cls.addClassCleanup(setattr, cls, "_instalado", None)  # tras la limpieza, quien lo pida de nuevo lo reconstruye
            tmp_path = Path(tmp.name)
            venv_dir = tmp_path / "venv"
            wheel = probar_entrega_a16.construir_artefactos(tmp_path / "dist")["wheel"]
            factory_bin, python_bin = probar_entrega_a16.crear_entorno_aislado(venv_dir, wheel)
            cls._instalado = (tmp_path, venv_dir, factory_bin, python_bin)
        return cls._instalado

    def test_ea2_tras_la_limpieza_el_entorno_instalado_se_reconstruye(self):
        """La trazabilidad vuelve a correr los casos en el mismo intérprete, después de la limpieza de la clase."""
        cls = type(self)
        carpeta = cls.instalado()[0]
        cls.doClassCleanups()
        self.assertFalse(carpeta.exists())
        self.assertIsNone(cls._instalado)
        nueva = cls.instalado()[0]
        self.assertTrue(nueva.exists())
        self.assertNotEqual(nueva, carpeta)

    def test_ea2_el_origen_y_la_version_instalados_se_verifican(self):
        tmp_path, venv_dir, factory_bin, python_bin = self.instalado()
        verif = probar_entrega_a16.verificar_origen_y_version(python_bin, factory_bin, venv_dir, "0.1.0a16", ROOT)
        self.assertIn(str(venv_dir), verif["archivo_modulo"])
        self.assertNotIn(str(ROOT), verif["archivo_modulo"])

        # Los casos negativos usan este entorno temporal; no dependen del editable
        # del Python que ejecuta unittest (que puede pertenecer a otro checkout).
        pth = Path(verif['archivo_modulo']).parent.parent / 'origen_sonda.pth'
        try:
            pth.write_text('import sys; sys.path.insert(0, ' + repr(str(ROOT)) + ')\n')
            with self.assertRaisesRegex(AssertionError, 'Importación accidental desde el checkout'):
                probar_entrega_a16.verificar_origen_y_version(python_bin, factory_bin, venv_dir, '0.1.0a16', ROOT)
        finally:
            pth.unlink(missing_ok=True)
        modulo = Path(verif['archivo_modulo'])
        original = modulo.read_bytes()
        try:
            self.assertEqual(original.count(b'__version__ = "0.1.0a16"'), 1)
            modulo.write_bytes(original.replace(b'__version__ = "0.1.0a16"', b'__version__ = "0.1.0a15"'))
            with self.assertRaisesRegex(AssertionError, 'Versión incorrecta instalada'):
                probar_entrega_a16.verificar_origen_y_version(python_bin, factory_bin, venv_dir, '0.1.0a16', ROOT)
        finally:
            modulo.write_bytes(original)
        probar_entrega_a16.verificar_origen_y_version(python_bin, factory_bin, venv_dir, '0.1.0a16', ROOT)

    def test_ea2_el_wheel_instalado_ofrece_las_novedades_de_a16(self):
        tmp_path, _, factory_bin, _ = self.instalado()
        res = probar_entrega_a16.probar_novedades(factory_bin, tmp_path)
        self.assertTrue(res["exitoso"])
        self.assertIn("alfa 1.2.3", res["componentes"])
        self.assertTrue(res["inventario_guardado"].endswith("procedencia/cyclonedx.json"))
        self.assertTrue(res["sin_red_rechazada"])
        self.assertEqual(res["aviso"], "GHSA-prueba-0001")
        self.assertEqual(res["consultas"], [{"package": {"name": "alfa", "ecosystem": "PyPI"}, "version": "1.2.3"}])

    def test_ea2_la_validacion_de_las_novedades_rechaza_cada_novedad_que_falta(self):
        bueno = {
            "ident": "c1",
            "inventario": {"bomFormat": "CycloneDX", "components": [{"name": "alfa", "version": "1.2.3"}]},
            "guardados": [".factory/cambios/c1/candidatos/abc/procedencia/cyclonedx.json"],
            "buscar": "alfa==1.2.3 figura en 1 inventario(s):\n  - c1 · candidato abc · alfa 1.2.3",
            "auditar": "Afectados:\n  - GHSA-prueba-0001: alfa 1.2.3 (corregida en: 1.2.4) · c1 · candidato abc",
            "sin_red": "--consultar-osv se conecta a OSV.dev: autorizalo con --red",
            "pedidos_sin_red": 0,
            "con_red": "Consulta a OSV\nAfectados:\n  - GHSA-prueba-0001: alfa 1.2.3 · c1 · candidato abc",
            "avisos_guardados": [{"id": "GHSA-prueba-0001"}],
            "consultas": [{"package": {"name": "alfa", "ecosystem": "PyPI"}, "version": "1.2.3"}],
        }
        self.assertTrue(probar_entrega_a16.validar_novedades(bueno)["exitoso"])
        rotos = {
            "no es CycloneDX": {"inventario": {"bomFormat": "otro", "components": bueno["inventario"]["components"]}},
            "sin la dependencia": {"inventario": {"bomFormat": "CycloneDX", "components": []}},
            "sin guardar en el candidato": {"guardados": []},
            "guardado en otro cambio": {"guardados": [".factory/cambios/c2/candidatos/abc/procedencia/cyclonedx.json"]},
            "guardado dos veces": {"guardados": bueno["guardados"] * 2},
            "búsqueda sin el cambio": {"buscar": "alfa figura en 1 inventario(s)"},
            "búsqueda sin la dependencia": {"buscar": "c1"},
            "auditoría sin el aviso": {"auditar": "Afectados:\n  - c1"},
            "auditoría sin el cambio": {"auditar": "Afectados:\n  - GHSA-prueba-0001"},
            "auditoría sin afectados": {"auditar": "GHSA-prueba-0001 c1"},
            "consulta sin bandera que no nombra la bandera": {"sin_red": "falló"},
            "consulta sin bandera que se conectó": {"pedidos_sin_red": 1},
            "consulta con red sin el aviso": {"con_red": "Afectados: c1"},
            "consulta con red sin el cambio": {"con_red": "Afectados: GHSA-prueba-0001"},
            "consulta con red sin afectados": {"con_red": "GHSA-prueba-0001 c1"},
            "avisos guardados distintos": {"avisos_guardados": [{"id": "otro"}]},
            "sin avisos guardados": {"avisos_guardados": []},
            "sale algo más que nombre y versión": {"consultas": [{"package": {"name": "alfa", "ecosystem": "PyPI"}, "version": "1.2.3", "repo": "x"}]},
            "se consulta dos veces": {"consultas": bueno["consultas"] * 2},
            "otro ecosistema": {"consultas": [{"package": {"name": "alfa", "ecosystem": "npm"}, "version": "1.2.3"}]},
        }
        for nombre, cambio in rotos.items():
            with self.subTest(nombre):
                with self.assertRaises(AssertionError):
                    probar_entrega_a16.validar_novedades({**bueno, **cambio})

    def test_ea2_las_consultas_de_la_entrega_anterior_siguen_en_el_wheel(self):
        tmp_path, _, factory_bin, _ = self.instalado()
        # Proyecto fixture con 2 cerrados archivados, 1 abierto, 1 abandonado
        proyecto_dir = probar_entrega_a16.crear_proyecto_fixture_registro(tmp_path, factory_bin)

        # Escenario: contar sin depender del checkout ni del modelo
        res_conteo = probar_entrega_a16.probar_conteo_registro(factory_bin, proyecto_dir)
        self.assertTrue(res_conteo["exitoso"])
        self.assertEqual(len(res_conteo["casos"]), 4)
        conteo_map = {c["filtro"]: c["observado"] for c in res_conteo["casos"]}
        self.assertEqual(conteo_map, {"cerrados": 2, "abiertos": 1, "abandonados": 1, "todos": 4})

        # Escenario: elaborar con un proveedor fixture explícito y rechazo de escrituras
        res_elab = probar_entrega_a16.probar_elaboracion_servidor_fixture(factory_bin, proyecto_dir)
        self.assertTrue(res_elab["exitoso"])
        self.assertTrue(res_elab["simulado"])
        self.assertTrue(res_elab["rechazo_escritura"])
        trazas = res_elab["trazas"]
        self.assertTrue(any(t["herramienta"] == "escribir" and t["exitoso"] is False for t in trazas))
        self.assertFalse((proyecto_dir / "malicioso.txt").exists())

    # --- ea3: la entrega registra sus pruebas y sus límites ---------------------------------
    def test_ea3_entrega_registra_pruebas_y_limites(self):
        _, _, factory_bin, python_bin = self.instalado()
        res_arneses = probar_entrega_a16.probar_arneses(factory_bin, python_bin)
        self.assertTrue(res_arneses["exitoso"])
        self.assertEqual(res_arneses["verify_installed"]["returncode"], 0)
        self.assertEqual(res_arneses["verify_guide"]["returncode"], 0)

    def test_ea3_un_arnes_fallido_no_se_registra_como_exitoso(self):
        from types import SimpleNamespace
        from unittest import mock
        _, _, factory_bin, python_bin = self.instalado()
        for fallido in ("verify_installed.py", "verify_guide.py"):
            def ejecutar(argv, **kwargs):
                roto = any(str(a).endswith(fallido) for a in argv)
                return SimpleNamespace(returncode=1 if roto else 0, stdout="", stderr="falla simulada")
            with self.subTest(fallido=fallido), mock.patch.object(probar_entrega_a16, "ejecutar", ejecutar):
                with self.assertRaisesRegex(AssertionError, f"{fallido} falló"):
                    probar_entrega_a16.probar_arneses(factory_bin, python_bin)


if __name__ == "__main__":
    unittest.main()
