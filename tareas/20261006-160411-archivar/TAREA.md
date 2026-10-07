# Archivar al cerrar: fusionar la spec del cambio en openspec/specs/<capacidad>/

- ESTADO: CERRADA
- PRIORIDAD: 10
- ETIQUETAS: compresion


## Objetivo

Al cerrar (o con `archivar`), fusionar la spec delta del cambio en `openspec/specs/<capacidad>/spec.md` (fuente de verdad, como OpenSpec) y mover el cambio a `openspec/changes/archive/`. Los requisitos de Oracle de versiones reemplazadas quedan marcados como reemplazados (estilo ADR *superseded*). Incluye migrar los 16 cambios existentes.

Referencias: OpenSpec concepts (https://github.com/Fission-AI/OpenSpec/blob/main/docs/concepts.md), discusión #737 (capacidades fragmentadas).

Parte del plan «comprimir lo que se lee, no lo que se guarda» (2026-10-06): el registro sigue append-only y atado a hashes; encima, vistas derivadas que la herramienta regenera de forma determinista.

### Nota (2026-10-07 00:33:04 UTC)

Cumplida por el cambio 20261006-161029-archivar-al, cerrado por Brian e incluido en 0.1.0a5. Cerrada a pedido de Brian.
