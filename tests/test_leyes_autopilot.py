"""El conductor autopilot como leyes probadas en Bend (lp1), sin leyes vacías (lp2) e igual a autopilot.decidir (lp3).

El modelo vive en modelos/autopilot/. Sin `bend`, `lean`/`leanc` o `node` la prueba que los necesita se omite y dice cuál falta.
"""
import importlib.util
import itertools
import json
import shlex
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_leyes_bend import ENTORNO, ROOT, requiere  # noqa: E402
from test_verdict_bend import herramientas, veredicto  # noqa: E402
from oracle_factory import autopilot  # noqa: E402

MODELO = ROOT / "modelos" / "autopilot"
ORIGINAL_DECIDIR = autopilot.decidir

MUTANTES = {
    "cerrar lo corre el agente": ("    case Cerrar{}:\n      Salida{PedirAPersona{}, Cerrar{}}", "    case Cerrar{}:\n      Salida{Actuar{}, Cerrar{}}"),
    "con frenos no frena": ("    case True{}:\n      frena()\n    case False{}:\n      sin_frenos",
                            "    case True{}:\n      sin_frenos(s, terminada, segundo, candidato, propuesta)\n    case False{}:\n      sin_frenos"),
    "confirmar medidas se delega": ("    case MedirConfirmar{}:\n      Salida{PedirAPersona{}, MedirConfirmar{}}", "    case MedirConfirmar{}:\n      delega()"),
    "revisar con propuesta lo corre el agente": ("    case False{} True{} True{}:\n      Salida{PedirAPersona{}, Revisar{}}",
                                                 "    case False{} True{} True{}:\n      Salida{Actuar{}, Revisar{}}"),
    "el segundo revisor no se pide": ("    case True{} _ _:\n      Salida{Actuar{}, PedirRevision{}}", "    case True{} _ _:\n      Salida{PedirAPersona{}, Revisar{}}"),
    "es mecánico incluye cerrar": ("    case Sincronizar{}:\n      True{}\n    case _:", "    case Sincronizar{}:\n      True{}\n    case Cerrar{}:\n      True{}\n    case _:"),
    "delegar trae un comando": ("def delega() -> Salida:\n  Salida{DelegarAlAgente{}, SinPaso{}}", "def delega() -> Salida:\n  Salida{DelegarAlAgente{}, Importar{}}"),
    "aprobar el sensor lo corre el agente": ("    case AprobarSensor{}:\n      frena()", "    case AprobarSensor{}:\n      Salida{Actuar{}, AprobarSensor{}}"),
    "la prosa frena": ("    case Prosa{}:\n      delega()", "    case Prosa{}:\n      frena()"),
    "importar se le pide a una persona": ("    case Importar{}:\n      Salida{Actuar{}, Importar{}}", "    case Importar{}:\n      Salida{PedirAPersona{}, Importar{}}"),
    "termina sin estar cerrado": ("        case False{}:\n          frena()\n    case Prosa{}:", "        case False{}:\n          Salida{Terminado{}, SinPaso{}}\n    case Prosa{}:"),
    "sin candidato pide la revisión": ("    case False{}:\n      delega()\n\ndef sin_frenos", "    case False{}:\n      Salida{Actuar{}, s}\n\ndef sin_frenos"),
    "revisar sin propuesta se le pide igual": ("    case False{} True{} False{}:\n      delega()", "    case False{} True{} False{}:\n      Salida{PedirAPersona{}, Revisar{}}"),
}

