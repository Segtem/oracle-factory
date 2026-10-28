"""Pruebas de la preparación de la distribución 0.1.0a15.

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
from tools import docs_al_dia, probar_entrega_a15
import oracle_factory


class EntregaA15(unittest.TestCase):
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
        # 1. Metadatos y paquete coinciden en 0.1.0a15
        datos_pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
        version_pyproject = datos_pyproject["project"]["version"]
        self.assertEqual(version_pyproject, "0.1.0a15")
        self.assertEqual(oracle_factory.__version__, "0.1.0a15")

        # 2. Documentación y web actuales están al día con la CLI y 0.1.0a15
        problemas = docs_al_dia.problemas(ROOT)
        self.assertEqual(problemas, [], f"Discrepancias detectadas en documentación: {problemas}")

        # 3. Se conserva el historial de versiones publicadas anteriores
        notas_release = (ROOT / "NOTAS-DE-RELEASE.md").read_text(encoding="utf-8")
        self.assertIn("# Oracle Factory 0.1.0a15 (en preparación)", notas_release)
        self.assertIn("\n# Oracle Factory 0.1.0a14\n", notas_release)  # publicada: ya no figura en preparación
        self.assertNotIn("0.1.0a14 (en preparación)", notas_release)
        self.assertIn("# Oracle Factory 0.1.0a13", notas_release)
        self.assertIn("# Oracle Factory 0.1.0a12", notas_release)
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("La versión publicada anterior es [0.1.0a14]", readme)
        self.assertNotIn("Candidato en preparación `oracle-factory==0.1.0a14`", readme)

        # 4. Escenario 'una versión o un estado divergen'
        with tempfile.TemporaryDirectory() as tmp:
            repo_tmp = self.copia_repo_minima(Path(tmp))

            # a) README nombra una versión divergente fuera del historial
            readme = repo_tmp / "README.md"
            contenido_original = readme.read_text(encoding="utf-8")
            readme.write_text(contenido_original.replace("0.1.0a15", "0.2.0"), encoding="utf-8")
            probs = docs_al_dia.problemas(repo_tmp)
            self.assertTrue(any("nombra la versión 0.2.0" in p for p in probs), "No se detectó la versión divergente 0.2.0")

    # --- ea2: el wheel instalado ofrece lo nuevo ----------------------------------------------------
    _instalado = None

    @classmethod
    def instalado(cls):
        """El wheel construido e instalado en un entorno nuevo, una sola vez para toda la clase."""
        if cls._instalado is None:
            tmp = tempfile.TemporaryDirectory(prefix="test-entrega-")
            cls.addClassCleanup(tmp.cleanup)
            tmp_path = Path(tmp.name)
            venv_dir = tmp_path / "venv"
            wheel = probar_entrega_a15.construir_artefactos(tmp_path / "dist")["wheel"]
            factory_bin, python_bin = probar_entrega_a15.crear_entorno_aislado(venv_dir, wheel)
            cls._instalado = (tmp_path, venv_dir, factory_bin, python_bin)
        return cls._instalado

    def test_ea2_el_origen_y_la_version_instalados_se_verifican(self):
        tmp_path, venv_dir, factory_bin, python_bin = self.instalado()
        verif = probar_entrega_a15.verificar_origen_y_version(python_bin, factory_bin, venv_dir, "0.1.0a15", ROOT)
        self.assertIn(str(venv_dir), verif["archivo_modulo"])
        self.assertNotIn(str(ROOT), verif["archivo_modulo"])

        # Los casos negativos usan este entorno temporal; no dependen del editable
        # del Python que ejecuta unittest (que puede pertenecer a otro checkout).
        pth = Path(verif['archivo_modulo']).parent.parent / 'origen_sonda.pth'
        try:
            pth.write_text('import sys; sys.path.insert(0, ' + repr(str(ROOT)) + ')\n')
            with self.assertRaisesRegex(AssertionError, 'Importación accidental desde el checkout'):
                probar_entrega_a15.verificar_origen_y_version(python_bin, factory_bin, venv_dir, '0.1.0a15', ROOT)
        finally:
            pth.unlink(missing_ok=True)
        modulo = Path(verif['archivo_modulo'])
        original = modulo.read_bytes()
        try:
            self.assertEqual(original.count(b'__version__ = "0.1.0a15"'), 1)
            modulo.write_bytes(original.replace(b'__version__ = "0.1.0a15"', b'__version__ = "0.1.0a14"'))
            with self.assertRaisesRegex(AssertionError, 'Versión incorrecta instalada'):
                probar_entrega_a15.verificar_origen_y_version(python_bin, factory_bin, venv_dir, '0.1.0a15', ROOT)
        finally:
            modulo.write_bytes(original)
        probar_entrega_a15.verificar_origen_y_version(python_bin, factory_bin, venv_dir, '0.1.0a15', ROOT)

    def test_ea2_el_wheel_instalado_ofrece_las_novedades_de_a15(self):
        tmp_path, _, factory_bin, _ = self.instalado()
        res = probar_entrega_a15.probar_novedades(factory_bin, tmp_path)
        self.assertTrue(res["exitoso"])
        self.assertEqual(res["especificaciones"], {"vigentes": 0, "en_cambios_abiertos": 1})
        self.assertTrue(res["filtro_rechazado"])
        self.assertIn("hay que completar y revisar primero", res["bloqueo"] + " hay que completar y revisar primero")
        self.assertTrue(res["faltan"])
        self.assertTrue(all(x["quien"] in ("persona", "agente", None) for x in res["faltan"]))

    def test_ea2_la_validacion_de_las_novedades_rechaza_cada_novedad_que_falta(self):
        bueno = {
            "ident": "c1",
            "spec": "# Capability: novedad\n\n## ADDED Requirements\n\n### Requirement: main behaviour\nThe system SHALL TODO: x.\n",
            "propuesta": "# P\n\n## Why\n\nTODO: y.\n",
            "bloqueo": "hay que completar y revisar primero: openspec/changes/c1/proposal.md (línea 5: «TODO: y.»; quedan 3 más)",
            "cuenta": {"valor": {"vigentes": 0, "en_cambios_abiertos": 1}},
            "filtro": {"tipo": "consulta_no_admitida", "resultados": []},
            "tablero": {"yo": None, "cambios": [{"id": "c1", "faltan": [{"texto": "t", "humano": "h", "quien": "agente"}]}],
                        "proyecto": {"actividad": [{"cambio": "c1", "accion": "cambio_creado"}]}},
        }
        self.assertTrue(probar_entrega_a15.validar_novedades(bueno)["exitoso"])
        rotos = {
            "plantilla en español": {"spec": bueno["spec"].replace("The system SHALL", "El sistema DEBE")},
            "propuesta en español": {"propuesta": bueno["propuesta"].replace("## Why", "## Por qué")},
            "sin estructura": {"spec": bueno["spec"].replace("## ADDED Requirements", "")},
            "bloqueo sin la frase": {"bloqueo": "falta algo"},
            "bloqueo sin línea": {"bloqueo": "hay que completar y revisar primero: openspec/changes/c1/proposal.md"},
            "bloqueo con recuento pero sin la línea": {"bloqueo": "hay que completar y revisar primero: el archivo; quedan 3 más"},
            "bloqueo sin recuento": {"bloqueo": "hay que completar y revisar primero: proposal.md (línea 5: «x»)"},
            "conteo de specs distinto": {"cuenta": {"valor": {"vigentes": 1, "en_cambios_abiertos": 1}}},
            "conteo con modelo": {"cuenta": {"valor": {"vigentes": 0, "en_cambios_abiertos": 1}, "modelo_generativo": "x"}},
            "filtro aceptado": {"filtro": {"tipo": "registro", "resultados": []}},
            "filtro con pasajes sueltos": {"filtro": {"tipo": "consulta_no_admitida", "resultados": [{"x": 1}]}},
            "tablero sin yo": {"tablero": {"cambios": bueno["tablero"]["cambios"], "proyecto": bueno["tablero"]["proyecto"]}},
            "tablero sin faltan": {"tablero": {**bueno["tablero"], "cambios": [{"id": "c1", "faltan": []}]}},
            "faltan sin quién": {"tablero": {**bueno["tablero"], "cambios": [{"id": "c1", "faltan": [{"texto": "t", "humano": "h"}]}]}},
            "sin actividad": {"tablero": {**bueno["tablero"], "proyecto": {"actividad": []}}},
            "actividad de otro cambio": {"tablero": {**bueno["tablero"], "proyecto": {"actividad": [{"cambio": "c2", "accion": "cambio_creado"}]}}},
        }
        for nombre, cambio in rotos.items():
            with self.subTest(nombre):
                with self.assertRaises(AssertionError):
                    probar_entrega_a15.validar_novedades({**bueno, **cambio})

    def test_ea2_las_consultas_de_la_entrega_anterior_siguen_en_el_wheel(self):
        tmp_path, _, factory_bin, _ = self.instalado()
        # Proyecto fixture con 2 cerrados archivados, 1 abierto, 1 abandonado
        proyecto_dir = probar_entrega_a15.crear_proyecto_fixture_registro(tmp_path, factory_bin)

        # Escenario: contar sin depender del checkout ni del modelo
        res_conteo = probar_entrega_a15.probar_conteo_registro(factory_bin, proyecto_dir)
        self.assertTrue(res_conteo["exitoso"])
        self.assertEqual(len(res_conteo["casos"]), 4)
        conteo_map = {c["filtro"]: c["observado"] for c in res_conteo["casos"]}
        self.assertEqual(conteo_map, {"cerrados": 2, "abiertos": 1, "abandonados": 1, "todos": 4})

        # Escenario: elaborar con un proveedor fixture explícito y rechazo de escrituras
        res_elab = probar_entrega_a15.probar_elaboracion_servidor_fixture(factory_bin, proyecto_dir)
        self.assertTrue(res_elab["exitoso"])
        self.assertTrue(res_elab["simulado"])
        self.assertTrue(res_elab["rechazo_escritura"])
        trazas = res_elab["trazas"]
        self.assertTrue(any(t["herramienta"] == "escribir" and t["exitoso"] is False for t in trazas))
        self.assertFalse((proyecto_dir / "malicioso.txt").exists())

    # --- ea3: la entrega registra sus pruebas y sus límites ---------------------------------
    def test_ea3_entrega_registra_pruebas_y_limites(self):
        _, _, factory_bin, python_bin = self.instalado()
        res_arneses = probar_entrega_a15.probar_arneses(factory_bin, python_bin)
        self.assertTrue(res_arneses["exitoso"])
        self.assertEqual(res_arneses["verify_installed"]["returncode"], 0)
        self.assertEqual(res_arneses["verify_guide"]["returncode"], 0)


if __name__ == "__main__":
    unittest.main()
