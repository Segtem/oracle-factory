# Capability: flujo

## ADDED Requirements

### Requirement: estado_dice_la_ultima_propuesta_de_revision_de_un_agente
Tipo: funcional
El sistema DEBE ofrecer en `estado --json` la clave `propuesta_de_revision`: la última propuesta de revisión de un agente (decisión, candidato, quién y cuándo), o `null` si no hay ninguna, sin cambiar ningún otro dato del estado, y sin romper con un registro cuyos eventos no se pueden leer.

#### Scenario: con propuesta
- DADO un cambio al que un agente propuso una revisión
- CUANDO se pide `estado --json`
- ENTONCES `propuesta_de_revision` trae la decisión, el candidato, el actor y la fecha de la última propuesta

#### Scenario: sin propuesta
- DADO un cambio sin propuestas
- CUANDO se pide `estado --json`
- ENTONCES `propuesta_de_revision` es `null`

#### Scenario: varias propuestas
- DADO un cambio con dos propuestas de agentes
- CUANDO se pide `estado --json`
- ENTONCES trae la última

### Requirement: el_conductor_delega_la_propuesta_antes_de_pedir_la_revision
Tipo: funcional
El sistema DEBE, ante un próximo paso `revisar` con un candidato vigente, decidir `delegar_al_agente` (con la instrucción de preparar el informe y proponer la decisión, diciendo que la decisión final es de una persona) cuando no hay una propuesta para ese candidato, y `pedir_a_persona` cuando sí la hay; una propuesta de otro candidato, o un dato de propuesta ilegible, no cuenta; sin candidato vigente la acción no cambia (`pedir_a_persona`); y los frenos y los datos ilegibles siguen yendo primero.

#### Scenario: sin propuesta
- DADO el próximo paso `revisar` con candidato `abc1234` y sin propuesta
- CUANDO el conductor decide
- ENTONCES la acción es `delegar_al_agente` y la instrucción nombra `revision-preparar`, `revisar --decision` y que decide una persona

#### Scenario: con propuesta del candidato vigente
- DADO el próximo paso `revisar` con candidato `abc1234` y una propuesta para `abc1234`
- CUANDO el conductor decide
- ENTONCES la acción es `pedir_a_persona` con el comando de la persona

#### Scenario: propuesta de otro candidato
- DADO una propuesta para un candidato anterior
- CUANDO el conductor decide
- ENTONCES la acción es `delegar_al_agente`

#### Scenario: con un freno
- DADO el próximo paso `revisar` sin propuesta y un freno
- CUANDO el conductor decide
- ENTONCES la acción es `frenar`