ID, CANDIDATO = "20261118-000000-abc-x", "abc1234"
# Un comando que el parser real de Factory acepta por cada clase de próximo paso, como los da `estado`.
PASOS = {
    "SinPaso": None, "Prosa": "corregí los hallazgos y commiteá", "Ilegible": "algo que no es un comando",
    "AprobarSpec": f"oracle-factory aprobar-spec {ID}", "Revisar": f"oracle-factory revisar {ID}", "Cerrar": f"oracle-factory cerrar {ID}",
    "Abandonar": f"oracle-factory abandonar {ID}", "Modo": f"oracle-factory modo {ID} autonomo", "Autonomia": "oracle-factory autonomia integracion autonomo",
    "Soltar": f"oracle-factory soltar {ID}", "DecidirUnion": f"oracle-factory decidir-union {ID} revision nuestro",
    "Conectar": "oracle-factory conectar /tmp/almacen", "Desconectar": "oracle-factory desconectar", "Importar": f"oracle-factory importar {ID}",
    "Juzgar": f"oracle-factory juzgar {ID}", "PedirRevision": f"oracle-factory pedir-revision {ID} --a codex",
    "RevisionPreparar": f"oracle-factory revision-preparar {ID}", "Tomar": f"oracle-factory tomar {ID}", "Mensaje": f"oracle-factory mensaje {ID} hola",
    "Sincronizar": "oracle-factory sincronizar", "MedirConfirmar": f"oracle-factory medir {ID} --confirmar",
    "MedirListar": f"oracle-factory medir {ID} --listar", "MedirOtro": f"oracle-factory medir {ID} --requisito r --medida m",
    "AprobarSensor": "oracle-factory aprobar-sensor", "Evidencia": f"oracle-factory evidencia {ID}", "Otro": f"oracle-factory estado {ID}",
}
ACCION = {"terminado": "Terminado", "frenar": "Frenar", "pedir_a_persona": "PedirAPersona", "delegar_al_agente": "DelegarAlAgente", "actuar": "Actuar"}
POR_NOMBRE = {"aprobar-spec": "AprobarSpec", "revisar": "Revisar", "cerrar": "Cerrar", "abandonar": "Abandonar", "modo": "Modo",
              "autonomia": "Autonomia", "soltar": "Soltar", "decidir-union": "DecidirUnion", "conectar": "Conectar", "desconectar": "Desconectar",
              "importar": "Importar", "juzgar": "Juzgar", "pedir-revision": "PedirRevision", "revision-preparar": "RevisionPreparar",
              "tomar": "Tomar", "mensaje": "Mensaje", "sincronizar": "Sincronizar", "aprobar-sensor": "AprobarSensor", "evidencia": "Evidencia"}


def pruebas_valen(bend: str, carpeta: Path) -> tuple[int, str]:
    r = subprocess.run([bend, "PROOF.bend"], cwd=carpeta, env=ENTORNO, capture_output=True, text=True, timeout=120)
    return r.returncode, r.stdout + r.stderr


def sobrevivientes(bend: str, modelo: Path = MODELO) -> list[str]:
    original = (modelo / "autopilot.bend").read_text(encoding="utf-8")
    vivos = []
    for nombre, (viejo, nuevo) in MUTANTES.items():
        if original.count(viejo) != 1:
            raise AssertionError(f"el mutante «{nombre}» ya no encuentra su línea en autopilot.bend")
        with tempfile.TemporaryDirectory() as tmp:
            copia = Path(tmp) / "q"
            shutil.copytree(modelo, copia)
            (copia / "autopilot.bend").write_text(original.replace(viejo, nuevo), encoding="utf-8")
            codigo, salida = pruebas_valen(bend, copia)
            if codigo == 0 and "ALL PROOFS CHECK" in salida:
                vivos.append(nombre)
    return vivos


def sub_del_comando(comando) -> str:
    """El subcomando del comando que devuelve decidir, leído con el parser real de Factory; SinPaso si no trae comando."""
    if comando is None:
        return "SinPaso"
    args = autopilot._analizar(shlex.split(comando)[1:])
    if args.comando == "medir":
        return "MedirConfirmar" if args.confirmar else "MedirListar" if args.listar else "MedirOtro"
    return POR_NOMBRE.get(args.comando, "Otro")


FASES = ("revision", "cerrada", "abandonada")  # el modelo sólo distingue si el cambio está terminado (cerrado o abandonado)


def datos(frenos, fase, sub, segundo, candidato, propuesta) -> dict:
    return {"proximo_paso": PASOS[sub], "fase": fase, "candidato": CANDIDATO if candidato else None,
            "frenos": [{"id": "freno"}] if frenos else [], "segundo_revisor": "agy" if segundo else None,
            "propuesta_de_revision": {"decision": "aprobar", "candidato": CANDIDATO, "actor": "claude-code", "cuando": "2026-11-18"} if propuesta else None}


