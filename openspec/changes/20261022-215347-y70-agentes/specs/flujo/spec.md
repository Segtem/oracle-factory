# Capability: flujo

## ADDED Requirements

### Requirement: la guía para agentes se genera y no se desactualiza
Tipo: funcional
`oracle-factory agentes` SHALL escribir en `AGENTS.md` (creándolo si falta) un bloque entre marcas, armado desde la CLI, con quién decide qué en cada modo de trabajo según `modos.via_agente` (marcando el modo por defecto del proyecto), los comandos de una persona y los de un agente con `--agente`, cómo ver el próximo paso y cómo consultar el proyecto (estado, preguntar, por-que y el MCP); SHALL conservar lo que está fuera del bloque y SHALL agregar `@AGENTS.md` al `CLAUDE.md` si no lo tiene. `--verificar` SHALL fallar sin escribir si el bloque falta o no coincide, e `init` SHALL escribirlo.

#### Scenario: un proyecto con su propio AGENTS.md
- GIVEN un proyecto con un AGENTS.md escrito por personas y un CLAUDE.md sin la línea
- WHEN se corre agentes, se cambia el modo por defecto del proyecto y se corre agentes --verificar
- THEN el bloque está, con la tabla de quién decide y los comandos, lo de las personas sigue igual, CLAUDE.md tiene @AGENTS.md, y la verificación falla por el modo nuevo hasta que se vuelve a correr agentes

### Requirement: la guía dice lo que hace la CLI
Tipo: funcional
Cada comando que la guía presenta como decisión de una persona SHALL negarse cuando lo corre un agente con `--agente`, o dejar sólo una propuesta sin decidir; y cada comando que presenta como de un agente SHALL aceptar `--agente`. Una prueba SHALL recorrer la lista de la guía y comprobarlo, de modo que la guía no pueda prometer algo que la CLI no hace.

#### Scenario: un agente intenta las decisiones de una persona
- GIVEN un cambio en modo confirmación
- WHEN un agente corre con --agente cada comando que la guía marca como de una persona
- THEN cada uno se niega o deja sólo una propuesta, y el registro no tiene ninguna decisión a nombre del agente
