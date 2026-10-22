"""La guía para agentes: un bloque de AGENTS.md que se arma desde la CLI (`oracle-factory agentes`) y se verifica.

Lo que dice sale del código: quién decide qué en cada modo (modos.via_agente) y qué comandos son de una persona o de un
agente (las listas de abajo, que tests/test_agentes.py contrasta con lo que hace la CLI). Lo que el proyecto escribió en
AGENTS.md fuera del bloque no se toca.
"""
from __future__ import annotations

from . import modos

INICIO = "<!-- oracle-factory agentes: inicio (generado por `oracle-factory agentes`; no se edita a mano) -->"
FIN = "<!-- oracle-factory agentes: fin -->"
CLAUDE = "@AGENTS.md"
# Las cuatro decisiones del flujo: con --agente, decide, propone o no puede según el modo (modos.via_agente, la tabla).
DECISIONES = (
    ("spec", "aprobar-spec ID", "aprobar la propuesta y la spec"),
    ("medidas", "medir ID --requisito R --medida M --quitar-sin-medir", "elegir las medidas de un requisito"),
    ("revision", "revision ID --informe INFORME --revisor R --decision aprobar|cambios --hallazgos-abiertos N",
     "registrar la decisión de una revisión"),
    ("cierre", "cerrar ID", "cerrar el cambio"),
)
# Sólo de una persona, en cualquier modo: con --agente se niegan o dejan sólo una propuesta.
PERSONA = (
    ("medir ID --confirmar", "confirmar las medidas que propuso un agente"),
    ("revisar ID", "revisar paso a paso y registrar la decisión (un agente la propone con --agente --decision --motivo)"),
    ("abandonar ID", "abandonar el cambio (un agente propone el motivo con --agente --motivo)"),
    ("modo ID MODO", "bajar la intervención humana de un cambio"),
    ("soltar ID", "dejar de ser responsable de un cambio"),
    ("decidir-union ID CAMPO nuestro|suyo", "elegir qué vale cuando dos ramas decidieron distinto"),
    ("kb revisada NOTA", "marcar revisada una nota de personas del vault"),
)
# Los de un agente, siempre con --agente NOMBRE (queda registrado como agente); no deciden nada.
AGENTE = (
    ("nuevo --capacidad C --sufijo S \"TÍTULO\"", "crear un cambio con su propuesta y su spec para completar"),
    ("importar ID", "importar los requisitos de la spec aprobada"),
    ("pedir-revision ID --a REVISOR", "pedir una revisión independiente del candidato"),
    ("revision-preparar ID", "preparar el informe para que una persona revise"),
    ("revisar ID --decision aprobar|cambios --motivo M", "proponer la decisión de la revisión"),
    ("juzgar ID", "correr Oracle sobre la evidencia del candidato"),
    ("mensaje ID \"TEXTO\"", "dejar un mensaje en el registro del cambio"),
    ("tomar ID", "sumarse como agente al cambio"),
    ("abandonar ID --motivo M", "proponer el motivo de un abandono"),
)
LECTURA = ("estado ID", "preguntar \"PREGUNTA\"", "por-que ARCHIVO:LÍNEA", "buscar TEXTO", "log ID", "resumen", "listar")
QUE = {"decide": "decide", "propone": "propone", "rechaza": "no puede"}


