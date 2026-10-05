# Ordenar la integración de colaboración y revisión guiada

- ESTADO: ABIERTA
- PRIORIDAD: 40
- ETIQUETAS: colaboracion, integracion


## Objetivo

`tarea/20261004-005956-revision-guiada` parte de `6af15e4`, así que contiene el protocolo de colaboración (`tarea/colaboracion-personas-agentes`), que todavía no fue revisado. Si se integra revisión-guiada en `main`, entra también colaboración sin revisión.

## Decisión propuesta (pendiente de la persona integradora)

- No rebasear revisión-guiada sobre `main`: su evidencia fija los commits `109e2b5`, `5b54dc8` y `b89340f`, y sus docs enlazan `docs/colaboracion.md`.
- Integrar primero colaboración (revisada y cerrada en Factory) y después revisión-guiada. Así, el diff de revisión-guiada contra `main` es sólo suyo.
- Si revisión-guiada necesita commits nuevos de colaboración antes de eso, se traen con merge, no con rebase.

Relacionadas: `20261004-121432-coordinar-dos`, `20261004-005956-revision-guiada`.
