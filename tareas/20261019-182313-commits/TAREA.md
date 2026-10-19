# Los commits unidos a su cambio: trailer Cambio, oracle-factory log, estado y tablero

- ESTADO: ABIERTA
- PRIORIDAD: 50
- ETIQUETAS: 

### Nota (2026-10-19 18:23:13 UTC)

OpenSpec: openspec/changes/20261019-182313-commits. Modo de trabajo: confirmacion. Estado de factory: espera aceptación de proposal.md y spec.md.

### Nota (2026-10-19 18:27:07 UTC)

Brian Hollweg (persona, decidio, modo confirmacion) aceptó propuesta y spec openspec/changes/20261019-182313-commits/specs/trazabilidad/spec.md; se reiniciaron las validaciones dependientes.

### Nota (2026-10-19 18:28:40 UTC)

Requisitos importados: trazabilidad_c03c40840efaaab69.cada_commit_nuevo_dice_de_que_cambio_es (funcional), trazabilidad_c03c40840efaaab69.los_commits_de_un_cambio_se_ven_en_log_estado_y_el_tablero (funcional). Los nuevos nacen SIN MEDIR; verificá cobertura antes del juicio.

### Nota (2026-10-19 18:38:05 UTC)

Medidas de trazabilidad_c03c40840efaaab69.cada_commit_nuevo_dice_de_que_cambio_es: factory_commits.cada_commit_nuevo_dice_de_que_cambio_es, factory_commits.corrida_completa; propuestas por claude-code (agente, propuso, modo confirmacion). SIN MEDIR: sin medida todavía; escenarios: «un commit con un cambio abierto», «sin un único cambio abierto, o con un hook ajeno». Revisión y juicio anteriores invalidados; no se declara cumplimiento ni aprobación de pertinencia.

### Nota (2026-10-19 18:38:05 UTC)

Medidas de trazabilidad_c03c40840efaaab69.los_commits_de_un_cambio_se_ven_en_log_estado_y_el_tablero: factory_commits.los_commits_de_un_cambio_se_ven_en_log_estado_y_el_tablero, factory_commits.corrida_completa; propuestas por claude-code (agente, propuso, modo confirmacion). SIN MEDIR: sin límite adicional declarado. Revisión y juicio anteriores invalidados; no se declara cumplimiento ni aprobación de pertinencia.

### Nota (2026-10-19 18:50:07 UTC)

Medidas de trazabilidad_c03c40840efaaab69.cada_commit_nuevo_dice_de_que_cambio_es: Brian Hollweg (persona, confirmo, modo confirmacion).

### Nota (2026-10-19 18:50:07 UTC)

Medidas de trazabilidad_c03c40840efaaab69.los_commits_de_un_cambio_se_ven_en_log_estado_y_el_tablero: Brian Hollweg (persona, confirmo, modo confirmacion).

### Nota (2026-10-19 21:21:09 UTC)

Revisión guiada Brian Hollweg: aprobar; registrada por Brian Hollweg (persona, confirmo, modo confirmacion; motivo: Cinco vueltas de codex y agy; en la última ninguno dejó hallazgos. Corregido con pruebas que fallan sin cada corrección: commit-msg para el mensaje del editor (cerrarlo vacío sigue abortando, también con core.commentChar), con un hook ajeno no se instala ninguno, la línea encadenable no corta con set -e, el trailer se confirma en el bloque de trailers, revisado exige informe, y la deducción busca el merge en la línea principal. Límite conocido: con commit.template una plantilla sin editar ya no aborta el commit.); 0 abiertos derivados; commit e130609d3cf50306de3f06cd4012b90a4a5b91d7; informe tareas/20261019-182313-commits/revisiones/registro-61xq7bih/informe.json; decisiones tareas/20261019-182313-commits/revisiones/registro-61xq7bih/decisiones.json.

### Nota (2026-10-19 21:21:45 UTC)

Medidas de trazabilidad_c03c40840efaaab69.cada_commit_nuevo_dice_de_que_cambio_es: factory_commits.cada_commit_nuevo_dice_de_que_cambio_es, factory_commits.corrida_completa; propuestas por claude-code (agente, propuso, modo confirmacion). SIN MEDIR: sin límite adicional declarado. Revisión y juicio anteriores invalidados; no se declara cumplimiento ni aprobación de pertinencia.

### Nota (2026-10-19 21:22:32 UTC)

Medidas de trazabilidad_c03c40840efaaab69.cada_commit_nuevo_dice_de_que_cambio_es: Brian Hollweg (persona, confirmo, modo confirmacion).

### Nota (2026-10-19 23:03:08 UTC)

Revisión guiada Brian Hollweg: aprobar; registrada por Brian Hollweg (persona, confirmo, modo confirmacion; motivo: Seis vueltas de codex y agy; en las dos últimas ninguno dejó hallazgos (la 6 sólo quitó la marca sin_medir del primer requisito). Corregido con pruebas que fallan sin cada corrección: commit-msg para el mensaje del editor (cerrarlo vacío sigue abortando, también con core.commentChar), con un hook ajeno no se instala ninguno, la línea encadenable no corta con set -e, el trailer se confirma en el bloque de trailers, revisado exige informe, y la deducción busca el merge en la línea principal. Límite conocido: con commit.template una plantilla sin editar ya no aborta el commit.); 0 abiertos derivados; commit 08368ab18f8d743680e42a846a1363f052774640; informe tareas/20261019-182313-commits/revisiones/registro-jpiyr2ld/informe.json; decisiones tareas/20261019-182313-commits/revisiones/registro-jpiyr2ld/decisiones.json.
