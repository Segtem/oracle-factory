# Capability: tablero

## ADDED Requirements

### Requirement: el_tablero_dice_a_quien_necesita
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
