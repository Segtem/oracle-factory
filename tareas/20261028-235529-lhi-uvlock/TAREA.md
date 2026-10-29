# Rastrear el uv.lock de Factory y no dar por no confiable un paquete que el entorno no instala

- ESTADO: ABIERTA
- PRIORIDAD: 50
- ETIQUETAS: 

### Nota (2026-10-28 23:55:29 UTC)

OpenSpec: openspec/changes/20261028-235529-lhi-uvlock. Modo de trabajo: confirmacion. Estado de factory: espera aceptación de proposal.md y spec.md.

### Nota (2026-10-28 23:56:29 UTC)

Brian Hollweg (persona, decidio, modo confirmacion) aceptó propuesta y spec openspec/changes/20261028-235529-lhi-uvlock/specs/procedencia/spec.md; se reiniciaron las validaciones dependientes.

### Nota (2026-10-28 23:56:40 UTC)

Requisitos importados: procedencia_cadae59b33b0c0b2c.el_lock_de_factory_coincide_con_su_pyproject (funcional), procedencia_cadae59b33b0c0b2c.el_lock_de_factory_viaja_con_el_repositorio (funcional), procedencia_cadae59b33b0c0b2c.un_paquete_que_el_entorno_no_instala_no_vuelve_no_confiable_el_inventario (funcional). Los nuevos nacen SIN MEDIR; verificá cobertura antes del juicio.

### Nota (2026-10-29 00:07:45 UTC)

Medidas de procedencia_cadae59b33b0c0b2c.el_lock_de_factory_viaja_con_el_repositorio: factory_uv_lock.el_lock_de_factory_viaja_con_el_repositorio, factory_uv_lock.corrida_completa; propuestas por claude-code (agente, propuso, modo confirmacion). SIN MEDIR: sin límite adicional declarado. Revisión y juicio anteriores invalidados; no se declara cumplimiento ni aprobación de pertinencia.

### Nota (2026-10-29 00:07:46 UTC)

Medidas de procedencia_cadae59b33b0c0b2c.el_lock_de_factory_coincide_con_su_pyproject: factory_uv_lock.el_lock_de_factory_coincide_con_su_pyproject, factory_uv_lock.corrida_completa; propuestas por claude-code (agente, propuso, modo confirmacion). SIN MEDIR: sin límite adicional declarado. Revisión y juicio anteriores invalidados; no se declara cumplimiento ni aprobación de pertinencia.

### Nota (2026-10-29 00:07:47 UTC)

Medidas de procedencia_cadae59b33b0c0b2c.un_paquete_que_el_entorno_no_instala_no_vuelve_no_confiable_el_inventario: factory_uv_lock.un_paquete_que_el_entorno_no_instala_no_vuelve_no_confiable_el_inventario, factory_uv_lock.corrida_completa; propuestas por claude-code (agente, propuso, modo confirmacion). SIN MEDIR: sin límite adicional declarado. Revisión y juicio anteriores invalidados; no se declara cumplimiento ni aprobación de pertinencia.

### Nota (2026-10-29 00:20:52 UTC)

Medidas de procedencia_cadae59b33b0c0b2c.el_lock_de_factory_coincide_con_su_pyproject: Brian Hollweg (persona, confirmo, modo confirmacion).

### Nota (2026-10-29 00:20:52 UTC)

Medidas de procedencia_cadae59b33b0c0b2c.el_lock_de_factory_viaja_con_el_repositorio: Brian Hollweg (persona, confirmo, modo confirmacion).

### Nota (2026-10-29 00:20:52 UTC)

Medidas de procedencia_cadae59b33b0c0b2c.un_paquete_que_el_entorno_no_instala_no_vuelve_no_confiable_el_inventario: Brian Hollweg (persona, confirmo, modo confirmacion).

### Nota (2026-10-29 15:29:19 UTC)

Revisión guiada Brian Hollweg: aprobar; registrada por Brian Hollweg (persona, confirmo, modo confirmacion; motivo: Dos rondas con agy y agy2: la primera dejó un hallazgo informativo real (verify_procedencia.py seguía el nombre viejo del caso pr2), corregido y verificado; la segunda, 0 hallazgos en ambos. Suite de 723 pruebas sin fallas ni omisiones y evidencia con éxito.); 0 abiertos derivados; commit 27ed4fc9a80b6096e40a893a7c7196e55a669724; informe tareas/20261028-235529-lhi-uvlock/revisiones/registro-kn8xyghe/informe.json; decisiones tareas/20261028-235529-lhi-uvlock/revisiones/registro-kn8xyghe/decisiones.json.
