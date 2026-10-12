# Producir en la estructura propia: evidencia, paquetes de Clue e informes en ruta

- ESTADO: CERRADA
- PRIORIDAD: 5
- ETIQUETAS: autoproduccion


## Objetivo

Que los verificadores (`tools/verify_*.py`), los paquetes de Clue y los informes de revisión se escriban donde dice `oracle-factory ruta ID TIPO` (`.factory/cambios/<ID>/candidatos/<sha7>/{evidencia,clue,revision}`) y no en `tareas/<ID>/evidencia-<sha>/` ni en el scratchpad. Hoy Factory define esa estructura y no la usa. Incluye que `juzgar` acepte la evidencia del candidato sin ruta explícita y que `donde` la muestre.

Parte del objetivo «Factory se construye a sí misma» (pedido de Brian, 2026-10-07): que lo que hoy hace el agente a mano, con scripts sueltos del scratchpad, lo haga Factory y quede registrado.

### Nota (2026-10-12 21:40:44 UTC)

Hecha por el cambio 20261007-150043-autoproduccion (requisitos juzgar_encuentra_la_evidencia_del_candidato y este_repositorio_produce_en_la_carpeta_del_candidato, verdes al cerrar). Lo que queda de ruta, en 20261007-212700-ruta-vigente.
