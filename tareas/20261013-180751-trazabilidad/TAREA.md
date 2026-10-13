# Trazabilidad por candidato: requisito, casos y líneas cambiadas

- ESTADO: ABIERTA
- PRIORIDAD: 50
- ETIQUETAS: 

### Nota (2026-10-13 18:07:51 UTC)

OpenSpec: openspec/changes/20261013-180751-trazabilidad. Modo de trabajo: confirmacion. Estado de factory: espera aceptación de proposal.md y spec.md.

### Nota (2026-10-13 18:10:45 UTC)

Brian Hollweg (persona, decidio, modo confirmacion) aceptó propuesta y spec openspec/changes/20261013-180751-trazabilidad/specs/trazabilidad/spec.md; se reiniciaron las validaciones dependientes.

### Nota (2026-10-13 18:12:38 UTC)

Requisitos importados: trazabilidad_cca95191eb0039b11.el_sensor_registra_que_lineas_ejecuta_cada_caso (funcional), trazabilidad_cca95191eb0039b11.los_limites_de_la_trazabilidad_se_declaran (funcional), trazabilidad_cca95191eb0039b11.trazabilidad_cruza_los_casos_con_el_diff_del_candidato (funcional). Los nuevos nacen SIN MEDIR; verificá cobertura antes del juicio.

### Nota (2026-10-13 18:21:16 UTC)

Medidas de trazabilidad_cca95191eb0039b11.el_sensor_registra_que_lineas_ejecuta_cada_caso: factory_trazabilidad.el_sensor_registra_que_lineas_ejecuta_cada_caso, factory_trazabilidad.corrida_completa; propuestas por claude-code (agente, propuso, modo confirmacion). SIN MEDIR: sin límite adicional declarado. Revisión y juicio anteriores invalidados; no se declara cumplimiento ni aprobación de pertinencia.

### Nota (2026-10-13 18:21:16 UTC)

Medidas de trazabilidad_cca95191eb0039b11.trazabilidad_cruza_los_casos_con_el_diff_del_candidato: factory_trazabilidad.trazabilidad_cruza_los_casos_con_el_diff_del_candidato, factory_trazabilidad.corrida_completa; propuestas por claude-code (agente, propuso, modo confirmacion). SIN MEDIR: sin límite adicional declarado. Revisión y juicio anteriores invalidados; no se declara cumplimiento ni aprobación de pertinencia.

### Nota (2026-10-13 18:21:16 UTC)

Medidas de trazabilidad_cca95191eb0039b11.los_limites_de_la_trazabilidad_se_declaran: factory_trazabilidad.los_limites_de_la_trazabilidad_se_declaran, factory_trazabilidad.corrida_completa; propuestas por claude-code (agente, propuso, modo confirmacion). SIN MEDIR: sin límite adicional declarado. Revisión y juicio anteriores invalidados; no se declara cumplimiento ni aprobación de pertinencia.

### Nota (2026-10-13 18:22:36 UTC)

Medidas de trazabilidad_cca95191eb0039b11.el_sensor_registra_que_lineas_ejecuta_cada_caso: Brian Hollweg (persona, confirmo, modo confirmacion).

### Nota (2026-10-13 18:22:36 UTC)

Medidas de trazabilidad_cca95191eb0039b11.los_limites_de_la_trazabilidad_se_declaran: Brian Hollweg (persona, confirmo, modo confirmacion).

### Nota (2026-10-13 18:22:36 UTC)

Medidas de trazabilidad_cca95191eb0039b11.trazabilidad_cruza_los_casos_con_el_diff_del_candidato: Brian Hollweg (persona, confirmo, modo confirmacion).

### Nota (2026-10-13 21:59:59 UTC)

Revisión guiada Brian Hollweg: aprobar; registrada por Brian Hollweg (persona, confirmo, modo confirmacion; motivo: cinco vueltas de codex y agy (la 4 y la 5 incrementales, porque el paquete completo pasaba el límite de 1 MB de Clue por la evidencia ya commiteada): la 1 trajo 11 hallazgos (3 altos), la 2, 5, la 3, 2, y la 4, 1; todos corregidos con aserciones que fallan en el código anterior, en los mismos 5 casos. La 5 dejó sólo una variante más del guard __main__ (con and), que Brian aceptó como riesgo: las líneas mal clasificadas siguen visibles en «corren al importar». Suite 332 y evidencia en verde.); 0 abiertos derivados; commit 0c2ab0a78bfeab76d43f3882758c2c76e2d7caa0; informe tareas/20261013-180751-trazabilidad/revisiones/registro-ym1a4uj5/informe.json; decisiones tareas/20261013-180751-trazabilidad/revisiones/registro-ym1a4uj5/decisiones.json.

### Nota (2026-10-13 22:00:09 UTC)

Juicio Factory: verde; salida Oracle 0; informe .factory/cambios/20261013-180751-trazabilidad/oracle-veredicto.txt.