def distintas(node: str) -> list[str]:
    # Hallazgo autopilot-abandonada-sin-paso de codex: las tres fases, no sólo cerrada o en curso.
    combinaciones = [(f, fase, s, g, k, p) for f, g, k, p in itertools.product((True, False), repeat=4) for fase in FASES for s in PASOS]
    script = (f"import Q from {json.dumps(str(MODELO / 'autopilot.mjs'))};\n"
              f"const casos = {json.dumps(combinaciones)};\n"
              "console.log(JSON.stringify(casos.map(([f, fase, s, g, k, p]) => { const r = Q.decidir(f, fase !== 'revision', {$: s}, g, k, p); return [r.accion.$, r.sub.$]; })));\n")
    r = subprocess.run([node, "--input-type=module", "-e", script], capture_output=True, text=True, timeout=60, check=True)
    modelo = json.loads(r.stdout)
    assert len(modelo) == len(combinaciones) == 1248
    salida = []
    for combinacion, dice_el_modelo in zip(combinaciones, modelo):
        d = autopilot.decidir(datos(*combinacion))
        dice_el_codigo = [ACCION[d["accion"]], sub_del_comando(d["comando"])]
        if dice_el_codigo != dice_el_modelo:
            salida.append(f"{combinacion}: el código dice {dice_el_codigo}, el modelo dice {dice_el_modelo}")
    return salida


def generador(modelo: Path = MODELO):
    spec = importlib.util.spec_from_file_location("generar_autopilot", modelo / "generar.py")
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    return modulo


class Leyes(unittest.TestCase):
    # --- lp1: las leyes del autopilot están probadas ----------------------------------------------------------------------
    def test_lp1_bend_acepta_las_pruebas_generadas_y_el_modelo_compilado_esta_al_dia(self):
        bend = requiere("bend")
        codigo, salida = pruebas_valen(bend, MODELO)
        self.assertEqual(codigo, 0, salida)
        self.assertIn("ALL PROOFS CHECK", salida)
        self.assertEqual((MODELO / "PROOF.bend").read_text(encoding="utf-8"), generador().pruebas(),
                         "modelos/autopilot/PROOF.bend no es el que escribe generar.py: corré python3 modelos/autopilot/generar.py")
        with tempfile.TemporaryDirectory() as tmp:
            copia = Path(tmp) / "q"
            shutil.copytree(MODELO, copia)
            (copia / "autopilot.mjs").unlink()
            subprocess.run([bend, "autopilot.bend", "-o", "autopilot.mjs"], cwd=copia, env=ENTORNO, check=True, capture_output=True, timeout=120)
            self.assertEqual((copia / "autopilot.mjs").read_bytes(), (MODELO / "autopilot.mjs").read_bytes(),
                             "modelos/autopilot/autopilot.mjs no es el que genera bend: regeneralo con bend autopilot.bend -o autopilot.mjs")

    def test_lp1_cada_ley_tiene_su_prueba(self):
        leyes = {l.split()[1].rstrip(":") for l in (MODELO / "LAWS.bend").read_text(encoding="utf-8").splitlines() if l.startswith("law ")}
        pruebas = {l.split("(")[0].removeprefix("def Laws.") for l in generador().pruebas().splitlines() if l.startswith("def Laws.")}
        self.assertEqual(len(leyes), 22)
        self.assertEqual(leyes, pruebas)

    def test_lp1_generar_escribe_proof_al_correrlo_y_no_al_importarlo(self):
        with tempfile.TemporaryDirectory() as tmp:
            copia = Path(tmp) / "q"
            shutil.copytree(MODELO, copia)
            (copia / "PROOF.bend").unlink()
            esperado = generador(copia).pruebas()
            self.assertFalse((copia / "PROOF.bend").exists(), "importar generar.py no tiene que escribir PROOF.bend")
            subprocess.run([sys.executable, "generar.py"], cwd=copia, check=True, capture_output=True, timeout=60)
            self.assertEqual((copia / "PROOF.bend").read_text(encoding="utf-8"), esperado)

    def test_lp1_el_nucleo_probado_acepta_las_pruebas(self):
        codigo, salida = veredicto(herramientas(), MODELO)
        self.assertEqual(codigo, 0, salida)
        self.assertIn("ALL PROOFS CHECK", salida)

    def test_lp1_sin_bend_se_omite_diciendo_que_falta(self):
        with tempfile.TemporaryDirectory() as vacio, self.assertRaises(unittest.SkipTest) as omitida:
            requiere("bend", path=vacio)
        self.assertIn("falta bend", str(omitida.exception))


