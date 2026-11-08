# Capability: flujo

## ADDED Requirements

### Requirement: los_frenos_salen_de_los_datos_del_cambio
Tipo: funcional
El sistema DEBE calcular, solo con los registros del cambio, su candidato vigente y Git, los frenos del cambio, cada uno con un identificador y un motivo: `juicios_rojos` (los dos últimos juicios de Oracle son rojos), `hallazgo_alto_abierto` (un informe del candidato vigente trae un hallazgo de severidad alta y no hay una revisión aprobada vigente), `prueba_existente_editada`, `cambio_grande` y `bucle_de_revision` (los dos últimos con los umbrales que ya usa `estado`). Un dato que no se puede leer NO DEBE producir un freno ni romper `estado`.

#### Scenario: dos juicios rojos seguidos
- DADO un cambio cuyos dos últimos juicios de Oracle terminaron con código distinto de cero
- CUANDO se calculan los frenos
- ENTONCES figura `juicios_rojos` con su motivo

#### Scenario: un juicio rojo y uno verde
- DADO un cambio con un juicio rojo y después uno verde, o con un solo juicio rojo
- CUANDO se calculan los frenos
- ENTONCES no figura `juicios_rojos`

#### Scenario: hallazgo alto sin revisión aprobada
- DADO un informe del candidato vigente con un hallazgo de severidad alta y sin revisión aprobada vigente
- CUANDO se calculan los frenos
- ENTONCES figura `hallazgo_alto_abierto`; con una revisión aprobada vigente, no

#### Scenario: datos ilegibles
- DADO un registro con eventos que no se pueden leer, o un informe sin hallazgos legibles
- CUANDO se calculan los frenos
- ENTONCES no se inventa ningún freno y `estado` sigue funcionando

### Requirement: estado_muestra_los_frenos
Tipo: funcional
El sistema DEBE mostrar los frenos en `estado --json` como la clave `frenos` (lista de objetos con `id` y `motivo`, vacía si no hay) y en `estado` como avisos que empiezan con «FRENO:», sin cambiar el próximo paso, los pendientes ni ningún otro dato del estado.

#### Scenario: con frenos
- DADO un cambio con un freno
- CUANDO se pide `estado --json` y `estado`
- ENTONCES el JSON lo lista en `frenos` y el texto trae un aviso «FRENO:» con el mismo motivo

#### Scenario: sin frenos
- DADO un cambio sin frenos
- CUANDO se pide `estado --json`
- ENTONCES `frenos` es una lista vacía y no hay avisos «FRENO:»

#### Scenario: un freno no decide nada
- DADO un cambio con un freno
- CUANDO se pide su estado
- ENTONCES el próximo paso y los pendientes son los mismos que sin el freno
