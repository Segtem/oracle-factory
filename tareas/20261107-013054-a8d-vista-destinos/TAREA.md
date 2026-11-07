# Vista Destinos en el tablero de VS Code

- ESTADO: ABIERTA
- PRIORIDAD: 50
- ETIQUETAS: 

### Nota (2026-11-07 01:30:54 UTC)

OpenSpec: openspec/changes/20261107-013054-a8d-vista-destinos. Modo de trabajo: confirmacion. Estado de factory: espera aceptación de proposal.md y spec.md.

### Nota (2026-11-07 01:39:35 UTC)

Brian Hollweg (persona, decidio, modo confirmacion) aceptó propuesta y spec openspec/changes/20261107-013054-a8d-vista-destinos/specs/tablero/spec.md; se reiniciaron las validaciones dependientes.

### Nota (2026-11-07 01:39:47 UTC)

Requisitos importados: tablero_c67ccc28106a13a74.el_contrato_de_la_extension_cubre_destinos (funcional), tablero_c67ccc28106a13a74.el_tablero_muestra_cada_destino_con_su_estado (funcional), tablero_c67ccc28106a13a74.el_tablero_no_consulta_los_destinos_sin_que_se_pida (funcional), tablero_c67ccc28106a13a74.el_tablero_no_despliega_ni_autoriza (funcional), tablero_c67ccc28106a13a74.sin_destinos_o_con_error_el_tablero_sigue (funcional). Los nuevos nacen SIN MEDIR; verificá cobertura antes del juicio.

### Nota (2026-11-07 01:51:03 UTC)

Medidas de tablero_c67ccc28106a13a74.el_tablero_muestra_cada_destino_con_su_estado: factory_tablero_destinos.el_tablero_muestra_cada_destino_con_su_estado, factory_tablero_destinos.corrida_completa; propuestas por claude-code (agente, propuso, modo confirmacion). SIN MEDIR: sin límite adicional declarado. Revisión y juicio anteriores invalidados; no se declara cumplimiento ni aprobación de pertinencia.

### Nota (2026-11-07 01:51:04 UTC)

Medidas de tablero_c67ccc28106a13a74.el_tablero_no_consulta_los_destinos_sin_que_se_pida: factory_tablero_destinos.el_tablero_no_consulta_los_destinos_sin_que_se_pida, factory_tablero_destinos.corrida_completa; propuestas por claude-code (agente, propuso, modo confirmacion). SIN MEDIR: sin límite adicional declarado. Revisión y juicio anteriores invalidados; no se declara cumplimiento ni aprobación de pertinencia.

### Nota (2026-11-07 01:51:06 UTC)

Medidas de tablero_c67ccc28106a13a74.el_tablero_no_despliega_ni_autoriza: factory_tablero_destinos.el_tablero_no_despliega_ni_autoriza, factory_tablero_destinos.corrida_completa; propuestas por claude-code (agente, propuso, modo confirmacion). SIN MEDIR: sin límite adicional declarado. Revisión y juicio anteriores invalidados; no se declara cumplimiento ni aprobación de pertinencia.

### Nota (2026-11-07 01:51:08 UTC)

Medidas de tablero_c67ccc28106a13a74.sin_destinos_o_con_error_el_tablero_sigue: factory_tablero_destinos.sin_destinos_o_con_error_el_tablero_sigue, factory_tablero_destinos.corrida_completa; propuestas por claude-code (agente, propuso, modo confirmacion). SIN MEDIR: sin límite adicional declarado. Revisión y juicio anteriores invalidados; no se declara cumplimiento ni aprobación de pertinencia.

### Nota (2026-11-07 01:51:09 UTC)

Medidas de tablero_c67ccc28106a13a74.el_contrato_de_la_extension_cubre_destinos: factory_tablero_destinos.el_contrato_de_la_extension_cubre_destinos, factory_tablero_destinos.corrida_completa; propuestas por claude-code (agente, propuso, modo confirmacion). SIN MEDIR: sin límite adicional declarado. Revisión y juicio anteriores invalidados; no se declara cumplimiento ni aprobación de pertinencia.

### Nota (2026-11-07 02:25:13 UTC)

Medidas de tablero_c67ccc28106a13a74.el_contrato_de_la_extension_cubre_destinos: Brian Hollweg (persona, confirmo, modo confirmacion).

### Nota (2026-11-07 02:25:13 UTC)

Medidas de tablero_c67ccc28106a13a74.el_tablero_muestra_cada_destino_con_su_estado: Brian Hollweg (persona, confirmo, modo confirmacion).

### Nota (2026-11-07 02:25:14 UTC)

Medidas de tablero_c67ccc28106a13a74.el_tablero_no_consulta_los_destinos_sin_que_se_pida: Brian Hollweg (persona, confirmo, modo confirmacion).

### Nota (2026-11-07 02:25:14 UTC)

Medidas de tablero_c67ccc28106a13a74.el_tablero_no_despliega_ni_autoriza: Brian Hollweg (persona, confirmo, modo confirmacion).

### Nota (2026-11-07 02:25:14 UTC)

Medidas de tablero_c67ccc28106a13a74.sin_destinos_o_con_error_el_tablero_sigue: Brian Hollweg (persona, confirmo, modo confirmacion).

### Nota (2026-11-07 05:00:09 UTC)

Revisión guiada Brian Hollweg: aprobar; registrada por Brian Hollweg (persona, confirmo, modo confirmacion; motivo: Tres rondas de codex: la última sin hallazgos. Cerrados la pintura concurrente que descartaba la consulta, la caché compartida entre proyectos y las consultas simultáneas fuera de orden: la consulta se hace en su propio manejador, guarda {raiz, datos} y una generación invalida las anteriores. Evidencia: 1200 pruebas, 10 casos de contrato, éxito. Declarado: tres pruebas existentes editadas de forma aditiva (tests/contrato_en_node.cjs, tests/tablero_en_node.cjs, tests/test_contrato_vscode.py). Límites: el cambio de raíz con el panel abierto y la guarda de consultar-destinos para invitados no tienen prueba propia. agy no pudo revisar: su wrapper pide un modelo que ya no existe.); 0 abiertos derivados; commit 46c2bc519bb667cd4030b6700d0af983e962dfc5; informe tareas/20261107-013054-a8d-vista-destinos/revisiones/registro-i_xlp3yg/informe.json; decisiones tareas/20261107-013054-a8d-vista-destinos/revisiones/registro-i_xlp3yg/decisiones.json.
