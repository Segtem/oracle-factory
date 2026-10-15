# Una medida confirmada cuyo catálogo cambia vuelve a pedir decisión

## Why

Una decisión de medidas (de una persona, o de un agente donde el modo lo deja) guarda la huella del `.requisito`: si alguien cambia qué medidas usa, la decisión deja de valer. Pero no guarda la de los catálogos de esas medidas. El 2026-10-15, en `docs-web-modos`, después de que Brian confirmara las medidas, el agente cambió el `alcance` de dos catálogos por un hallazgo de revisión, y `estado` siguió dando la confirmación por vigente. Lo mismo pasaría con un umbral o un filtro: la persona confirmó una regla y se juzga con otra.

Tarea de origen: `20261015-131816-catalogo-confirmado`.

## What changes

- **La decisión guarda la huella del archivo de cada medida** que el requisito nombra (las del proyecto y las del catálogo base de Oracle).
- **Si alguno cambia, la decisión deja de valer**, igual que cuando cambia el `.requisito`: `estado` la muestra pendiente y nombra la medida y su archivo, `juzgar` no la usa y `cerrar` no cierra.
- **Se vuelve a decidir con las mismas medidas**: `medir ID --requisito R --medida …` ya no responde «Sin cambios» si el catálogo cambió; registra la decisión nueva (o, por la vía de agente en `confirmacion`, una propuesta que la persona confirma con `medir ID --confirmar`).
- **Una propuesta de un agente** cuyo catálogo cambia antes de confirmarla ya no se confirma tal cual: `medir --confirmar` avisa, como cuando cambia el `.requisito`.
- **Las decisiones anteriores**, que no tienen esa huella, siguen valiendo: no se puede saber con qué catálogo se tomaron.

## Out of scope

- Mostrar qué cambió dentro del catálogo (Factory guarda la huella, no el contenido; el diff está en Git).

## Human decisions

- Brian pidió la tarea el 2026-10-15, al ver el caso en `docs-web-modos`.
