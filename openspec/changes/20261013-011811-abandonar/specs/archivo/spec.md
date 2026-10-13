# Capability: archivo

## ADDED Requirements

### Requirement: abandonar es una decisión de persona con motivo
Tipo: funcional
`oracle-factory abandonar ID` SHALL pedir a una persona, desde una terminal interactiva y en cualquier modo de trabajo, que confirme el abandono con un menú y elija un motivo. Con `--agente` SHALL NOT abandonar: con `--motivo` SHALL dejar ese motivo propuesto para que la persona lo vea como opción. Un cambio cerrado o ya abandonado SHALL rechazarse.

#### Scenario: la persona abandona con el motivo propuesto
- GIVEN un cambio abierto y un motivo propuesto por un agente
- WHEN la persona ejecuta abandonar, confirma y elige el motivo propuesto
- THEN el cambio queda en la fase abandonada, con la persona, la fecha y el motivo con su origen

#### Scenario: un agente no abandona
- GIVEN un cambio abierto en modo autónomo
- WHEN un agente ejecuta abandonar con --agente y --motivo
- THEN el cambio sigue abierto y el motivo queda propuesto

#### Scenario: la persona cancela
- GIVEN un cambio abierto
- WHEN la persona elige cancelar en el menú
- THEN el registro, los requisitos y la tarea no cambian

#### Scenario: un cambio cerrado
- GIVEN un cambio cerrado
- WHEN se ejecuta abandonar
- THEN se rechaza sin cambiar nada

### Requirement: lo abandonado no queda abierto ni medido
Tipo: funcional
Al abandonar, Factory SHALL quitar de `requisitos/` los archivos de los requisitos del cambio y listarlos en el registro, SHALL cerrar la tarea del tracker con una nota que dé el motivo, y SHALL NOT modificar la propuesta, la spec del cambio ni `openspec/specs/`. Después, `estado` SHALL mostrar quién lo abandonó y por qué, sin próximo paso; los comandos que modifican un cambio SHALL rechazarlo; y `listar --abiertos` SHALL NOT mostrarlo.

#### Scenario: abandonar un cambio con requisitos importados
- GIVEN un cambio con requisitos importados
- WHEN la persona lo abandona
- THEN sus archivos de requisito ya no están en requisitos/, el registro los lista, la tarea está cerrada y la spec consolidada no cambió

#### Scenario: un comando sobre un cambio abandonado
- GIVEN un cambio abandonado
- WHEN se ejecuta medir, juzgar o cerrar
- THEN se rechaza diciendo que el cambio está abandonado

### Requirement: el resumen muestra lo abandonado aparte
Tipo: funcional
`oracle-factory resumen` SHALL listar los cambios abandonados en una sección propia, con su título, quién lo decidió y el motivo, y SHALL NOT contarlos entre los cambios abiertos.

#### Scenario: un cambio abandonado en el resumen
- GIVEN un cambio abierto y otro abandonado
- WHEN se genera el resumen
- THEN dice 1 cambio abierto, y el abandonado aparece en su sección con el motivo

### Requirement: una carpeta sin registro también se abandona
Tipo: funcional
Sobre una carpeta de `openspec/changes/` sin registro de Factory, `abandonar` SHALL crear un registro mínimo en la fase abandonada, con la misma decisión de persona y motivo, y el resumen SHALL dejar de listarla como carpeta sin registro.

#### Scenario: una carpeta anterior al flujo
- GIVEN una carpeta de openspec/changes/ con propuesta y sin registro
- WHEN la persona la abandona con un motivo
- THEN tiene un registro en la fase abandonada y el resumen la muestra entre los abandonados, no entre las carpetas sin registro
