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

### Nota (2026-11-12 11:28:25 UTC)

Medidas de flujo_c3b7c8e521b99f547.el_ensayo_sobre_una_copia propuestas por claude-code (agente, modo confirmacion); no cuentan hasta que una persona las confirme.

### Nota (2026-11-12 11:28:28 UTC)

Medidas de flujo_c3b7c8e521b99f547.migrar_al_almacen_copia_conecta_y_deja_la_baja propuestas por claude-code (agente, modo confirmacion); no cuentan hasta que una persona las confirme.

### Nota (2026-11-12 11:28:30 UTC)

Medidas de flujo_c3b7c8e521b99f547.migrar_al_almacen_se_niega_sin_tocar_nada propuestas por claude-code (agente, modo confirmacion); no cuentan hasta que una persona las confirme.

### Nota (2026-11-12 11:28:32 UTC)

Medidas de flujo_c3b7c8e521b99f547.migrar_verificar_no_escribe propuestas por claude-code (agente, modo confirmacion); no cuentan hasta que una persona las confirme.

### Nota (2026-11-12 11:29:50 UTC)

Medidas de flujo_c3b7c8e521b99f547.el_ensayo_sobre_una_copia: Brian Hollweg (persona, confirmo, modo confirmacion).

### Nota (2026-11-12 11:29:50 UTC)

Medidas de flujo_c3b7c8e521b99f547.migrar_al_almacen_copia_conecta_y_deja_la_baja: Brian Hollweg (persona, confirmo, modo confirmacion).

### Nota (2026-11-12 11:29:50 UTC)

Medidas de flujo_c3b7c8e521b99f547.migrar_al_almacen_se_niega_sin_tocar_nada: Brian Hollweg (persona, confirmo, modo confirmacion).

### Nota (2026-11-12 11:29:50 UTC)

Medidas de flujo_c3b7c8e521b99f547.migrar_verificar_no_escribe: Brian Hollweg (persona, confirmo, modo confirmacion).

### Nota (2026-11-12 11:54:01 UTC)

Revisión guiada Brian Hollweg: aprobar; registrada por Brian Hollweg (persona, confirmo, modo confirmacion; motivo: Desde bc3d969 (revisado por codex en la cuarta vuelta, sin hallazgos, y aprobado por Brian) sólo cambiaron 4 líneas de catálogos: los umbrales de casos pasan de 15 a 23 (2→4, 8→12, 2→4) por las pruebas que se sumaron con MIG-001…005; ninguna línea de código ni de pruebas. Medidas confirmadas de nuevo por Brian. Evidencia de 6251421: 1465 pruebas, 23 casos de contrato, éxito. Ensayo con el código final sobre una copia de Factory (567c4f8): 6637 archivos migrados, listar igual; fuera de las 2 pruebas ya conocidas (p6, vg3), la suite de la copia pasa después de migrar. Se editaron dos ayudantes de prueba existentes (tests/terminal_en_node.cjs, tests/vscode_en_node.cjs), declarados y aceptados por codex. Migrar Factory mismo queda como decisión aparte.); 0 abiertos derivados; commit e8987e2c246f36a905f7702205cdb31e5ecd8c3c; informe tareas/20261112-005922-f5r-almacen-migrar/revisiones/registro-tlo7iapk/informe.json; decisiones tareas/20261112-005922-f5r-almacen-migrar/revisiones/registro-tlo7iapk/decisiones.json.

### Nota (2026-11-12 11:54:31 UTC)

Juicio Factory: verde; salida Oracle 0; informe .factory/cambios/20261112-005922-f5r-almacen-migrar/oracle-veredicto.txt.
