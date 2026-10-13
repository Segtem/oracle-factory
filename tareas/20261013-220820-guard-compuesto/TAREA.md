# docs/trazabilidad: el guard __main__ compuesto no se reconoce

- ESTADO: ABIERTA
- PRIORIDAD: 5
- ETIQUETAS: 

### Nota (2026-10-13 22:08:20 UTC)

Riesgo aceptado por Brian en 20261013-180751-trazabilidad (TRZ-MODULE-GUARD-COMPOUND-001 de codex): sólo se reconoce __name__ == "__main__" simple (en cualquier orden); con and, elif o if anidados, el cuerpo figura en «corren al importar». Anotarlo en los límites de docs/trazabilidad.md.
