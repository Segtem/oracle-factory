# Capability: tablero

<!-- Generada por Oracle Factory al cerrar cada cambio: no se edita a mano. -->

## Requirements

### Requirement: que_falta_en_cada_cambio
Origen: 20261027-140946-d48-bloqueos · tablero_cae12f0cad890a9c2.que_falta_en_cada_cambio
Tipo: funcional
The system SHALL show, for each change in the board, the list of what is still pending, or say that nothing is pending.

#### Scenario: un cambio con pendientes
- GIVEN un cambio abierto con tres pendientes
- WHEN se arma el tablero
- THEN el cambio muestra una sección «Qué falta» con los tres, en el orden de `estado`

#### Scenario: un cambio sin pendientes
- GIVEN un cambio sin pendientes
- WHEN se arma el tablero
- THEN la sección dice que nada falta, en vez de quedar vacía

### Requirement: instruccion_distinta_de_comando
Origen: 20261027-140946-d48-bloqueos · tablero_cae12f0cad890a9c2.instruccion_distinta_de_comando
Tipo: funcional
The system SHALL show a next step that is an explanation as plain text labelled «QUÉ HACER» with no terminal button, and keep showing a Factory command as a command with its button.

#### Scenario: el paso es una explicación
- GIVEN un próximo paso cuyo texto no empieza con `oracle-factory`
- WHEN se arma el tablero
- THEN se muestra como texto con el rótulo «QUÉ HACER», sin botón «Escribir en la terminal» y sin formato de código

#### Scenario: el paso es un comando
- GIVEN un próximo paso que empieza con `oracle-factory`
- WHEN se arma el tablero
- THEN se muestra como código con su botón, como hasta ahora

### Requirement: el_texto_del_registro_se_escapa
Origen: 20261027-140946-d48-bloqueos · tablero_cae12f0cad890a9c2.el_texto_del_registro_se_escapa
Tipo: funcional
The system SHALL escape every pending and every step text it shows, so that text from the registry cannot add markup to the board.

#### Scenario: un pendiente con marcado
- GIVEN un pendiente cuyo texto contiene `<script>`
- WHEN se arma el tablero
- THEN la página muestra el texto literal y no contiene esa etiqueta sin escapar

### Requirement: el_tablero_dice_a_quien_necesita
Origen: 20261027-160716-arb-equipo · tablero_ca9f1ed71bc00602b.el_tablero_dice_a_quien_necesita
Tipo: funcional
The system SHALL label a pending human decision of a change held by another person as decided by that person, and keep labelling it as needing the viewer when the change has no holder or the viewer holds it.

#### Scenario: el cambio lo tiene otra persona
- GIVEN un cambio con una decisión pendiente de una persona y como responsable a Ana, y `yo` es Brian
- WHEN se arma el tablero
- THEN el paso se rotula «LA DECIDE ANA» y no «TE NECESITA»

#### Scenario: el cambio lo tengo yo o no lo tiene nadie
- GIVEN un cambio con una decisión pendiente de una persona, que tiene como responsable a quien lo mira o a nadie
- WHEN se arma el tablero
- THEN el paso se rotula «TE NECESITA»

#### Scenario: el JSON dice quién sos
- GIVEN un proyecto donde el nombre de Git es Brian Hollweg
- WHEN se corre `oracle-factory tablero --json`
- THEN trae `yo` igual a «Brian Hollweg» sin modificar la configuración de Git

### Requirement: actividad_reciente_del_proyecto
Origen: 20261027-160716-arb-equipo · tablero_ca9f1ed71bc00602b.actividad_reciente_del_proyecto
Tipo: funcional
The system SHALL list the latest ten events across the open changes, newest first, with who did what, in which change and when.

#### Scenario: más de diez eventos
- GIVEN dos cambios abiertos con doce eventos entre los dos
- WHEN se arma el tablero
- THEN `actividad` trae los diez más nuevos, del más nuevo al más viejo, cada uno con cambio, acción, actor, tipo de actor y hora

#### Scenario: la página la muestra
- GIVEN un proyecto con actividad
- WHEN se arma la página
- THEN hay una sección «Actividad reciente» con cada evento, y el texto del registro está escapado

#### Scenario: un cambio cerrado no entra
- GIVEN un cambio cerrado con eventos recientes y uno abierto
- WHEN se arma el tablero
- THEN la actividad sólo trae eventos del abierto

### Requirement: cada_pendiente_dice_quien_lo_hace
Origen: 20261027-200012-41p-quienhace · tablero_c36d16c32608f4c53.cada_pendiente_dice_quien_lo_hace
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
Origen: 20261027-200012-41p-quienhace · tablero_c36d16c32608f4c53.ahora_no_te_toca_nada
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
