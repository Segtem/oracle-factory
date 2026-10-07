# Producir en la estructura propia: evidencia, paquetes de Clue e informes en ruta

- ESTADO: ABIERTA
- PRIORIDAD: 5
- ETIQUETAS: autoproduccion


## Objetivo

Que los verificadores (`tools/verify_*.py`), los paquetes de Clue y los informes de revisión se escriban donde dice `oracle-factory ruta ID TIPO` (`.factory/cambios/<ID>/candidatos/<sha7>/{evidencia,clue,revision}`) y no en `tareas/<ID>/evidencia-<sha>/` ni en el scratchpad. Hoy Factory define esa estructura y no la usa. Incluye que `juzgar` acepte la evidencia del candidato sin ruta explícita y que `donde` la muestre.

Parte del objetivo «Factory se construye a sí misma» (pedido de Brian, 2026-10-07): que lo que hoy hace el agente a mano, con scripts sueltos del scratchpad, lo haga Factory y quede registrado.
