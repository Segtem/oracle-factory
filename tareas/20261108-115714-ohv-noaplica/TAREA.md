# El verificador respeta «Pruebas: no aplica»

- ESTADO: ABIERTA
- PRIORIDAD: 50
- ETIQUETAS: 

### Nota (2026-11-08 11:57:14 UTC)

OpenSpec: openspec/changes/20261108-115714-ohv-noaplica. Modo de trabajo: confirmacion. Estado de factory: espera aceptación de proposal.md y spec.md.

### Nota (2026-11-08 12:00:12 UTC)

Brian Hollweg (persona, decidio, modo confirmacion) aceptó propuesta y spec openspec/changes/20261108-115714-ohv-noaplica/specs/practicas/spec.md; se reiniciaron las validaciones dependientes.

### Nota (2026-11-08 12:00:22 UTC)

Requisitos importados: practicas_c7e9c76d84c2a7a09.el_verificador_no_pide_casos_para_un_requisito_exceptuado (funcional), practicas_c7e9c76d84c2a7a09.la_evidencia_y_los_catalogos_cuentan_solo_los_requisitos_con_casos (funcional), practicas_c7e9c76d84c2a7a09.una_excepcion_mal_escrita_no_se_ignora (funcional). Los nuevos nacen SIN MEDIR; verificá cobertura antes del juicio.

### Nota (2026-11-08 12:01:27 UTC)

Medidas de practicas_c7e9c76d84c2a7a09.el_verificador_no_pide_casos_para_un_requisito_exceptuado: factory_noaplica.el_verificador_no_pide_casos_para_un_requisito_exceptuado, factory_noaplica.corrida_completa; propuestas por claude-code (agente, propuso, modo confirmacion). SIN MEDIR: sin límite adicional declarado. Revisión y juicio anteriores invalidados; no se declara cumplimiento ni aprobación de pertinencia.

### Nota (2026-11-08 12:01:28 UTC)

Medidas de practicas_c7e9c76d84c2a7a09.la_evidencia_y_los_catalogos_cuentan_solo_los_requisitos_con_casos: factory_noaplica.la_evidencia_y_los_catalogos_cuentan_solo_los_requisitos_con_casos, factory_noaplica.corrida_completa; propuestas por claude-code (agente, propuso, modo confirmacion). SIN MEDIR: sin límite adicional declarado. Revisión y juicio anteriores invalidados; no se declara cumplimiento ni aprobación de pertinencia.

### Nota (2026-11-08 12:01:30 UTC)

Medidas de practicas_c7e9c76d84c2a7a09.una_excepcion_mal_escrita_no_se_ignora: factory_noaplica.una_excepcion_mal_escrita_no_se_ignora, factory_noaplica.corrida_completa; propuestas por claude-code (agente, propuso, modo confirmacion). SIN MEDIR: sin límite adicional declarado. Revisión y juicio anteriores invalidados; no se declara cumplimiento ni aprobación de pertinencia.

### Nota (2026-11-08 12:01:45 UTC)

Medidas de practicas_c7e9c76d84c2a7a09.el_verificador_no_pide_casos_para_un_requisito_exceptuado: Brian Hollweg (persona, confirmo, modo confirmacion).

### Nota (2026-11-08 12:01:45 UTC)

Medidas de practicas_c7e9c76d84c2a7a09.la_evidencia_y_los_catalogos_cuentan_solo_los_requisitos_con_casos: Brian Hollweg (persona, confirmo, modo confirmacion).

### Nota (2026-11-08 12:01:45 UTC)

Medidas de practicas_c7e9c76d84c2a7a09.una_excepcion_mal_escrita_no_se_ignora: Brian Hollweg (persona, confirmo, modo confirmacion).

### Nota (2026-11-08 12:11:15 UTC)

Medidas de practicas_c7e9c76d84c2a7a09.el_verificador_no_pide_casos_para_un_requisito_exceptuado propuestas por claude-code (agente, modo confirmacion); no cuentan hasta que una persona las confirme.

### Nota (2026-11-08 12:11:16 UTC)

Medidas de practicas_c7e9c76d84c2a7a09.la_evidencia_y_los_catalogos_cuentan_solo_los_requisitos_con_casos propuestas por claude-code (agente, modo confirmacion); no cuentan hasta que una persona las confirme.

### Nota (2026-11-08 12:11:18 UTC)

Medidas de practicas_c7e9c76d84c2a7a09.una_excepcion_mal_escrita_no_se_ignora propuestas por claude-code (agente, modo confirmacion); no cuentan hasta que una persona las confirme.

### Nota (2026-11-08 12:12:08 UTC)

Medidas de practicas_c7e9c76d84c2a7a09.el_verificador_no_pide_casos_para_un_requisito_exceptuado: Brian Hollweg (persona, confirmo, modo confirmacion).

### Nota (2026-11-08 12:12:08 UTC)

Medidas de practicas_c7e9c76d84c2a7a09.la_evidencia_y_los_catalogos_cuentan_solo_los_requisitos_con_casos: Brian Hollweg (persona, confirmo, modo confirmacion).

### Nota (2026-11-08 12:12:08 UTC)

Medidas de practicas_c7e9c76d84c2a7a09.una_excepcion_mal_escrita_no_se_ignora: Brian Hollweg (persona, confirmo, modo confirmacion).

### Nota (2026-11-08 12:24:49 UTC)

Revisión guiada Brian Hollweg: aprobar; registrada por Brian Hollweg (persona, confirmo, modo confirmacion; motivo: Codex: un hallazgo bajo (F1), no del cambio: el lector compartido oracle_factory/pruebas.py sólo alterna cercas con tres comillas invertidas y no con ~~~, mientras requisitos_de_la_spec sí entiende ambas. Preexistente: lo comparten aprobar-spec e importar, y la spec dejó fuera cambiar ese lector. Propongo dejarlo como seguimiento. Evidencia 1255 pruebas OK, 10 casos. 6 mutaciones propias, 5 detectadas; la que sobrevive es equivalente (un caso para un exceptuado ya falla antes). Declaro una prueba existente editada: test_vg1_un_requisito_que_declara_pruebas_no_aplica_… en test_verificador_generico.py, sólo su regex sobre docs/tests.md, que fijaba el límite que este cambio levanta. No toca cli.py ni reglas de decisión.); 0 abiertos derivados; commit 1eb5e2dcf54325ec2ea62b21a2ae07f1acdc4951; informe tareas/20261108-115714-ohv-noaplica/revisiones/registro-x20j3b0v/informe.json; decisiones tareas/20261108-115714-ohv-noaplica/revisiones/registro-x20j3b0v/decisiones.json.
