# Capability: ide

## ADDED Requirements

### Requirement: la_extension_solo_lee_de_los_json_de_la_cli_lo_que_el_contrato_declara
Tipo: funcional
El sistema DEBE fallar una prueba, nombrando el comando y la clave, cuando la extensión de VS Code lee de un JSON de la CLI una clave que `editores/vscode/contrato.json` no declara.

#### Scenario: la extensión lee una clave declarada
- DADO el contrato completo y proyectos con cambios en varios estados
- CUANDO se corre la extensión en node sobre la salida real de la CLI
- ENTONCES toda clave leída está declarada y la prueba pasa

#### Scenario: la extensión empieza a leer una clave nueva
- DADO el contrato sin la clave `tablero.cambios[].avisos`
- CUANDO se corre la extensión sobre la salida real
- ENTONCES la prueba falla nombrando el comando `tablero` y la clave `cambios[].avisos`

#### Scenario: las claves de los índices de un arreglo
- DADO un arreglo de cambios con varios elementos
- CUANDO la extensión lee el título de cada uno
- ENTONCES se anota una sola clave `abiertos[].titulo`

### Requirement: la_cli_entrega_cada_clave_declarada_con_un_tipo_permitido
Tipo: funcional
El sistema DEBE fallar una prueba, nombrando el comando, la clave, el tipo esperado y el encontrado, cuando la CLI no entrega una clave declarada en el contrato o la entrega con un tipo que el contrato no permite, y NO DEBE fallar por claves de más en la salida de la CLI.

#### Scenario: la CLI cumple el contrato
- DADO proyectos temporales con cambios en varios estados
- CUANDO se piden `resumen`, `estado`, `donde` y `tablero` con `--json`
- ENTONCES cada clave declarada está y su tipo es uno de los permitidos

#### Scenario: la CLI renombra una clave
- DADO una salida donde la clave declarada `estado.proximo_paso` pasó a llamarse `siguiente_paso`
- CUANDO se comprueba el contrato
- ENTONCES falla nombrando `estado` y `proximo_paso`

#### Scenario: la CLI cambia un tipo
- DADO una salida donde `estado.requisitos` es un objeto en vez de un arreglo
- CUANDO se comprueba el contrato
- ENTONCES falla nombrando la clave, el tipo `array` esperado y el tipo `object` encontrado

#### Scenario: la CLI agrega una clave
- DADO una salida con una clave de más que el contrato no declara
- CUANDO se comprueba el contrato
- ENTONCES la prueba pasa

#### Scenario: una clave opcional
- DADO una clave marcada opcional que no está en un estado cuyo objeto padre no existe
- CUANDO se comprueba el contrato
- ENTONCES no falla por ese estado

### Requirement: el_documento_explica_como_actualizar_el_contrato
Tipo: funcional
El sistema DEBE explicar en `docs/` cómo se actualiza el contrato cuando la extensión pasa a leer algo nuevo o cuando la CLI cambia un JSON, y DEBE nombrar los cuatro comandos que cubre y el archivo del contrato.

#### Scenario: el documento coincide con el contrato
- DADO el contrato y el documento
- CUANDO se comparan
- ENTONCES el documento nombra cada comando del contrato y el archivo `editores/vscode/contrato.json`
