# Un valor del registro que no es una ruta se informa sin caerse

## Why

El 2026-10-16, al probar la extensión de VS Code (cambio 20261016-101007-vscode), un `factory.json` con `revision.informe = 5` hizo caer `estado` y `resumen` con un `TypeError` en vez de decir qué está mal; la extensión sólo pudo mostrar ese error. Pasa con los cuatro campos que el registro guarda como ruta —el informe y las decisiones de la revisión, el informe y los hechos del juicio— cuando traen un número, una lista o un objeto: se unen con la raíz del proyecto sin mirar que sean texto, en cinco lugares. `donde` ya los marca `no_valido` (estructura e6). Tarea `20261016-113944-informe-no-texto`.

## What changes

- **Un solo criterio**: una ruta del registro vale si es texto no vacío y sin bytes nulos —el mismo de `donde`—. Lo que no, no se toma por ruta.
- **`estado` y `resumen` lo nombran**: un pendiente «<campo> no válido en el registro (no es una ruta de texto)», en vez de un traceback.
- **El próximo paso rehace lo que ya no vale**: una revisión con un informe o unas decisiones no válidos ya no cuenta, y el paso es rehacerla (pedir-revision, o revisar si ya hay informes de revisores); un juicio con un informe o unos hechos no válidos ya no vale, y el paso es juzgar.

## Out of scope

- El campo `spec` del registro (lo escribe `nuevo` y no lo toca otro comando).
- Reparar el registro: Factory no lo reescribe; se rehace la revisión o el juicio.

## Human decisions

- Brian eligió este arreglo el 2026-10-16, después del cambio vscode.
