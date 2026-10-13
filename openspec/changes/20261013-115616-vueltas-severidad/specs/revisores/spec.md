# Capability: revisores

## ADDED Requirements

### Requirement: el corte de vueltas sigue la severidad
Tipo: funcional
Después de guardar un informe, `pedir-revision` SHALL mostrar cuántos hallazgos trae por severidad. Si entre los informes del candidato vigente no queda ningún hallazgo de severidad media o alta sin un riesgo aceptado que coincida, SHALL decir que no hace falta otra vuelta y que los bajos los decide una persona en `revisar`; si queda alguno, SHALL pedir corregirlo y pedir otra vuelta. Una severidad desconocida o ausente SHALL contar como media. `estado` SHALL sugerir el mismo próximo paso.

#### Scenario: sólo quedan bajos
- GIVEN un candidato cuyos informes traen sólo hallazgos bajos
- WHEN termina pedir-revision
- THEN la salida cuenta los bajos y sugiere revisar en vez de otra vuelta, y estado sugiere revisar

#### Scenario: queda uno medio
- GIVEN un candidato con un informe que trae un hallazgo medio y otro con sólo bajos
- WHEN termina pedir-revision
- THEN la salida pide corregir el hallazgo medio y pedir otra vuelta, y estado sugiere lo mismo

#### Scenario: severidad desconocida
- GIVEN un informe con un hallazgo sin severidad
- WHEN termina pedir-revision
- THEN cuenta como medio y pide otra vuelta

### Requirement: un riesgo aceptado persiste entre vueltas
Tipo: funcional
Cuando una persona acepta un riesgo en `revisar`, el registro del cambio SHALL guardarlo con su archivo, título, motivo, persona, fecha y candidato, aunque la revisión termine pidiendo cambios. `pedir-revision` SHALL incluir los riesgos aceptados vigentes del cambio en el pedido a cada revisor. Un hallazgo medio o alto que coincide con un riesgo aceptado SHALL NOT pedir otra vuelta.

#### Scenario: aceptado en una vuelta, presente en el pedido siguiente
- GIVEN una persona que aceptó un riesgo en la revisión de un candidato
- WHEN se pide una revisión del candidato siguiente
- THEN el pedido al revisor nombra ese riesgo, su archivo y su motivo

#### Scenario: un medio aceptado no pide otra vuelta
- GIVEN un riesgo medio aceptado en una vuelta anterior
- WHEN el mismo hallazgo vuelve en el informe del candidato nuevo
- THEN pedir-revision no pide otra vuelta por ese hallazgo

### Requirement: revisar reconoce un riesgo ya aceptado
Tipo: funcional
En `revisar`, un hallazgo con el mismo archivo y el mismo título normalizado (minúsculas, sin puntuación y con espacios simples) que un riesgo aceptado SHALL mostrarse como ya aceptado, con quién, cuándo y por qué. La persona SHALL elegir entre mantenerlo, que lo registra como riesgo aceptado con el mismo motivo, o revocarlo, que lo saca de los aceptados y lo decide como un hallazgo nuevo. Un hallazgo que no coincide SHALL decidirse como hoy.

#### Scenario: mantener un riesgo aceptado
- GIVEN un riesgo aceptado y un hallazgo nuevo que coincide
- WHEN la persona elige mantenerlo
- THEN la decisión del hallazgo es riesgo aceptado con el motivo anterior, y el riesgo sigue vigente

#### Scenario: revocar un riesgo aceptado
- GIVEN un riesgo aceptado y un hallazgo nuevo que coincide
- WHEN la persona elige revocarlo y lo deja abierto
- THEN el riesgo deja de estar aceptado y el hallazgo queda abierto

#### Scenario: un título distinto no coincide
- GIVEN un riesgo aceptado
- WHEN vuelve un hallazgo del mismo archivo con otro título
- THEN revisar lo presenta como un hallazgo nuevo
