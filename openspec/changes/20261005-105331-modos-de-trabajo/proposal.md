# Modos de trabajo según quién decide los requisitos

## Why

Hoy Factory tiene un solo modo: una persona decide cada gate. El [piloto con agentes](../../../tareas/20261004-121432-coordinar-dos/piloto-agentes-01/piloto.md) mostró dos cosas. Un agente coordinador puede llevar un cambio de punta a punta tomando todas las decisiones, y eso es útil para prototipos o trabajo de bajo riesgo. Pero Factory no lo distingue: aceptó por pipe las frases de confirmación y registró «workstation» como autor de todo, así que un cierre autónomo queda igual que uno humano.

Brian pidió tres formas de trabajar, según cuánto interviene la persona en las decisiones sobre requisitos funcionales y no funcionales. Elegir el modo es explícito, y cada decisión registra quién la tomó y en qué modo, para que un verde nunca aparente una aprobación humana que no existió.

## What changes

**Tres modos por cambio.** Se eligen al crear el cambio (`nuevo --modo`), con un valor por defecto por proyecto:

| Decisión | `autonomo` | `funcional` | `confirmacion` |
| --- | --- | --- | --- |
| Aceptar requisitos funcionales | agente | **persona decide** | agente propone, **persona confirma** |
| Aceptar requisitos no funcionales | agente | agente | agente propone, **persona confirma** |
| Medidas de un requisito | agente | según el tipo del requisito, como arriba | agente propone, **persona confirma** |
| Hallazgos de revisión | agente | según el tipo del requisito afectado | agente propone, **persona confirma** |
| Cierre | agente | **persona confirma** | **persona confirma** |

- **«Persona decide»:** la persona da la decisión y su motivo; el agente puede preparar opciones, pero no la registra. **«Persona confirma»:** el agente registra una propuesta completa y la persona la acepta o la rechaza tal cual.
- **Tipo de requisito.** Cada requisito de la spec declara `Tipo: funcional` o `Tipo: no funcional`. Si no lo declara, se trata como funcional (lo más estricto). `importar` lo guarda.
- **Actor en cada evento.** Cada evento de `factory.json` registra `actor` (persona o agente, con nombre o sesión), `modo` y si fue `decidio`, `propuso` o `confirmo`. Ya no se registra el usuario del sistema como si fuera el autor.
- **Gates humanos desde una terminal interactiva.** Una decisión registrada como de persona exige una terminal interactiva y rechaza la entrada por pipe. Las decisiones de agente se registran por la vía de agente, que nunca queda como humana. No es autenticación, pero hace imposible confundirlas por accidente.
- **El modo lo elige una persona.** Elegir `autonomo` o pasar a un modo con menos intervención humana exige confirmación humana. Pasar a uno con más intervención la puede pedir cualquiera. Cambiar de modo queda como evento e invalida las decisiones pendientes que el modo nuevo exige de otra forma.
- **El veredicto muestra el modo.** `estado`, el cierre y la nota de la tarea dicen el modo y quién decidió cada gate. Un cierre autónomo se lee como «cerrado por agente en modo autónomo».

## Out of scope

- Autenticar personas o agentes, y firmas criptográficas.
- Que el agente redacte specs o decida por sí mismo: Factory registra y aplica las reglas del modo, pero no ejecuta agentes.
- Clasificar requisitos automáticamente como funcionales o no funcionales.
- Modos por requisito individual o por equipo.
- Cambiar los gates de Oracle o de Clue.

## Human decisions

Pendiente: aceptar proposal.md y spec.md. Preguntas abiertas para Brian:

1. **¿Lo que hace Factory hoy es `confirmacion`, o se conserva un cuarto modo, `manual`, donde la persona decide (no sólo confirma) todo?** Se recomienda conservarlo como valor por defecto, porque es el comportamiento actual y el más estricto.
2. **En `funcional`, ¿el cierre lo confirma la persona** (lo propuesto) **o lo decide el agente cuando todos los gates funcionales ya pasaron por la persona?**
3. **Requisito sin tipo:** ¿se trata como funcional (lo propuesto) o `importar` lo rechaza?
4. **Orden:** este cambio toca los mismos gates que `revision-guiada`, así que se implementa después de integrar colaboración y revisión guiada.

Preparar esta propuesta no acepta el cambio ni autoriza implementarlo.
