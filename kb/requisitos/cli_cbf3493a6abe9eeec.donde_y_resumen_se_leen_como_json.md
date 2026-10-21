---
generado: oracle-factory kb
id: "cli_cbf3493a6abe9eeec.donde_y_resumen_se_leen_como_json"
vigente: true
---

# donde y resumen se leen como json

> Generado por `oracle-factory kb` desde el registro de Factory: no se edita a mano.

- Id: `cli_cbf3493a6abe9eeec.donde_y_resumen_se_leen_como_json`
- Vigente: sí
- Cambio: [[cambios/20261014-204205-donde-no-valido]]
- Veredicto: cumple
- Medidas: `factory_no_valido.donde_y_resumen_se_leen_como_json`, `factory_no_valido.corrida_completa`
- Fuente: openspec/changes/20261014-204205-donde-no-valido/specs/cli/spec.md#donde y resumen se leen como JSON

Tipo: funcional `oracle-factory donde ID --json` SHALL imprimir un objeto con `esquema` `oracle-factory.donde/1` y la lista de artefactos, cada uno con gate, ruta, situación (`existe`, `ausente`, `historico` o `no_valido`) y nota. `historico` es lo que hay en la carpeta de la tarea además de su nota (`TAREA.md`); `no_valido`, una entrada del registro del cambio que no se puede leer como ruta. `ausente` es un artefacto que el cambio espera y no está en el disco: los fijos de su convención (propuesta, diseño, tareas, la nota de la tarea) o uno que un registro nombra, como los hechos de un juicio; lo que todavía no se produjo, como la evidencia de un candidato sin sensor corrido, no se lista. `oracle-factory resumen --json` SHALL imprimir un objeto con `esquema` `oracle-factory.resumen/1` con lo vigente por capacidad (cada requisito con su requisito de Oracle, tipo, medidas, veredicto al cerrar y cambio de origen), los cambios abiertos con sus pendientes, los abandonados con su motivo, las carpetas sin registro, los riesgos aceptados y los límites; SHALL NOT escribir el resumen en disco, y las mismas entradas SHALL dar los mismos bytes.
