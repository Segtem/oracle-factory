# Una lista previa a la revisión con las clases de problema que más rondas cuestan

- ESTADO: CERRADA
- PRIORIDAD: 50
- ETIQUETAS: 

### Nota (2026-10-31 22:07:42 UTC)

OpenSpec: openspec/changes/20261031-220741-vts-listaprevia. Modo de trabajo: confirmacion. Estado de factory: espera aceptación de proposal.md y spec.md.

### Nota (2026-10-31 22:09:31 UTC)

Brian Hollweg (persona, decidio, modo confirmacion) aceptó propuesta y spec openspec/changes/20261031-220741-vts-listaprevia/specs/practicas/spec.md; se reiniciaron las validaciones dependientes.

### Nota (2026-10-31 22:25:03 UTC)

Brian Hollweg (persona, decidio, modo confirmacion) aceptó propuesta y spec openspec/changes/20261031-220741-vts-listaprevia/specs/practicas/spec.md; se reiniciaron las validaciones dependientes.

### Nota (2026-10-31 22:25:13 UTC)

Requisitos importados: practicas_c728beae6c9b6fedb.la_guia_para_agentes_nombra_la_lista_previa (funcional), practicas_c728beae6c9b6fedb.la_lista_previa_tiene_una_sola_fuente (funcional), practicas_c728beae6c9b6fedb.pedir_revision_muestra_la_lista_previa_sin_bloquear (funcional). Los nuevos nacen SIN MEDIR; verificá cobertura antes del juicio.

### Nota (2026-10-31 22:28:25 UTC)

Medidas de practicas_c728beae6c9b6fedb.pedir_revision_muestra_la_lista_previa_sin_bloquear: factory_lista_previa.pedir_revision_muestra_la_lista_previa_sin_bloquear, factory_lista_previa.corrida_completa; propuestas por claude-code (agente, propuso, modo confirmacion). SIN MEDIR: sin límite adicional declarado. Revisión y juicio anteriores invalidados; no se declara cumplimiento ni aprobación de pertinencia.

### Nota (2026-10-31 22:28:26 UTC)

Medidas de practicas_c728beae6c9b6fedb.la_lista_previa_tiene_una_sola_fuente: factory_lista_previa.la_lista_previa_tiene_una_sola_fuente, factory_lista_previa.corrida_completa; propuestas por claude-code (agente, propuso, modo confirmacion). SIN MEDIR: sin límite adicional declarado. Revisión y juicio anteriores invalidados; no se declara cumplimiento ni aprobación de pertinencia.

### Nota (2026-10-31 22:28:27 UTC)

Medidas de practicas_c728beae6c9b6fedb.la_guia_para_agentes_nombra_la_lista_previa: factory_lista_previa.la_guia_para_agentes_nombra_la_lista_previa, factory_lista_previa.corrida_completa; propuestas por claude-code (agente, propuso, modo confirmacion). SIN MEDIR: sin límite adicional declarado. Revisión y juicio anteriores invalidados; no se declara cumplimiento ni aprobación de pertinencia.

### Nota (2026-10-31 22:36:27 UTC)

Medidas de practicas_c728beae6c9b6fedb.la_guia_para_agentes_nombra_la_lista_previa: Brian Hollweg (persona, confirmo, modo confirmacion).

### Nota (2026-10-31 22:36:27 UTC)

Medidas de practicas_c728beae6c9b6fedb.la_lista_previa_tiene_una_sola_fuente: Brian Hollweg (persona, confirmo, modo confirmacion).

### Nota (2026-10-31 22:36:27 UTC)

Medidas de practicas_c728beae6c9b6fedb.pedir_revision_muestra_la_lista_previa_sin_bloquear: Brian Hollweg (persona, confirmo, modo confirmacion).

### Nota (2026-10-31 23:48:34 UTC)

