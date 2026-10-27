# Capability: tablero

## ADDED Requirements

### Requirement: cada_pendiente_dice_quien_lo_hace
Tipo: funcional
The system SHALL give each pending item of a change a plain-language sentence and who does it, a person or an agent, and keep showing unrecognized items with their original text and no owner.

#### Scenario: los pendientes de un cambio recién aprobado
- GIVEN un cambio con spec aprobada, sin requisitos importados, sin revisión y sin veredicto
- WHEN se corre `oracle-factory tablero --json`
- THEN `faltan` trae «Importar los requisitos de la spec» como de un agente, «Revisar el cambio y decidir si se aprueba» como de una persona y «Correr Oracle sobre la evidencia» como de un agente, en el orden de `pendientes`

#### Scenario: una propuesta sin confirmar
- GIVEN un cambio con medidas propuestas por un agente, sin confirmar
- WHEN se corre `oracle-factory tablero --json`
- THEN ese pendiente figura como de una persona, con la frase «Confirmar las medidas que propuso un agente»

#### Scenario: un pendiente que Factory no reconoce
- GIVEN un pendiente con un texto que Factory no clasifica
- WHEN se arma el tablero
- THEN aparece con su texto original, sin responsable, y la página lo muestra igual que antes

#### Scenario: la página los marca
- GIVEN un cambio con pendientes de una persona y de un agente
- WHEN se arma la página
- THEN cada uno lleva su frase y la marca «tuyo» o «de un agente», con el texto escapado

### Requirement: ahora_no_te_toca_nada
Tipo: funcional
The system SHALL say, above what is missing, that nothing is the viewer's turn when the next step is a command an agent runs, and SHALL NOT say it when the next step is a person's decision, an explanation, or the change is held by someone else.

#### Scenario: el próximo paso lo corre un agente
- GIVEN un cambio sin responsable o tuyo, cuyo próximo paso es `oracle-factory importar ID`
- WHEN se arma la página
- THEN dice «Ahora no te toca nada: sigue Importar los requisitos de la spec (lo hace un agente)»

#### Scenario: el próximo paso es tuyo o una explicación
- GIVEN un cambio cuyo próximo paso es una decisión de una persona, o una explicación
- WHEN se arma la página
- THEN no aparece el aviso

#### Scenario: el cambio lo tiene otra persona
- GIVEN un cambio de otra persona cuyo próximo paso lo corre un agente
- WHEN se arma la página
- THEN no aparece el aviso
