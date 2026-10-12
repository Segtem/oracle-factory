# Vista «estado actual» generada: oracle-factory resumen

- ESTADO: CERRADA
- PRIORIDAD: 20
- ETIQUETAS: compresion


## Objetivo

`oracle-factory resumen` genera un documento corto y regenerable: capacidades, requisitos vigentes con medida y último veredicto, cambios abiertos con lo que les falta, riesgos aceptados y límites declarados. Sale de los registros (sin LLM); si queda viejo se detecta por hash. Equivalente a un ARCHITECTURE.md vigente.

Parte del plan «comprimir lo que se lee, no lo que se guarda» (2026-10-06): el registro sigue append-only y atado a hashes; encima, vistas derivadas que la herramienta regenera de forma determinista.

### Nota (2026-10-12 21:40:44 UTC)

Hecha por el cambio 20261007-003414-resumen-del: oracle-factory resumen genera .factory/resumen.md y --verificar detecta si quedó viejo.