class SinLeyesVacias(unittest.TestCase):
    # --- lp2: ninguna ley del autopilot está vacía ------------------------------------------------------------------------
    def test_lp2_cada_mutante_del_modelo_hace_fallar_alguna_prueba(self):
        self.assertEqual(sobrevivientes(requiere("bend")), [])

    def test_lp2_sin_la_ley_de_que_nada_de_persona_es_mecanico_un_mutante_sobrevive(self):
        bend = requiere("bend")
        with tempfile.TemporaryDirectory() as tmp:
            copia = Path(tmp) / "q"
            shutil.copytree(MODELO, copia)
            for archivo, inicio in (("LAWS.bend", "\n# Ninguna decisión de una persona"), ("PROOF.bend", "\ndef Laws.lo_de_persona_no_es_mecanico")):
                texto = (copia / archivo).read_text(encoding="utf-8")
                self.assertEqual(texto.count(inicio), 1, archivo)
                desde = texto.index(inicio)
                hasta = min((i for i in (texto.find("\n\n# ", desde + 1), texto.find("\n\ndef ", desde + 1), texto.find("\n\nlaw ", desde + 1)) if i != -1),
                            default=len(texto))
                (copia / archivo).write_text(texto[:desde] + texto[hasta:], encoding="utf-8")
            codigo, salida = pruebas_valen(bend, copia)
            self.assertEqual(codigo, 0, salida)
            self.assertEqual(sobrevivientes(bend, copia), ["es mecánico incluye cerrar"])


class ModeloYCodigo(unittest.TestCase):
    # --- lp3: el modelo del autopilot coincide con el código (1248 combinaciones: 2^4 banderas × 3 fases × 26 pasos) --------------------------------------------------------------
    def test_lp3_el_modelo_compilado_y_decidir_dicen_lo_mismo(self):
        self.assertEqual(distintas(requiere("node")), [])

    def test_lp3_un_cambio_abandonado_sin_paso_termina_en_el_modelo_y_en_el_codigo(self):
        # Hallazgo autopilot-abandonada-sin-paso de codex: la comparación tiene que recorrer la fase abandonada.
        node = requiere("node")
        for fase, esperado in (("abandonada", "terminado"), ("cerrada", "terminado"), ("revision", "frenar")):
            with self.subTest(fase=fase):
                self.assertEqual(autopilot.decidir(datos(False, fase, "SinPaso", False, False, False))["accion"], esperado)
        script = (f"import Q from {json.dumps(str(MODELO / 'autopilot.mjs'))};\n"
                  "console.log(JSON.stringify([true, false].map(t => Q.decidir(false, t, {$: 'SinPaso'}, false, false, false).accion.$)));\n")
        r = subprocess.run([node, "--input-type=module", "-e", script], capture_output=True, text=True, timeout=60, check=True)
        self.assertEqual(json.loads(r.stdout), ["Terminado", "Frenar"])
        with patch.object(autopilot, "decidir", lambda d: {"accion": "frenar", "comando": None} if d.get("fase") == "abandonada" and not d.get("proximo_paso")
                          else ORIGINAL_DECIDIR(d)):
            self.assertTrue(any("'abandonada', 'SinPaso'" in x for x in distintas(node)))

    def test_lp3_si_el_codigo_cambia_y_el_modelo_no_se_nombran_las_combinaciones(self):
        node = requiere("node")
        with patch.object(autopilot, "PERSONA", autopilot.PERSONA - {"cerrar"}):
            diferencias = distintas(node)
        self.assertEqual(len(diferencias), 24)  # cerrar sin frenos: 2^3 banderas × 3 fases
        self.assertTrue(all("'Cerrar'" in d and "el código dice ['Frenar', 'SinPaso']" in d for d in diferencias), diferencias[:3])


if __name__ == "__main__":
    unittest.main()
