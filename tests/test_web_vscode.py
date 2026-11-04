"""La web muestra capturas reales de VS Code y salidas reales, sin datos personales: escenarios wv1–wv3."""
import json
from pathlib import Path
import shutil
import tempfile
import unittest

from tests.test_web import comandos_nombrados
from tools import sitio_vscode

ROOT = Path(__file__).resolve().parents[1]
PNG = b"\x89PNG\r\n\x1a\n" + b"0" * 100


def copia(tmp: Path) -> Path:
    dest = tmp / "repo"
    (dest / "tests").mkdir(parents=True)
    shutil.copytree(ROOT / "site", dest / "site")
    shutil.copytree(ROOT / "tests" / "datos", dest / "tests" / "datos")
    shutil.copytree(ROOT / "tools", dest / "tools", ignore=shutil.ignore_patterns("__pycache__"))
    return dest


def con_pagina(dest: Path, nombre: str, agregar: str) -> None:
    p = dest / "site" / nombre
    p.write_text(p.read_text(encoding="utf-8").replace("</main>", agregar + "</main>", 1), encoding="utf-8")


class WebVscode(unittest.TestCase):
    def setUp(self):
        self._t = tempfile.TemporaryDirectory()
        self.addCleanup(self._t.cleanup)
        self.tmp = Path(self._t.name)

    # --- wv1: capturas reales de VS Code -----------------------------------------------------------------------------------
    def test_wv1_el_repositorio_muestra_cuatro_capturas_con_alt_medidas_y_peso(self):
        self.assertEqual(sitio_vscode.problemas(ROOT), [])
        imagenes = list((ROOT / "site" / "img").glob("vscode-*.png"))
        self.assertGreaterEqual(len(imagenes), 4)
        self.assertLessEqual(sum(p.stat().st_size for p in imagenes), sitio_vscode.MAX_TOTAL)

    def test_wv1_una_imagen_inexistente_o_sin_alt_o_sin_medidas_se_detecta(self):
        dest = copia(self.tmp)
        con_pagina(dest, "desde-cero.html", '<img src="./img/vscode-no-existe.png" alt="" width="10">')
        texto = "\n".join(sitio_vscode.problemas(dest))
        self.assertIn("desde-cero.html: la imagen ./img/vscode-no-existe.png no existe", texto)
        self.assertIn("no tiene texto alternativo", texto)
        self.assertIn("no declara ancho y alto", texto)

    def test_wv1_una_imagen_pesada_o_pocas_capturas_se_detectan(self):
        dest = copia(self.tmp)
        (dest / "site" / "img").mkdir(exist_ok=True)
        (dest / "site" / "img" / "vscode-pesada.png").write_bytes(PNG + b"0" * (sitio_vscode.MAX_IMAGEN + 1))
        con_pagina(dest, "desde-cero.html", '<img src="./img/vscode-pesada.png" alt="x" width="1" height="1">')
        self.assertTrue(any("el tope es 300 KB" in p for p in sitio_vscode.problemas(dest)))
        for f in (dest / "site" / "img").glob("vscode-*.png"):
            f.unlink()
        for h in (dest / "site").glob("*.html"):
            h.write_text(__import__("re").sub(r"<img\b[^>]*vscode-[^>]*>", "", h.read_text(encoding="utf-8")), encoding="utf-8")
        self.assertTrue(any("la spec pide al menos 4" in p for p in sitio_vscode.problemas(dest)))

    # --- wv2: ejemplos con salida real ---------------------------------------------------------------------------------------
    def test_wv2_cada_ejemplo_coincide_con_el_registro_y_hay_varios(self):
        registro = json.loads((ROOT / "tests" / "datos" / "ejemplos-demo.json").read_text(encoding="utf-8"))
        self.assertGreaterEqual(len(registro), 4)
        usados = {i for h in (ROOT / "site").glob("*.html") for i in sitio_vscode.EJEMPLO.findall(h.read_text(encoding="utf-8")) for i in (i[0],)}
        self.assertEqual(usados, set(registro))
        self.assertTrue((ROOT / "tools" / "capturas_vscode.py").is_file())

    def test_wv2_un_ejemplo_escrito_a_mano_se_detecta(self):
        dest = copia(self.tmp)
        registro = json.loads((dest / "tests" / "datos" / "ejemplos-demo.json").read_text(encoding="utf-8"))
        ident = next(iter(registro))
        con_pagina(dest, "colaboracion.html", f'<pre data-ejemplo="{ident}">otra cosa</pre><pre data-ejemplo="inventado">x</pre>')
        texto = "\n".join(sitio_vscode.problemas(dest))
        self.assertIn(f"colaboracion.html: el ejemplo {ident} no coincide con lo que contestó la CLI", texto)
        self.assertIn("el ejemplo inventado no está en el registro", texto)

    def test_wv2_la_puntuacion_de_la_salida_no_es_parte_del_subcomando(self):
        self.assertEqual(comandos_nombrados("con el hook de oracle-factory hooks)."), [("hooks", [])])
        self.assertEqual(comandos_nombrados("oracle-factory comando-inexistente)."), [("comando-inexistente", [])])

    # --- wv3: sin datos personales ---------------------------------------------------------------------------------------
    def test_wv3_ni_el_sitio_ni_el_registro_ni_el_script_traen_datos_personales(self):
        self.assertFalse([p for p in sitio_vscode.problemas(ROOT) if "dato personal" in p or "correo" in p])

    def test_wv3_una_ruta_de_home_o_un_correo_ajeno_se_detectan(self):
        dest = copia(self.tmp)
        ruta = dest / "tests" / "datos" / "ejemplos-demo.json"
        registro = json.loads(ruta.read_text(encoding="utf-8"))
        registro["extra"] = "Acuerdos: /home/alguien/proyecto y alguien@correo.com"
        ruta.write_text(json.dumps(registro), encoding="utf-8")
        texto = "\n".join(sitio_vscode.problemas(dest))
        self.assertIn("tests/datos/ejemplos-demo.json: contiene un dato personal (/home/a)", texto)
        self.assertIn("contiene un correo ajeno al ejemplo (alguien@correo.com)", texto)
        con_pagina(dest, "index.html", "<p>C:\\Users\\yo</p>")
        self.assertIn("index.html: contiene un dato personal", "\n".join(sitio_vscode.problemas(dest)))


if __name__ == "__main__":
    unittest.main()
