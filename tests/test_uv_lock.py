"""El uv.lock de Factory viaja con el repositorio, coincide con su pyproject.toml y no da falsas alarmas: escenarios ul1–ul3."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import test_archivo as _archivo  # noqa: E402
import test_procedencia as _procedencia  # noqa: E402
from oracle_factory import procedencia  # noqa: E402

SOURCE = Path(__file__).resolve().parents[1]


def git(*args):
    return subprocess.run(["git", "-C", str(SOURCE), *args], capture_output=True, text=True, stdin=subprocess.DEVNULL)


def copia(destino: Path, reemplazos=()) -> Path:
    """El pyproject.toml y el uv.lock de Factory en una carpeta temporal, con cambios de texto en el pyproject.toml."""
    destino.mkdir(parents=True, exist_ok=True)
    texto = (SOURCE / "pyproject.toml").read_text(encoding="utf-8")
    for viejo, nuevo in reemplazos:
        assert viejo in texto, viejo
        texto = texto.replace(viejo, nuevo, 1)
    (destino / "pyproject.toml").write_text(texto, encoding="utf-8")
    shutil.copy2(SOURCE / "uv.lock", destino / "uv.lock")
    return destino


class UvLock(unittest.TestCase):
    # --- ul1: el lock viaja con el repositorio -----------------------------------------------------------------------------
    def test_ul1_git_no_ignora_el_lock_y_lo_rastrea(self):
        self.assertEqual(git("check-ignore", "uv.lock").returncode, 1)  # 1: no lo ignora
        rastreados = git("ls-files", "--cached", "uv.lock").stdout.split()
        self.assertEqual(rastreados, ["uv.lock"])
        self.assertNotIn("uv.lock", (SOURCE / ".gitignore").read_text(encoding="utf-8").splitlines())

    def test_ul1_cada_dependencia_del_lock_trae_origen_y_hashes(self):
        lock = procedencia.leer_lock(SOURCE)
        self.assertEqual(lock["proyecto"]["nombre"], "oracle-factory")
        paquetes = lock["paquetes"]
        self.assertGreaterEqual(len(paquetes), 8)
        for nombre in ("oracle-metalenguaje", "oracle-task", "oracle-clue"):
            self.assertIn(nombre, paquetes)
        for nombre, entradas in paquetes.items():
            for e in entradas:
                self.assertTrue(e["origen"].startswith("https://"), (nombre, e["origen"]))
                self.assertTrue(e["hashes"], nombre)
                for h in e["hashes"]:
                    self.assertRegex(h, r"^[0-9a-f]{64}$", nombre)

    def test_ul1_todos_los_hashes_del_lock_son_sha256(self):
        import tomllib
        datos = tomllib.loads((SOURCE / "uv.lock").read_text(encoding="utf-8"))
        hashes = []
        for p in datos["package"]:
            hashes += [p["sdist"]["hash"]] if "sdist" in p else []
            hashes += [w["hash"] for w in p.get("wheels", [])]
        self.assertGreater(len(hashes), 100)
        self.assertEqual([h for h in hashes if not h.startswith("sha256:")], [])  # el lector de procedencia ignora cualquier otro

    def test_ul1_el_lock_no_incluye_al_proyecto_como_componente(self):
        bom, _, _ = procedencia.inventario(SOURCE, None)
        self.assertNotIn("oracle-factory", [c["name"] for c in bom["components"]])

    # --- ul2: el lock coincide con el pyproject ------------------------------------------------------------------------------
    def test_ul2_el_lock_versionado_coincide_con_el_pyproject(self):
        bom, diferencias, confiable = procedencia.inventario(SOURCE, None)
        self.assertEqual((diferencias, confiable), ([], True))
        self.assertEqual(bom["metadata"]["component"]["name"], "oracle-factory")

    def test_ul2_las_dependencias_directas_de_factory_estan_fijadas_en_el_lock(self):
        _, directas, _ = procedencia.requisitos(SOURCE)
        lock = procedencia.leer_lock(SOURCE)["paquetes"]
        self.assertEqual(sorted(directas), ["oracle-clue", "oracle-metalenguaje", "oracle-task"])
        for n, (nombre, especificacion) in directas.items():
            self.assertEqual(especificacion, "==" + lock[n][0]["version"], nombre)

    def test_ul2_la_version_del_proyecto_sin_regenerar_el_lock_se_detecta(self):
        with tempfile.TemporaryDirectory() as tmp:
            actual = procedencia.requisitos(SOURCE)[0]["version"]
            raiz = copia(Path(tmp), [(f'version = "{actual}"', 'version = "9.9.9"')])
            _, diferencias, confiable = procedencia.inventario(raiz, None)
        self.assertFalse(confiable)
        self.assertEqual(diferencias, [f"el lock es de la versión {actual} del proyecto y pyproject.toml dice 9.9.9"])

    def test_ul2_una_dependencia_cambiada_sin_regenerar_el_lock_se_detecta(self):
        with tempfile.TemporaryDirectory() as tmp:
            raiz = copia(Path(tmp), [("oracle-metalenguaje==0.39.0", "oracle-metalenguaje==0.40.0")])
            _, diferencias, confiable = procedencia.inventario(raiz, None)
        self.assertFalse(confiable)
        self.assertEqual(diferencias, ["oracle-metalenguaje: pyproject.toml exige ==0.40.0 y el lock fija 0.39.0"])

    def test_ul2_una_dependencia_nueva_sin_regenerar_el_lock_se_detecta(self):
        with tempfile.TemporaryDirectory() as tmp:
            raiz = copia(Path(tmp), [('"oracle-clue==0.1.0a2"]', '"oracle-clue==0.1.0a2", "requests==2.31"]')])
            _, diferencias, confiable = procedencia.inventario(raiz, None)
        self.assertFalse(confiable)
        self.assertEqual(diferencias, ["requests: lo exige pyproject.toml (==2.31) y no está en el lock"])


class UvLockEntorno(unittest.TestCase):
    """ul3: lo que el lock pide y el entorno no instala, con un «python» de mentira."""
    python = None
    setUp, escribe, git, salida = (_archivo.Archivo.setUp, _archivo.Archivo.escribe, _archivo.Archivo.git, _archivo.Archivo.salida)
    proyecto, correr, bom = _procedencia.Procedencia.proyecto, _procedencia.Procedencia.correr, _procedencia.Procedencia.bom
    componente, prop = _procedencia.Procedencia.componente, _procedencia.Procedencia.prop
    confiable, diferencias = _procedencia.Procedencia.confiable, _procedencia.Procedencia.diferencias

    # --- ul3: un paquete que el entorno no instala no vuelve no confiable el inventario ------------------------------------
    def test_ul3_un_paquete_del_lock_que_el_entorno_no_instala_se_marca_y_el_inventario_sigue_confiable(self):
        self.proyecto(instalado={"alfa": "1.2.3"})
        bom = self.bom()
        self.assertEqual((self.confiable(bom), self.diferencias(bom)), ("true", []))
        self.assertEqual(self.prop(self.componente(bom, "beta"), "factory:instalado"), "false")

    def test_ul3_un_paquete_instalado_como_el_lock_se_marca_instalado(self):
        self.proyecto(instalado={"alfa": "1.2.3", "beta": "2.0.1"})
        bom = self.bom()
        self.assertEqual([self.prop(c, "factory:instalado") for c in bom["components"]], ["true", "true"])

    def test_ul3_un_paquete_instalado_en_otra_version_sigue_siendo_una_diferencia(self):
        self.proyecto(instalado={"alfa": "1.2.4", "beta": "2.0.1"})
        bom = self.bom()
        self.assertEqual((self.confiable(bom), self.diferencias(bom)), ("false", ["alfa: el lock fija 1.2.3 y está instalada la 1.2.4"]))
        self.assertEqual(self.prop(self.componente(bom, "alfa"), "factory:instalado"), "false")

    def test_ul3_sin_consultar_el_entorno_no_hay_marca_de_instalado(self):
        self.proyecto()
        for c in self.bom()["components"]:
            self.assertIsNone(self.prop(c, "factory:instalado"))

    def test_ul3_sin_lock_lo_instalado_se_marca_instalado(self):
        self.proyecto(con_lock=False, instalado={"alfa": "1.0"})
        self.assertEqual(self.prop(self.bom()["components"][0], "factory:instalado"), "true")

    def test_ul3_con_dos_versiones_en_el_lock_la_instalada_es_la_unica_marcada(self):
        self.proyecto(lock_texto=_procedencia.lock(paquetes=[("alfa", "1.2.3", ("a",)), ("alfa", "1.0.0", ("b",)), ("beta", "2.0.1", ("c",))]),
                      instalado={"alfa": "1.2.3", "beta": "2.0.1"})
        marcas = {(c["name"], c["version"]): self.prop(c, "factory:instalado") for c in self.bom()["components"]}
        self.assertEqual(marcas, {("alfa", "1.0.0"): "false", ("alfa", "1.2.3"): "true", ("beta", "2.0.1"): "true"})

    def test_ul3_lo_instalado_que_no_esta_en_el_lock_no_es_una_diferencia(self):
        self.proyecto(instalado={"alfa": "1.2.3", "beta": "2.0.1", "pip": "24.0"})
        self.assertEqual(self.diferencias(self.bom()), [])


if __name__ == "__main__":
    unittest.main()
