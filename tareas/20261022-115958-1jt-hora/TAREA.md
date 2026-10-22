# La hora de cada evento con microsegundos: lo de dos ramas en el mismo segundo queda en orden

- ESTADO: ABIERTA
- PRIORIDAD: 50
- ETIQUETAS: 

### Nota (2026-10-22 11:59:58 UTC)

OpenSpec: openspec/changes/20261022-115958-1jt-hora. Modo de trabajo: confirmacion. Estado de factory: espera aceptación de proposal.md y spec.md.

### Nota (2026-10-22 12:00:36 UTC)

Brian Hollweg (persona, decidio, modo confirmacion) aceptó propuesta y spec openspec/changes/20261022-115958-1jt-hora/specs/colaboracion/spec.md; se reiniciaron las validaciones dependientes.

### Nota (2026-10-22 12:00:50 UTC)

Requisitos importados: colaboracion_cac5d9b2dbb283ed3.al_unir_dos_ramas_lo_del_mismo_segundo_queda_en_el_orden_en_que_se_escribio (funcional), colaboracion_cac5d9b2dbb283ed3.la_hora_de_un_evento_distingue_lo_escrito_en_el_mismo_segundo (funcional). Los nuevos nacen SIN MEDIR; verificá cobertura antes del juicio.

### Nota (2026-10-22 12:06:16 UTC)

Medidas de colaboracion_cac5d9b2dbb283ed3.la_hora_de_un_evento_distingue_lo_escrito_en_el_mismo_segundo: factory_hora.la_hora_de_un_evento_distingue_lo_escrito_en_el_mismo_segundo, factory_hora.corrida_completa; propuestas por claude-code (agente, propuso, modo confirmacion). SIN MEDIR: sin límite adicional declarado. Revisión y juicio anteriores invalidados; no se declara cumplimiento ni aprobación de pertinencia.

### Nota (2026-10-22 12:06:17 UTC)

Medidas de colaboracion_cac5d9b2dbb283ed3.al_unir_dos_ramas_lo_del_mismo_segundo_queda_en_el_orden_en_que_se_escribio: factory_hora.al_unir_dos_ramas_lo_del_mismo_segundo_queda_en_el_orden_en_que_se_escribio, factory_hora.corrida_completa; propuestas por claude-code (agente, propuso, modo confirmacion). SIN MEDIR: sin límite adicional declarado. Revisión y juicio anteriores invalidados; no se declara cumplimiento ni aprobación de pertinencia.

### Nota (2026-10-22 12:07:37 UTC)

Medidas de colaboracion_cac5d9b2dbb283ed3.al_unir_dos_ramas_lo_del_mismo_segundo_queda_en_el_orden_en_que_se_escribio: Brian Hollweg (persona, confirmo, modo confirmacion).

### Nota (2026-10-22 12:07:37 UTC)

Medidas de colaboracion_cac5d9b2dbb283ed3.la_hora_de_un_evento_distingue_lo_escrito_en_el_mismo_segundo: Brian Hollweg (persona, confirmo, modo confirmacion).

### Nota (2026-10-22 14:47:35 UTC)

Revisión guiada Brian Hollweg: aprobar; registrada por Brian Hollweg (persona, confirmo, modo confirmacion; motivo: Seis vueltas de codex y agy; todos los hallazgos corregidos con pruebas y mutaciones muertas salvo HORA-PROC-002, que propongo aceptar como riesgo: dos clones independientes que escriben en el mismo microsegundo exacto no tienen un orden real que Factory pueda conocer sin un reloj común entre máquinas (fuera de alcance en la propuesta); en ese caso queda primero lo de la rama que integra. Dentro de un registro el orden está garantizado (evento() va después del último).); 0 abiertos derivados; commit d479643152d802bd3cb6672fd27c0c163d86c801; informe tareas/20261022-115958-1jt-hora/revisiones/registro-6k503dqv/informe.json; decisiones tareas/20261022-115958-1jt-hora/revisiones/registro-6k503dqv/decisiones.json.

### Nota (2026-10-22 16:05:36 UTC)

Revisión guiada Brian Hollweg: aprobar; registrada por Brian Hollweg (persona, confirmo, modo confirmacion; motivo: Ocho vueltas de codex y agy: todos los hallazgos medios y altos corregidos con pruebas y mutaciones muertas, incluido HORA-PROC-002 con el desempate determinista que eligió Brian (lo común primero y, ante la misma hora entre ramas, quién y qué, igual en todos los clones), y un defecto que la evidencia destapó (el vault ordenaba los cambios por ID; ahora por su hora de creación). La 8 no dejó medios ni altos. Queda una baja: HORA-009, la prueba de un registro viejo no compara la hora que devuelve estado --json.); 0 abiertos derivados; commit 6aa25275ae1008dfbb1edf0fed3cfe70039bdc69; informe tareas/20261022-115958-1jt-hora/revisiones/registro-v1oo34gs/informe.json; decisiones tareas/20261022-115958-1jt-hora/revisiones/registro-v1oo34gs/decisiones.json.
