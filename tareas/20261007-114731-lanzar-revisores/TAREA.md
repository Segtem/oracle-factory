# Lanzar revisores desde Factory: revisar --con codex|agy

- ESTADO: ABIERTA
- PRIORIDAD: 7
- ETIQUETAS: autoproduccion


## Objetivo

Un comando que prepare el paquete de Clue del candidato, lance un revisor externo (Codex, Agy u otro configurado), valide su informe con oracle-clue y lo guarde en la carpeta del candidato, registrando proveedor y modelo. Hoy el agente lo orquesta a mano con ask-codex y ask-agy. Debe respetar los límites de costo (salida pesada a archivos) y no conceder decisiones al revisor.

Parte del objetivo «Factory se construye a sí misma» (pedido de Brian, 2026-10-07): que lo que hoy hace el agente a mano, con scripts sueltos del scratchpad, lo haga Factory y quede registrado.
