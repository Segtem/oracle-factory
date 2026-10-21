# El checkout de un revisor no toca el repositorio: un clon aparte en vez de un worktree

- ESTADO: ABIERTA
- PRIORIDAD: 50
- ETIQUETAS: 

### Nota (2026-10-20 20:00:30 UTC)

OpenSpec: openspec/changes/20261020-200030-aislar. Modo de trabajo: confirmacion. Estado de factory: espera aceptación de proposal.md y spec.md.

### Nota (2026-10-20 20:01:13 UTC)

Brian Hollweg (persona, decidio, modo confirmacion) aceptó propuesta y spec openspec/changes/20261020-200030-aislar/specs/revisores/spec.md; se reiniciaron las validaciones dependientes.

### Nota (2026-10-20 20:01:23 UTC)

Requisitos importados: revisores_c0acaae89b46617f5.el_checkout_de_un_revisor_no_toca_el_repositorio (funcional). Los nuevos nacen SIN MEDIR; verificá cobertura antes del juicio.

### Nota (2026-10-20 20:05:46 UTC)

Medidas de revisores_c0acaae89b46617f5.el_checkout_de_un_revisor_no_toca_el_repositorio: factory_aislar.el_checkout_de_un_revisor_no_toca_el_repositorio, factory_aislar.corrida_completa; propuestas por claude-code (agente, propuso, modo confirmacion). SIN MEDIR: sin límite adicional declarado. Revisión y juicio anteriores invalidados; no se declara cumplimiento ni aprobación de pertinencia.

### Nota (2026-10-20 21:11:26 UTC)

Medidas de revisores_c0acaae89b46617f5.el_checkout_de_un_revisor_no_toca_el_repositorio: Brian Hollweg (persona, confirmo, modo confirmacion).

### Nota (2026-10-20 22:17:50 UTC)

Brian Hollweg (persona, decidio, modo confirmacion) aceptó propuesta y spec openspec/changes/20261020-200030-aislar/specs/revisores/spec.md; se reiniciaron las validaciones dependientes.

### Nota (2026-10-20 22:18:06 UTC)

Requisitos importados: revisores_c0acaae89b46617f5.el_checkout_de_un_revisor_no_toca_el_repositorio (funcional). Los nuevos nacen SIN MEDIR; verificá cobertura antes del juicio.

### Nota (2026-10-20 23:06:31 UTC)

Brian Hollweg (persona, decidio, modo confirmacion) aceptó propuesta y spec openspec/changes/20261020-200030-aislar/specs/revisores/spec.md; se reiniciaron las validaciones dependientes.

### Nota (2026-10-21 00:15:33 UTC)

Requisitos importados: revisores_c0acaae89b46617f5.el_checkout_de_un_revisor_no_toca_el_repositorio (funcional). Los nuevos nacen SIN MEDIR; verificá cobertura antes del juicio.

### Nota (2026-10-21 00:33:50 UTC)

Revisión guiada Brian Hollweg: aprobar; registrada por Brian Hollweg (persona, confirmo, modo confirmacion; motivo: Cinco vueltas de codex y agy; en la última ninguno dejó hallazgos, y en ninguna vuelta cambió el user.name ni las ramas del repositorio. Corregido con pruebas que fallan sin cada corrección: el checkout es un clon --local por pedido, sin remotos ni alternates (un gc no lo rompe), vuelve al candidato antes de validar, --base se traduce a SHA, y el número del pedido es el más alto exacto del revisor mirando informes versionados, paquetes y clones. Queda bajo (aceptado en la vuelta 1, F-006): aislar al revisor del resto del disco es cosa de su sandbox.); 0 abiertos derivados; commit e6b528e7d6a9f1102c206c3bacd3d200d6f174ff; informe tareas/20261020-200030-aislar/revisiones/registro-n2enjd_g/informe.json; decisiones tareas/20261020-200030-aislar/revisiones/registro-n2enjd_g/decisiones.json.
