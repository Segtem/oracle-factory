"""El conductor `autopilot`, la mitad que observa y razona: un bucle de control de proceso determinista, sin modelo de lenguaje.

Lee los datos de `estado` (el próximo paso y los frenos) y dice qué viene, por reglas fijas. No actúa: quien corre los comandos y lanza
al agente es `conductor.py` (la otra mitad). Ante la duda frena: un paso que no reconoce, un comando incompleto o un dato ilegible devuelven
la decisión a una persona, y las decisiones de una persona (`PERSONA`) lo son aunque una etapa esté en `autonomo`."""
from __future__ import annotations

import contextlib
import io
import re
import shlex

# Decisiones que son sólo de una persona (docs/agentes.md): el conductor las pide, nunca las toma.
PERSONA = frozenset({"aprobar-spec", "revisar", "cerrar", "abandonar", "modo", "autonomia", "soltar", "decidir-union"})
# Comandos mecánicos de Factory: un agente los corre con `--agente NOMBRE`.
MECANICO = frozenset({"importar", "juzgar", "pedir-revision", "revision-preparar", "tomar", "mensaje"})
# Un paso en prosa que `estado` da cuando hay trabajo creativo: corregir, commitear, resolver.
PROSA = ("corregí", "commiteá", "resolvé")
MARCADOR = re.compile(r"^RUTA_\w*$")  # un comando que estado deja por completar: «--con RUTA_DE_HECHOS»


def _analizar(argumentos: list[str]):
    """Los argumentos como los entiende el parser real de Factory (opciones globales como --agente o --proyecto antes del subcomando, `=`,
    abreviaturas); None si no los acepta. Así el conductor no tiene su propia lectura de la línea de comandos."""
    from .parser import construir_parser
    try:
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            return construir_parser().parse_args(argumentos)
    except SystemExit:
        return None


def ultima_propuesta(estado) -> dict | None:
    """La última propuesta de revisión de un agente ({decision, candidato, actor, cuando}) del registro de un cambio; None si no hay o no se lee.
    Una propuesta de quien no es un agente (una persona decide con `revisar`, que es otro evento) no cuenta."""
    eventos = estado.get("eventos") if isinstance(estado, dict) else None
    if not isinstance(eventos, list):
        return None
    for e in reversed(eventos):
        if isinstance(e, dict) and e.get("accion") == "revision_propuesta" and e.get("tipo_actor") == "agente":
            return {k: e.get(k) for k in ("decision", "candidato", "actor", "cuando")}
    return None


SHA = re.compile(r"[0-9a-fA-F]{7,40}")  # un candidato como lo guarda Factory: un commit de 7 caracteres o más
DECISIONES = ("aprobar", "cambios")


def _propuesta_del_candidato(propuesta, candidato) -> bool:
    """Si la propuesta es completa y del candidato vigente (con 7 caracteres y en minúsculas, como los guarda Factory). Una propuesta incompleta
    o con algo que no se entiende (decisión, candidato, actor o fecha) no cuenta: el agente tiene que dejarla bien."""
    if not isinstance(propuesta, dict):
        return False
    propio = propuesta.get("candidato")
    if not (isinstance(propio, str) and SHA.fullmatch(propio) and propuesta.get("decision") in DECISIONES
            and all(isinstance(propuesta.get(k), str) and propuesta[k] for k in ("actor", "cuando"))):
        return False
    return propio[:7].lower() == candidato[:7].lower()


GLOBALES = ("--agente", "--proyecto")  # las opciones del parser que van antes del subcomando y llevan un valor


def argumentos_mecanicos(comando) -> list[str] | None:
    """Los argumentos de un comando mecánico (sin `oracle-factory` ni las opciones globales), listos para que el conductor los corra con
    su propio `--agente`; None si el comando no es uno que un agente pueda correr (una decisión de una persona o uno que no se reconoce).
    Es la defensa de quien ejecuta: no depende de que `decidir` haya clasificado bien."""
    try:
        tokens = shlex.split(comando) if isinstance(comando, str) else []
    except ValueError:
        return None
    if len(tokens) < 3 or tokens[0] != "oracle-factory" or any(MARCADOR.match(t) for t in tokens):
        return None
    args = _analizar(tokens[1:])
    if args is None or args.comando not in MECANICO:
        return None
    i = 1
    while i < len(tokens) and tokens[i].startswith("--"):  # las opciones globales, con su valor, abreviadas o con «=»
        nombre = tokens[i].split("=")[0]
        if len(nombre) < 3 or not any(g.startswith(nombre) for g in GLOBALES):
            return None
        i += 1 if "=" in tokens[i] else 2
    return tokens[i:] if i < len(tokens) and tokens[i] == args.comando else None


