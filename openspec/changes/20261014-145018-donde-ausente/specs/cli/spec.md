# Capability: cli

## MODIFIED Requirements

### Requirement: donde y resumen se leen como JSON
Tipo: funcional
`oracle-factory donde ID --json` SHALL imprimir un objeto con `esquema` `oracle-factory.donde/1` y la lista de artefactos, cada uno con gate, ruta, situación (`existe`, `ausente`, `historico` o `no_valido`) y nota; `ausente` es un artefacto que un registro del cambio nombra y ya no está. `oracle-factory resumen --json` SHALL imprimir un objeto con `esquema` `oracle-factory.resumen/1` con lo vigente por capacidad (cada requisito con su requisito de Oracle, tipo, medidas, veredicto al cerrar y cambio de origen), los cambios abiertos con sus pendientes, los abandonados con su motivo, las carpetas sin registro, los riesgos aceptados y los límites; SHALL NOT escribir el resumen en disco, y las mismas entradas SHALL dar los mismos bytes.

#### Scenario: donde con un artefacto ausente
- GIVEN un cambio con un juicio registrado cuyos hechos ya no están
- WHEN se pide donde con --json
- THEN esos hechos figuran con gate juicio y situación ausente, y los artefactos que existen figuran como existe

#### Scenario: resumen sin escribir
- GIVEN un proyecto con un cambio cerrado y uno abierto
- WHEN se pide resumen con --json dos veces
- THEN las dos salidas son idénticas, nombran el requisito vigente y el cambio abierto con sus pendientes, y .factory/resumen.md no cambia
