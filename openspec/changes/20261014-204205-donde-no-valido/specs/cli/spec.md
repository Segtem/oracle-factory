# Capability: cli

## MODIFIED Requirements

### Requirement: donde y resumen se leen como JSON
Tipo: funcional
`oracle-factory donde ID --json` SHALL imprimir un objeto con `esquema` `oracle-factory.donde/1` y la lista de artefactos, cada uno con gate, ruta, situación (`existe`, `ausente`, `historico` o `no_valido`) y nota. `historico` es lo que queda en la carpeta de la tarea; `no_valido`, una entrada del registro del cambio que no se puede leer como ruta. `ausente` es un artefacto que el cambio espera y no está en el disco: los fijos de su convención (propuesta, diseño, tareas, la nota de la tarea) o uno que un registro nombra, como los hechos de un juicio; lo que todavía no se produjo, como la evidencia de un candidato sin sensor corrido, no se lista. `oracle-factory resumen --json` SHALL imprimir un objeto con `esquema` `oracle-factory.resumen/1` con lo vigente por capacidad (cada requisito con su requisito de Oracle, tipo, medidas, veredicto al cerrar y cambio de origen), los cambios abiertos con sus pendientes, los abandonados con su motivo, las carpetas sin registro, los riesgos aceptados y los límites; SHALL NOT escribir el resumen en disco, y las mismas entradas SHALL dar los mismos bytes.

#### Scenario: donde con un artefacto ausente
- GIVEN un cambio con un juicio registrado cuyos hechos ya no están
- WHEN se pide donde con --json
- THEN esos hechos figuran con gate juicio y situación ausente, y cada artefacto que no es histórico ni inválido figura como existe si está en el disco y como ausente si no

#### Scenario: donde con una entrada inválida
- GIVEN un cambio cuyo registro tiene un campo con un valor que no es una ruta, y archivos en la carpeta de su tarea
- WHEN se pide donde con --json
- THEN ese campo figura con situación no_valido, lo de la carpeta de la tarea figura como historico, y los demás artefactos se siguen listando

#### Scenario: resumen sin escribir
- GIVEN un proyecto con un cambio cerrado y uno abierto con dos requisitos que tienen el mismo pendiente de medidas
- WHEN se pide resumen con --json dos veces
- THEN las dos salidas son idénticas, nombran el requisito de Oracle vigente del cambio cerrado y el cambio abierto con los pendientes de estado, con los de medidas que dicen lo mismo de varios requisitos juntos en un renglón, y .factory/resumen.md no cambia
