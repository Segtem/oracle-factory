# El paquete de revisión deja fuera lo que no es producto

## Why

`pedir-revision` arma el paquete de Clue con el diff del candidato contra `main`, y ese diff trae también los registros de Factory: informes y pedidos de cada vuelta, evidencia (`hechos.json`, `suite.txt`, `trazabilidad.json`) y notas del tracker. El paquete lleva el texto completo de cada archivo y tiene un límite de 1 MB, así que cada vuelta lo agranda hasta que la revisión deja de ser posible: pasó en `revisores` (17 vueltas), en `decisiones-guiadas` y en `trazabilidad`, donde la vuelta 4 midió 1,22 MB y hubo que seguir con vueltas incrementales. Además los revisores gastan contexto en archivos que no revisan: varias veces informaron «el diff sólo trae metadatos».

Oracle Clue 0.1.0a2 (publicada el 2026-10-13, a pedido de Factory) suma `preparar --excluir RUTA`. Con eso el paquete de `trazabilidad` baja de 1,22 MB a 486 KB.

Tarea de origen: `20261007-220000-paquete-producto`. Brian eligió el enfoque el 2026-10-13: la exclusión en Clue y Factory que la use.

## What changes

- **Factory fija `oracle-clue==0.1.0a2`.**
- **`pedir-revision` excluye del paquete lo que no es producto**: `.factory/` y `tareas/`, más cualquier otro archivo del diff que no cuente en la huella del producto (la misma regla de siempre, `es_producto`). Lo excluido figura en el paquete y en el pedido, y ningún hallazgo puede señalarlo.
- **Factory comprueba las exclusiones**: un paquete que excluye un archivo del producto no se usa, ni al pedir la revisión ni al prepararla (`revision-preparar`, `revisar`, `estado`), y se avisa por qué. Clue confía en las exclusiones del paquete como en su contexto; quien integra tiene que verificarlas.
- **Los informes guardados siguen valiendo**: los paquetes sin exclusiones de vueltas anteriores se validan igual con 0.1.0a2.

## Out of scope

- Partir el paquete o mandar sólo parches en archivos grandes: con un diff de producto de más de 1 MB (como en `decisiones-guiadas`) sigue haciendo falta una base incremental (`--base`).
- Rutas relativas en el pedido guardado (otra nota de la misma tarea).

## Human decisions

- Brian eligió que la exclusión esté en Clue y que Factory la use (2026-10-13), y publicó oracle-clue 0.1.0a2 en PyPI.
