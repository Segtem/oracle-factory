"""Los textos que `nuevo` crea para un cambio: propuesta, spec, diseño y tareas, enteros en un idioma.

Lo que exige el formato no se traduce: `# Capability:`, `## ADDED Requirements`, `### Requirement:`, `#### Scenario:`, `Tipo:`
y la marca de pendiente (la que impide aprobar mientras quede). El resto es del idioma."""
from __future__ import annotations

IDIOMAS = ("es", "en")
POR_DEFECTO = "es"

_ES = {
    "propuesta": """# {titulo}

## Por qué

TODO: qué problema humano resuelve y para quién.

## Qué cambia

TODO: comportamiento observable que se propone.

## Fuera de alcance

TODO: qué queda explícitamente fuera.

## Decisiones humanas

TODO: preguntas que requieren la decisión de una persona del equipo.
""",
    "spec": """# Capability: {capacidad}

## ADDED Requirements

### Requirement: comportamiento principal
Tipo: funcional
El sistema DEBE TODO: escribir una promesa que se pueda comprobar.

#### Scenario: caso esperado
- DADO TODO: un estado inicial conocido
- CUANDO TODO: la persona hace una acción
- ENTONCES TODO: sigue un resultado observable
""",
    "diseno": "# Diseño\n\nTODO: completar si la solución necesita una decisión técnica.\n",
    "tareas": """# Tareas

- [ ] Persona: revisar y aceptar proposal.md + spec.md.
- [ ] Agente: importar requisitos Oracle y señalar lo aún sin medir.
- [ ] Persona + agente: acordar medidas y evidencia para cada requisito.
- [ ] Agente: implementar y correr las pruebas del producto.
- [ ] Revisor: revisar el diff; registrar y resolver hallazgos.
- [ ] Agente: correr Oracle sobre hechos observados.
- [ ] Persona: revisar el informe y decidir si se cierra.
""",
}

_EN = {
    "propuesta": """# {titulo}

## Why

TODO: which human problem it solves and for whom.

## What changes

TODO: the observable behaviour being proposed.

## Out of scope

TODO: what is explicitly left out.

## Human decisions

TODO: questions that need a team member's decision.
""",
    "spec": """# Capability: {capacidad}

## ADDED Requirements

### Requirement: main behaviour
Tipo: funcional
The system SHALL TODO: write one testable promise.

#### Scenario: expected case
- GIVEN TODO: a known starting state
- WHEN TODO: the user performs an action
- THEN TODO: an observable result follows
""",
    "diseno": "# Design\n\nTODO: complete if the solution needs a technical decision.\n",
    "tareas": """# Tasks

- [ ] Person: review and accept proposal.md + spec.md.
- [ ] Agent: import the Oracle requirements and point out what is still unmeasured.
- [ ] Person + agent: agree the measures and evidence for each requirement.
- [ ] Agent: implement and run the product tests.
- [ ] Reviewer: review the diff; record and resolve findings.
- [ ] Agent: run Oracle on observed facts.
- [ ] Person: review the report and decide whether to close.
""",
}

TEXTOS = {"es": _ES, "en": _EN}


def validar(idioma: str) -> str:
    """El idioma, o un error que dice cuáles hay."""
    if idioma not in IDIOMAS:
        raise ValueError(f"idioma {idioma!r} no admitido: se admiten {' y '.join(IDIOMAS)}")
    return idioma
