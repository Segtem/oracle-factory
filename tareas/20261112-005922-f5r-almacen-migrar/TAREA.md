# Registros fuera del repo del producto, etapa 6: migrar los registros de un proyecto a un almacén

- ESTADO: ABIERTA
- PRIORIDAD: 50
- ETIQUETAS: 

### Nota (2026-11-12 00:59:22 UTC)

OpenSpec: openspec/changes/20261112-005922-f5r-almacen-migrar. Modo de trabajo: confirmacion. Estado de factory: espera aceptación de proposal.md y spec.md.

### Nota (2026-11-12 01:04:34 UTC)

Brian Hollweg (persona, decidio, modo confirmacion) aceptó propuesta y spec openspec/changes/20261112-005922-f5r-almacen-migrar/specs/flujo/spec.md; se reiniciaron las validaciones dependientes.

### Nota (2026-11-12 01:04:44 UTC)

Brian Hollweg (persona, decidio, modo confirmacion) aceptó propuesta y spec openspec/changes/20261112-005922-f5r-almacen-migrar/specs/flujo/spec.md; se reiniciaron las validaciones dependientes.

### Nota (2026-11-12 01:04:57 UTC)

Requisitos importados: flujo_c3b7c8e521b99f547.el_ensayo_sobre_una_copia (funcional), flujo_c3b7c8e521b99f547.migrar_al_almacen_copia_conecta_y_deja_la_baja (funcional), flujo_c3b7c8e521b99f547.migrar_al_almacen_se_niega_sin_tocar_nada (funcional), flujo_c3b7c8e521b99f547.migrar_verificar_no_escribe (funcional). Los nuevos nacen SIN MEDIR; verificá cobertura antes del juicio.

### Nota (2026-11-12 01:53:53 UTC)

Medidas de flujo_c3b7c8e521b99f547.el_ensayo_sobre_una_copia: factory_almacen_migrar.el_ensayo_sobre_una_copia, factory_almacen_migrar.corrida_completa; propuestas por claude-code (agente, propuso, modo confirmacion). SIN MEDIR: sin límite adicional declarado. Revisión y juicio anteriores invalidados; no se declara cumplimiento ni aprobación de pertinencia.

### Nota (2026-11-12 01:53:55 UTC)

Medidas de flujo_c3b7c8e521b99f547.migrar_al_almacen_copia_conecta_y_deja_la_baja: factory_almacen_migrar.migrar_al_almacen_copia_conecta_y_deja_la_baja, factory_almacen_migrar.corrida_completa; propuestas por claude-code (agente, propuso, modo confirmacion). SIN MEDIR: sin límite adicional declarado. Revisión y juicio anteriores invalidados; no se declara cumplimiento ni aprobación de pertinencia.

### Nota (2026-11-12 01:53:57 UTC)

Medidas de flujo_c3b7c8e521b99f547.migrar_al_almacen_se_niega_sin_tocar_nada: factory_almacen_migrar.migrar_al_almacen_se_niega_sin_tocar_nada, factory_almacen_migrar.corrida_completa; propuestas por claude-code (agente, propuso, modo confirmacion). SIN MEDIR: sin límite adicional declarado. Revisión y juicio anteriores invalidados; no se declara cumplimiento ni aprobación de pertinencia.

### Nota (2026-11-12 01:53:59 UTC)

Medidas de flujo_c3b7c8e521b99f547.migrar_verificar_no_escribe: factory_almacen_migrar.migrar_verificar_no_escribe, factory_almacen_migrar.corrida_completa; propuestas por claude-code (agente, propuso, modo confirmacion). SIN MEDIR: sin límite adicional declarado. Revisión y juicio anteriores invalidados; no se declara cumplimiento ni aprobación de pertinencia.

### Nota (2026-11-12 09:57:24 UTC)

Medidas de flujo_c3b7c8e521b99f547.el_ensayo_sobre_una_copia: Brian Hollweg (persona, confirmo, modo confirmacion).

### Nota (2026-11-12 09:57:24 UTC)

Medidas de flujo_c3b7c8e521b99f547.migrar_al_almacen_copia_conecta_y_deja_la_baja: Brian Hollweg (persona, confirmo, modo confirmacion).

### Nota (2026-11-12 09:57:25 UTC)

Medidas de flujo_c3b7c8e521b99f547.migrar_al_almacen_se_niega_sin_tocar_nada: Brian Hollweg (persona, confirmo, modo confirmacion).

### Nota (2026-11-12 09:57:25 UTC)

Medidas de flujo_c3b7c8e521b99f547.migrar_verificar_no_escribe: Brian Hollweg (persona, confirmo, modo confirmacion).

### Nota (2026-11-12 11:25:26 UTC)

Revisión guiada Brian Hollweg: aprobar; registrada por Brian Hollweg (persona, confirmo, modo confirmacion; motivo: Cuatro vueltas de codex: MIG-001 a MIG-005 (una alta, cuatro medias: la migración dejaba estados a medias o declaraba éxito falso al fallar git rm, la copia de lo local, el bloqueo, el commit, la conexión o --verificar con una URL) corregidos con su prueba y su mutación; la cuarta vuelta, sin hallazgos. Evidencia de bc3d969: 1465 pruebas, 23 casos de contrato, éxito. Ensayo sobre una copia de Factory: 6607 archivos migrados y listar igual. Se editaron dos ayudantes de prueba existentes (tests/terminal_en_node.cjs, tests/vscode_en_node.cjs), declarados y aceptados por el revisor. Migrar Factory mismo queda como decisión aparte.); 0 abiertos derivados; commit 567c4f8a6c21ebc2e6fe930ba4e9427aef57b43a; informe tareas/20261112-005922-f5r-almacen-migrar/revisiones/registro-ad8uab9s/informe.json; decisiones tareas/20261112-005922-f5r-almacen-migrar/revisiones/registro-ad8uab9s/decisiones.json.

### Nota (2026-11-12 11:27:40 UTC)

Juicio Factory: incompleto/rojo; salida Oracle 1; informe .factory/cambios/20261112-005922-f5r-almacen-migrar/oracle-veredicto.txt.
