# Spec de cli: lo ausente en donde es lo que un registro nombra y ya no está

## Why

El requisito «donde y resumen se leen como JSON» (cambio `20261013-153440-cli-json`) tiene el escenario «donde con un artefacto ausente: un cambio sin evidencia → la evidencia figura ausente». Pero `donde` lista la evidencia de un candidato sólo cuando existe, y cumplir el escenario así cambiaría el texto de `donde`, que el mismo cambio promete no cambiar. Lo que `donde` marca como `ausente` es un artefacto que el cambio espera y no está: uno fijo de su convención (como `proposal.md`) o uno que un registro nombra (como los hechos de un juicio registrado que se borraron, que es lo que se probó). Lo señaló agy (CLI-JSON-001, medio) y quedó nombrado como límite en aquella revisión.

Tarea de origen: `20261013-180553-donde-ausente`.

## What changes

- **El escenario se reescribe (MODIFIED) con lo que pasa de verdad**: un cambio con un juicio registrado cuyos hechos ya no están → esos hechos figuran en `donde --json` con gate `juicio` y situación `ausente`, y cada artefacto no histórico figura `existe` o `ausente` según esté en el disco. El requisito dice qué es `ausente`, y el escenario de `resumen` nombra qué comprueba (el requisito de Oracle y los mismos pendientes que `estado`).
- **Pruebas más estrictas** en los dos casos cj2: todos los artefactos de `donde`, y el requisito y los pendientes de `resumen`.
- **Una corrección de registro**: el `design.md` de `cli-json` dice que la vigencia de revisión y juicio usa `mismo_producto`; desde su vuelta 1 usa `juicio_vigente` y `problemas_de_revision`, como `estado` en texto. Ese documento es parte de un cambio cerrado y no se reescribe: la corrección queda acá.
- El código del producto no cambia.

## Out of scope

- Listar en `donde` artefactos que se esperan y todavía no existen (la evidencia de un candidato sin sensor corrido).

## Human decisions

- Ninguna: corrige una promesa que no se cumplía tal como estaba escrita.
