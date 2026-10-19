# Lo que la prueba del ajedrez dejó a la vista: revisores cortados, acciones sin autor y carpetas de más

- ESTADO: ABIERTA
- PRIORIDAD: 50
- ETIQUETAS: 

### Nota (2026-10-17 13:59:53 UTC)

OpenSpec: openspec/changes/20261017-135953-higiene. Modo de trabajo: confirmacion. Estado de factory: espera aceptación de proposal.md y spec.md.

### Nota (2026-10-17 14:02:37 UTC)

Brian Hollweg (persona, decidio, modo confirmacion) aceptó propuesta y spec openspec/changes/20261017-135953-higiene/specs/flujo/spec.md; se reiniciaron las validaciones dependientes.

### Nota (2026-10-19 10:01:04 UTC)

Requisitos importados: flujo_cecdfd053bebfee21.init_no_deja_carpetas_que_factory_no_usa (funcional), flujo_cecdfd053bebfee21.las_acciones_sin_autor_se_avisan (funcional), flujo_cecdfd053bebfee21.un_pedido_de_revision_cortado_queda_a_la_vista (funcional). Los nuevos nacen SIN MEDIR; verificá cobertura antes del juicio.

### Nota (2026-10-19 11:53:28 UTC)

Medidas de flujo_cecdfd053bebfee21.un_pedido_de_revision_cortado_queda_a_la_vista: factory_higiene.un_pedido_de_revision_cortado_queda_a_la_vista, factory_higiene.corrida_completa; propuestas por claude-code (agente, propuso, modo confirmacion). SIN MEDIR: sin límite adicional declarado. Revisión y juicio anteriores invalidados; no se declara cumplimiento ni aprobación de pertinencia.

### Nota (2026-10-19 11:53:28 UTC)

Medidas de flujo_cecdfd053bebfee21.las_acciones_sin_autor_se_avisan: factory_higiene.las_acciones_sin_autor_se_avisan, factory_higiene.corrida_completa; propuestas por claude-code (agente, propuso, modo confirmacion). SIN MEDIR: sin límite adicional declarado. Revisión y juicio anteriores invalidados; no se declara cumplimiento ni aprobación de pertinencia.

### Nota (2026-10-19 11:53:28 UTC)

Medidas de flujo_cecdfd053bebfee21.init_no_deja_carpetas_que_factory_no_usa: factory_higiene.init_no_deja_carpetas_que_factory_no_usa, factory_higiene.corrida_completa; propuestas por claude-code (agente, propuso, modo confirmacion). SIN MEDIR: sin límite adicional declarado. Revisión y juicio anteriores invalidados; no se declara cumplimiento ni aprobación de pertinencia.

### Nota (2026-10-19 11:57:07 UTC)

Medidas de flujo_cecdfd053bebfee21.init_no_deja_carpetas_que_factory_no_usa: Brian Hollweg (persona, confirmo, modo confirmacion).

### Nota (2026-10-19 11:57:07 UTC)

Medidas de flujo_cecdfd053bebfee21.las_acciones_sin_autor_se_avisan: Brian Hollweg (persona, confirmo, modo confirmacion).

### Nota (2026-10-19 11:57:07 UTC)

Medidas de flujo_cecdfd053bebfee21.un_pedido_de_revision_cortado_queda_a_la_vista: Brian Hollweg (persona, confirmo, modo confirmacion).

### Nota (2026-10-19 17:41:52 UTC)

Revisión guiada Brian Hollweg: aprobar; registrada por Brian Hollweg (persona, confirmo, modo confirmacion; motivo: Cinco vueltas de codex y agy; todos los medios y altos corregidos con pruebas que fallan sobre el código anterior y mutantes muertos (lanzamientos con nombre, cortados siempre a la vista con texto que dice si repetir, Ctrl-C en la validación, init sin carpetas vacías, guía en .factory/local). Quedan dos bajos iguales (HG-005, HG-011): hg2 no ejecuta importar sin --agente; el aviso es el mismo para cualquier acción sin autor y hg2 ya lo prueba con nuevo.); 0 abiertos derivados; commit b5b2d3b0202a01b3895732fa25986689611aa901; informe tareas/20261017-135953-higiene/revisiones/registro-p4khnxxx/informe.json; decisiones tareas/20261017-135953-higiene/revisiones/registro-p4khnxxx/decisiones.json.
