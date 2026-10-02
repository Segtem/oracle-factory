# Workflow validations

## ADDED Requirements

### Requirement: cumplimiento explícito y vigente
The system SHALL require explicit fulfillment of every imported requirement and current evidence before offering closure.

#### Scenario: Oracle sale cero sin juicio
- WHEN Oracle devuelve exit code 0 con una fila sin juicio o una falla en sombra
- THEN Factory bloquea el cierre

#### Scenario: cambia el producto o la evidencia
- WHEN cambian HEAD, archivos revisados, propuesta, spec, informes o hechos
- THEN el cierre exige renovar las validaciones afectadas

### Requirement: cancelación sin cambios
The system SHALL preserve the existing review report and state when confirmation is canceled.

#### Scenario: cancelar reemplazo de informe
- WHEN una persona cancela el registro de una nueva revisión
- THEN se conservan el informe y el estado anteriores

### Requirement: aislamiento de versiones
The system SHALL invalidate dependent checks after scope reapproval and isolate imported requirements by task and spec version.

#### Scenario: una promesa cambia conservando el título
- WHEN se aprueba una versión nueva de la spec
- THEN se importan requisitos nuevos sin heredar la medición anterior
