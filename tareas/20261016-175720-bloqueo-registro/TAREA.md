# Dos procesos que escriben el mismo registro no se pisan

- ESTADO: ABIERTA
- PRIORIDAD: 50
- ETIQUETAS: 

### Nota (2026-10-16 17:57:20 UTC)

OpenSpec: openspec/changes/20261016-175720-bloqueo-registro. Modo de trabajo: confirmacion. Estado de factory: espera aceptación de proposal.md y spec.md.

### Nota (2026-10-16 18:01:02 UTC)

Brian Hollweg (persona, decidio, modo confirmacion) aceptó propuesta y spec openspec/changes/20261016-175720-bloqueo-registro/specs/flujo/spec.md; se reiniciaron las validaciones dependientes.

### Nota (2026-10-16 18:01:15 UTC)

Requisitos importados: flujo_c467adb55cba3c0a6.dos_procesos_que_escriben_el_mismo_registro_no_se_pisan (funcional). Los nuevos nacen SIN MEDIR; verificá cobertura antes del juicio.

### Nota (2026-10-16 18:05:12 UTC)

Medidas de flujo_c467adb55cba3c0a6.dos_procesos_que_escriben_el_mismo_registro_no_se_pisan: factory_bloqueo.dos_procesos_que_escriben_el_mismo_registro_no_se_pisan, factory_bloqueo.corrida_completa; propuestas por claude-code (agente, propuso, modo confirmacion). SIN MEDIR: sin límite adicional declarado. Revisión y juicio anteriores invalidados; no se declara cumplimiento ni aprobación de pertinencia.

### Nota (2026-10-16 18:07:00 UTC)

Medidas de flujo_c467adb55cba3c0a6.dos_procesos_que_escriben_el_mismo_registro_no_se_pisan: Brian Hollweg (persona, confirmo, modo confirmacion).

### Nota (2026-10-16 19:55:16 UTC)

Revisión guiada Brian Hollweg: aprobar; registrada por Brian Hollweg (persona, confirmo, modo confirmacion; motivo: tres vueltas de codex y agy: la 1 marcó un alto y tres medios (la primera escritura sin leer no quedaba protegida, un archivo borrado daba un error crudo, bl2 no enfrentaba dos escrituras de Factory) y la 2 un medio (bl1 no aislaba la lectura), corregidos con pruebas que fallan sobre el código anterior y mutaciones; la 3 no encontró nada; quedan bajas de la vuelta 2 sobre el alcance del catálogo, el sensor y el flock en carpetas compartidas); 0 abiertos derivados; commit d9c38661e3fa22d05b01dbdd565c4f194efa4e1c; informe tareas/20261016-175720-bloqueo-registro/revisiones/registro-_qrs0clz/informe.json; decisiones tareas/20261016-175720-bloqueo-registro/revisiones/registro-_qrs0clz/decisiones.json.

### Nota (2026-10-16 19:55:29 UTC)

Juicio Factory: verde; salida Oracle 0; informe .factory/cambios/20261016-175720-bloqueo-registro/oracle-veredicto.txt.
