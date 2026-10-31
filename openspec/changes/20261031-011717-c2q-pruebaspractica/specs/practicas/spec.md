# Capability: practicas

## ADDED Requirements

### Requirement: la_plantilla_de_tareas_pide_escribir_primero_las_pruebas
Tipo: funcional
El sistema DEBE incluir en la plantilla de tareas de un cambio nuevo, en español y en inglés, el paso de escribir primero las pruebas de cada escenario de la spec, antes de implementar.

#### Scenario: un cambio nuevo en español
- DADO un proyecto con Factory inicializado
- CUANDO se crea un cambio nuevo
- ENTONCES su tasks.md tiene el paso de escribir las pruebas de cada escenario, y está antes del paso de implementar

#### Scenario: un cambio nuevo en inglés
- DADO un proyecto con Factory inicializado
- CUANDO se crea un cambio nuevo con el idioma inglés
- ENTONCES su tasks.md tiene ese mismo paso en inglés, y está antes del paso de implementar

### Requirement: el_estado_avisa_de_los_requisitos_sin_pruebas_sin_bloquear
Tipo: funcional
El sistema DEBE avisar en el estado de un cambio, y en su JSON, de los requisitos que no tienen ningún caso de prueba en la trazabilidad del candidato vigente y de que el candidato no tiene trazabilidad, sin cambiar los pasos pendientes ni impedir ninguna decisión.

#### Scenario: un requisito sin casos
- DADO un cambio con dos requisitos importados y una trazabilidad del candidato donde uno tiene casos y el otro ninguno
- CUANDO se pide el estado
- ENTONCES el aviso nombra el requisito sin casos y no al otro, y el próximo paso y los pendientes no cambian

#### Scenario: un candidato sin trazabilidad
- DADO un cambio con requisitos importados y un candidato cuyo sensor no dejó trazabilidad
- CUANDO se pide el estado
- ENTONCES el aviso dice que el candidato no tiene trazabilidad de pruebas, y el próximo paso y los pendientes no cambian

#### Scenario: todos con casos
- DADO un cambio cuyos requisitos tienen todos casos en la trazabilidad
- CUANDO se pide el estado
- ENTONCES no hay aviso de pruebas

### Requirement: una_excepcion_declarada_en_la_spec_explica_por_que_no_hay_pruebas
Tipo: funcional
El sistema DEBE reconocer la línea `Pruebas: no aplica — motivo` de un requisito en su spec, mostrarla en el estado con su motivo y no avisar por falta de pruebas de ese requisito, y DEBE rechazar una excepción sin motivo.

#### Scenario: una excepción con motivo
- DADO un requisito con la línea Pruebas: no aplica y un motivo, y sin casos en la trazabilidad
- CUANDO se pide el estado
- ENTONCES el estado muestra la excepción con su motivo y no avisa de falta de pruebas de ese requisito

#### Scenario: una excepción sin motivo
- DADO un requisito con la línea Pruebas: no aplica y sin motivo
- CUANDO se importa o se pide el estado
- ENTONCES se rechaza diciendo que la excepción necesita un motivo, y el requisito no queda exceptuado
