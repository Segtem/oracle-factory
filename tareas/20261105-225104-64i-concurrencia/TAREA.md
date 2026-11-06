# Web: simulación pixel art de personas y agentes trabajando a la vez

- ESTADO: CERRADA
- PRIORIDAD: 50
- ETIQUETAS: 

### Nota (2026-11-05 22:51:04 UTC)

OpenSpec: openspec/changes/20261105-225104-64i-concurrencia. Modo de trabajo: confirmacion. Estado de factory: espera aceptación de proposal.md y spec.md.

### Nota (2026-11-05 22:59:11 UTC)

Brian Hollweg (persona, decidio, modo confirmacion) aceptó propuesta y spec openspec/changes/20261105-225104-64i-concurrencia/specs/web/spec.md; se reiniciaron las validaciones dependientes.

### Nota (2026-11-05 23:00:07 UTC)

Requisitos importados: web_cc8d4b754936380f4.la_escena_se_controla_y_es_accesible (funcional), web_cc8d4b754936380f4.la_simulacion_dice_que_es_una_simulacion (funcional), web_cc8d4b754936380f4.la_simulacion_sigue_las_reglas (funcional), web_cc8d4b754936380f4.los_escenarios_cuentan_la_concurrencia (funcional). Los nuevos nacen SIN MEDIR; verificá cobertura antes del juicio.

### Nota (2026-11-05 23:10:17 UTC)

Medidas de web_cc8d4b754936380f4.la_simulacion_sigue_las_reglas: factory_web_concurrencia.la_simulacion_sigue_las_reglas, factory_web_concurrencia.corrida_completa; propuestas por claude-code (agente, propuso, modo confirmacion). SIN MEDIR: sin límite adicional declarado. Revisión y juicio anteriores invalidados; no se declara cumplimiento ni aprobación de pertinencia.

### Nota (2026-11-05 23:10:19 UTC)

Medidas de web_cc8d4b754936380f4.los_escenarios_cuentan_la_concurrencia: factory_web_concurrencia.los_escenarios_cuentan_la_concurrencia, factory_web_concurrencia.corrida_completa; propuestas por claude-code (agente, propuso, modo confirmacion). SIN MEDIR: sin límite adicional declarado. Revisión y juicio anteriores invalidados; no se declara cumplimiento ni aprobación de pertinencia.

### Nota (2026-11-05 23:10:20 UTC)

Medidas de web_cc8d4b754936380f4.la_escena_se_controla_y_es_accesible: factory_web_concurrencia.la_escena_se_controla_y_es_accesible, factory_web_concurrencia.corrida_completa; propuestas por claude-code (agente, propuso, modo confirmacion). SIN MEDIR: sin límite adicional declarado. Revisión y juicio anteriores invalidados; no se declara cumplimiento ni aprobación de pertinencia.

### Nota (2026-11-05 23:10:22 UTC)

Medidas de web_cc8d4b754936380f4.la_simulacion_dice_que_es_una_simulacion: factory_web_concurrencia.la_simulacion_dice_que_es_una_simulacion, factory_web_concurrencia.corrida_completa; propuestas por claude-code (agente, propuso, modo confirmacion). SIN MEDIR: sin límite adicional declarado. Revisión y juicio anteriores invalidados; no se declara cumplimiento ni aprobación de pertinencia.

### Nota (2026-11-05 23:23:44 UTC)

Medidas de web_cc8d4b754936380f4.la_escena_se_controla_y_es_accesible: Brian Hollweg (persona, confirmo, modo confirmacion).

### Nota (2026-11-05 23:23:45 UTC)

Medidas de web_cc8d4b754936380f4.la_simulacion_dice_que_es_una_simulacion: Brian Hollweg (persona, confirmo, modo confirmacion).

### Nota (2026-11-05 23:23:45 UTC)

Medidas de web_cc8d4b754936380f4.la_simulacion_sigue_las_reglas: Brian Hollweg (persona, confirmo, modo confirmacion).

### Nota (2026-11-05 23:23:45 UTC)

Medidas de web_cc8d4b754936380f4.los_escenarios_cuentan_la_concurrencia: Brian Hollweg (persona, confirmo, modo confirmacion).

### Nota (2026-11-06 00:13:00 UTC)

Revisión guiada Brian Hollweg: aprobar; registrada por Brian Hollweg (persona, confirmo, modo confirmacion; motivo: Cinco rondas con codex (agy2-flash sin cuota, agy y agy2 fallan por el --effort del wrapper): la última cerró con 0 hallazgos. Hallazgos corregidos con prueba y mutaciones: CC-1 (cerrar exige revisión vigente), CC-2 (ids de evento por rama y secuencia), CC-3 y CC-4 (un agente sólo edita y trae main), CC-5 a CC-8 (cada actor en su checkout; acciones, actores y decisiones no modeladas lanzan error). Evidencia: 1155 pruebas, 9 casos de contrato, éxito. Límites declarados: es una simulación de las reglas con cinco guiones fijos, no ejecuta Factory ni Git; sólo un revisor independiente revisó (codex); con movimiento reducido la simulación elige por la persona la primera opción y lo dice. Test existente: ninguno editado; tests/datos/guias-texto.json se regeneró por una frase nueva con enlace en colaboracion.html.); 0 abiertos derivados; commit 8ab59b40276d1f3033d9d930a0b1f5f1c112585c; informe tareas/20261105-225104-64i-concurrencia/revisiones/registro-rf6sf402/informe.json; decisiones tareas/20261105-225104-64i-concurrencia/revisiones/registro-rf6sf402/decisiones.json.

### Nota (2026-11-06 00:13:34 UTC)

Juicio Factory: verde; salida Oracle 0; informe .factory/cambios/20261105-225104-64i-concurrencia/oracle-veredicto.txt.

### Nota (2026-11-06 00:15:40 UTC)

Cierre: Brian Hollweg (persona, decidio, modo confirmacion), tras revisar el informe de código y el veredicto Oracle.
