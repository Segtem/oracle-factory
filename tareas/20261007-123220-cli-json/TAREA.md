# Salidas en JSON de la CLI: estado, donde y resumen

- ESTADO: ABIERTA
- PRIORIDAD: 11
- ETIQUETAS: revision, ide


## Objetivo

`estado --json`, `donde --json` y `resumen --json` con un esquema versionado y estable: fase, modo, requisitos con medidas y veredicto, pendientes, quién decidió qué, artefactos y rutas. Es la base del IDE y de factory-mcp. Sin cambiar la salida de texto actual.

Parte del plan de revisión en el IDE (tarea 20261005-112955-revision-ide, Brian 2026-10-07): unir requisitos, medidas, veredicto y código para que una persona revise el código hecho por IA por promesa, no por archivo. Las decisiones siguen siendo humanas y pasan por la terminal.
