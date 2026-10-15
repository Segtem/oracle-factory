# El proyecto Oracle puede estar en una carpeta del proyecto

- ESTADO: ABIERTA
- PRIORIDAD: 50
- ETIQUETAS: 

### Nota (2026-10-15 15:53:46 UTC)

OpenSpec: openspec/changes/20261015-155346-oracle-en-carpeta. Modo de trabajo: confirmacion. Estado de factory: espera aceptación de proposal.md y spec.md.

### Nota (2026-10-15 16:15:06 UTC)

Brian Hollweg (persona, decidio, modo confirmacion) aceptó propuesta y spec openspec/changes/20261015-155346-oracle-en-carpeta/specs/estructura/spec.md; se reiniciaron las validaciones dependientes.

### Nota (2026-10-15 16:15:17 UTC)

Requisitos importados: estructura_c01f2e6fb0af5aed6.el_proyecto_oracle_puede_estar_en_una_carpeta (funcional), estructura_c01f2e6fb0af5aed6.init_adopta_un_proyecto_oracle_existente (funcional), estructura_c01f2e6fb0af5aed6.los_escalares_del_proyecto_se_ejecutan_solo_si_el_proyecto_lo_declara (funcional). Los nuevos nacen SIN MEDIR; verificá cobertura antes del juicio.

### Nota (2026-10-15 16:27:37 UTC)

Medidas de estructura_c01f2e6fb0af5aed6.el_proyecto_oracle_puede_estar_en_una_carpeta: factory_carpeta.el_proyecto_oracle_puede_estar_en_una_carpeta, factory_carpeta.corrida_completa; propuestas por claude-code (agente, propuso, modo confirmacion). SIN MEDIR: sin límite adicional declarado. Revisión y juicio anteriores invalidados; no se declara cumplimiento ni aprobación de pertinencia.

### Nota (2026-10-15 16:27:37 UTC)

Medidas de estructura_c01f2e6fb0af5aed6.init_adopta_un_proyecto_oracle_existente: factory_carpeta.init_adopta_un_proyecto_oracle_existente, factory_carpeta.corrida_completa; propuestas por claude-code (agente, propuso, modo confirmacion). SIN MEDIR: sin límite adicional declarado. Revisión y juicio anteriores invalidados; no se declara cumplimiento ni aprobación de pertinencia.

### Nota (2026-10-15 16:27:37 UTC)

Medidas de estructura_c01f2e6fb0af5aed6.los_escalares_del_proyecto_se_ejecutan_solo_si_el_proyecto_lo_declara: factory_carpeta.los_escalares_del_proyecto_se_ejecutan_solo_si_el_proyecto_lo_declara, factory_carpeta.corrida_completa; propuestas por claude-code (agente, propuso, modo confirmacion). SIN MEDIR: sin límite adicional declarado. Revisión y juicio anteriores invalidados; no se declara cumplimiento ni aprobación de pertinencia.

### Nota (2026-10-15 16:30:22 UTC)

Medidas de estructura_c01f2e6fb0af5aed6.el_proyecto_oracle_puede_estar_en_una_carpeta: Brian Hollweg (persona, confirmo, modo confirmacion).

### Nota (2026-10-15 16:30:22 UTC)

Medidas de estructura_c01f2e6fb0af5aed6.init_adopta_un_proyecto_oracle_existente: Brian Hollweg (persona, confirmo, modo confirmacion).

### Nota (2026-10-15 16:30:22 UTC)

Medidas de estructura_c01f2e6fb0af5aed6.los_escalares_del_proyecto_se_ejecutan_solo_si_el_proyecto_lo_declara: Brian Hollweg (persona, confirmo, modo confirmacion).

### Nota (2026-10-15 19:21:17 UTC)

Revisión guiada Brian Hollweg: aprobar; registrada por Brian Hollweg (persona, confirmo, modo confirmacion; motivo: tres vueltas de codex y agy, a la vez. La 1: dos altos (buscar ocultaba una carpeta inválida; init sin --oracle recreaba Oracle en la raíz) y tres medios; la 2: un alto (juzgar no entregaba el error de Oracle con escalares sin declarar) y tres medios (una prueba que pasaba por vacuidad, rutas de Windows). Todo corregido con pruebas que fallan sin el arreglo. La 3 no encontró nada. Suite 367 y evidencia en verde, con Oracle 0.38.2.); 0 abiertos derivados; commit 92bebd7ff7962ef9470fe7f3858d262ea31c29ad; informe tareas/20261015-155346-oracle-en-carpeta/revisiones/registro-y1zbjnms/informe.json; decisiones tareas/20261015-155346-oracle-en-carpeta/revisiones/registro-y1zbjnms/decisiones.json.

### Nota (2026-10-15 19:21:46 UTC)

Juicio Factory: verde; salida Oracle 0; informe .factory/cambios/20261015-155346-oracle-en-carpeta/oracle-veredicto.txt.
