# Distribución con Oracle Task

## ADDED Requirements

### Requirement: Oracle Task como dependencia
Factory MUST usar oracle-task==0.2.0 e invocar tasks desde ese mismo entorno Python.

#### Scenario: instalación aislada
- GIVEN Factory instalado sin trackertast ni comandos globales Oracle/tasks
- WHEN una persona sigue el ejemplo de notas
- THEN puede crear tareas, registrar notas y cerrar la tarea fixture conservando su ID.

### Requirement: Instrucciones vigentes
La guía MUST nombrar Oracle Task, mostrar la instalación y explicar cómo migrar la herramienta antigua.
