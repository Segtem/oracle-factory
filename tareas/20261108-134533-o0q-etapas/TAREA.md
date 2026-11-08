# Autonomía por etapa: construcción, integración, publicación y producción

- ESTADO: CERRADA
- PRIORIDAD: 50
- ETIQUETAS: 

### Nota (2026-11-08 13:45:33 UTC)

OpenSpec: openspec/changes/20261108-134533-o0q-etapas. Modo de trabajo: confirmacion. Estado de factory: espera aceptación de proposal.md y spec.md.

### Nota (2026-11-08 13:54:25 UTC)

Brian Hollweg (persona, decidio, modo confirmacion) aceptó propuesta y spec openspec/changes/20261108-134533-o0q-etapas/specs/modos/spec.md; se reiniciaron las validaciones dependientes.

### Nota (2026-11-08 13:54:44 UTC)

Requisitos importados: modos_ce25b1098e45c53ae.autonomia_muestra_las_etapas_y_quien_decide_en_cada_una (funcional), modos_ce25b1098e45c53ae.desplegar_autorizar_respeta_la_autonomia_de_produccion (funcional), modos_ce25b1098e45c53ae.la_autonomia_se_declara_por_etapa_y_lo_no_declarado_pide_a_una_persona (funcional), modos_ce25b1098e45c53ae.solo_una_persona_cambia_la_autonomia_de_una_etapa (funcional), modos_ce25b1098e45c53ae.un_agente_solo_decide_en_una_etapa_autonoma (funcional). Los nuevos nacen SIN MEDIR; verificá cobertura antes del juicio.

### Nota (2026-11-08 13:59:32 UTC)

Medidas de modos_ce25b1098e45c53ae.la_autonomia_se_declara_por_etapa_y_lo_no_declarado_pide_a_una_persona: factory_etapas.la_autonomia_se_declara_por_etapa_y_lo_no_declarado_pide_a_una_persona, factory_etapas.corrida_completa; propuestas por claude-code (agente, propuso, modo confirmacion). SIN MEDIR: sin límite adicional declarado. Revisión y juicio anteriores invalidados; no se declara cumplimiento ni aprobación de pertinencia.

### Nota (2026-11-08 13:59:34 UTC)

Medidas de modos_ce25b1098e45c53ae.un_agente_solo_decide_en_una_etapa_autonoma: factory_etapas.un_agente_solo_decide_en_una_etapa_autonoma, factory_etapas.corrida_completa; propuestas por claude-code (agente, propuso, modo confirmacion). SIN MEDIR: sin límite adicional declarado. Revisión y juicio anteriores invalidados; no se declara cumplimiento ni aprobación de pertinencia.

### Nota (2026-11-08 13:59:36 UTC)

Medidas de modos_ce25b1098e45c53ae.autonomia_muestra_las_etapas_y_quien_decide_en_cada_una: factory_etapas.autonomia_muestra_las_etapas_y_quien_decide_en_cada_una, factory_etapas.corrida_completa; propuestas por claude-code (agente, propuso, modo confirmacion). SIN MEDIR: sin límite adicional declarado. Revisión y juicio anteriores invalidados; no se declara cumplimiento ni aprobación de pertinencia.

### Nota (2026-11-08 13:59:38 UTC)

Medidas de modos_ce25b1098e45c53ae.solo_una_persona_cambia_la_autonomia_de_una_etapa: factory_etapas.solo_una_persona_cambia_la_autonomia_de_una_etapa, factory_etapas.corrida_completa; propuestas por claude-code (agente, propuso, modo confirmacion). SIN MEDIR: sin límite adicional declarado. Revisión y juicio anteriores invalidados; no se declara cumplimiento ni aprobación de pertinencia.

### Nota (2026-11-08 13:59:40 UTC)

Medidas de modos_ce25b1098e45c53ae.desplegar_autorizar_respeta_la_autonomia_de_produccion: factory_etapas.desplegar_autorizar_respeta_la_autonomia_de_produccion, factory_etapas.corrida_completa; propuestas por claude-code (agente, propuso, modo confirmacion). SIN MEDIR: sin límite adicional declarado. Revisión y juicio anteriores invalidados; no se declara cumplimiento ni aprobación de pertinencia.

### Nota (2026-11-08 14:00:38 UTC)

Medidas de modos_ce25b1098e45c53ae.autonomia_muestra_las_etapas_y_quien_decide_en_cada_una: Brian Hollweg (persona, confirmo, modo confirmacion).

### Nota (2026-11-08 14:00:38 UTC)

Medidas de modos_ce25b1098e45c53ae.desplegar_autorizar_respeta_la_autonomia_de_produccion: Brian Hollweg (persona, confirmo, modo confirmacion).

### Nota (2026-11-08 14:00:38 UTC)

Medidas de modos_ce25b1098e45c53ae.la_autonomia_se_declara_por_etapa_y_lo_no_declarado_pide_a_una_persona: Brian Hollweg (persona, confirmo, modo confirmacion).

### Nota (2026-11-08 14:00:38 UTC)

Medidas de modos_ce25b1098e45c53ae.solo_una_persona_cambia_la_autonomia_de_una_etapa: Brian Hollweg (persona, confirmo, modo confirmacion).

### Nota (2026-11-08 14:00:39 UTC)

Medidas de modos_ce25b1098e45c53ae.un_agente_solo_decide_en_una_etapa_autonoma: Brian Hollweg (persona, confirmo, modo confirmacion).

### Nota (2026-11-08 15:00:27 UTC)

Revisión guiada Brian Hollweg: aprobar; registrada por Brian Hollweg (persona, confirmo, modo confirmacion; motivo: Codex sin hallazgos sobre d2f0ec3. Evidencia 1276 pruebas OK, 16 casos. Toca reglas de decisión (cli.py, modos.py): camino completo. Por defecto el cambio es cero: las tres etapas siguen en confirmacion y desplegar --autorizar sigue siendo solo de una persona hasta que una persona ponga produccion en autonomo con el comando. Cambiar la autonomía de una etapa es solo de una persona con confirmación en su terminal; un agente no puede. 12 mutaciones propias, 11 detectadas; la que sobrevive es equivalente (quitar el rechazo explícito a un agente en comando_autonomia: confirmar_persona→exigir_terminal ya lo niega). Declaro pruebas existentes tocadas, solo de forma aditiva o regenerada: test_agentes.py suma la orden 'autonomia ETAPA MODO' a las de persona que recorre; ayuda-cli.json regenerado (índice, desplegar y autonomia). Limite: integración y publicación no tienen comando de Factory que las aplique todavía; la política queda declarada y la salida lo dice. Seguimiento: un agente podría editar a mano .factory/config.json (la guía ya dice que no se edita a mano .factory/) y así darse autonomía; no hay una guarda técnica contra eso, solo la regla escrita.); 0 abiertos derivados; commit 6efe70a845511c7c344c94af1f6327d5c3a3443a; informe tareas/20261108-134533-o0q-etapas/revisiones/registro-z_9p1a4s/informe.json; decisiones tareas/20261108-134533-o0q-etapas/revisiones/registro-z_9p1a4s/decisiones.json.

### Nota (2026-11-08 15:00:56 UTC)

Juicio Factory: verde; salida Oracle 0; informe .factory/cambios/20261108-134533-o0q-etapas/oracle-veredicto.txt.

### Nota (2026-11-08 15:01:34 UTC)

Cierre: Brian Hollweg (persona, decidio, modo confirmacion), tras revisar el informe de código y el veredicto Oracle.
