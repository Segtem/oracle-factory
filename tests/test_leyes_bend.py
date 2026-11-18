"""La regla de quién decide como leyes probadas en Bend (lb1), sin leyes vacías (lb2) y igual al código (lb3).

El modelo vive en modelos/quien-decide/. Sin `bend` (lb1, lb2) o sin `node` (lb3) la prueba se omite y dice qué falta.
"""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from oracle_factory import modos  # noqa: E402

MODELO = ROOT / "modelos" / "quien-decide"
ENTORNO = {**os.environ, "BEND_NO_TELEMETRY": "1"}

# Cada mutante rompe una parte de la regla; con cualquiera, alguna prueba tiene que dejar de valer.
MUTANTES = {
    "confirmación: un agente decide la revisión": ("    case Confirmacion{} _ _:\n      Propone{}",
                                                   "    case Confirmacion{} _ Revision{}:\n      Decide{}\n    case Confirmacion{} _ _:\n      Propone{}"),
    "el agente aprueba el sensor en autónomo": ("    case _ _ AprobarSensor{}:\n      NoPuede{}\n    case Autonomo{} _ _:", "    case Autonomo{} _ _:"),
    "confirmación: un agente propone el cierre": ("    case Confirmacion{} _ Cierre{}:\n      NoPuede{}\n", ""),
    "el registro no cuenta nada": ("          sumar(es_agente(a) && es_decide(puede(a, m, t, d)), decididas_por_agente(m, resto))",
                                   "          decididas_por_agente(m, resto)"),
    "funcional: el agente decide lo funcional": ("    case Funcional{} Func{} _:\n      NoPuede{}", "    case Funcional{} Func{} _:\n      Decide{}"),
    "una persona sólo propone": ("    case Persona{}:\n      Decide{}", "    case Persona{}:\n      Propone{}"),
    "el registro cuenta a las personas": ("          sumar(es_agente(a) && es_decide(puede(a, m, t, d)), decididas_por_agente(m, resto))",
                                          "          sumar(es_decide(puede(a, m, t, d)), decididas_por_agente(m, resto))"),
    "proponer se lee como decidir": ("    case Propone{}:\n      False{}", "    case Propone{}:\n      True{}"),
}
MODO = {"autonomo": "Autonomo", "funcional": "Funcional", "confirmacion": "Confirmacion"}
DECISION = {"spec": "Spec", "medidas": "Medidas", "revision": "Revision", "cierre": "Cierre"}
TIPO = {"funcional": "Func", "no funcional": "NoFunc"}
RESULTADO = {"Decide": "decide", "Propone": "propone", "NoPuede": "rechaza"}


def requiere(programa: str, path: str | None = None) -> str:
    """La ruta de `programa`, o SkipTest diciendo que falta."""
    ruta = shutil.which(programa, path=path)
    if ruta is None:
        raise unittest.SkipTest(f"falta {programa} en el PATH: esta prueba del modelo de modelos/quien-decide no se puede correr")
    return ruta


def copia_del_modelo(tmp: str) -> Path:
    destino = Path(tmp) / "quien-decide"
    shutil.copytree(MODELO, destino)
    return destino


def pruebas_valen(bend: str, carpeta: Path) -> bool:
    r = subprocess.run([bend, "PROOF.bend"], cwd=carpeta, env=ENTORNO, capture_output=True, text=True, timeout=120)
    return "ALL PROOFS CHECK" in r.stdout


def sobrevivientes(bend: str, modelo: Path = MODELO) -> list[str]:
    original = (modelo / "quien.bend").read_text(encoding="utf-8")
    vivos = []
    for nombre, (viejo, nuevo) in MUTANTES.items():
        if original.count(viejo) != 1:
            raise AssertionError(f"el mutante «{nombre}» ya no encuentra su línea en quien.bend")
        with tempfile.TemporaryDirectory() as tmp:
            copia = Path(tmp) / "q"
            shutil.copytree(modelo, copia)
            (copia / "quien.bend").write_text(original.replace(viejo, nuevo), encoding="utf-8")
            if pruebas_valen(bend, copia):
                vivos.append(nombre)
    return vivos


