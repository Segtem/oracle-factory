# Herramientas de revisión de código en el IDE

- ESTADO: ABIERTA
- PRIORIDAD: 30
- ETIQUETAS: revision, ide, clue


## Objetivo

Exploración posterior. Mejorar la revisión de código, probablemente con una extensión de VS Code: ver el diff del candidato junto a los requisitos y las medidas, escribir hallazgos con la ubicación tomada del editor (schema de Clue) y decidir el triage sin editar JSON a mano. El piloto mostró que hoy el informe se arma con scripts y que el paquete de Clue no muestra el diff (`oracle-clue`, tarea `20261005-105254-triage-piloto`).

### Nota (2026-10-07 12:32:20 UTC)

Plan acordado con Brian el 2026-10-07: cli-json → trazabilidad → sarif → vscode (tareas 20261007-*). El enlace que faltaba es requisito → casos → líneas, medido con cobertura por caso.
