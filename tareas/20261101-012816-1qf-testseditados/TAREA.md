# Avisar de los tests que ya existían y el cambio modificó o borró

- ESTADO: ABIERTA
- PRIORIDAD: 50
- ETIQUETAS: 

### Nota (2026-11-01 01:28:16 UTC)

OpenSpec: openspec/changes/20261101-012816-1qf-testseditados. Modo de trabajo: confirmacion. Estado de factory: espera aceptación de proposal.md y spec.md.

### Nota (2026-11-01 01:29:14 UTC)

Brian Hollweg (persona, decidio, modo confirmacion) aceptó propuesta y spec openspec/changes/20261101-012816-1qf-testseditados/specs/practicas/spec.md; se reiniciaron las validaciones dependientes.

### Nota (2026-11-01 01:29:25 UTC)

Requisitos importados: practicas_c30250c98e6023842.el_estado_avisa_de_los_tests_existentes_que_el_cambio_modifico_o_borro (funcional), practicas_c30250c98e6023842.el_pedido_al_revisor_lleva_los_tests_editados (funcional), practicas_c30250c98e6023842.solo_cuentan_los_archivos_de_pruebas (funcional). Los nuevos nacen SIN MEDIR; verificá cobertura antes del juicio.

### Nota (2026-11-01 01:36:15 UTC)

Medidas de practicas_c30250c98e6023842.el_estado_avisa_de_los_tests_existentes_que_el_cambio_modifico_o_borro: factory_tests_editados.el_estado_avisa_de_los_tests_existentes_que_el_cambio_modifico_o_borro, factory_tests_editados.corrida_completa; propuestas por claude-code (agente, propuso, modo confirmacion). SIN MEDIR: sin límite adicional declarado. Revisión y juicio anteriores invalidados; no se declara cumplimiento ni aprobación de pertinencia.

### Nota (2026-11-01 01:36:17 UTC)

Medidas de practicas_c30250c98e6023842.el_pedido_al_revisor_lleva_los_tests_editados: factory_tests_editados.el_pedido_al_revisor_lleva_los_tests_editados, factory_tests_editados.corrida_completa; propuestas por claude-code (agente, propuso, modo confirmacion). SIN MEDIR: sin límite adicional declarado. Revisión y juicio anteriores invalidados; no se declara cumplimiento ni aprobación de pertinencia.

### Nota (2026-11-01 01:36:18 UTC)

Medidas de practicas_c30250c98e6023842.solo_cuentan_los_archivos_de_pruebas: factory_tests_editados.solo_cuentan_los_archivos_de_pruebas, factory_tests_editados.corrida_completa; propuestas por claude-code (agente, propuso, modo confirmacion). SIN MEDIR: sin límite adicional declarado. Revisión y juicio anteriores invalidados; no se declara cumplimiento ni aprobación de pertinencia.

### Nota (2026-11-01 01:38:34 UTC)

Medidas de practicas_c30250c98e6023842.el_estado_avisa_de_los_tests_existentes_que_el_cambio_modifico_o_borro: Brian Hollweg (persona, confirmo, modo confirmacion).

### Nota (2026-11-01 01:38:34 UTC)

Medidas de practicas_c30250c98e6023842.el_pedido_al_revisor_lleva_los_tests_editados: Brian Hollweg (persona, confirmo, modo confirmacion).

### Nota (2026-11-01 01:38:34 UTC)

Medidas de practicas_c30250c98e6023842.solo_cuentan_los_archivos_de_pruebas: Brian Hollweg (persona, confirmo, modo confirmacion).

### Nota (2026-11-01 02:15:35 UTC)

Medidas de practicas_c30250c98e6023842.el_estado_avisa_de_los_tests_existentes_que_el_cambio_modifico_o_borro propuestas por claude-code (agente, modo confirmacion); no cuentan hasta que una persona las confirme.

### Nota (2026-11-01 02:15:36 UTC)

Medidas de practicas_c30250c98e6023842.el_pedido_al_revisor_lleva_los_tests_editados propuestas por claude-code (agente, modo confirmacion); no cuentan hasta que una persona las confirme.

### Nota (2026-11-01 02:15:38 UTC)

Medidas de practicas_c30250c98e6023842.solo_cuentan_los_archivos_de_pruebas propuestas por claude-code (agente, modo confirmacion); no cuentan hasta que una persona las confirme.

### Nota (2026-11-01 02:18:56 UTC)

Medidas de practicas_c30250c98e6023842.el_estado_avisa_de_los_tests_existentes_que_el_cambio_modifico_o_borro: Brian Hollweg (persona, confirmo, modo confirmacion).

### Nota (2026-11-01 02:18:56 UTC)

Medidas de practicas_c30250c98e6023842.el_pedido_al_revisor_lleva_los_tests_editados: Brian Hollweg (persona, confirmo, modo confirmacion).

### Nota (2026-11-01 02:18:57 UTC)

Medidas de practicas_c30250c98e6023842.solo_cuentan_los_archivos_de_pruebas: Brian Hollweg (persona, confirmo, modo confirmacion).

### Nota (2026-11-01 11:24:50 UTC)

Revisión guiada Brian Hollweg: aprobar; registrada por Brian Hollweg (persona, confirmo, modo confirmacion; motivo: Dos vueltas de revisión. La primera (agy2 y codex) dejó hallazgos reales, entre ellos que los renombres puros no avisaban (se podía desactivar un test en silencio), que se clasificaba por el destino y no por la base, que se miraban archivos generados, que los pathspecs no eran literales, que faltaban las aserciones de Go y otros lenguajes, y que el contrato del verificador tenía nombres de casos inexistentes; todo corregido, con pruebas que ahora fallan si se vuelven a romper. La segunda vuelta la hicieron codex y agy2-flash (gemini-3.8-flash-high, porque la cuota de Gemini 4 Argon de las dos cuentas de agy se agotó): ningún hallazgo medio ni alto; codex dejó un hallazgo bajo, que el contador de aserciones cuenta también comentarios y nombres con la palabra assert, que queda como límite declarado y como riesgo aceptado. Suite completa sin fallas y evidencia con éxito (30 casos de contrato). Revisor agy2-flash agregado a la configuración por pedido de Brian.); 0 abiertos derivados; commit d8944c2b1fb092f5735430f2ee5f1f0cf7c14c22; informe tareas/20261101-012816-1qf-testseditados/revisiones/registro-3_z4i_kd/informe.json; decisiones tareas/20261101-012816-1qf-testseditados/revisiones/registro-3_z4i_kd/decisiones.json.
