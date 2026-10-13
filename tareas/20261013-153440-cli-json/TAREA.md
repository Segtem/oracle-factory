# Salidas en JSON de estado, donde y resumen

- ESTADO: ABIERTA
- PRIORIDAD: 50
- ETIQUETAS: 

### Nota (2026-10-13 15:34:40 UTC)

OpenSpec: openspec/changes/20261013-153440-cli-json. Modo de trabajo: confirmacion. Estado de factory: espera aceptación de proposal.md y spec.md.

### Nota (2026-10-13 15:46:25 UTC)

Brian Hollweg (persona, decidio, modo confirmacion) aceptó propuesta y spec openspec/changes/20261013-153440-cli-json/specs/cli/spec.md; se reiniciaron las validaciones dependientes.

### Nota (2026-10-13 15:46:35 UTC)

Requisitos importados: cli_c38d280a51dea748e.donde_y_resumen_se_leen_como_json (funcional), cli_c38d280a51dea748e.estado_se_lee_como_json (funcional), cli_c38d280a51dea748e.la_salida_de_texto_no_cambia_y_los_errores_no_se_mezclan_con_el_json (funcional). Los nuevos nacen SIN MEDIR; verificá cobertura antes del juicio.

### Nota (2026-10-13 15:52:46 UTC)

Medidas de cli_c38d280a51dea748e.estado_se_lee_como_json: factory_cli_json.estado_se_lee_como_json, factory_cli_json.corrida_completa; propuestas por claude-code (agente, propuso, modo confirmacion). SIN MEDIR: sin límite adicional declarado. Revisión y juicio anteriores invalidados; no se declara cumplimiento ni aprobación de pertinencia.

### Nota (2026-10-13 15:52:46 UTC)

Medidas de cli_c38d280a51dea748e.donde_y_resumen_se_leen_como_json: factory_cli_json.donde_y_resumen_se_leen_como_json, factory_cli_json.corrida_completa; propuestas por claude-code (agente, propuso, modo confirmacion). SIN MEDIR: sin límite adicional declarado. Revisión y juicio anteriores invalidados; no se declara cumplimiento ni aprobación de pertinencia.

### Nota (2026-10-13 15:52:46 UTC)

Medidas de cli_c38d280a51dea748e.la_salida_de_texto_no_cambia_y_los_errores_no_se_mezclan_con_el_json: factory_cli_json.la_salida_de_texto_no_cambia_y_los_errores_no_se_mezclan_con_el_json, factory_cli_json.corrida_completa; propuestas por claude-code (agente, propuso, modo confirmacion). SIN MEDIR: sin límite adicional declarado. Revisión y juicio anteriores invalidados; no se declara cumplimiento ni aprobación de pertinencia.

### Nota (2026-10-13 16:03:35 UTC)

Medidas de cli_c38d280a51dea748e.donde_y_resumen_se_leen_como_json: Brian Hollweg (persona, confirmo, modo confirmacion).

### Nota (2026-10-13 16:03:35 UTC)

Medidas de cli_c38d280a51dea748e.estado_se_lee_como_json: Brian Hollweg (persona, confirmo, modo confirmacion).

### Nota (2026-10-13 16:03:35 UTC)

Medidas de cli_c38d280a51dea748e.la_salida_de_texto_no_cambia_y_los_errores_no_se_mezclan_con_el_json: Brian Hollweg (persona, confirmo, modo confirmacion).

### Nota (2026-10-13 17:34:36 UTC)

Revisión guiada Brian Hollweg: aprobar; registrada por Brian Hollweg (persona, confirmo, modo confirmacion; motivo: dos vueltas de codex y agy: la 1 trajo 2 medios, 2 bajos y 1 informativo; se corrigieron la vigencia del juicio y de la revisión (mismas reglas que estado en texto), las pruebas de oracle y del resumen y el actor de registros viejos, con aserciones que fallan en el código anterior dentro de los mismos 7 casos; la 2 no encontró nada. CLI-JSON-001 (un cambio sin evidencia no la lista como ausente en donde: cumplirlo cambiaría el texto de donde, que otro requisito prohíbe) queda como límite: el escenario se probó con los hechos de un juicio registrado que ya no están, y ajustar la spec va aparte. Suite 327 y evidencia en verde.); 0 abiertos derivados; commit 2e783f5118de7a45495c7fdced33fe4fca9e16da; informe tareas/20261013-153440-cli-json/revisiones/registro-j2d0pmoy/informe.json; decisiones tareas/20261013-153440-cli-json/revisiones/registro-j2d0pmoy/decisiones.json.
