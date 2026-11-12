# Registros fuera del repo del producto: preparar la migración real de Factory

- ESTADO: ABIERTA
- PRIORIDAD: 50
- ETIQUETAS: 

### Nota (2026-11-12 12:18:37 UTC)

OpenSpec: openspec/changes/20261112-121837-6bu-pmr. Modo de trabajo: confirmacion. Estado de factory: espera aceptación de proposal.md y spec.md.

### Nota (2026-11-12 12:26:16 UTC)

Brian Hollweg (persona, decidio, modo confirmacion) aceptó propuesta y spec openspec/changes/20261112-121837-6bu-pmr/specs/flujo/spec.md; se reiniciaron las validaciones dependientes.

### Nota (2026-11-12 12:29:20 UTC)

Requisitos importados: flujo_c281f4f7154afdb2f.agentes_en_el_repo_mantiene_una_guia_versionada (funcional), flujo_c281f4f7154afdb2f.la_puerta_funciona_con_el_producto_conectado (funcional), flujo_c281f4f7154afdb2f.las_pruebas_y_herramientas_leen_los_registros_del_almacen (funcional), flujo_c281f4f7154afdb2f.migrar_limpia_lo_de_factory_del_producto (funcional). Los nuevos nacen SIN MEDIR; verificá cobertura antes del juicio.

### Nota (2026-11-12 12:56:43 UTC)

Medidas de flujo_c281f4f7154afdb2f.agentes_en_el_repo_mantiene_una_guia_versionada: factory_preparar_migracion.agentes_en_el_repo_mantiene_una_guia_versionada, factory_preparar_migracion.corrida_completa; propuestas por claude-code (agente, propuso, modo confirmacion). SIN MEDIR: sin límite adicional declarado. Revisión y juicio anteriores invalidados; no se declara cumplimiento ni aprobación de pertinencia.

### Nota (2026-11-12 12:56:45 UTC)

Medidas de flujo_c281f4f7154afdb2f.la_puerta_funciona_con_el_producto_conectado: factory_preparar_migracion.la_puerta_funciona_con_el_producto_conectado, factory_preparar_migracion.corrida_completa; propuestas por claude-code (agente, propuso, modo confirmacion). SIN MEDIR: sin límite adicional declarado. Revisión y juicio anteriores invalidados; no se declara cumplimiento ni aprobación de pertinencia.

### Nota (2026-11-12 12:56:47 UTC)

Medidas de flujo_c281f4f7154afdb2f.las_pruebas_y_herramientas_leen_los_registros_del_almacen: factory_preparar_migracion.las_pruebas_y_herramientas_leen_los_registros_del_almacen, factory_preparar_migracion.corrida_completa; propuestas por claude-code (agente, propuso, modo confirmacion). SIN MEDIR: sin límite adicional declarado. Revisión y juicio anteriores invalidados; no se declara cumplimiento ni aprobación de pertinencia.

### Nota (2026-11-12 12:56:49 UTC)

Medidas de flujo_c281f4f7154afdb2f.migrar_limpia_lo_de_factory_del_producto: factory_preparar_migracion.migrar_limpia_lo_de_factory_del_producto, factory_preparar_migracion.corrida_completa; propuestas por claude-code (agente, propuso, modo confirmacion). SIN MEDIR: sin límite adicional declarado. Revisión y juicio anteriores invalidados; no se declara cumplimiento ni aprobación de pertinencia.

### Nota (2026-11-12 12:58:14 UTC)

Medidas de flujo_c281f4f7154afdb2f.agentes_en_el_repo_mantiene_una_guia_versionada: Brian Hollweg (persona, confirmo, modo confirmacion).

### Nota (2026-11-12 12:58:15 UTC)

Medidas de flujo_c281f4f7154afdb2f.la_puerta_funciona_con_el_producto_conectado: Brian Hollweg (persona, confirmo, modo confirmacion).

### Nota (2026-11-12 12:58:15 UTC)

Medidas de flujo_c281f4f7154afdb2f.las_pruebas_y_herramientas_leen_los_registros_del_almacen: Brian Hollweg (persona, confirmo, modo confirmacion).

### Nota (2026-11-12 12:58:15 UTC)

Medidas de flujo_c281f4f7154afdb2f.migrar_limpia_lo_de_factory_del_producto: Brian Hollweg (persona, confirmo, modo confirmacion).

### Nota (2026-11-12 13:23:05 UTC)

Revisión guiada Brian Hollweg: aprobar; registrada por Brian Hollweg (persona, confirmo, modo confirmacion; motivo: Codex, una vuelta, sin hallazgos. Evidencia de 1c29dfa: 1478 pruebas, 13 casos de contrato, éxito. 18 mutaciones a mano, todas detectadas. Ensayo sobre una copia de Factory (4f9beb71): 6672 archivos migrados, listar igual, .gitignore y .gitattributes limpiados, y las 1478 pruebas bien antes y después de migrar (en la etapa 6 fallaban 17). Arreglo de paso: la puerta con el producto conectado buscaba secretos en el almacén y dejaba pasar en silencio. Pruebas existentes editadas, declaradas y aceptadas por codex: p6, vg3, mg1 y los dos dorados de la ayuda. Los drivers de unión que hooks dejó en .git/config quedan (sacarlos sería cambiar la configuración de Git). La migración real de ~/Dev/factory queda como decisión aparte.); 0 abiertos derivados; commit f33e65de15d499ad9c4f29351855be699489a65b; informe tareas/20261112-121837-6bu-pmr/revisiones/registro-nds51upy/informe.json; decisiones tareas/20261112-121837-6bu-pmr/revisiones/registro-nds51upy/decisiones.json.