def distintas(node: str, modulo: Path = MODELO / "quien.mjs") -> list[str]:
    """Las combinaciones en las que el modelo compilado y modos.via_agente dicen cosas distintas."""
    combinaciones = [(m, d, t) for m in modos.MODOS for d in modos.DECISIONES for t in modos.TIPOS]
    script = (f"import Q from {json.dumps(str(modulo))};\n"
              f"const casos = {json.dumps([[MODO[m], DECISION[d], TIPO[t]] for m, d, t in combinaciones])};\n"
              "console.log(JSON.stringify(casos.map(([m, d, t]) => Q.del_agente({$: m}, {$: t}, {$: d}).$)));\n")
    r = subprocess.run([node, "--input-type=module", "-e", script], capture_output=True, text=True, timeout=60, check=True)
    dice_el_modelo = json.loads(r.stdout)
    assert len(dice_el_modelo) == len(combinaciones) == 24
    return [f"{m} / {d} / {t}: el código dice {modos.via_agente(m, d, [t])}, el modelo dice {RESULTADO[b]}"
            for (m, d, t), b in zip(combinaciones, dice_el_modelo) if RESULTADO[b] != modos.via_agente(m, d, [t])]


class Leyes(unittest.TestCase):
    # --- lb1: las leyes de quién decide están probadas --------------------------------------------------------------------
    def test_lb1_bend_acepta_las_pruebas_y_el_modelo_compilado_esta_al_dia(self):
        bend = requiere("bend")
        self.assertTrue(pruebas_valen(bend, MODELO))
        with tempfile.TemporaryDirectory() as tmp:
            copia = copia_del_modelo(tmp)
            (copia / "quien.mjs").unlink()
            subprocess.run([bend, "quien.bend", "-o", "quien.mjs"], cwd=copia, env=ENTORNO, check=True, capture_output=True, timeout=120)
            self.assertEqual((copia / "quien.mjs").read_bytes(), (MODELO / "quien.mjs").read_bytes(),
                             "modelos/quien-decide/quien.mjs no es el que genera bend: regeneralo con bend quien.bend -o quien.mjs")

    def test_lb1_una_ley_sin_prueba_no_se_acepta(self):
        bend = requiere("bend")
        with tempfile.TemporaryDirectory() as tmp:
            copia = copia_del_modelo(tmp)
            with (copia / "LAWS.bend").open("a", encoding="utf-8") as leyes:
                leyes.write("\nlaw una_ley_sin_prueba:\n  for m: Q.Modo\n  {Q.puede(Q.Agente{}, m, Q.Func{}, Q.Spec{}) == Q.Decide{} : Q.Resultado}\n")
            self.assertFalse(pruebas_valen(bend, copia))

    def test_lb1_sin_bend_se_omite_diciendo_que_falta(self):
        with tempfile.TemporaryDirectory() as vacio:
            for programa in ("bend", "node"):
                with self.subTest(programa=programa), self.assertRaises(unittest.SkipTest) as omitida:
                    requiere(programa, path=vacio)
                self.assertIn(f"falta {programa}", str(omitida.exception))


class SinLeyesVacias(unittest.TestCase):
    # --- lb2: ninguna ley de quién decide está vacía ----------------------------------------------------------------------
    def test_lb2_cada_mutante_del_modelo_hace_fallar_alguna_prueba(self):
        self.assertEqual(sobrevivientes(requiere("bend")), [])

    def test_lb2_sin_la_ley_de_la_persona_un_mutante_sobrevive_y_se_nombra(self):
        bend = requiere("bend")
        with tempfile.TemporaryDirectory() as tmp:
            copia = copia_del_modelo(tmp)
            for archivo, inicio in (("LAWS.bend", "\n# Una persona, desde su terminal, siempre decide"),
                                    ("PROOF.bend", "\ndef Laws.una_persona_siempre_decide")):
                texto = (copia / archivo).read_text(encoding="utf-8")
                self.assertEqual(texto.count(inicio), 1, archivo)
                (copia / archivo).write_text(texto[:texto.index(inicio)] + "\n", encoding="utf-8")  # es la última de cada archivo
            self.assertTrue(pruebas_valen(bend, copia))
            self.assertEqual(sobrevivientes(bend, copia), ["una persona sólo propone"])


class ModeloYCodigo(unittest.TestCase):
    # --- lb3: el modelo coincide con el código ----------------------------------------------------------------------------
    def test_lb3_el_modelo_compilado_y_via_agente_dicen_lo_mismo(self):
        self.assertEqual(distintas(requiere("node")), [])

    def test_lb3_si_el_codigo_cambia_y_el_modelo_no_se_nombra_la_combinacion(self):
        node = requiere("node")
        original = modos.via_agente

        def cambiado(modo, decision, tipos):
            return "decide" if (modo, decision) == ("confirmacion", "revision") else original(modo, decision, tipos)

        with patch.object(modos, "via_agente", cambiado):
            self.assertEqual(distintas(node), ["confirmacion / revision / funcional: el código dice decide, el modelo dice propone",
                                               "confirmacion / revision / no funcional: el código dice decide, el modelo dice propone"])


if __name__ == "__main__":
    unittest.main()
