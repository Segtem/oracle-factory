# buscar no recorre la evidencia ni los paquetes de Clue

## Why

`oracle-factory buscar` recorre `.factory/cambios/` entero, también la evidencia de cada candidato (`suite.txt`, `hechos.json`, `trazabilidad.json`) y los paquetes de Clue. Nadie los lee de corrido: están atados a hashes y se leen con las herramientas que los usan (`juzgar`, `trazabilidad`, la preparación de la revisión). En el repositorio de Factory, el 2026-10-14, 100 de las 386 líneas al buscar «severidad» y 83 de las 735 al buscar «revisar» salían de la evidencia. En `tareas/` ya se saltean los JSON por la misma razón.

Tarea de origen: `20261006-160411-evidencia-fuera` (plan «comprimir lo que se lee, no lo que se guarda», 2026-10-06).

## What changes

- **`buscar` deja afuera `evidencia/` y `clue/` de cada candidato.** Sigue leyendo los informes y los pedidos de `revision/`, que sí son texto para leer, y el resto de los registros.
- **El requisito «buscar en todo el proyecto» (MODIFIED) lo dice**, con un escenario nuevo.

## Out of scope

- Git LFS o adjuntar la evidencia a un release: Brian lo descartó el 2026-10-14 (17 MB entre `tareas/` y `.factory/cambios/` no molestan, y LFS cambia cómo se clona el repositorio).
- Cambiar lo que se guarda: la evidencia sigue versionada y referenciada por hash.

## Human decisions

- Brian eligió el alcance el 2026-10-14: sólo `buscar`, sin LFS.
