# Alcance opcional de los destinos: desplegar sólo lo que cambió

- ESTADO: ABIERTA
- PRIORIDAD: 50
- ETIQUETAS: 

### Nota (2026-11-08 02:09:32 UTC)

OpenSpec: openspec/changes/20261108-020932-3t5-alcance. Modo de trabajo: confirmacion. Estado de factory: espera aceptación de proposal.md y spec.md.

### Nota (2026-11-08 02:16:10 UTC)

Brian Hollweg (persona, decidio, modo confirmacion) aceptó propuesta y spec openspec/changes/20261108-020932-3t5-alcance/specs/despliegue/spec.md; se reiniciaron las validaciones dependientes.

### Nota (2026-11-08 02:16:20 UTC)

Requisitos importados: despliegue_c15d6443128edff6b.cambios_elige_los_destinos_afectados (funcional), despliegue_c15d6443128edff6b.el_plan_explica_la_eleccion_y_no_ejecuta_si_no_hay_nada (funcional), despliegue_c15d6443128edff6b.sin_cambios_nada_cambia_y_la_guia_cuenta_el_alcance (funcional), despliegue_c15d6443128edff6b.un_destino_declara_su_alcance_opcional (funcional). Los nuevos nacen SIN MEDIR; verificá cobertura antes del juicio.

### Nota (2026-11-08 02:18:07 UTC)

Medidas de despliegue_c15d6443128edff6b.un_destino_declara_su_alcance_opcional: factory_destinos_alcance.un_destino_declara_su_alcance_opcional, factory_destinos_alcance.corrida_completa; propuestas por claude-code (agente, propuso, modo confirmacion). SIN MEDIR: sin límite adicional declarado. Revisión y juicio anteriores invalidados; no se declara cumplimiento ni aprobación de pertinencia.

### Nota (2026-11-08 02:18:09 UTC)

Medidas de despliegue_c15d6443128edff6b.cambios_elige_los_destinos_afectados: factory_destinos_alcance.cambios_elige_los_destinos_afectados, factory_destinos_alcance.corrida_completa; propuestas por claude-code (agente, propuso, modo confirmacion). SIN MEDIR: sin límite adicional declarado. Revisión y juicio anteriores invalidados; no se declara cumplimiento ni aprobación de pertinencia.

### Nota (2026-11-08 02:18:10 UTC)

Medidas de despliegue_c15d6443128edff6b.el_plan_explica_la_eleccion_y_no_ejecuta_si_no_hay_nada: factory_destinos_alcance.el_plan_explica_la_eleccion_y_no_ejecuta_si_no_hay_nada, factory_destinos_alcance.corrida_completa; propuestas por claude-code (agente, propuso, modo confirmacion). SIN MEDIR: sin límite adicional declarado. Revisión y juicio anteriores invalidados; no se declara cumplimiento ni aprobación de pertinencia.

### Nota (2026-11-08 02:18:12 UTC)

Medidas de despliegue_c15d6443128edff6b.sin_cambios_nada_cambia_y_la_guia_cuenta_el_alcance: factory_destinos_alcance.sin_cambios_nada_cambia_y_la_guia_cuenta_el_alcance, factory_destinos_alcance.corrida_completa; propuestas por claude-code (agente, propuso, modo confirmacion). SIN MEDIR: sin límite adicional declarado. Revisión y juicio anteriores invalidados; no se declara cumplimiento ni aprobación de pertinencia.

### Nota (2026-11-08 02:18:38 UTC)

Medidas de despliegue_c15d6443128edff6b.cambios_elige_los_destinos_afectados: Brian Hollweg (persona, confirmo, modo confirmacion).

### Nota (2026-11-08 02:18:39 UTC)

Medidas de despliegue_c15d6443128edff6b.el_plan_explica_la_eleccion_y_no_ejecuta_si_no_hay_nada: Brian Hollweg (persona, confirmo, modo confirmacion).

### Nota (2026-11-08 02:18:39 UTC)

Medidas de despliegue_c15d6443128edff6b.sin_cambios_nada_cambia_y_la_guia_cuenta_el_alcance: Brian Hollweg (persona, confirmo, modo confirmacion).

### Nota (2026-11-08 02:18:39 UTC)

Medidas de despliegue_c15d6443128edff6b.un_destino_declara_su_alcance_opcional: Brian Hollweg (persona, confirmo, modo confirmacion).

### Nota (2026-11-08 04:24:51 UTC)

