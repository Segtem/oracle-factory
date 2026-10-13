# Capability: cli

## ADDED Requirements

### Requirement: estado se lee como JSON
Tipo: funcional
`oracle-factory estado ID --json` SHALL imprimir en stdout un único objeto JSON con `esquema` igual a `oracle-factory.estado/1` y, como mínimo: `id`, `titulo`, `fase`, `modo`, `candidato` (el vigente o null), `requisitos` (cada uno con sus medidas y la decisión que las respalda), `pendientes`, `proximo_paso`, `decisiones` (spec, revisión, cierre y abandono, cada una con actor, tipo de actor, forma, cuándo y motivo si lo tiene), `revision` y `oracle` (cada uno con el commit al que se refiere y si sigue vigente para el producto actual) y `aceptados`. SHALL NOT ofrecer ejecutar el próximo paso ni leer de la terminal, y SHALL NOT escribir archivos.

#### Scenario: un cambio en revisión
- GIVEN un cambio con medidas confirmadas y una revisión registrada
- WHEN se pide estado con --json
- THEN la salida es un objeto JSON con el esquema, las medidas con quién las confirmó, la revisión con su commit y vigencia, y el próximo paso, sin preguntar nada

#### Scenario: la revisión vence
- GIVEN un cambio con una revisión registrada
- WHEN cambia el producto y se pide estado con --json
- THEN la revisión figura como no vigente

#### Scenario: un cambio abandonado
- GIVEN un cambio abandonado
- WHEN se pide estado con --json
- THEN la fase es abandonada, la decisión de abandono tiene su motivo y el próximo paso es null

### Requirement: donde y resumen se leen como JSON
Tipo: funcional
`oracle-factory donde ID --json` SHALL imprimir un objeto con `esquema` `oracle-factory.donde/1` y la lista de artefactos, cada uno con gate, ruta, situación (`existe`, `ausente`, `historico` o `no_valido`) y nota. `oracle-factory resumen --json` SHALL imprimir un objeto con `esquema` `oracle-factory.resumen/1` con lo vigente por capacidad (cada requisito con su requisito de Oracle, tipo, medidas, veredicto al cerrar y cambio de origen), los cambios abiertos con sus pendientes, los abandonados con su motivo, las carpetas sin registro, los riesgos aceptados y los límites; SHALL NOT escribir el resumen en disco, y las mismas entradas SHALL dar los mismos bytes.

#### Scenario: donde con un artefacto ausente
- GIVEN un cambio sin evidencia
- WHEN se pide donde con --json
- THEN la evidencia figura con situación ausente

#### Scenario: resumen sin escribir
- GIVEN un proyecto con un cambio cerrado y uno abierto
- WHEN se pide resumen con --json dos veces
- THEN las dos salidas son idénticas, nombran el requisito vigente y el cambio abierto con sus pendientes, y .factory/resumen.md no cambia

### Requirement: la salida de texto no cambia y los errores no se mezclan con el JSON
Tipo: funcional
Sin `--json`, `estado`, `donde` y `resumen` SHALL imprimir lo mismo que antes de este cambio. Con `--json`, un error SHALL ir a stderr con código 1 y stdout SHALL quedar vacío.

#### Scenario: el texto sigue igual
- GIVEN un cambio
- WHEN se pide estado, donde y resumen sin --json
- THEN la salida es la misma que antes de este cambio

#### Scenario: un cambio inexistente
- WHEN se pide estado con --json de un ID que no existe
- THEN stdout está vacío, el error va a stderr y el código es 1
