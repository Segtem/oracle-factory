# Capability: decisiones

<!-- Generada por Oracle Factory al cerrar cada cambio: no se edita a mano. -->

## Requirements

### Requirement: las confirmaciones son un menú
Origen: 20261007-223645-decisiones-guiadas · decisiones_c59754a250f5b3593.las_confirmaciones_son_un_menu
Tipo: funcional
Cada confirmación de una persona SHALL mostrarse como un menú en la terminal, en lugar de pedir que se tipee una frase. El menú dice qué se decide y sobre qué cambio, y ofrece opciones numeradas con una línea que explica qué implica cada una; la decisión SHALL quedar registrada sólo al elegir una opción que confirma, y cualquier otra respuesta SHALL cancelar sin registrar nada.

#### Scenario: cerrar con el menú
- GIVEN un cambio listo para cerrar, en una terminal interactiva
- WHEN la persona ejecuta `cerrar ID` y elige la opción de cerrar
- THEN el cambio se cierra sin haber tipeado ninguna frase

#### Scenario: cancelar
- GIVEN el mismo cambio
- WHEN la persona elige cancelar o responde algo que no es una opción
- THEN no se registra nada y el registro queda igual

### Requirement: revisar guía la revisión de punta a punta
Origen: 20261007-223645-decisiones-guiadas · decisiones_c59754a250f5b3593.revisar_guia_la_revision_de_punta_a_punta
Tipo: funcional
`revisar ID` SHALL dejar la revisión del candidato vigente registrada sin que la persona edite JSON ni copie rutas o hashes. El recorrido:
- prepara el informe si hace falta y muestra en texto los hallazgos, las comprobaciones y la evidencia;
- pide decidir cada hallazgo abierto con opciones;
- ofrece aprobar sólo si nada queda abierto y todo cumple, o pedir cambios;
- registra con el nombre de la persona.

#### Scenario: revisión sin hallazgos
- GIVEN un candidato vigente con evidencia y un informe de revisor sin hallazgos
- WHEN la persona ejecuta `revisar ID`, elige aprobar y un motivo
- THEN la revisión queda registrada como aprobada por esa persona, con ese motivo

#### Scenario: un hallazgo abierto
- GIVEN un candidato vigente con un hallazgo de un revisor
- WHEN la persona ejecuta `revisar ID`
- THEN se le pide decidir ese hallazgo antes de poder aprobar, y la decisión queda en el registro

### Requirement: el motivo se elige
Origen: 20261007-223645-decisiones-guiadas · decisiones_c59754a250f5b3593.el_motivo_se_elige
Tipo: funcional
Al decidir con motivo, el menú SHALL ofrecer:
- el motivo propuesto por el agente, si dejó uno con `--agente … --motivo`;
- un motivo armado con los datos del cambio (candidato, hallazgos, evidencia);
- «Otro», para escribirlo.

Se ve el texto completo de cada motivo antes de elegirlo, y el registro dice si el motivo fue el del agente, el armado o uno escrito.

#### Scenario: motivo propuesto por el agente
- GIVEN un agente que dejó el motivo «sin hallazgos; acepto el límite X» para la revisión
- WHEN la persona ejecuta `revisar ID` y elige ese motivo
- THEN la revisión se registra con ese texto, como confirmado por la persona y propuesto por el agente

### Requirement: confirmar las medidas propuestas de una vez
Origen: 20261007-223645-decisiones-guiadas · decisiones_c59754a250f5b3593.confirmar_las_medidas_propuestas_de_una_vez
Tipo: funcional
`medir ID --confirmar` SHALL listar, por requisito, las medidas que propuso el agente y si propuso quitar `sin_medir`, y ofrecer confirmarlas todas, decidir de a una o cancelar; confirmar SHALL dar el mismo resultado que repetir cada comando propuesto sin `--agente`.

#### Scenario: siete requisitos propuestos
- GIVEN un agente que propuso medidas y quitar `sin_medir` para siete requisitos
- WHEN la persona ejecuta `medir ID --confirmar` y elige confirmar todas
- THEN los siete quedan confirmados por la persona y `oracle cobertura` los da cubiertos

### Requirement: sin terminal no hay decisión de persona
Origen: 20261007-223645-decisiones-guiadas · decisiones_c59754a250f5b3593.sin_terminal_no_hay_decision_de_persona
Tipo: no funcional
El menú SHALL exigir una terminal interactiva como la frase de hoy: sin ella, ninguna decisión de persona se registra, y el error SHALL nombrar la decisión y cómo un agente deja su propuesta con `--agente`.

#### Scenario: entrada por pipe
- GIVEN un proceso sin terminal que envía «1» por la entrada estándar
- WHEN ejecuta `cerrar ID` sin `--agente`
- THEN se rechaza y no se registra nada
