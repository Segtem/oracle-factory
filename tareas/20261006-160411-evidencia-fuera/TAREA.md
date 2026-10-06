# La evidencia fuera del camino de lectura

- ESTADO: ABIERTA
- PRIORIDAD: 50
- ETIQUETAS: compresion


## Objetivo

Los paquetes de Clue y los hechos son ~6,5 de los 9,5 MB de `tareas/` y nadie los lee de corrido. Siguen versionados y referenciados por hash, pero `buscar` y el resumen no los recorren. Evaluar Git LFS o adjuntarlos a un release si el peso molesta.

Parte del plan «comprimir lo que se lee, no lo que se guarda» (2026-10-06): el registro sigue append-only y atado a hashes; encima, vistas derivadas que la herramienta regenera de forma determinista.