def _decision(accion, quien=None, comando=None, instruccion=None, motivo="", frenos=()):
    return {"accion": accion, "quien": quien, "comando": comando, "instruccion": instruccion, "motivo": motivo, "frenos": list(frenos)}


def _frena(motivo: str, frenos=()):
    return _decision("frenar", "persona", motivo=motivo, frenos=frenos)


def decidir(datos) -> dict:
    """{accion, quien, comando, instruccion, motivo, frenos} de los datos de `estado` (`lecturas.datos_estado`).

    accion: `terminado`, `frenar`, `pedir_a_persona`, `delegar_al_agente` o `actuar`. Frenar nunca trae comando ni instrucción."""
    if not isinstance(datos, dict):
        return _frena("no se pudieron leer los datos del cambio")
    paso, fase, candidato = datos.get("proximo_paso"), datos.get("fase"), datos.get("candidato")
    frenos = datos.get("frenos")
    if not isinstance(frenos, list) or not all(isinstance(x, dict) for x in frenos):
        return _frena("no se pudieron leer los frenos del cambio")
    if frenos:
        return _frena("hay frenos: " + "; ".join(f"{x.get('id')}" for x in frenos), frenos)
    if fase in ("cerrada", "abandonada") and not paso:
        return _decision("terminado", motivo=f"el cambio está {fase}")
    if not isinstance(paso, str) or not paso.strip():
        return _frena("el cambio no terminó y estado no dice cuál es el próximo paso")
    if "faltan archivos" in paso:
        return _frena("faltan archivos del cambio: se recuperan desde Git, no con un comando de Factory")
    if paso.startswith(PROSA):
        return _decision("delegar_al_agente", "agente", instruccion=paso, motivo="el próximo paso es trabajo sobre el código o las pruebas")
    try:
        tokens = shlex.split(paso)
    except ValueError:
        return _frena("el próximo paso no se puede leer como un comando")
    if len(tokens) < 3 or tokens[0] != "oracle-factory":
        return _frena("el próximo paso no es un comando ni un trabajo que el conductor conozca")
    if any(MARCADOR.match(t) for t in tokens):
        return _frena("el comando del próximo paso está incompleto: falta una ruta que decidir")
    args = _analizar(tokens[1:])
    if args is None:
        return _frena("el próximo paso no es un comando que Factory acepte tal cual")
    sub = args.comando
    if sub == "medir" and getattr(args, "confirmar", False):
        return _decision("pedir_a_persona", "persona", paso, motivo="confirmar las medidas es sólo de una persona")
    if sub == "medir" and getattr(args, "listar", False):
        return _decision("delegar_al_agente", "agente", instruccion="elegí las medidas de cada requisito (oracle-factory medir ... --requisito R --medida M) y proponelas",
                         motivo="elegir medidas es trabajo del agente; confirmarlas es de una persona")
    if sub == "revisar" and isinstance(candidato, str) and candidato and not _propuesta_del_candidato(datos.get("propuesta_de_revision"), candidato):
        return _decision("delegar_al_agente", "agente", motivo="antes de pedirle la revisión a una persona, el agente prepara el informe y deja su propuesta",
                         instruccion=f"dejá tu propuesta de revisión del candidato {candidato}: corré `oracle-factory --agente NOMBRE revision-preparar {args.id}` y proponé "
                         f"la decisión con `oracle-factory --agente NOMBRE revisar {args.id} --decision aprobar|cambios --motivo MOTIVO` (rondas, evidencia, hallazgos, "
                         f"mutaciones y límites); la decisión final es de una persona; después: {paso}")
    if sub in PERSONA:
        return _decision("pedir_a_persona", "persona", paso, motivo=f"«{sub}» es una decisión de una persona")
    if sub in ("pedir-revision", "revision-preparar") and not candidato:
        return _decision("delegar_al_agente", "agente", instruccion="construí el cambio según la spec aprobada: pruebas primero, evidencia y commit del candidato; "
                         f"después: {paso}", motivo="no hay candidato vigente: antes de revisar hay que construir")
    if sub in MECANICO:
        return _decision("actuar", "agente", paso, motivo=f"«{sub}» es un comando mecánico de Factory: lo corre un agente con --agente")
    return _frena(f"«{sub}» no es un paso que el conductor conozca")
