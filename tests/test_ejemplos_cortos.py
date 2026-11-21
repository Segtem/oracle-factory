"""ec1–ec4: tres ejercicios mínimos que muestran hechos y decisiones de Factory."""

import importlib.util
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
EJEMPLOS = ROOT / "examples/cortos"
GUIA = ROOT / "docs/ejemplos-cortos.md"


def cargar(nombre, ruta):
    spec = importlib.util.spec_from_file_location(nombre, ruta)
    modulo = importlib.util.module_from_spec(spec)
    sys.path.insert(0, str(ruta.parent))
    try:
        spec.loader.exec_module(modulo)
    finally:
        sys.path.pop(0)
    return modulo


class EjemplosCortos(unittest.TestCase):
    def test_ec1_precio_respeta_limite_y_sensor_detecta_regresion(self):
        carpeta = EJEMPLOS / "precio"
        producto = cargar("total_corto", carpeta / "total.py")
        sensor = cargar("sensor_precio_corto", carpeta / "sensor.py")
        self.assertEqual(producto.calcular(1001, 50), 501)
        for descuento in (-1, 51):
            with self.assertRaises(ValueError):
                producto.calcular(1001, descuento)
        self.assertEqual(sensor.observar()["casos"], [{"caso": "limite", "codigo": 0}])
        original = sensor.calcular

        def sin_limite(centavos, porcentaje):
            return centavos if porcentaje == 51 else original(centavos, porcentaje)

        with patch.object(sensor, "calcular", side_effect=sin_limite):
            self.assertEqual(sensor.observar()["casos"], [{"caso": "limite", "codigo": 1}])
        with patch.object(sensor, "calcular", side_effect=RuntimeError("producto roto")):
            self.assertEqual(sensor.observar()["casos"], [{"caso": "limite", "codigo": 1}])

    def test_ec1_precio_tiene_prueba_copiable(self):
        self._prueba_de_ejemplo("precio", "test_total.py")
        self.assertIn("### Requirement:", (EJEMPLOS / "precio/spec.md").read_text())

    def test_ec2_csv_rechaza_fila_y_sensor_detecta_aceptacion_indebida(self):
        carpeta = EJEMPLOS / "csv"
        producto = cargar("lector_corto", carpeta / "lector.py")
        sensor = cargar("sensor_csv_corto", carpeta / "sensor.py")
        self.assertEqual(producto.sumar("A,3\nB,4\n"), 7)
        for texto in ("A,3\nB,-4\n", "A,3\nB\n"):
            with self.assertRaises(ValueError):
                producto.sumar(texto)
        self.assertEqual(sensor.observar()["casos"], [{"caso": "fila", "codigo": 0}])
        with patch.object(sensor, "sumar", return_value=7):
            self.assertEqual(sensor.observar()["casos"], [{"caso": "fila", "codigo": 1}])
        with patch.object(sensor, "sumar", side_effect=RuntimeError("producto roto")):
            self.assertEqual(sensor.observar()["casos"], [{"caso": "fila", "codigo": 1}])

    def test_ec2_csv_tiene_prueba_copiable(self):
        self._prueba_de_ejemplo("csv", "test_lector.py")
        self.assertIn("### Requirement:", (EJEMPLOS / "csv/spec.md").read_text())

    def test_ec3_ayuda_distingue_enlace_correcto_y_roto(self):
        carpeta = EJEMPLOS / "ayuda"
        sensor = cargar("sensor_ayuda_corto", carpeta / "sensor.py")
        self.assertEqual(sensor.observar(carpeta)["casos"], [{"caso": "enlace", "codigo": 0}])
        with tempfile.TemporaryDirectory() as temporal:
            copia = Path(temporal)
            (copia / "uso.md").write_text("# Uso\n\n[Primer paso](faltante.md)\n", encoding="utf-8")
            (copia / "pasos.md").write_text("# Pasos\n", encoding="utf-8")
            self.assertEqual(sensor.observar(copia)["casos"], [{"caso": "enlace", "codigo": 1}])
        with tempfile.TemporaryDirectory() as temporal:
            self.assertEqual(sensor.observar(Path(temporal))["casos"], [{"caso": "enlace", "codigo": 1}])

    def test_ec3_ayuda_tiene_prueba_copiable(self):
        self._prueba_de_ejemplo("ayuda", "test_ayuda.py")
        self.assertIn("### Requirement:", (EJEMPLOS / "ayuda/spec.md").read_text())

    def test_ec4_sensores_escriben_hechos_con_un_caso(self):
        for nombre in ("precio", "csv", "ayuda"):
            with self.subTest(nombre=nombre), tempfile.TemporaryDirectory() as temporal:
                carpeta = EJEMPLOS / nombre
                salida = Path(temporal) / "hechos.json"
                proceso = subprocess.run([sys.executable, "sensor.py", "--salida", str(salida)], cwd=carpeta,
                                         capture_output=True, text=True, timeout=10)
                self.assertEqual(proceso.returncode, 0, proceso.stderr)
                hechos = json.loads(salida.read_text(encoding="utf-8"))
                self.assertEqual(len(hechos["casos"]), 1)
                self.assertEqual(hechos["casos"][0]["codigo"], 0)
                self.assertEqual(hechos["corrida"], [{"completa": 1, "casos": 1}])

    def test_ec4_oracle_acepta_verde_y_rechaza_rojo(self):
        oracle = Path(sys.executable).with_name("oracle")
        with tempfile.TemporaryDirectory() as temporal:
            raiz = Path(temporal)
            subprocess.run([str(oracle), "init", str(raiz)], check=True, capture_output=True, text=True)
            config = raiz / "oracle.json"
            datos = json.loads(config.read_text(encoding="utf-8"))
            datos["catalogo_base"] = False
            config.write_text(json.dumps(datos), encoding="utf-8")
            for origen in (EJEMPLOS / "comun/catalogos").glob("*.oracle"):
                shutil.copy2(origen, raiz / "catalogos" / origen.name)
            hechos = raiz / "hechos.json"
            orden = [str(oracle), "--proyecto", str(raiz), "juzgar", "--con", str(hechos)]
            for nombre in ("precio", "csv", "ayuda"):
                with self.subTest(nombre=nombre):
                    sensor = EJEMPLOS / nombre / "sensor.py"
                    subprocess.run([sys.executable, str(sensor), "--salida", str(hechos)],
                                   cwd=sensor.parent, check=True, capture_output=True, text=True)
                    verde = subprocess.run(orden, capture_output=True, text=True, timeout=10)
                    self.assertEqual(verde.returncode, 0, verde.stdout + verde.stderr)
                    datos = json.loads(hechos.read_text(encoding="utf-8"))
                    datos["casos"][0]["codigo"] = 1
                    hechos.write_text(json.dumps(datos), encoding="utf-8")
                    rojo = subprocess.run(orden, capture_output=True, text=True, timeout=10)
                    self.assertNotEqual(rojo.returncode, 0, rojo.stdout + rojo.stderr)

    def test_ec4_las_tres_variantes_de_la_guia_dan_rojo(self):
        variantes = (
            ("precio", "total.py", "<= 50", "<= 51"),
            ("csv", "lector.py", "cantidad <= 0", "cantidad == 0"),
            ("ayuda", "uso.md", "pasos.md", "faltante.md"),
        )
        for nombre, archivo, antes, despues in variantes:
            with self.subTest(nombre=nombre), tempfile.TemporaryDirectory() as temporal:
                copia = Path(temporal) / nombre
                shutil.copytree(EJEMPLOS / nombre, copia)
                destino = copia / archivo
                texto = destino.read_text(encoding="utf-8")
                self.assertEqual(texto.count(antes), 1)
                destino.write_text(texto.replace(antes, despues), encoding="utf-8")
                hechos = copia / "hechos.json"
                proceso = subprocess.run([sys.executable, "sensor.py", "--salida", str(hechos)], cwd=copia,
                                         capture_output=True, text=True, timeout=10)
                self.assertEqual(proceso.returncode, 0, proceso.stderr)
                self.assertEqual(json.loads(hechos.read_text(encoding="utf-8"))["casos"][0]["codigo"], 1)

    def test_ec4_bloques_copiables_y_navegacion(self):
        texto = GUIA.read_text(encoding="utf-8")
        bloques = dict(re.findall(r"```(?:python|markdown|json|oracle) archivo=([^\n]+)\n(.*?)\n```", texto, re.S))
        for ruta in ("precio/total.py", "csv/lector.py", "ayuda/uso.md", "comun/config.json",
                     "comun/catalogos/cortos.caso.oracle", "comun/catalogos/cortos.corrida.oracle"):
            self.assertIn(ruta, bloques)
            self.assertEqual(bloques[ruta], (EJEMPLOS / ruta).read_text(encoding="utf-8").rstrip("\n"), ruta)
        for nombre in ("precio", "csv", "ayuda"):
            self.assertIn(f"examples/cortos/{nombre}", texto)
        for paso in ("oracle-factory nuevo", "oracle-factory aprobar-spec", "oracle-factory medir",
                     "oracle-factory evidencia", "oracle-factory revisar", "oracle-factory por-que"):
            self.assertIn(paso, texto)
        self.assertIn("tutorial-buscaminas.md", texto)
        self.assertIn("sin clonar", texto.lower())
        for nombre in ("README.md", "site/desde-cero.html", "site/documentacion.html"):
            self.assertIn("ejemplos-cortos.md", (ROOT / nombre).read_text(encoding="utf-8"), nombre)

    def _prueba_de_ejemplo(self, nombre, archivo):
        carpeta = EJEMPLOS / nombre
        proceso = subprocess.run([sys.executable, "-m", "unittest", archivo.removesuffix(".py")], cwd=carpeta,
                                 capture_output=True, text=True, timeout=10)
        self.assertEqual(proceso.returncode, 0, proceso.stdout + proceso.stderr)


if __name__ == "__main__":
    unittest.main()
