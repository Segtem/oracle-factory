# Preparar la distribución 0.1.0a17

- ESTADO: ABIERTA
- PRIORIDAD: 50
- ETIQUETAS: 

### Nota (2026-11-03 23:22:02 UTC)

OpenSpec: openspec/changes/20261103-232202-jo3-entregaa17. Modo de trabajo: confirmacion. Estado de factory: espera aceptación de proposal.md y spec.md.

### Nota (2026-11-03 23:24:57 UTC)

Brian Hollweg (persona, decidio, modo confirmacion) aceptó propuesta y spec openspec/changes/20261103-232202-jo3-entregaa17/specs/distribucion/spec.md; se reiniciaron las validaciones dependientes.

### Nota (2026-11-03 23:25:09 UTC)

Requisitos importados: distribucion_c4b4c8c6521232d76.el_wheel_a17_instalado_ofrece_lo_nuevo (funcional), distribucion_c4b4c8c6521232d76.la_entrega_a17_registra_sus_hashes_y_sus_limites (funcional), distribucion_c4b4c8c6521232d76.la_version_a17_es_coherente_y_declara_su_estado (funcional). Los nuevos nacen SIN MEDIR; verificá cobertura antes del juicio.

### Nota (2026-11-03 23:40:59 UTC)

Medidas de distribucion_c4b4c8c6521232d76.la_version_a17_es_coherente_y_declara_su_estado: factory_entrega_a17.la_version_a17_es_coherente_y_declara_su_estado, factory_entrega_a17.corrida_completa; propuestas por claude-code (agente, propuso, modo confirmacion). SIN MEDIR: sin límite adicional declarado. Revisión y juicio anteriores invalidados; no se declara cumplimiento ni aprobación de pertinencia.

### Nota (2026-11-03 23:41:00 UTC)

Medidas de distribucion_c4b4c8c6521232d76.el_wheel_a17_instalado_ofrece_lo_nuevo: factory_entrega_a17.el_wheel_a17_instalado_ofrece_lo_nuevo, factory_entrega_a17.corrida_completa; propuestas por claude-code (agente, propuso, modo confirmacion). SIN MEDIR: sin límite adicional declarado. Revisión y juicio anteriores invalidados; no se declara cumplimiento ni aprobación de pertinencia.

### Nota (2026-11-03 23:41:02 UTC)

Medidas de distribucion_c4b4c8c6521232d76.la_entrega_a17_registra_sus_hashes_y_sus_limites: factory_entrega_a17.la_entrega_a17_registra_sus_hashes_y_sus_limites, factory_entrega_a17.corrida_completa; propuestas por claude-code (agente, propuso, modo confirmacion). SIN MEDIR: sin límite adicional declarado. Revisión y juicio anteriores invalidados; no se declara cumplimiento ni aprobación de pertinencia.

### Nota (2026-11-04 00:37:53 UTC)

Medidas de distribucion_c4b4c8c6521232d76.el_wheel_a17_instalado_ofrece_lo_nuevo: Brian Hollweg (persona, confirmo, modo confirmacion).

### Nota (2026-11-04 00:37:53 UTC)

Medidas de distribucion_c4b4c8c6521232d76.la_entrega_a17_registra_sus_hashes_y_sus_limites: Brian Hollweg (persona, confirmo, modo confirmacion).

### Nota (2026-11-04 00:37:53 UTC)

Medidas de distribucion_c4b4c8c6521232d76.la_version_a17_es_coherente_y_declara_su_estado: Brian Hollweg (persona, confirmo, modo confirmacion).

### Nota (2026-11-04 03:15:36 UTC)

Revisión guiada Brian Hollweg: aprobar; registrada por Brian Hollweg (persona, confirmo, modo confirmacion; motivo: Dos rondas con agy2-flash y codex sobre el candidato. La primera trajo 3 hallazgos (1 media y 2 bajos): el probador no ejercitaba hooks en el wheel instalado, registro.json podía quedar con ok verdadero y con problemas a la vez, y no se exigía que el módulo viniera del entorno nuevo. Los tres se arreglaron y cada arreglo tiene una prueba que falla si se lo quita (4 mutaciones, todas detectadas). La segunda ronda cerró con 0 hallazgos de los dos revisores. La evidencia del candidato cc05132 corrió la suite completa: 1113 pruebas y 19 casos de contrato, éxito. Quedan declarados el borrado de test_entrega_a16.py y test_publicada_a16.py (fijados a la a16, reemplazados por test_entrega_a17.py), los cambios de cadenas de versión en test_docs.py y la regeneración de guias-texto.json. No sube nada a PyPI ni crea tag: eso queda para después del cierre.); 0 abiertos derivados; commit 5a92ce54a7245e858d939b5f903dfe1551bacc61; informe tareas/20261103-232202-jo3-entregaa17/revisiones/registro-u6_d2szh/informe.json; decisiones tareas/20261103-232202-jo3-entregaa17/revisiones/registro-u6_d2szh/decisiones.json.

### Nota (2026-11-04 03:15:54 UTC)

Medidas de distribucion_c4b4c8c6521232d76.el_wheel_a17_instalado_ofrece_lo_nuevo propuestas por claude-code (agente, modo confirmacion); no cuentan hasta que una persona las confirme.

### Nota (2026-11-04 03:15:55 UTC)

Medidas de distribucion_c4b4c8c6521232d76.la_entrega_a17_registra_sus_hashes_y_sus_limites propuestas por claude-code (agente, modo confirmacion); no cuentan hasta que una persona las confirme.

### Nota (2026-11-04 03:15:57 UTC)

Medidas de distribucion_c4b4c8c6521232d76.la_version_a17_es_coherente_y_declara_su_estado propuestas por claude-code (agente, modo confirmacion); no cuentan hasta que una persona las confirme.
