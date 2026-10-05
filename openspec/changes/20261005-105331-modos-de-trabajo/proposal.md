# Modos de trabajo según quién decide los requisitos

## Why

Hoy Factory tiene un solo modo: una persona decide cada gate. El [piloto con agentes](../../../tareas/20261004-121432-coordinar-dos/piloto-agentes-01/piloto.md) mostró dos cosas. Un agente coordinador puede llevar un cambio de punta a punta tomando todas las decisiones, y eso es útil para prototipos o trabajo de bajo riesgo. Pero Factory no lo distingue: aceptó por pipe las frases de confirmación y registró «workstation» como autor de todo, así que un cierre autónomo queda igual que uno humano.

Brian pidió tres formas de trabajar, según cuánto interviene la persona en las decisiones sobre requisitos funcionales y no funcionales. Elegir el modo es explícito, y cada decisión registra quién la tomó y en qué modo, para que un verde nunca aparente una aprobación humana que no existió.

## What changes

**Tres modos por cambio.** Se eligen al crear el cambio (`nuevo --modo`). El valor por defecto del proyecto es `confirmacion`:

| Decisión | `autonomo` | `funcional` | `confirmacion` |
| --- | --- | --- | --- |
| Aceptar requisitos funcionales | agente | **persona decide** | agente propone, **persona confirma** |
| Aceptar requisitos no funcionales | agente | agente | agente propone, **persona confirma** |
| Medidas de un requisito | agente | según el tipo del requisito, como arriba | agente propone, **persona confirma** |
| Hallazgos de revisión | agente | según el tipo del requisito afectado | agente propone, **persona confirma** |
| Cierre | agente | **persona confirma** | **persona confirma** |

- **«Persona decide»:** la persona da la decisión y su motivo; el agente puede preparar opciones, pero no la registra. **«Persona confirma»:** el agente registra una propuesta completa y la persona la acepta o la rechaza tal cual.
- **Tipo de requisito.** Cada requisito de la spec declara `Tipo: funcional` o `Tipo: no funcional`. Si no lo declara, se trata como funcional. Con la opción de proyecto `tipos_obligatorios`, `importar` rechaza los requisitos sin tipo. `importar` guarda el tipo.
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

Brian respondió en la conversación del 2026-10-05:

1. **El modo por defecto es `confirmacion`** y no hay un cuarto modo. El comportamiento actual de Factory corresponde a `confirmacion`, y los cambios existentes sin modo se leen así.
2. **En `funcional`, el cierre lo hace la persona.**
3. **Un requisito sin tipo se trata como funcional**, que es la opción con menos fricción. Una opción del proyecto, `tipos_obligatorios`, hace que `importar` rechace los requisitos sin tipo. Los dos comportamientos conviven según esa opción.
4. **Se implementa después de integrar colaboración y revisión guiada.**

La persona conserva la elección del modo y las decisiones que cada modo le reserva.
