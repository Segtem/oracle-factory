# Lo determinista en cada commit, el revisor LLM en cada candidato

- ESTADO: ABIERTA
- PRIORIDAD: 12
- ETIQUETAS: revision, ci


## Objetivo

Los analizadores deterministas cuestan segundos: correrlos en el pre-push (o en ci-remoto) para detectar lo barato en el momento en que se introduce; los revisores LLM (≈10 min por vuelta) quedan para el candidato.

Origen: video «AI Coding Agents + Static Code Analysis for Safer Code» (IBM Developer, 2026-10-08), que Brian pidió aplicar a Factory. Es su consejo de correr el análisis en cada commit (shift left).

## Notas

- Depende de analizadores. Los consumidores de Oracle ya versionan `.githooks/pre-push`.
