# ruta apunta al candidato vigente, no a HEAD

## Why

`oracle-factory ruta ID evidencia` imprime la carpeta del candidato de HEAD. Pero un commit que sólo guarda informes, pedidos o evidencia no cambia el producto: el candidato sigue siendo el anterior. Si el verificador escribe en la ruta de HEAD, Factory crea una carpeta de candidato nueva, que pasa a ser la vigente y deja huérfanos los informes del candidato real.

Pasó en el cambio 20261007-192608-revisores: tras commitear el informe de agy, `ruta` dio `11b2048` en vez de `962ede7`, el verificador escribió ahí y `revision-preparar` no encontró la revisión. Desde entonces el agente escribe la evidencia con `ruta_canonica(..., candidato_vigente(ID))` a mano. `pedir-revision` y `juzgar` ya usan el candidato vigente; `ruta` es el único que no.

Tarea de origen: `20261007-212700-ruta-vigente`.

## What changes

- **`ruta` usa el candidato vigente**, el mismo que usan `pedir-revision` y `juzgar`: el commit con carpeta propia más cercano a HEAD, si el producto no cambió desde él. Si no hay ninguno (el primer candidato, o un producto cambiado después), sigue usando HEAD, como hoy.
- **La spec de estructura cambia ese requisito** (`## MODIFIED Requirements`): donde dice «sobre el HEAD actual» pasa a decir «sobre el candidato vigente».
- Vale para los cuatro tipos (`evidencia`, `clue`, `revision`, `checkout`), porque los cuatro son del mismo candidato.

## Out of scope

- Mover o borrar carpetas de candidato creadas por error en cambios anteriores: lo cerrado no se toca.
- Avisar de cambios de producto sin commitear: hoy `ruta` tampoco lo hace, y `estado` ya pide commitear.

## Human decisions

Brian eligió este cambio el 2026-10-12, con un menú, como el primero del backlog ordenado.
