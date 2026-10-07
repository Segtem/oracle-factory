# Revisar los comandos de Factory para que una persona trabaje cómoda

- ESTADO: ABIERTA
- PRIORIDAD: 40
- ETIQUETAS: cli, modos, ux


## Objetivo

Revisar el recorrido completo de la CLI pensando en la persona, no en el agente: nombres, mensajes, próximos pasos, cómo se muestran los requisitos para decidir y la instalación (hoy hace falta `uv run python fabrica.py`, y `oracle-factory` no está como comando). Incluye `20261005-105254-cli-piloto` (fricciones del piloto) y debe hacerse junto con los modos, que agregan las decisiones de persona.

### Nota (2026-10-07 00:40:23 UTC)

2026-10-07, pedido de Brian: el Markdown en la consola se ve como texto plano. Mientras tanto se abre con glow -p (instalado). Decidir acá cómo se ven las salidas de estado, donde y resumen (p. ej. resumen --ver con glow si está).

### Nota (2026-10-07 19:09:01 UTC)

2026-10-07: completar la revisión guiada (revisor, completa, informe_sha256, actor, motivo) obliga a editar JSON a mano o pegar un script; hace falta un comando del estilo revision-completar --revisor.