Brian Hollweg (persona, decidio, modo confirmacion) aceptó propuesta y spec openspec/changes/20261031-220741-vts-listaprevia/specs/practicas/spec.md; se reiniciaron las validaciones dependientes.

### Nota (2026-10-31 23:59:32 UTC)

Requisitos importados: practicas_c728beae6c9b6fedb.la_guia_para_agentes_nombra_la_lista_previa (funcional), practicas_c728beae6c9b6fedb.la_lista_previa_tiene_una_sola_fuente (funcional), practicas_c728beae6c9b6fedb.pedir_revision_muestra_la_lista_previa_sin_bloquear (funcional). Los nuevos nacen SIN MEDIR; verificá cobertura antes del juicio.

### Nota (2026-11-01 00:00:24 UTC)

Medidas de practicas_c728beae6c9b6fedb.pedir_revision_muestra_la_lista_previa_sin_bloquear propuestas por claude-code (agente, modo confirmacion); no cuentan hasta que una persona las confirme.

### Nota (2026-11-01 00:00:25 UTC)

Medidas de practicas_c728beae6c9b6fedb.la_lista_previa_tiene_una_sola_fuente propuestas por claude-code (agente, modo confirmacion); no cuentan hasta que una persona las confirme.

### Nota (2026-11-01 00:00:26 UTC)

Medidas de practicas_c728beae6c9b6fedb.la_guia_para_agentes_nombra_la_lista_previa propuestas por claude-code (agente, modo confirmacion); no cuentan hasta que una persona las confirme.

### Nota (2026-11-01 00:45:18 UTC)

Medidas de practicas_c728beae6c9b6fedb.la_guia_para_agentes_nombra_la_lista_previa: Brian Hollweg (persona, confirmo, modo confirmacion).

### Nota (2026-11-01 00:45:18 UTC)

Medidas de practicas_c728beae6c9b6fedb.la_lista_previa_tiene_una_sola_fuente: Brian Hollweg (persona, confirmo, modo confirmacion).

### Nota (2026-11-01 00:45:18 UTC)

Medidas de practicas_c728beae6c9b6fedb.pedir_revision_muestra_la_lista_previa_sin_bloquear: Brian Hollweg (persona, confirmo, modo confirmacion).

### Nota (2026-11-01 01:14:20 UTC)

Revisión guiada Brian Hollweg: aprobar; registrada por Brian Hollweg (persona, confirmo, modo confirmacion; motivo: Dos vueltas de revisión. La primera (agy2 y codex) dejó hallazgos reales, entre ellos que las cifras de la medición que justificaba el cambio estaban mal (las rondas se ordenaban por la fecha de los archivos y no por los eventos): se corrigió la medición, se volvió a aprobar la propuesta, la medición quedó reproducible con tools/medir_rondas.py y protegida por pruebas, la comprobación del documento exige que la lista numerada sea exactamente la del código y pedir-revision vacía el buffer. La segunda vuelta dio 0 hallazgos en ambos revisores. Suite completa sin fallas y evidencia con éxito. Todas las mutaciones aplicadas al código nuevo se detectan, salvo dos equivalentes declaradas (vaciar el buffer en las dos primeras líneas impresas, porque la última ya vacía todo lo anterior).); 0 abiertos derivados; commit ee0a578353b39104d11568da20dcf3a25fac1ce2; informe tareas/20261031-220741-vts-listaprevia/revisiones/registro-6h4630vy/informe.json; decisiones tareas/20261031-220741-vts-listaprevia/revisiones/registro-6h4630vy/decisiones.json.

### Nota (2026-11-01 01:14:28 UTC)

Juicio Factory: verde; salida Oracle 0; informe .factory/cambios/20261031-220741-vts-listaprevia/oracle-veredicto.txt.

### Nota (2026-11-01 01:16:32 UTC)

Cierre: Brian Hollweg (persona, decidio, modo confirmacion), tras revisar el informe de código y el veredicto Oracle.
