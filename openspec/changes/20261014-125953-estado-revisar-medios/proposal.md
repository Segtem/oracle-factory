# estado ofrece revisar cuando quedan hallazgos medios

## Why

Cuando una vuelta de revisión deja un hallazgo medio o más sin aceptar, `estado` y `pedir-revision` sólo sugieren corregirlo y pedir otra vuelta, y el menú de `estado` no ofrece nada (el paso no es un comando que se pueda ejecutar). Pero la persona también puede decidir que es un riesgo aceptable, o que el hallazgo no es cierto, y eso se hace en `revisar`, que nada nombra en ese momento. Pasó en `trazabilidad`: Brian aceptó como riesgo el guard compuesto, y para llegar a `revisar` hubo que decirle que existía.

Tarea de origen: `20261013-220820-estado-revisar-medios`.

## What changes

- **El próximo paso trae una alternativa**: con hallazgos medios o más sin aceptar, además de «corregí y pedí otra vuelta», `estado` dice que se pueden aceptar como riesgo o descartar con motivo en `oracle-factory revisar ID`.
- **El menú de `estado` la ofrece**: en una terminal, ofrece ejecutar `revisar` (que abre su propio menú de decisiones).
- **`pedir-revision` dice lo mismo** al guardar un informe que deja medios sin aceptar.
- **`estado --json` suma `alternativas`**: la lista de comandos que también valen como próximo paso (vacía casi siempre).

## Out of scope

- Cambiar qué cuenta como medio o el corte de vueltas.
- Otras alternativas del flujo (por ejemplo, abandonar): se suman a la misma lista cuando haga falta.

## Human decisions

- Ninguna: lo pidió Brian al ver el caso de `trazabilidad`.