def bloque(modo_por_defecto: str) -> str:
    filas = []
    for modo in modos.MODOS:
        celdas = []
        for decision in modos.DECISIONES:
            funcional, no_funcional = (QUE[modos.via_agente(modo, decision, [t])] for t in ("funcional", "no funcional"))
            celdas.append(funcional if funcional == no_funcional else f"{funcional} (funcional) / {no_funcional} (no funcional)")
        nombre = f"**{modo}** (el de este proyecto)" if modo == modo_por_defecto else modo
        filas.append(f"| {nombre} | " + " | ".join(celdas) + " |")
    lineas = [
        INICIO, "",
        "## Trabajar con Oracle Factory (para agentes)", "",
        "Este proyecto usa Oracle Factory: cada cambio tiene su propuesta, su spec, requisitos medidos por Oracle, una "
        "revisión y un cierre. Las decisiones son de una persona; un agente trabaja, propone y deja todo registrado.", "",
        "- Corré cada comando de Factory como agente: `oracle-factory --agente NOMBRE …` (tu nombre: `claude-code`, `codex`…). "
        "Sin `--agente` la acción se registra como de una persona, y no lo sos.",
        "- El próximo paso de un cambio lo dice `oracle-factory estado ID` (o `--json`): seguilo en vez de adivinar.",
        "- Antes de implementar, la spec tiene que estar aprobada por una persona. No edites a mano `.factory/`, "
        "`tareas/` ni `kb/` generado.", "",
        "### Las decisiones, según el modo de trabajo", "",
        "Cada decisión tiene su comando. Con `--agente`, según el modo del cambio, el agente la decide, la propone (cuenta "
        "cuando una persona la confirma repitiendo el comando sin `--agente`) o no puede; una persona, desde su terminal, "
        "siempre decide:", "",
        *[f"- {nombre.capitalize()}: `oracle-factory {c}` ({q})" for nombre, c, q in
          ((n.replace("revision", "revisión"), c, q) for n, c, q in DECISIONES)], "",
        "| Modo | Spec | Medidas | Revisión | Cierre |", "| --- | --- | --- | --- | --- |", *filas, "",
        "### Sólo de una persona, en cualquier modo", "",
        "Con `--agente` se niegan o dejan sólo una propuesta. Pedíselos a la persona, con el comando listo para copiar:", "",
        *[f"- `oracle-factory {c}`: {q}" for c, q in PERSONA], "",
        "### Comandos de un agente (con `--agente NOMBRE`)", "",
        *[f"- `oracle-factory --agente NOMBRE {c}`: {q}" for c, q in AGENTE], "",
        "### Consultar el proyecto (sólo lectura)", "",
        "- " + ", ".join(f"`oracle-factory {c}`" for c in LECTURA) + ".",
        "- `preguntar` devuelve pasajes vigentes del conocimiento del proyecto con su cita: úsalo antes de suponer por qué "
        "algo es como es.",
        "- Por MCP, las mismas consultas como herramientas: `claude mcp add factory -- oracle-factory --proyecto RUTA mcp` "
        "(o `codex mcp add …`).", "",
        FIN,
    ]
    return "\n".join(lineas) + "\n"


class MarcasRotas(ValueError):
    """AGENTS.md tiene las marcas del bloque repetidas, sin cerrar o al revés: no se adivina qué borrar."""


def con_bloque(texto: str, nuevo: str) -> str:
    """El texto de AGENTS.md con el bloque nuevo: en su lugar si ya estaba (un solo par de marcas, en orden), al final si
    no había ninguna. Con las marcas rotas no se toca nada: lo arregla una persona."""
    inicios, fines = texto.count(INICIO), texto.count(FIN)
    if inicios == fines == 0:
        return (texto.rstrip("\n") + "\n\n" if texto.strip() else "") + nuevo
    if inicios != 1 or fines != 1 or texto.index(INICIO) > texto.index(FIN):
        raise MarcasRotas(f"AGENTS.md tiene {inicios} marca(s) de inicio y {fines} de fin del bloque de Factory; dejá un "
                          "solo par (o ninguno) y volvé a correr oracle-factory agentes. No cambié nada")
    antes, resto = texto.split(INICIO, 1)
    despues = resto.split(FIN, 1)[1].lstrip("\n")
    return antes + nuevo + (("\n" + despues) if despues else "")


def con_claude(texto: str) -> str:
    if any(linea.strip() == CLAUDE for linea in texto.splitlines()):
        return texto
    return (texto.rstrip("\n") + "\n\n" if texto.strip() else "") + CLAUDE + "\n"
