# Avisar de los bucles de revisión y de los cambios demasiado grandes

- ESTADO: ABIERTA
- PRIORIDAD: 50
- ETIQUETAS: 

### Nota (2026-11-01 20:57:30 UTC)

OpenSpec: openspec/changes/20261101-205730-dm3-alarmasflujo. Modo de trabajo: confirmacion. Estado de factory: espera aceptación de proposal.md y spec.md.

### Nota (2026-11-01 21:08:43 UTC)

Brian Hollweg (persona, decidio, modo confirmacion) aceptó propuesta y spec openspec/changes/20261101-205730-dm3-alarmasflujo/specs/practicas/spec.md; se reiniciaron las validaciones dependientes.

### Nota (2026-11-01 21:10:12 UTC)

Requisitos importados: practicas_c58d3f9c8777a3388.el_documento_nombra_los_umbrales_y_dice_que_el_conteo_de_aserciones_es_aproximado (funcional), practicas_c58d3f9c8777a3388.el_estado_avisa_cuando_el_candidato_agrega_mas_de_450_lineas_de_producto (funcional), practicas_c58d3f9c8777a3388.el_estado_avisa_cuando_la_revision_lleva_cuatro_rondas (funcional). Los nuevos nacen SIN MEDIR; verificá cobertura antes del juicio.

### Nota (2026-11-01 21:13:18 UTC)

Medidas de practicas_c58d3f9c8777a3388.el_estado_avisa_cuando_la_revision_lleva_cuatro_rondas: factory_alarmas_flujo.el_estado_avisa_cuando_la_revision_lleva_cuatro_rondas, factory_alarmas_flujo.corrida_completa; propuestas por claude-code (agente, propuso, modo confirmacion). SIN MEDIR: sin límite adicional declarado. Revisión y juicio anteriores invalidados; no se declara cumplimiento ni aprobación de pertinencia.

### Nota (2026-11-01 21:13:19 UTC)

Medidas de practicas_c58d3f9c8777a3388.el_estado_avisa_cuando_el_candidato_agrega_mas_de_450_lineas_de_producto: factory_alarmas_flujo.el_estado_avisa_cuando_el_candidato_agrega_mas_de_450_lineas_de_producto, factory_alarmas_flujo.corrida_completa; propuestas por claude-code (agente, propuso, modo confirmacion). SIN MEDIR: sin límite adicional declarado. Revisión y juicio anteriores invalidados; no se declara cumplimiento ni aprobación de pertinencia.

### Nota (2026-11-01 21:13:21 UTC)

Medidas de practicas_c58d3f9c8777a3388.el_documento_nombra_los_umbrales_y_dice_que_el_conteo_de_aserciones_es_aproximado: factory_alarmas_flujo.el_documento_nombra_los_umbrales_y_dice_que_el_conteo_de_aserciones_es_aproximado, factory_alarmas_flujo.corrida_completa; propuestas por claude-code (agente, propuso, modo confirmacion). SIN MEDIR: sin límite adicional declarado. Revisión y juicio anteriores invalidados; no se declara cumplimiento ni aprobación de pertinencia.

### Nota (2026-11-01 21:22:39 UTC)

Medidas de practicas_c58d3f9c8777a3388.el_documento_nombra_los_umbrales_y_dice_que_el_conteo_de_aserciones_es_aproximado: Brian Hollweg (persona, confirmo, modo confirmacion).

### Nota (2026-11-01 21:22:39 UTC)

Medidas de practicas_c58d3f9c8777a3388.el_estado_avisa_cuando_el_candidato_agrega_mas_de_450_lineas_de_producto: Brian Hollweg (persona, confirmo, modo confirmacion).

### Nota (2026-11-01 21:22:39 UTC)

Medidas de practicas_c58d3f9c8777a3388.el_estado_avisa_cuando_la_revision_lleva_cuatro_rondas: Brian Hollweg (persona, confirmo, modo confirmacion).

### Nota (2026-11-01 22:08:41 UTC)

Medidas de practicas_c58d3f9c8777a3388.el_estado_avisa_cuando_la_revision_lleva_cuatro_rondas propuestas por claude-code (agente, modo confirmacion); no cuentan hasta que una persona las confirme.

### Nota (2026-11-01 22:08:42 UTC)

Medidas de practicas_c58d3f9c8777a3388.el_estado_avisa_cuando_el_candidato_agrega_mas_de_450_lineas_de_producto propuestas por claude-code (agente, modo confirmacion); no cuentan hasta que una persona las confirme.

### Nota (2026-11-01 22:08:44 UTC)

Medidas de practicas_c58d3f9c8777a3388.el_documento_nombra_los_umbrales_y_dice_que_el_conteo_de_aserciones_es_aproximado propuestas por claude-code (agente, modo confirmacion); no cuentan hasta que una persona las confirme.

### Nota (2026-11-01 22:28:14 UTC)

Medidas de practicas_c58d3f9c8777a3388.el_documento_nombra_los_umbrales_y_dice_que_el_conteo_de_aserciones_es_aproximado: Brian Hollweg (persona, confirmo, modo confirmacion).

### Nota (2026-11-01 22:28:14 UTC)

Medidas de practicas_c58d3f9c8777a3388.el_estado_avisa_cuando_el_candidato_agrega_mas_de_450_lineas_de_producto: Brian Hollweg (persona, confirmo, modo confirmacion).

### Nota (2026-11-01 22:28:14 UTC)

Medidas de practicas_c58d3f9c8777a3388.el_estado_avisa_cuando_la_revision_lleva_cuatro_rondas: Brian Hollweg (persona, confirmo, modo confirmacion).

### Nota (2026-11-01 22:49:13 UTC)

Revisión guiada Brian Hollweg: aprobar; registrada por Brian Hollweg (persona, confirmo, modo confirmacion; motivo: Dos rondas con revisores independientes (agy2-flash y codex): ronda 1, 8 hallazgos (7 de flash, 1 de codex), todos reales y corregidos con prueba y mutación; ronda 2, 0 de ambos sobre el candidato 2aab69a. Se arregló la clase y no sólo el caso: la rama principal (main o master) y los nombres no UTF-8 también en la alarma de tests editados, salidas de Git rotas, SHA de otro largo, eventos raros y cambios abandonados. Evidencia con éxito: 995 pruebas, 26 casos de contrato. Mutaciones: 12 de la primera tanda (4 sobrevivían, se agregaron pruebas y se detectan) y 10 de la segunda, todas detectadas. Declarado: un test existente cambió (test_te1_sin_candidato_o_sin_base_no_se_calcula_y_no_se_llama_a_git_de_mas pasó de 1 a 2 llamadas porque el merge-base prueba main y master); es consecuencia directa de ese arreglo y los revisores lo vieron en su pedido. Fuera del arreglo: un evento con candidato no textual rompe commits_del_cambio, fragilidad anterior a este cambio.); 0 abiertos derivados; commit d569cc9c20c2d3a1c29078663e114c5f3339b7c0; informe tareas/20261101-205730-dm3-alarmasflujo/revisiones/registro-xcz437z7/informe.json; decisiones tareas/20261101-205730-dm3-alarmasflujo/revisiones/registro-xcz437z7/decisiones.json.

### Nota (2026-11-01 22:49:57 UTC)

Juicio Factory: verde; salida Oracle 0; informe .factory/cambios/20261101-205730-dm3-alarmasflujo/oracle-veredicto.txt.
