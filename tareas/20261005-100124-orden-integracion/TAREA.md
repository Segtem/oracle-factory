# Ordenar la integración de colaboración y revisión guiada

- ESTADO: CERRADA
- PRIORIDAD: 40
- ETIQUETAS: colaboracion, integracion


## Objetivo

`tarea/20261004-005956-revision-guiada` parte de `6af15e4`, así que contiene el protocolo de colaboración (`tarea/colaboracion-personas-agentes`), que todavía no fue revisado. Si se integra revisión-guiada en `main`, entra también colaboración sin revisión.

## Decisión propuesta (pendiente de la persona integradora)

- No rebasear revisión-guiada sobre `main`: su evidencia fija los commits `109e2b5`, `5b54dc8` y `b89340f`, y sus docs enlazan `docs/colaboracion.md`.
- Integrar primero colaboración (revisada y cerrada en Factory) y después revisión-guiada. Así, el diff de revisión-guiada contra `main` es sólo suyo.
- Si revisión-guiada necesita commits nuevos de colaboración antes de eso, se traen con merge, no con rebase.

Relacionadas: `20261004-121432-coordinar-dos`, `20261004-005956-revision-guiada`.

### Nota (2026-10-05 10:07:26 UTC)

Decisión confirmada por Brian (2026-10-05, conversación: «1. Confirmo.»): sin rebase; colaboración entra primero a main, ya revisada y cerrada, y después revisión guiada; si hace falta traer commits, se usa merge. La tarea queda abierta hasta que se ejecute la integración.

### Nota (2026-10-05, decisión de Brian)

Opción 1: colaboración entra a `main` revisada (revisión registrada por Brian desde su terminal, 0 hallazgos abiertos) y con el cambio `20261004-121432-coordinar-dos` abierto. Oracle no puede dar cobertura completa mientras el piloto humano siga sin medir, así que el cierre espera a ese piloto. Esto reemplaza el «revisada y cerrada» del acuerdo anterior.

### Nota (2026-10-05 12:02:03 UTC)

Integración completa (2026-10-05): colaboración (922fa33) y revisión guiada (01deb4c) en main y subidas. Ambos cambios quedan abiertos hasta cubrir lo sin medir. Sigue modos-de-trabajo sobre este main.
