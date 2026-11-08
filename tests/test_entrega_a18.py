"""La entrega 0.1.0a18: escenarios ea1–ea3, con el repositorio, el wheel construido e instalado de verdad y datos armados para el juicio."""
from copy import deepcopy
from pathlib import Path
import shutil
import sys
import tempfile
import tomllib
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import oracle_factory  # noqa: E402
from tools import docs_al_dia, probar_entrega_a18 as pr  # noqa: E402

VERSION = "0.1.0a18"
BUENA = {
    "archivos_del_wheel": ["oracle_factory/__init__.py", pr.SKILL_EN_EL_WHEEL],
    "importacion": {"rc": 0, "archivo": "/entorno/lib/oracle_factory/__init__.py", "version": VERSION, "desde_el_checkout": False, "en_el_entorno": True},
    "cli_version": {"rc": 0, "salida": f"oracle-factory {VERSION}"},
    "ayuda_skill": {"rc": 0, "usage": "usage: oracle-factory skill [-h]"},
    "ayuda_puerta": {"rc": 0, "usage": "usage: oracle-factory puerta [-h]"},
    "ayuda_hooks": {"rc": 0, "usage": "usage: oracle-factory hooks [-h]"},
    "ayuda_verificar": {"rc": 0, "usage": "usage: oracle-factory verificar [-h]"},
    "ayuda_destinos": {"rc": 0, "usage": "usage: oracle-factory destinos [-h]"},
    "ayuda_desplegar": {"rc": 0, "usage": "usage: oracle-factory desplegar [-h]"},
    "skill": {"rc": 0, "empieza_bien": True, "largo": 5000},
    "skill_instalar": {"rc": 0, "stdout": "Skill instalada", "archivo_existe": True, "igual_a_la_del_comando": True},
    "puerta": {"rc": 0, "salida": "Puerta local de salida"},
    "agentes": {"rc": 0, "nombra_la_skill": True, "nombra_el_camino_ligero": True},
    "verificar": {"rc": 0, "esquema": True},
    "destinos": {"rc": 0, "nombres": ["app"]},
    "desplegar_simulado": {"rc": 0, "muestra_el_plan": True},
}
ARTEFACTOS = {"wheel": Path("oracle_factory-0.1.0a18-py3-none-any.whl"), "sdist": Path("oracle_factory-0.1.0a18.tar.gz"),
              "wheel_sha256": "a" * 64, "sdist_sha256": "b" * 64}


