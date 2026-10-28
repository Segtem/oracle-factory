"""Partir cli.py en módulos sin cambiar nada de lo que hace: escenarios cm1–cm3."""
import argparse
import ast
import inspect
import json
import os
from pathlib import Path
import re
import sys
import tempfile
import unittest
from unittest.mock import patch

SOURCE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SOURCE))
from oracle_factory import cli, flujo_medidas, flujo_revision, lecturas, parser  # noqa: E402
from tools import tamanos  # noqa: E402

DATOS = SOURCE / "tests/datos"
MODULOS = {"parser": parser, "flujo_revision": flujo_revision, "flujo_medidas": flujo_medidas, "lecturas": lecturas}


def firma(obj):
    try:
        return re.sub(r" at 0x[0-9a-f]+", "", str(inspect.signature(obj)))
    except (TypeError, ValueError):
        return None


def definidos_en(ruta: Path) -> set[str]:
    """Los nombres que define (no importa) un archivo, en su primer nivel."""
    nombres = set()
    for n in ast.parse(ruta.read_text(encoding="utf-8")).body:
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            nombres.add(n.name)
        elif isinstance(n, ast.Assign):
            nombres.update(t.id for t in n.targets if isinstance(t, ast.Name))
        elif isinstance(n, ast.AnnAssign) and isinstance(n.target, ast.Name):
            nombres.add(n.target.id)
    return nombres


def ligados_en(funcion) -> set[str]:
    """Los nombres que una función liga adentro: parámetros, asignaciones, for, with, import, def, except as."""
    s = set()
    for x in ast.walk(funcion):
        if isinstance(x, ast.Name) and isinstance(x.ctx, (ast.Store, ast.Del)):
            s.add(x.id)
        elif isinstance(x, ast.arg):
            s.add(x.arg)
        elif isinstance(x, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) and x is not funcion:
            s.add(x.name)
        elif isinstance(x, ast.ExceptHandler) and x.name:
            s.add(x.name)
        elif isinstance(x, (ast.Import, ast.ImportFrom)):
            s.update((a.asname or a.name).split(".")[0] for a in x.names)
    return s


