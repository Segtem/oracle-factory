# Analizadores deterministas como revisores: SARIF a review/v1 de Clue

- ESTADO: ABIERTA
- PRIORIDAD: 7
- ETIQUETAS: revision, clue


## Objetivo

Que ruff, bandit, semgrep, mypy (o cualquier herramienta que emita SARIF) puedan declararse en `revisores` como un revisor más: un adaptador convierte su SARIF en un informe `oracle-clue.review/v1` sobre el paquete del candidato (sólo hallazgos dentro del diff), y entra al mismo `revisar`. Baratos, repetibles y complementarios de los revisores LLM.

Origen: video «AI Coding Agents + Static Code Analysis for Safer Code» (IBM Developer, 2026-10-08), que Brian pidió aplicar a Factory.

## Notas

- Probablemente un comando de oracle-clue (`oracle-clue desde-sarif`); es la dirección inversa de la tarea sarif.
- Conservar regla, severidad y kind de la herramienta.
