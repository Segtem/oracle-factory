"""tb1–tb4: tutorial reproducible de Buscaminas con Factory."""

import importlib
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
EJEMPLO = ROOT / "examples/buscaminas"
GUIA = ROOT / "docs/tutorial-buscaminas.md"


def juego():
    sys.path.insert(0, str(EJEMPLO))
    return importlib.import_module("buscaminas")


class TutorialBuscaminas(unittest.TestCase):
    def test_tb1_guia_recorre_decisiones_y_recuperacion(self):
        texto = GUIA.read_text(encoding="utf-8")
        for paso in ("oracle-factory init", "oracle-factory nuevo", "oracle-factory listar",
                     "oracle-factory estado", "oracle-factory aprobar-spec", "oracle-factory importar",
                     "oracle-factory aprobar-sensor", "oracle-factory medir", "oracle-factory evidencia",
                     "oracle-factory revision", "oracle-factory juzgar", "oracle-factory cerrar"):
            self.assertIn(paso, texto, paso)
        self.assertIn("--agente NOMBRE", texto)
        self.assertIn("review.md", texto)
        self.assertIn("sin clonar", texto.lower())
        self.assertIn("0.1.0a20", texto)

    def test_tb1_guia_explica_que_repetir_si_cambia_el_candidato(self):
        texto = GUIA.read_text(encoding="utf-8")
        self.assertIn("antes de implementar", texto.lower())
        self.assertIn("falla", texto.lower())
        self.assertIn("nuevo commit", texto.lower())
        self.assertIn("repetir", texto.lower())
        self.assertIn("juicio", texto.lower())

    def test_tb2_cuenta_vecinas_y_oculta_las_minas(self):
        m = juego()
        partida = m.Partida()
        self.assertEqual(partida.numero(2, 2), 2)
        partida.destapar(2, 2)
        self.assertIn((2, 2), partida.destapadas)
        self.assertNotIn((1, 1), partida.destapadas)
        self.assertNotIn("*", partida.vista())

    def test_tb2_expande_cero_y_respeta_banderas(self):
        m = juego()
        partida = m.Partida()
        partida.alternar_bandera(1, 1)
        with self.assertRaises(ValueError):
            partida.destapar(1, 1)
        partida.destapar(3, 1)
        self.assertEqual(partida.destapadas, {(2, 1), (2, 2), (3, 1), (3, 2), (4, 1), (4, 2)})
        self.assertFalse(partida.destapadas & m.MINAS)
        self.assertIn((1, 1), partida.banderas)
        partida.alternar_bandera(1, 1)
        self.assertNotIn((1, 1), partida.banderas)

    def test_tb2_victoria_derrota_y_errores_conservan_estado(self):
        m = juego()
        derrota = m.Partida()
        with self.assertRaises(ValueError):
            derrota.destapar(0, 1)
        self.assertEqual(derrota.estado, "jugando")
        self.assertEqual(derrota.destapadas, set())
        derrota.destapar(1, 1)
        self.assertEqual(derrota.estado, "perdida")
        with self.assertRaises(ValueError):
            derrota.alternar_bandera(2, 2)
        victoria = m.Partida()
        for fila in range(1, 6):
            for columna in range(1, 6):
                if (fila, columna) not in m.MINAS and victoria.estado == "jugando":
                    victoria.destapar(fila, columna)
        self.assertEqual(victoria.estado, "ganada")
        with self.assertRaises(ValueError):
            victoria.destapar(1, 1)

    def test_tb2_interfaz_acepta_salir_y_rechaza_comando_invalido(self):
        p = subprocess.run([sys.executable, str(EJEMPLO / "buscaminas.py")],
                           input="desconocido\nsalir\n", capture_output=True, text=True, timeout=10)
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertIn("Buscaminas", p.stdout)
        self.assertIn("Comando", p.stdout)

    def test_tb3_sensor_escribe_hechos_correctos(self):
        with tempfile.TemporaryDirectory() as tmp:
            salida = Path(tmp) / "hechos.json"
            p = subprocess.run([sys.executable, str(EJEMPLO / "sensor.py"), "--salida", str(salida)],
                               cwd=EJEMPLO, capture_output=True, text=True, timeout=10)
            self.assertEqual(p.returncode, 0, p.stderr)
            hechos = json.loads(salida.read_text(encoding="utf-8"))
            self.assertGreaterEqual(len(hechos["casos"]), 6)
            self.assertTrue(all(c["codigo"] == 0 for c in hechos["casos"]))
            self.assertEqual(hechos["corrida"], [{"completa": 1, "casos": len(hechos["casos"])}])

        m = juego()
        sensor = importlib.import_module("sensor")
        original = m.Partida.destapar

        def roto(partida, fila, columna):
            original(partida, fila, columna)
            if (fila, columna) == (3, 1):
                partida.destapadas.update((f, c) for f in range(1, 6)
                                          for c in range(1, 6) if (f, c) not in m.MINAS)
                partida.estado = "ganada"

        with patch.object(m.Partida, "destapar", new=roto):
            hechos_rotos = sensor.observar()
        self.assertEqual(next(c for c in hechos_rotos["casos"] if c["caso"] == "cero")["codigo"], 1)

    def test_tb3_sensor_detecta_numero_equivocado(self):
        m = juego()
        sensor = importlib.import_module("sensor")
        with patch.object(m.Partida, "numero", return_value=0):
            hechos = sensor.observar()
        self.assertEqual(next(c for c in hechos["casos"] if c["caso"] == "numero")["codigo"], 1)
        original = m.Partida.numero

        def roto(partida, fila, columna):
            valor = original(partida, fila, columna)
            return valor + 1 if (fila, columna) == (2, 3) else valor

        with patch.object(m.Partida, "numero", new=roto):
            hechos = sensor.observar()
        self.assertEqual(next(c for c in hechos["casos"] if c["caso"] == "numero")["codigo"], 1)

    def test_tb3_catalogos_miden_casos_y_corrida(self):
        casos = (EJEMPLO / "catalogos/buscaminas.casos_correctos.oracle").read_text(encoding="utf-8")
        corrida = (EJEMPLO / "catalogos/buscaminas.corrida_completa.oracle").read_text(encoding="utf-8")
        self.assertIn("medida buscaminas.casos_correctos:", casos)
        self.assertIn("requiere casos", casos)
        self.assertIn("codigo == 0", casos)
        self.assertIn("medida buscaminas.corrida_completa:", corrida)
        self.assertIn("requiere corrida", corrida)
        self.assertIn("completa == 1", corrida)

    def test_tb3_oracle_acepta_hechos_correctos_y_rechaza_un_error(self):
        oracle = Path(sys.executable).with_name("oracle")
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            subprocess.run([str(oracle), "init", str(base)], check=True, capture_output=True, text=True)
            config = base / "oracle.json"
            datos = json.loads(config.read_text(encoding="utf-8"))
            datos["catalogo_base"] = False
            config.write_text(json.dumps(datos), encoding="utf-8")
            for archivo in (EJEMPLO / "catalogos").glob("*.oracle"):
                shutil.copy2(archivo, base / "catalogos" / archivo.name)
            sensor = importlib.import_module("sensor")
            hechos = sensor.observar()
            hechos_path = base / "hechos.json"
            hechos_path.write_text(json.dumps(hechos), encoding="utf-8")
            comando = [str(oracle), "--proyecto", str(base), "juzgar", "--con", str(hechos_path)]
            verde = subprocess.run(comando, capture_output=True, text=True, timeout=10)
            self.assertEqual(verde.returncode, 0, verde.stdout + verde.stderr)
            hechos["casos"][0]["codigo"] = 1
            hechos_path.write_text(json.dumps(hechos), encoding="utf-8")
            rojo = subprocess.run(comando, capture_output=True, text=True, timeout=10)
            self.assertNotEqual(rojo.returncode, 0)
            self.assertIn("buscaminas.casos_correctos", rojo.stdout)

    def test_tb4_fragmentos_copiables_coinciden_con_el_ejemplo(self):
        texto = GUIA.read_text(encoding="utf-8")
        bloques = dict(re.findall(r"```(?:python|json|oracle|markdown) archivo=([^\n]+)\n(.*?)\n```", texto, re.S))
        requeridos = ("buscaminas.py", "test_buscaminas.py", "sensor.py", "config.json", "proposal.md", "spec.md",
                      "catalogos/buscaminas.casos_correctos.oracle", "catalogos/buscaminas.corrida_completa.oracle")
        for nombre in requeridos:
            self.assertIn(nombre, bloques)
            self.assertEqual(bloques[nombre], (EJEMPLO / nombre).read_text(encoding="utf-8").rstrip("\n"), nombre)

    def test_tb4_entradas_enlazan_el_tutorial(self):
        for nombre in ("README.md", "site/desde-cero.html", "site/documentacion.html"):
            texto = (ROOT / nombre).read_text(encoding="utf-8")
            self.assertIn("tutorial-buscaminas.md", texto, nombre)
        self.assertIn("data-doc=\"tutorial-buscaminas\"", (ROOT / "site/documentacion.html").read_text())


if __name__ == "__main__":
    unittest.main()