class Version(unittest.TestCase):
    # --- ea1: la versión es coherente y declara su estado -------------------------------------------------------------------
    def test_ea1_la_version_es_la_misma_en_los_metadatos_la_cli_y_el_lock(self):
        self.assertEqual(tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))["project"]["version"], VERSION)
        self.assertEqual(oracle_factory.__version__, VERSION)
        [propio] = [p for p in tomllib.loads((ROOT / "uv.lock").read_text(encoding="utf-8"))["package"] if p["name"] == "oracle-factory"]
        self.assertEqual(propio["version"], VERSION)

    def test_ea1_los_textos_y_la_web_estan_al_dia_y_la_a17_y_la_a18_figuran_publicadas(self):
        self.assertEqual(docs_al_dia.problemas(ROOT), [])
        notas = (ROOT / "NOTAS-DE-RELEASE.md").read_text(encoding="utf-8")
        # La a18 pasó de «en preparación» a publicada (publicada-a18): el estado de cada una lo fija test_publicada_a18.
        self.assertTrue(notas.startswith("# Oracle Factory 0.1.0a18\n"))
        self.assertIn("\n# Oracle Factory 0.1.0a17\n", "\n" + notas)
        self.assertIn("**Publicada.** En PyPI como `oracle-factory==0.1.0a17`", notas)
        self.assertIn("**Publicada.** En PyPI como `oracle-factory==0.1.0a18`", notas)
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("Versión publicada en PyPI: `oracle-factory==0.1.0a18`", readme)
        self.assertIn("La versión publicada anterior es [0.1.0a17]", readme)
        for archivo in ("site/desde-cero.html", "site/colaboracion.html", "site/modos.html", "docs/colaboracion.md", "README.md"):
            self.assertIn(VERSION, (ROOT / archivo).read_text(encoding="utf-8"), archivo)

    def test_ea1_un_texto_que_quedo_con_la_version_vieja_se_nombra(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "repo"
            repo.mkdir()
            for nombre in ("pyproject.toml", "README.md", "NOTAS-DE-RELEASE.md"):
                shutil.copy2(ROOT / nombre, repo / nombre)
            shutil.copytree(ROOT / "docs", repo / "docs")
            shutil.copytree(ROOT / "site", repo / "site")
            guia = repo / "site/desde-cero.html"
            guia.write_text(guia.read_text(encoding="utf-8").replace("Usá la 0.1.0a18", "Usá la 0.1.0a15"), encoding="utf-8")
            problemas = docs_al_dia.problemas(repo)
            self.assertTrue(any(p.startswith("site/desde-cero.html:") and "0.1.0a15" in p for p in problemas), problemas)

    def test_ea1_no_queda_ningun_texto_actual_con_la_version_anterior(self):
        for archivo in ("pyproject.toml", "oracle_factory/__init__.py", "site/desde-cero.html", "site/colaboracion.html", "site/modos.html", "docs/colaboracion.md"):
            self.assertNotIn("0.1.0a17", (ROOT / archivo).read_text(encoding="utf-8"), archivo)


class Juicio(unittest.TestCase):
    # --- ea2: el wheel instalado ofrece lo nuevo (el juicio, con datos armados) -----------------------------------------------
    def test_ea2_lo_observado_correcto_no_tiene_problemas(self):
        self.assertEqual(pr.validar(BUENA), [])

    def roto(self, *camino, valor):
        obs = deepcopy(BUENA)
        destino = obs
        for clave in camino[:-1]:
            destino = destino[clave]
        destino[camino[-1]] = valor
        return pr.validar(obs)

    def test_ea2_el_wheel_sin_la_skill_se_nombra(self):
        [p] = self.roto("archivos_del_wheel", valor=["oracle_factory/__init__.py"])
        self.assertIn(pr.SKILL_EN_EL_WHEEL, p)

    def test_ea2_un_comando_instalado_que_falla_se_nombra(self):
        for camino, dicen in ((("skill_instalar", "rc"), "skill --instalar"), (("skill_instalar", "archivo_existe"), "skill --instalar"),
                              (("skill_instalar", "igual_a_la_del_comando"), "skill --instalar"), (("skill", "empieza_bien"), "oracle-factory skill"),
                              (("puerta", "rc"), "puerta"), (("agentes", "nombra_la_skill"), "agentes"), (("agentes", "nombra_el_camino_ligero"), "agentes"),
                              (("destinos", "rc"), "destinos"), (("destinos", "nombres"), "destinos"), (("desplegar_simulado", "rc"), "desplegar"), (("desplegar_simulado", "muestra_el_plan"), "desplegar"), (("verificar", "rc"), "verificar"), (("verificar", "esquema"), "verificar"), (("ayuda_destinos", "rc"), "destinos"), (("ayuda_skill", "rc"), "skill"), (("ayuda_puerta", "usage"), "puerta"), (("ayuda_hooks", "rc"), "hooks")):
            with self.subTest(camino=camino):
                [p] = self.roto(*camino, valor=1 if camino[-1] == "rc" else False if camino[-1] != "usage" else "")
                self.assertIn(dicen, p)

    def test_ea2_la_version_o_el_origen_equivocados_se_nombran(self):
        self.assertTrue(any("0.1.0a17" in p for p in self.roto("importacion", "version", valor="0.1.0a17")))
        self.assertTrue(any("fuera del entorno nuevo" in p for p in self.roto("importacion", "desde_el_checkout", valor=True)))
        self.assertTrue(any("fuera del entorno nuevo" in p for p in self.roto("importacion", "archivo", valor="")))
        self.assertTrue(any("fuera del entorno nuevo" in p for p in self.roto("importacion", "en_el_entorno", valor=False)))  # ni del checkout ni del entorno: de otro lado
        self.assertTrue(any("--version" in p for p in self.roto("cli_version", "salida", valor="oracle-factory 0.1.0a17")))
        self.assertTrue(any("--version" in p for p in self.roto("cli_version", "rc", valor=2)))


@unittest.skipUnless(shutil.which("uv"), "hace falta uv")
class WheelReal(unittest.TestCase):
    """El wheel de verdad: construido con uv build, instalado en un venv nuevo y probado desde otra carpeta; una sola vez para toda la clase."""
    _datos = None

    @classmethod
    def datos(cls):
        if cls._datos is None:
            tmp = tempfile.TemporaryDirectory(prefix="test-entrega-a18-")
            cls.addClassCleanup(tmp.cleanup)
            cls.addClassCleanup(setattr, cls, "_datos", None)
            base = Path(tmp.name)
            artefactos = pr.construir(base / "dist")
            factory, python = pr.instalar(base / "venv", artefactos["wheel"])
            trabajo = base / "trabajo"
            trabajo.mkdir()
            cls._datos = (artefactos, pr.observar(artefactos["wheel"], factory, python, trabajo), (base, factory, python))
        return cls._datos

    def test_ea2_el_wheel_construido_e_instalado_cumple_lo_prometido(self):
        artefactos, obs, _ = self.datos()
        self.assertEqual(pr.validar(obs), [])
        self.assertIn(pr.SKILL_EN_EL_WHEEL, obs["archivos_del_wheel"])
        self.assertEqual(obs["importacion"]["version"], VERSION)
        self.assertFalse(obs["importacion"]["desde_el_checkout"])
        self.assertTrue(obs["importacion"]["en_el_entorno"])
        self.assertTrue(artefactos["wheel"].name.endswith("-py3-none-any.whl"))
        self.assertTrue(artefactos["sdist"].name.endswith(".tar.gz"))

    def test_ea2_si_el_modulo_estuviera_dentro_del_checkout_se_detecta(self):
        artefactos, _, (base, factory, python) = self.datos()
        trabajo = base / "trabajo2"
        trabajo.mkdir()
        obs = pr.observar(artefactos["wheel"], factory, python, trabajo, raiz=base / "venv")  # «el checkout» es el entorno: el módulo está adentro
        self.assertTrue(obs["importacion"]["desde_el_checkout"])
        self.assertTrue(any("fuera del entorno nuevo" in p for p in pr.validar(obs)))

    def test_ea2_si_el_modulo_viene_de_fuera_del_entorno_se_detecta(self):
        artefactos, _, (base, factory, python) = self.datos()
        trabajo = base / "trabajo3"
        trabajo.mkdir()
        otro = base / "otro" / "bin"
        otro.mkdir(parents=True)
        envoltorio = otro / "python"  # corre el python del entorno pero «vive» fuera de él
        envoltorio.write_text(f'#!/bin/sh\nexec "{python}" "$@"\n', encoding="utf-8")
        envoltorio.chmod(0o755)
        obs = pr.observar(artefactos["wheel"], factory, envoltorio, trabajo)
        self.assertEqual(obs["importacion"]["rc"], 0)
        self.assertFalse(obs["importacion"]["en_el_entorno"])
        self.assertTrue(any("fuera del entorno nuevo" in p for p in pr.validar(obs)))

    def test_ea3_main_construye_instala_juzga_y_deja_el_registro(self):
        import json
        with tempfile.TemporaryDirectory() as tmp:
            salida = Path(tmp) / "entrega"
            self.assertEqual(pr.main(["--salida", str(salida)]), 0)
            reg = json.loads((salida / "registro.json").read_text(encoding="utf-8"))
            self.assertEqual(pr.problemas_del_registro(reg), [])
            self.assertTrue(reg["ok"] and reg["publicada"] is False)
            self.assertEqual(reg["hashes"]["wheel"], pr.sha256(salida / "dist" / reg["archivos"]["wheel"]))
            self.assertEqual(reg["hashes"]["sdist"], pr.sha256(salida / "dist" / reg["archivos"]["sdist"]))
            with self.assertRaises(FileExistsError):
                pr.main(["--salida", str(salida)])  # no pisa una entrega anterior

    def test_ea2_la_construccion_exige_una_carpeta_nueva(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(FileExistsError):
                pr.construir(Path(tmp))


class ConFalsos(unittest.TestCase):
    """El probador con herramientas falsas: casos que el wheel real no produce."""

    def test_ea2_una_construccion_con_el_wheel_pero_sin_el_sdist_falla(self):
        from unittest.mock import patch
        with tempfile.TemporaryDirectory() as tmp:
            def uv_build(argv, **kw):
                out = Path(argv[argv.index("--out-dir") + 1])
                (out / f"oracle_factory-{VERSION}-py3-none-any.whl").write_bytes(b"x")  # sin sdist
                return type("R", (), {"returncode": 0, "stdout": "", "stderr": ""})()
            with patch.object(pr, "correr", side_effect=uv_build):
                with self.assertRaises(FileNotFoundError):
                    pr.construir(Path(tmp) / "dist")

    def test_ea2_lo_instalado_que_no_coincide_con_lo_que_muestra_el_comando_se_detecta(self):
        import zipfile
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            falso = base / "oracle-factory"
            falso.write_text('#!/bin/sh\ncase "$*" in\n"skill --instalar") mkdir -p .claude/skills/oracle-factory; echo B > .claude/skills/oracle-factory/SKILL.md; echo ok;;\n'
                             '"skill") printf -- \'---\\nname: oracle-factory\\n---\\nA\\n\';;\n*) echo "usage: oracle-factory $1";;\nesac\n', encoding="utf-8")
            falso.chmod(0o755)
            wheel = base / "w.whl"
            with zipfile.ZipFile(wheel, "w") as z:
                z.writestr(pr.SKILL_EN_EL_WHEEL, "x")
            trabajo = base / "trabajo"
            trabajo.mkdir()
            obs = pr.observar(wheel, falso, Path(sys.executable), trabajo, raiz=base / "otro")
            self.assertTrue(obs["skill_instalar"]["archivo_existe"])
            self.assertFalse(obs["skill_instalar"]["igual_a_la_del_comando"])
            self.assertTrue(any("skill --instalar" in p for p in pr.validar(obs)))

    def test_ea3_main_sale_con_1_si_el_juicio_o_el_registro_tienen_problemas(self):
        from unittest.mock import patch
        import json
        for parche, dice in ((("validar", ["algo mal"]), "juicio"), (("problemas_del_registro", ["falta algo"]), "registro")):
            with self.subTest(dice=dice), tempfile.TemporaryDirectory() as tmp, \
                    patch.object(pr, "construir", return_value=dict(ARTEFACTOS, wheel=Path(tmp) / "w.whl", sdist=Path(tmp) / "s.tar.gz")), \
                    patch.object(pr, "instalar", return_value=(Path("f"), Path("p"))), patch.object(pr, "observar", return_value=BUENA), \
                    patch.object(pr, parche[0], return_value=parche[1]):
                (Path(tmp) / "s").mkdir()  # lo que haría `construir`, que acá es falso
                self.assertEqual(pr.main(["--salida", str(Path(tmp) / "s")]), 1)
                self.assertTrue((Path(tmp) / "s" / "registro.json").is_file())
                guardado = json.loads((Path(tmp) / "s" / "registro.json").read_text())
                self.assertEqual(guardado["publicada"], False)
                self.assertFalse(guardado["ok"])  # el registro no se contradice: con problemas, ok es falso
                self.assertTrue(guardado["problemas"])


class Registro(unittest.TestCase):
    # --- ea3: el registro de la entrega -------------------------------------------------------------------------------------------
    def test_ea3_un_registro_completo_tiene_hashes_versiones_observaciones_y_limites_y_no_dice_publicada(self):
        reg = pr.registro(ARTEFACTOS, BUENA, [])
        self.assertEqual(pr.problemas_del_registro(reg), [])
        self.assertEqual((reg["hashes"], reg["publicada"], reg["ok"]), ({"wheel": "a" * 64, "sdist": "b" * 64}, False, True))
        self.assertTrue(reg["limites"] and reg["observaciones"] and reg["versiones"]["python"] and reg["versiones"]["uv"])
        self.assertTrue(any("No publica nada" in l for l in reg["limites"]))
        self.assertTrue(any("no es reproducible" in l for l in reg["limites"]))
        self.assertNotIn("archivos_del_wheel", reg["observaciones"])  # sólo la cuenta, no la lista entera

    def test_ea3_a_un_registro_incompleto_la_validacion_le_dice_que_falta(self):
        reg = pr.registro(ARTEFACTOS, BUENA, [])
        for quitar, dice in (("limites", "límites"), ("observaciones", "observaciones")):
            roto = deepcopy(reg)
            roto[quitar] = []
            self.assertTrue(any(dice in p for p in pr.problemas_del_registro(roto)), quitar)
        roto = deepcopy(reg)
        roto["hashes"]["wheel"] = "corto"
        self.assertTrue(any("hash sha256 del wheel" in p for p in pr.problemas_del_registro(roto)))
        roto = deepcopy(reg)
        roto["hashes"]["sdist"] = None
        self.assertTrue(any("hash sha256 del sdist" in p for p in pr.problemas_del_registro(roto)))
        roto = deepcopy(reg)
        roto["versiones"]["uv"] = ""
        self.assertTrue(any("versiones" in p for p in pr.problemas_del_registro(roto)))
        roto = deepcopy(reg)
        roto["publicada"] = True
        self.assertTrue(any("publicada" in p for p in pr.problemas_del_registro(roto)))

    def test_ea3_un_juicio_con_problemas_deja_el_registro_en_rojo_y_con_el_detalle(self):
        obs = deepcopy(BUENA)
        obs["archivos_del_wheel"] = []
        problemas = pr.validar(obs)
        reg = pr.registro(ARTEFACTOS, obs, problemas)
        self.assertFalse(reg["ok"])
        self.assertEqual(reg["problemas"], problemas)
        self.assertEqual(pr.problemas_del_registro(reg), [])  # un registro en rojo es un registro válido: dice la verdad


if __name__ == "__main__":
    unittest.main()
