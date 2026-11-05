# Web: capturas reales de VS Code y ejemplos en las guías

- ESTADO: ABIERTA
- PRIORIDAD: 50
- ETIQUETAS: 

### Nota (2026-11-04 11:54:30 UTC)

OpenSpec: openspec/changes/20261104-115430-dnr-vscode. Modo de trabajo: confirmacion. Estado de factory: espera aceptación de proposal.md y spec.md.

### Nota (2026-11-04 13:17:20 UTC)

Brian Hollweg (persona, decidio, modo confirmacion) aceptó propuesta y spec openspec/changes/20261104-115430-dnr-vscode/specs/web/spec.md; se reiniciaron las validaciones dependientes.

### Nota (2026-11-04 13:17:30 UTC)

Requisitos importados: web_c2e4546f9d843453e.las_guias_muestran_vscode_real (funcional), web_c2e4546f9d843453e.los_ejemplos_no_filtran_datos_personales (no funcional), web_c2e4546f9d843453e.los_ejemplos_son_salida_real (funcional). Los nuevos nacen SIN MEDIR; verificá cobertura antes del juicio.

### Nota (2026-11-04 13:41:43 UTC)

Medidas de web_c2e4546f9d843453e.las_guias_muestran_vscode_real: factory_web_vscode.las_guias_muestran_vscode_real, factory_web_vscode.corrida_completa; propuestas por claude-code (agente, propuso, modo confirmacion). SIN MEDIR: sin límite adicional declarado. Revisión y juicio anteriores invalidados; no se declara cumplimiento ni aprobación de pertinencia.

### Nota (2026-11-04 13:41:44 UTC)

Medidas de web_c2e4546f9d843453e.los_ejemplos_son_salida_real: factory_web_vscode.los_ejemplos_son_salida_real, factory_web_vscode.corrida_completa; propuestas por claude-code (agente, propuso, modo confirmacion). SIN MEDIR: sin límite adicional declarado. Revisión y juicio anteriores invalidados; no se declara cumplimiento ni aprobación de pertinencia.

### Nota (2026-11-04 13:41:46 UTC)

Medidas de web_c2e4546f9d843453e.los_ejemplos_no_filtran_datos_personales: factory_web_vscode.los_ejemplos_no_filtran_datos_personales, factory_web_vscode.corrida_completa; propuestas por claude-code (agente, propuso, modo confirmacion). SIN MEDIR: sin límite adicional declarado. Revisión y juicio anteriores invalidados; no se declara cumplimiento ni aprobación de pertinencia.

### Nota (2026-11-04 14:29:50 UTC)

Medidas de web_c2e4546f9d843453e.las_guias_muestran_vscode_real: Brian Hollweg (persona, confirmo, modo confirmacion).

### Nota (2026-11-04 14:29:50 UTC)

Medidas de web_c2e4546f9d843453e.los_ejemplos_no_filtran_datos_personales: Brian Hollweg (persona, confirmo, modo confirmacion).

### Nota (2026-11-04 14:29:50 UTC)

Medidas de web_c2e4546f9d843453e.los_ejemplos_son_salida_real: Brian Hollweg (persona, confirmo, modo confirmacion).

### Nota (2026-11-04 15:37:18 UTC)

Medidas de web_c2e4546f9d843453e.las_guias_muestran_vscode_real propuestas por claude-code (agente, modo confirmacion); no cuentan hasta que una persona las confirme.

### Nota (2026-11-04 15:37:20 UTC)

Medidas de web_c2e4546f9d843453e.los_ejemplos_son_salida_real propuestas por claude-code (agente, modo confirmacion); no cuentan hasta que una persona las confirme.

### Nota (2026-11-04 15:37:21 UTC)

Medidas de web_c2e4546f9d843453e.los_ejemplos_no_filtran_datos_personales propuestas por claude-code (agente, modo confirmacion); no cuentan hasta que una persona las confirme.

### Nota (2026-11-04 19:06:34 UTC)

Medidas de web_c2e4546f9d843453e.las_guias_muestran_vscode_real: Brian Hollweg (persona, confirmo, modo confirmacion).

### Nota (2026-11-04 19:06:34 UTC)

Medidas de web_c2e4546f9d843453e.los_ejemplos_no_filtran_datos_personales: Brian Hollweg (persona, confirmo, modo confirmacion).

### Nota (2026-11-04 19:06:34 UTC)

Medidas de web_c2e4546f9d843453e.los_ejemplos_son_salida_real: Brian Hollweg (persona, confirmo, modo confirmacion).

### Nota (2026-11-05 20:41:12 UTC)

Revisión guiada Brian Hollweg: aprobar; registrada por Brian Hollweg (persona, confirmo, modo confirmacion; motivo: Cuatro rondas. Las rondas 1 a 3 (codex y agy2-flash) cerraron con 0 hallazgos en la tercera; la ronda 4 repite la revisión sobre el candidato con main integrado para que el informe declare los cuatro PNG con «abierto: RUTA» (arreglo revision-binarios, ya en main): codex, 0 hallazgos, completa en lo demás. agy2-flash no pudo revisar la ronda 4: cuota agotada (429, se renueva en ~150 h); agy y agy2 siguen fallando por el --effort del wrapper. Evidencia: 1146 pruebas, 11 casos de contrato, éxito. Límite: el validador de imágenes no decodifica los píxeles; Factory no comprueba que el revisor abrió los PNG, queda listado en los límites. Tests existentes editados y declarados: tests/test_site.cjs, tests/test_web.py.); 0 abiertos derivados; commit 0a4bd9cacbec1e6aa80f503268c59e37f8274b4e; informe tareas/20261104-115430-dnr-vscode/revisiones/registro-nk28rkxh/informe.json; decisiones tareas/20261104-115430-dnr-vscode/revisiones/registro-nk28rkxh/decisiones.json.
