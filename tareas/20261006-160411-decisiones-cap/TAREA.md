# Decisiones por capacidad, con estado vigente o reemplazada

- ESTADO: ABIERTA
- PRIORIDAD: 40
- ETIQUETAS: compresion


## Objetivo

Destilar los eventos de cada `factory.json` en un registro de decisiones por capacidad (quién decidió qué, en qué modo, vigente o reemplazada), para no tener que leer todos los eventos.

Parte del plan «comprimir lo que se lee, no lo que se guarda» (2026-10-06): el registro sigue append-only y atado a hashes; encima, vistas derivadas que la herramienta regenera de forma determinista.
