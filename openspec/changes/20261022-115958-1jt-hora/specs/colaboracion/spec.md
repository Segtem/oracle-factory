# Capability: colaboracion

## ADDED Requirements

### Requirement: la hora de un evento distingue lo escrito en el mismo segundo
Tipo: funcional
La hora de cada evento y de cada decisión que Factory registra SHALL llevar microsegundos, en UTC, de modo que dos escrituras del mismo segundo tengan horas distintas y ordenadas. Un registro con horas en segundos SHALL seguir leyéndose, mostrándose y uniéndose sin migrarlo.

#### Scenario: dos mensajes en el mismo segundo
- GIVEN un cambio
- WHEN se dejan dos mensajes seguidos dentro del mismo segundo
- THEN sus horas son distintas, la segunda es posterior y las dos tienen microsegundos; y un registro viejo con horas en segundos se muestra en estado y en el vault como antes

### Requirement: al unir dos ramas lo del mismo segundo queda en el orden en que se escribió
Tipo: funcional
Al unir el registro de un cambio editado en dos ramas, los eventos SHALL quedar en el orden de sus horas aunque se hayan escrito en el mismo segundo, también si una rama tiene horas en segundos y la otra con microsegundos. El banco de concurrencia SHALL comprobarlo con mensajes de a turnos escritos en el mismo segundo, sin separar los días.

#### Scenario: mensajes de a turnos en el mismo segundo
- GIVEN dos personas que escriben en el mismo cambio, cada una en su rama, durante el mismo segundo
- WHEN sincronizan y se unen los registros
- THEN los mensajes quedan en el orden en que se escribieron, y el escenario de a turnos del banco pasa sin esperar entre días
