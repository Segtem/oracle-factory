# Trazabilidad por candidato: requisito, casos y líneas cambiadas

## Why

Hoy una persona revisa el código hecho por IA por archivo: lee el diff entero sin saber qué línea respalda qué promesa. Factory ya sabe qué casos prueban cada requisito (el sensor los enumera) y qué cambió en el candidato (el diff contra main), pero no los une. Tampoco hay forma de ver qué líneas cambiadas no ejecuta ningún caso del contrato: código que nadie probó. Es el segundo paso del plan de revisión en el IDE, sobre la API en JSON del cambio anterior (`cli-json`).

Tarea de origen: `20261007-123220-trazabilidad`. Brian eligió seguir con ésta el 2026-10-13.

## What changes

- **El sensor registra qué ejecuta cada caso.** Factory trae un ayudante, `oracle_factory.trazabilidad`, que corre los casos del contrato de cada requisito con una traza de líneas y escribe `trazabilidad.json` en la evidencia del candidato: por requisito, sus casos; por caso, las líneas del proyecto que ejecutó. Usa sólo la biblioteca estándar (`sys.settrace`), sin sumar dependencias, y traza sólo los casos del contrato, no la suite entera.
- **`oracle-factory trazabilidad ID`** cruza eso con el diff del candidato contra su base (la misma que usa `pedir-revision`) y muestra, por requisito, qué líneas cambiadas ejecutan sus casos; después, las líneas cambiadas ejecutables que no ejecuta ningún caso (**sin respaldo**) y los archivos cambiados que la traza no puede ver (no Python, o fuera del proyecto). Con `--json`, lo mismo con esquema `oracle-factory.trazabilidad/1`, como los comandos del cambio anterior.
- **Los límites van a la vista**: ejecutar una línea no prueba que sea correcta; el código que corre en otro proceso (por ejemplo, `oracle` o `tasks` llamados por la CLI) no se traza; y las líneas que no son ejecutables (comentarios, líneas en blanco) no cuentan como sin respaldo.

## Out of scope

- Usar el ayudante en los sensores de cambios anteriores: lo usa el de este cambio, y los siguientes lo suman al hacer su sensor.
- Mostrarlo en el IDE o exportarlo a SARIF: son las tareas `vscode` y `sarif`, que leen este JSON.
- Que la falta de respaldo bloquee algo: es información para la persona que revisa, no un gate.

## Human decisions

- Brian eligió seguir con trazabilidad (2026-10-13).
- Traza con la biblioteca estándar en vez de `coverage.py`: el proyecto pide Python 3.11 y `sys.monitoring` es de 3.12; `sys.settrace` es más lento, por eso sólo los casos del contrato.
