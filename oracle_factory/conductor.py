"""El conductor `autopilot`, la mitad que actúa: el bucle observar → razonar → dejar el porqué → actuar → volver a observar.

Razona `autopilot.decidir` (determinista); acá sólo se ejecuta, con topes y rastro. Nunca corre una decisión de una persona (aunque
llegue mal clasificada), y se detiene ante un freno, un error, la falta de progreso o un tope. El ejecutor y el reloj se pasan de
afuera para probar el bucle sin procesos ni esperas; `ejecutor` arma los de verdad."""
from __future__ import annotations

import os
import subprocess
import sys
import time

from . import autopilot

MAX_MENSAJE = 2000  # el largo de un mensaje del registro


def _recortar(texto: str, largo: int) -> str:
    return texto if len(texto) <= largo else texto[: largo - 1] + "…"


def _proceso(argv, cwd, plazo: float, env=None) -> tuple[int, str]:
    """(código, salida) de un proceso con un plazo; un plazo vencido o un proceso que no arranca son un código distinto de cero."""
    try:
        p = subprocess.run(argv, cwd=cwd, capture_output=True, text=True, stdin=subprocess.DEVNULL, timeout=max(1, plazo), env=env)
    except subprocess.TimeoutExpired:
        return 124, "se acabó el plazo"
    except (OSError, ValueError) as e:
        return 127, str(e)
    return p.returncode, (p.stdout + p.stderr).strip()


def ejecutor(raiz, agente: str):
    """(correr, lanzar): `correr(argv, plazo)` corre un comando de Factory como `agente` en un proceso aparte; `lanzar(argv, plazo)`, un
    agente externo, con FACTORY_AGENTE puesto para que lo que haga con Factory quede a su nombre."""
    def correr(argv, plazo):
        return _proceso([sys.executable, "-c", "import sys; from oracle_factory.cli import main; sys.exit(main())",
                         "--proyecto", str(raiz), "--agente", agente, *argv], raiz, plazo)

    def lanzar(argv, plazo):
        return _proceso(argv, raiz, plazo, {**os.environ, "FACTORY_AGENTE": agente})
    return correr, lanzar


def _porque(decision: dict) -> str:
    detalle = f"Comando: {decision['comando']}" if decision["comando"] else f"Instrucción: {decision['instruccion']}"
    return _recortar(f"autopilot {decision['accion']}: {decision['motivo']}. {detalle}", MAX_MENSAJE)


def bucle(ident: str, observar, correr, lanzar, lanzar_cmd: list[str] | None, max_pasos: int, max_minutos: float, ahora=time.monotonic) -> dict:
    """{motivo, pasos, decision, aviso?}: repite hasta que algo lo detenga y deja un mensaje final con el motivo.

    `observar()` da los datos de estado; `correr(argv, plazo)` y `lanzar(argv, plazo)` dan (código, salida)."""
    pasos, previa, decision, inicio = [], None, None, ahora()

    def detener(motivo: str) -> dict:
        texto = f"autopilot se detuvo: {motivo}" + (f". Comando para una persona: {decision['comando']}" if decision and decision["accion"] == "pedir_a_persona" else "")
        codigo, salida = correr(["mensaje", ident, _recortar(texto, MAX_MENSAJE)], 60)
        resultado = {"motivo": motivo, "pasos": pasos, "decision": decision}
        if codigo:
            resultado["aviso"] = f"no se pudo dejar el mensaje final en el registro: {salida[:200]}"
        return resultado

    while True:
        transcurrido = ahora() - inicio
        if len(pasos) >= max_pasos:
            return detener(f"se llegó al tope de {max_pasos} pasos")
        if transcurrido >= max_minutos * 60:
            return detener(f"se llegó al tope de {max_minutos:g} minutos")
        try:
            decision = autopilot.decidir(observar())
        except Exception as e:  # noqa: BLE001 — un estado que no se puede leer detiene el bucle, nunca lo rompe
            return detener(f"no se pudo leer el estado del cambio: {str(e)[:200]}")
        accion = decision["accion"]
        if accion in ("terminado", "frenar", "pedir_a_persona"):
            return detener(decision["motivo"])
        clave = (accion, decision["comando"], decision["instruccion"])
        if clave == previa:
            return detener("sin progreso: la misma decisión dos veces seguidas")
        argv = None
        if accion == "actuar":
            argv = autopilot.argumentos_mecanicos(decision["comando"])
            if argv is None:
                return detener("el comando no es uno que un agente pueda correr (es de una persona o no se reconoce): no se ejecuta")
        elif not lanzar_cmd:
            return detener("hay trabajo para un agente y falta --lanzar COMANDO para lanzarlo")
        previa = clave
        plazo = max_minutos * 60 - transcurrido
        codigo, _ = correr(["mensaje", ident, _porque(decision)], 60)
        if codigo:
            return detener("no se pudo dejar el porqué en el registro: no se actúa sin dejarlo")
        codigo, salida = correr(argv, plazo) if accion == "actuar" else lanzar([*lanzar_cmd, decision["instruccion"]], plazo)
        pasos.append({"accion": accion, "comando": decision["comando"], "instruccion": decision["instruccion"], "motivo": decision["motivo"],
                      "codigo": codigo, "salida": _recortar(salida, 300)})
        if codigo:
            return detener(f"el paso falló (código {codigo}): {_recortar(salida, 200)}")
