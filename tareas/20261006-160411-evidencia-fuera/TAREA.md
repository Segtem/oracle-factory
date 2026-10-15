# La evidencia fuera del camino de lectura

- ESTADO: CERRADA
- PRIORIDAD: 50
- ETIQUETAS: compresion


## Objetivo

Los paquetes de Clue y los hechos son ~6,5 de los 9,5 MB de `tareas/` y nadie los lee de corrido. Siguen versionados y referenciados por hash, pero `buscar` y el resumen no los recorren. Evaluar Git LFS o adjuntarlos a un release si el peso molesta.

Parte del plan «comprimir lo que se lee, no lo que se guarda» (2026-10-06): el registro sigue append-only y atado a hashes; encima, vistas derivadas que la herramienta regenera de forma determinista.

### Nota (2026-10-15 10:18:35 UTC)

Hecho en el cambio 20261015-001533-evidencia-fuera (merge 948886a): buscar saltea evidencia/ y clue/ de los candidatos (y, como antes, los JSON de tareas/); sigue leyendo revision/. En el repo, «severidad» bajó de 386 a 286 coincidencias. Git LFS y releases descartados por Brian el 2026-10-14: 17 MB no molestan.
