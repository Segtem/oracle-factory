# donde --json etiqueta no_valido una entrada inválida del registro

## Why

Al cerrar `20261014-145018-donde-ausente`, Brian aceptó como riesgo un hallazgo de codex (DONDE-TEST-001): el caso cj2 no arma una entrada inválida del registro, así que una regresión que etiquetara `ausente` lo que es `no_valido` pasaría; y la comprobación de los históricos usa `all()` sin exigir que haya alguno. `test_e6_valores_no_validos_en_el_registro` prueba el texto de `donde` («no válido»), no la etiqueta del JSON. El requisito nombra `no_valido` e `historico` sin decir qué son ni tener un escenario que los ejerza.

Tarea de origen: `20261014-195917-donde-no-valido`.

## What changes

- **El requisito «donde y resumen se leen como JSON» (MODIFIED) dice qué son `historico` y `no_valido`, y suma el escenario «donde con una entrada inválida»**. El resto no cambia.
- **Una prueba nueva** de ese escenario, con un registro que tiene un campo inválido y archivos en la carpeta de la tarea.
- El código del producto no cambia.

## Out of scope

- Cómo se ve una entrada inválida en el texto de `donde`: ya lo prueba `test_e6`.

## Human decisions

- Brian pidió la tarea al aceptar el riesgo (2026-10-14).
