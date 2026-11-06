# Despliegue a varios destinos con prueba de que todo quedó funcionando

- ESTADO: ABIERTA
- PRIORIDAD: 50
- ETIQUETAS: 

### Nota (2026-11-06 20:52:02 UTC)

OpenSpec: openspec/changes/20261106-205202-8od-destinos. Modo de trabajo: confirmacion. Estado de factory: espera aceptación de proposal.md y spec.md.

### Nota (2026-11-06 20:57:52 UTC)

Brian Hollweg (persona, decidio, modo confirmacion) aceptó propuesta y spec openspec/changes/20261106-205202-8od-destinos/specs/despliegue/spec.md; se reiniciaron las validaciones dependientes.

### Nota (2026-11-06 20:58:05 UTC)

Requisitos importados: despliegue_c1f413032a7a55aa1.cada_ejecucion_deja_evidencia_sin_secretos (funcional), despliegue_c1f413032a7a55aa1.los_destinos_los_declara_el_proyecto (funcional), despliegue_c1f413032a7a55aa1.se_prueba_cada_destino_y_el_conjunto (funcional), despliegue_c1f413032a7a55aa1.sirve_para_cualquier_proyecto (funcional), despliegue_c1f413032a7a55aa1.un_despliegue_es_un_plan_que_autoriza_una_persona (funcional), despliegue_c1f413032a7a55aa1.un_fallo_deja_cada_destino_en_un_estado_dicho (funcional). Los nuevos nacen SIN MEDIR; verificá cobertura antes del juicio.

### Nota (2026-11-06 21:12:06 UTC)

Medidas de despliegue_c1f413032a7a55aa1.los_destinos_los_declara_el_proyecto: factory_despliegue.los_destinos_los_declara_el_proyecto, factory_despliegue.corrida_completa; propuestas por claude-code (agente, propuso, modo confirmacion). SIN MEDIR: sin límite adicional declarado. Revisión y juicio anteriores invalidados; no se declara cumplimiento ni aprobación de pertinencia.

### Nota (2026-11-06 21:12:08 UTC)

Medidas de despliegue_c1f413032a7a55aa1.un_despliegue_es_un_plan_que_autoriza_una_persona: factory_despliegue.un_despliegue_es_un_plan_que_autoriza_una_persona, factory_despliegue.corrida_completa; propuestas por claude-code (agente, propuso, modo confirmacion). SIN MEDIR: sin límite adicional declarado. Revisión y juicio anteriores invalidados; no se declara cumplimiento ni aprobación de pertinencia.

### Nota (2026-11-06 21:12:09 UTC)

Medidas de despliegue_c1f413032a7a55aa1.se_prueba_cada_destino_y_el_conjunto: factory_despliegue.se_prueba_cada_destino_y_el_conjunto, factory_despliegue.corrida_completa; propuestas por claude-code (agente, propuso, modo confirmacion). SIN MEDIR: sin límite adicional declarado. Revisión y juicio anteriores invalidados; no se declara cumplimiento ni aprobación de pertinencia.

### Nota (2026-11-06 21:12:11 UTC)

Medidas de despliegue_c1f413032a7a55aa1.un_fallo_deja_cada_destino_en_un_estado_dicho: factory_despliegue.un_fallo_deja_cada_destino_en_un_estado_dicho, factory_despliegue.corrida_completa; propuestas por claude-code (agente, propuso, modo confirmacion). SIN MEDIR: sin límite adicional declarado. Revisión y juicio anteriores invalidados; no se declara cumplimiento ni aprobación de pertinencia.

### Nota (2026-11-06 21:12:13 UTC)

Medidas de despliegue_c1f413032a7a55aa1.cada_ejecucion_deja_evidencia_sin_secretos: factory_despliegue.cada_ejecucion_deja_evidencia_sin_secretos, factory_despliegue.corrida_completa; propuestas por claude-code (agente, propuso, modo confirmacion). SIN MEDIR: sin límite adicional declarado. Revisión y juicio anteriores invalidados; no se declara cumplimiento ni aprobación de pertinencia.

### Nota (2026-11-06 21:12:14 UTC)

Medidas de despliegue_c1f413032a7a55aa1.sirve_para_cualquier_proyecto: factory_despliegue.sirve_para_cualquier_proyecto, factory_despliegue.corrida_completa; propuestas por claude-code (agente, propuso, modo confirmacion). SIN MEDIR: sin límite adicional declarado. Revisión y juicio anteriores invalidados; no se declara cumplimiento ni aprobación de pertinencia.

### Nota (2026-11-06 21:13:08 UTC)

Medidas de despliegue_c1f413032a7a55aa1.cada_ejecucion_deja_evidencia_sin_secretos: Brian Hollweg (persona, confirmo, modo confirmacion).

### Nota (2026-11-06 21:13:08 UTC)

Medidas de despliegue_c1f413032a7a55aa1.los_destinos_los_declara_el_proyecto: Brian Hollweg (persona, confirmo, modo confirmacion).

### Nota (2026-11-06 21:13:08 UTC)

Medidas de despliegue_c1f413032a7a55aa1.se_prueba_cada_destino_y_el_conjunto: Brian Hollweg (persona, confirmo, modo confirmacion).

### Nota (2026-11-06 21:13:08 UTC)

Medidas de despliegue_c1f413032a7a55aa1.sirve_para_cualquier_proyecto: Brian Hollweg (persona, confirmo, modo confirmacion).

### Nota (2026-11-06 21:13:08 UTC)

Medidas de despliegue_c1f413032a7a55aa1.un_despliegue_es_un_plan_que_autoriza_una_persona: Brian Hollweg (persona, confirmo, modo confirmacion).

### Nota (2026-11-06 21:13:08 UTC)

Medidas de despliegue_c1f413032a7a55aa1.un_fallo_deja_cada_destino_en_un_estado_dicho: Brian Hollweg (persona, confirmo, modo confirmacion).

### Nota (2026-11-06 22:59:02 UTC)

Revisión guiada Brian Hollweg: aprobar; registrada por Brian Hollweg (persona, confirmo, modo confirmacion; motivo: Tres rondas de codex: la última sin hallazgos. Cerrados DPL-01 a DPL-06 con prueba y mutaciones: versión obligatoria, tope del conjunto validado, rollback también con seguir, el tope mata el grupo de procesos, --destino arrastra sus dependencias y el conjunto es obligatorio. Evidencia: 1190 pruebas, 23 casos de contrato, éxito. Declarado: tests/datos/ayuda-cli.json (entradas nuevas) y el conteo de guías de test_web_paginas.py (12 a 13). Fuera: 'alcance' del diseño no se implementó.); 0 abiertos derivados; commit 8b057d021e43dc65938720411025636f4d73ba12; informe tareas/20261106-205202-8od-destinos/revisiones/registro-m_7rqyuk/informe.json; decisiones tareas/20261106-205202-8od-destinos/revisiones/registro-m_7rqyuk/decisiones.json.

### Nota (2026-11-06 22:59:19 UTC)

Juicio Factory: verde; salida Oracle 0; informe .factory/cambios/20261106-205202-8od-destinos/oracle-veredicto.txt.