class CliModulos(unittest.TestCase):
    # --- cm1: la CLI se comporta igual --------------------------------------------------------------------------------------
    def test_cm1_todos_los_nombres_y_firmas_de_antes_siguen_en_cli(self):
        dorado = json.loads((DATOS / "nombres-cli.json").read_text(encoding="utf-8"))
        faltan, distintas = [], []
        for nombre, datos in dorado.items():
            if datos["tipo"] == "modulo":
                continue  # un módulo importado no es parte de lo que cli ofrece
            if not hasattr(cli, nombre):
                faltan.append(nombre)
                continue
            valor = getattr(cli, nombre)
            if datos["tipo"] in ("funcion", "clase") and firma(valor) != datos.get("firma"):
                distintas.append((nombre, datos.get("firma"), firma(valor)))
            if datos["tipo"] == "funcion" and not callable(valor):
                distintas.append((nombre, "función", type(valor).__name__))
        self.assertEqual((faltan, distintas), ([], []))
        self.assertGreater(len(dorado), 200)

    def test_cm1_la_ayuda_de_oracle_factory_y_de_cada_subcomando_es_identica(self):
        dorado = json.loads((DATOS / "ayuda-cli.json").read_text(encoding="utf-8"))
        with patch.dict(os.environ, {"COLUMNS": "100"}):
            p = cli.construir_parser()
            ayuda = {"": p.format_help()}
            for a in p._actions:
                if isinstance(a, argparse._SubParsersAction):
                    ayuda.update({n: sub.format_help() for n, sub in a.choices.items()})
        self.assertEqual(sorted(ayuda), sorted(dorado))
        self.assertEqual([n for n in dorado if ayuda[n] != dorado[n]], [])

    def test_cm1_lo_movido_es_el_mismo_objeto_en_cli_y_en_su_modulo(self):
        total = 0
        for nombre_modulo, modulo in MODULOS.items():
            for nombre in definidos_en(SOURCE / "oracle_factory" / f"{nombre_modulo}.py"):
                total += 1
                self.assertIs(getattr(cli, nombre), getattr(modulo, nombre), f"{nombre_modulo}.{nombre}")
        self.assertGreater(total, 60)

    def test_cm1_lo_movido_ya_no_se_define_en_cli(self):
        en_cli = definidos_en(SOURCE / "oracle_factory/cli.py")
        for nombre_modulo in MODULOS:
            repetidos = definidos_en(SOURCE / "oracle_factory" / f"{nombre_modulo}.py") & en_cli
            self.assertEqual(repetidos, set(), f"{nombre_modulo} define lo mismo que cli.py")

    def test_cm1_dos_modulos_nuevos_no_definen_el_mismo_nombre(self):
        vistos = {}
        for nombre_modulo in MODULOS:
            for nombre in definidos_en(SOURCE / "oracle_factory" / f"{nombre_modulo}.py"):
                self.assertNotIn(nombre, vistos, f"{nombre} en {nombre_modulo} y en {vistos.get(nombre)}")
                vistos[nombre] = nombre_modulo

    def test_cm1_cli_sigue_siendo_la_entrada_del_comando(self):
        self.assertTrue(callable(cli.main))
        self.assertIn("oracle-factory = \"oracle_factory.cli:main\"", (SOURCE / "pyproject.toml").read_text(encoding="utf-8"))
        self.assertIs(sys.modules["oracle_factory.cli"], cli)

    # --- cm2: lo movido lee a cli en el momento de usarlo ----------------------------------------------------------------------
    def test_cm2_un_valor_de_cli_cambiado_vale_para_lo_movido(self):
        with tempfile.TemporaryDirectory() as tmp:
            raiz = Path(tmp).resolve()
            with patch.object(cli, "ROOT", raiz):
                self.assertEqual(cli.ruta_resumen(), raiz / ".factory" / "resumen.md")  # lecturas
                self.assertEqual(cli.nombre_de_archivo(raiz / "a/b.oracle"), "a/b.oracle")  # flujo_medidas
        paquete = {"excluded_files": ["oracle_factory/cli.py"]}  # flujo_revision: lo que cli dice que es producto
        with patch.object(cli, "es_producto", return_value=True):
            self.assertEqual(cli.producto_excluido(paquete), ["oracle_factory/cli.py"])
        with patch.object(cli, "es_producto", return_value=False):
            self.assertEqual(cli.producto_excluido(paquete), [])

    def test_cm2_una_funcion_cambiada_en_cli_la_usa_lo_movido(self):
        class Marca(Exception):
            pass
        with patch.object(cli, "ejecutar", side_effect=Marca):
            with self.assertRaises(Marca):
                cli.nombres("HEAD")  # lecturas
            with self.assertRaises(Marca):
                cli.exclusiones_del_paquete("a", "b")  # flujo_revision

    def test_cm2_exclusiones_del_paquete_usa_ejecutar_y_es_producto_de_cli(self):
        class Salida:
            stdout = "a.py\0doc.txt\0"
        with patch.object(cli, "ejecutar", return_value=Salida()):
            with patch.object(cli, "es_producto", side_effect=lambda n: n == "a.py"):
                self.assertEqual(cli.exclusiones_del_paquete("b", "h"), [".factory", "doc.txt", "tareas"])
            with patch.object(cli, "es_producto", return_value=True):
                self.assertEqual(cli.exclusiones_del_paquete("b", "h"), [".factory", "tareas"])
            with patch.object(cli, "es_producto", return_value=False):
                self.assertEqual(cli.exclusiones_del_paquete("b", "h"), [".factory", "a.py", "doc.txt", "tareas"])

    def test_cm2_ninguna_funcion_movida_usa_un_nombre_de_cli_como_propio(self):
        en_cli = definidos_en(SOURCE / "oracle_factory/cli.py")
        for nombre_modulo in MODULOS:
            fuente = (SOURCE / "oracle_factory" / f"{nombre_modulo}.py").read_text(encoding="utf-8")
            otros = set().union(*(definidos_en(SOURCE / "oracle_factory" / f"{m}.py") for m in MODULOS))
            ajenos = en_cli | otros
            for f in ast.parse(fuente).body:
                if not isinstance(f, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    continue
                ligados = ligados_en(f)
                for x in ast.walk(f):
                    if isinstance(x, ast.Name) and isinstance(x.ctx, ast.Load) and x.id in ajenos and x.id not in ligados:
                        self.fail(f"{nombre_modulo}.{f.name} usa «{x.id}» sin pasar por cli (línea {x.lineno})")

    def test_cm2_ninguna_funcion_movida_usa_un_nombre_que_no_existe(self):
        import builtins
        for nombre_modulo in MODULOS:
            arbol = ast.parse((SOURCE / "oracle_factory" / f"{nombre_modulo}.py").read_text(encoding="utf-8"))
            propios = definidos_en(SOURCE / "oracle_factory" / f"{nombre_modulo}.py")
            for n in arbol.body:
                if isinstance(n, (ast.Import, ast.ImportFrom)):
                    propios.update((a.asname or a.name).split(".")[0] for a in n.names)
            for f in arbol.body:
                if not isinstance(f, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    continue
                ligados = ligados_en(f)
                for x in ast.walk(f):
                    if (isinstance(x, ast.Name) and isinstance(x.ctx, ast.Load) and x.id not in ligados and x.id not in propios
                            and not hasattr(builtins, x.id) and x.id != "annotations"):
                        self.fail(f"{nombre_modulo}.{f.name} usa «{x.id}», que no existe en el módulo (línea {x.lineno})")

    def test_cm2_los_modulos_nuevos_importan_a_cli_entero_y_no_sus_nombres(self):
        for nombre_modulo in MODULOS:
            fuente = (SOURCE / "oracle_factory" / f"{nombre_modulo}.py").read_text(encoding="utf-8")
            self.assertNotRegex(fuente, r"(?m)^\s*from\s+(?:\.cli|oracle_factory\.cli)\s+import\b", nombre_modulo)
            if nombre_modulo != "parser":
                self.assertRegex(fuente, r"(?m)^from \. import cli$", nombre_modulo)

    def test_cm2_ningun_modulo_nuevo_se_pasa_al_kb_en_lugar_de_cli(self):
        for nombre_modulo in MODULOS:
            fuente = (SOURCE / "oracle_factory" / f"{nombre_modulo}.py").read_text(encoding="utf-8")
            self.assertNotIn("sys.modules[__name__]", fuente, nombre_modulo)  # el kb se arma con el módulo cli
            propios = [x.lineno for x in ast.walk(ast.parse(fuente)) if isinstance(x, ast.Name) and x.id in ("__name__", "__file__", "__package__")]
            self.assertEqual(propios, [], nombre_modulo)  # esos nombres serían los del módulo nuevo y no los de cli

    # --- cm3: ningún archivo pasa del tope ---------------------------------------------------------------------------------------
    def test_cm3_cli_py_y_los_demas_archivos_estan_bajo_sus_topes(self):
        self.assertEqual(tamanos.problemas(SOURCE), [])
        self.assertLess((SOURCE / "oracle_factory/cli.py").stat().st_size, 160_000)
        self.assertEqual(max(p.stat().st_size for p in (SOURCE / "oracle_factory").rglob("*.py")) < 200_000, True)

    def test_cm3_un_archivo_que_crece_de_mas_se_nombra_con_su_tamano_y_el_limite_de_clue(self):
        with tempfile.TemporaryDirectory() as tmp:
            raiz = Path(tmp)
            (raiz / "oracle_factory").mkdir()
            (raiz / "oracle_factory/grande.py").write_text("x = 1\n" + "#" * 200_000)
            (raiz / "oracle_factory/cli.py").write_text("y = 2\n" + "#" * 160_000)
            (raiz / "oracle_factory/justo.py").write_text("z = 3\n" + "#" * 199_000)
            (raiz / "oracle_factory/sub").mkdir()
            (raiz / "oracle_factory/sub/cli.py").write_text("w = 4\n" + "#" * 170_000)  # un cli.py de otra carpeta tiene el tope general
            errores = tamanos.problemas(raiz)
        self.assertEqual(len(errores), 2)
        self.assertTrue(errores[0].startswith("oracle_factory/cli.py mide 160006 bytes y el tope es 160000"))
        self.assertTrue(errores[1].startswith("oracle_factory/grande.py mide 200006 bytes y el tope es 200000"))
        for e in errores:
            self.assertIn("Oracle Clue no acepta archivos de 256000", e)

    def test_cm3_justo_bajo_el_tope_no_es_un_problema(self):
        with tempfile.TemporaryDirectory() as tmp:
            raiz = Path(tmp)
            (raiz / "oracle_factory").mkdir()
            (raiz / "oracle_factory/cli.py").write_text("#" * 159_999)
            (raiz / "oracle_factory/otro.py").write_text("#" * 199_999)
            self.assertEqual(tamanos.problemas(raiz), [])


if __name__ == "__main__":
    unittest.main()
