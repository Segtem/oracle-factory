# Design

- `abandonar` reutiliza `confirmar_persona` y `elegir_motivo`, como `revisar`. La propuesta de motivo del agente va en `estado["motivos_propuestos"]["abandono"]`, no en `propuestas`, que guarda sólo decisiones canónicas.
- `abierto()` rechaza también la fase `abandonada`; así todos los comandos que modifican un cambio la rechazan sin tocarlos uno por uno.
- `mostrar`, `proximo_paso` y `resumen` tratan `abandonada` antes de calcular pendientes, porque un registro mínimo no tiene spec.
- El registro guarda `abandono` (`registro_decision`, más `requisitos_quitados`) y un evento `abandono`.
