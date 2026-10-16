# Capability: ide

## ADDED Requirements

### Requirement: la vista de Factory muestra los cambios abiertos
Tipo: funcional
La extensión de VS Code SHALL mostrar, en una vista «Factory», los cambios abiertos del proyecto, y bajo cada uno sus requisitos con sus medidas, la decisión que las respalda y el veredicto, su revisión y su próximo paso, tomados de `resumen --json` y `estado ID --json`. Sin un proyecto de Factory en la carpeta abierta SHALL decirlo, y si la CLI falla SHALL mostrar su error en vez de una vista vacía.

#### Scenario: un proyecto con un cambio abierto
- GIVEN un proyecto de Factory con un cambio medido y otro cerrado
- WHEN se arma la vista
- THEN aparece sólo el abierto, con su requisito, sus medidas y quién las decidió, su revisión y su próximo paso

#### Scenario: una carpeta sin Factory, o una CLI que falla
- GIVEN una carpeta sin .factory/, o una CLI que termina con error
- WHEN se arma la vista
- THEN la vista dice que no hay un proyecto de Factory, o muestra el error de la CLI

### Requirement: los artefactos de un cambio se abren desde la vista
Tipo: funcional
Bajo cada cambio, la vista SHALL listar los artefactos de `donde ID --json` con su gate y abrir el archivo al elegirlo; un artefacto ausente o no válido SHALL verse marcado y SHALL NOT ofrecer abrirse.

#### Scenario: los artefactos de un cambio
- GIVEN un cambio con propuesta, spec, requisitos e informe de revisión, y un artefacto que falta
- WHEN se despliega el cambio en la vista
- THEN cada artefacto que existe abre su archivo y el que falta aparece marcado sin abrirse

### Requirement: el próximo paso se escribe en la terminal sin ejecutarse
Tipo: funcional
Para un próximo paso que es un comando de Factory, la vista SHALL ofrecer escribirlo en una terminal integrada del proyecto sin ejecutarlo, con la CLI que usa la extensión; un paso que no es un comando SHALL mostrarse sin botón. La extensión SHALL NOT tomar ninguna decisión ni correr comandos que la registren.

#### Scenario: un paso que es un comando
- GIVEN un cambio cuyo próximo paso es oracle-factory aprobar-spec ID
- WHEN se elige escribirlo en la terminal
- THEN la terminal recibe ese comando con la CLI de la extensión y sin Enter

#### Scenario: un paso que no es un comando
- GIVEN un cambio cuyo próximo paso pide corregir y commitear
- WHEN se arma la vista
- THEN el paso se muestra sin botón de terminal