Revisión guiada Brian Hollweg: aprobar; registrada por Brian Hollweg (persona, confirmo, modo confirmacion; motivo: Codex sin hallazgos. Evidencia 1245 pruebas OK. 8 mutaciones propias sobre despliegue.py y cli.py detectadas; una sobrevive y es equivalente (invertir el rango del diff: --name-only es simétrico). Incluye un arreglo no pedido por la spec: despliegue.registros desempata por el momento en que se escribió el registro (dos corridas del mismo segundo quedaban en orden arbitrario), con prueba determinista; también corrige estados. Sin ediciones a pruebas existentes salvo el golden de la ayuda (sólo desplegar). Toca cli.py: camino completo.); 0 abiertos derivados; commit 69a95185532763fd98ac976ee90a0fcb6adab036; informe tareas/20261108-020932-3t5-alcance/revisiones/registro-_xyfh2af/informe.json; decisiones tareas/20261108-020932-3t5-alcance/revisiones/registro-_xyfh2af/decisiones.json.

### Nota (2026-11-08 04:25:02 UTC)

Juicio Factory: incompleto/rojo; salida Oracle 1; informe .factory/cambios/20261108-020932-3t5-alcance/oracle-veredicto.txt.

### Nota (2026-11-08 04:25:41 UTC)

Medidas de despliegue_c15d6443128edff6b.cambios_elige_los_destinos_afectados propuestas por claude-code (agente, modo confirmacion); no cuentan hasta que una persona las confirme.

### Nota (2026-11-08 04:25:44 UTC)

Medidas de despliegue_c15d6443128edff6b.el_plan_explica_la_eleccion_y_no_ejecuta_si_no_hay_nada propuestas por claude-code (agente, modo confirmacion); no cuentan hasta que una persona las confirme.

### Nota (2026-11-08 04:25:47 UTC)

Medidas de despliegue_c15d6443128edff6b.sin_cambios_nada_cambia_y_la_guia_cuenta_el_alcance propuestas por claude-code (agente, modo confirmacion); no cuentan hasta que una persona las confirme.

### Nota (2026-11-08 04:25:50 UTC)

Medidas de despliegue_c15d6443128edff6b.un_destino_declara_su_alcance_opcional propuestas por claude-code (agente, modo confirmacion); no cuentan hasta que una persona las confirme.

### Nota (2026-11-08 04:33:54 UTC)

Medidas de despliegue_c15d6443128edff6b.cambios_elige_los_destinos_afectados: Brian Hollweg (persona, confirmo, modo confirmacion).

### Nota (2026-11-08 04:33:54 UTC)

Medidas de despliegue_c15d6443128edff6b.el_plan_explica_la_eleccion_y_no_ejecuta_si_no_hay_nada: Brian Hollweg (persona, confirmo, modo confirmacion).

### Nota (2026-11-08 04:33:54 UTC)

Medidas de despliegue_c15d6443128edff6b.sin_cambios_nada_cambia_y_la_guia_cuenta_el_alcance: Brian Hollweg (persona, confirmo, modo confirmacion).

### Nota (2026-11-08 04:33:54 UTC)

Medidas de despliegue_c15d6443128edff6b.un_destino_declara_su_alcance_opcional: Brian Hollweg (persona, confirmo, modo confirmacion).

### Nota (2026-11-08 04:51:21 UTC)

Revisión guiada Brian Hollweg: aprobar; registrada por Brian Hollweg (persona, confirmo, modo confirmacion; motivo: Segunda ronda tras corregir los catálogos (14 casos; cambios_elige 6). Codex sin hallazgos sobre d1b6a74. Evidencia 1245 pruebas OK, 14 casos. Código y pruebas sin cambios desde la primera ronda: 8 mutaciones detectadas, una equivalente (invertir el rango del diff). Incluye el arreglo de despliegue.registros (desempate por momento de escritura) con prueba determinista. Toca cli.py: camino completo.); 0 abiertos derivados; commit 1f18689dac07063ffb7dfae1cc3cec3c66c0a30a; informe tareas/20261108-020932-3t5-alcance/revisiones/registro-a4koy_cu/informe.json; decisiones tareas/20261108-020932-3t5-alcance/revisiones/registro-a4koy_cu/decisiones.json.

### Nota (2026-11-08 05:00:07 UTC)

Revisión guiada Brian Hollweg: aprobar; registrada por Brian Hollweg (persona, decidio, modo confirmacion; motivo: Apruebo el candidato d1b6a74; 0 hallazgos de los revisores; evidencia del candidato: 1245 pruebas, 14 casos de contrato; 1 vuelta anterior registrada.); 0 abiertos derivados; commit 1f18689dac07063ffb7dfae1cc3cec3c66c0a30a; informe tareas/20261108-020932-3t5-alcance/revisiones/registro-_w9v6yr3/informe.json; decisiones tareas/20261108-020932-3t5-alcance/revisiones/registro-_w9v6yr3/decisiones.json.
