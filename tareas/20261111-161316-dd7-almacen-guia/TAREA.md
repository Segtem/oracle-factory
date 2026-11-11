# Registros fuera del repo del producto, etapa 5a: la guía de agentes y la skill van al producto sin versionar

- ESTADO: ABIERTA
- PRIORIDAD: 50
- ETIQUETAS: 

### Nota (2026-11-11 16:13:16 UTC)

OpenSpec: openspec/changes/20261111-161316-dd7-almacen-guia. Modo de trabajo: confirmacion. Estado de factory: espera aceptación de proposal.md y spec.md.

### Nota (2026-11-11 16:14:25 UTC)

Brian Hollweg (persona, decidio, modo confirmacion) aceptó propuesta y spec openspec/changes/20261111-161316-dd7-almacen-guia/specs/flujo/spec.md; se reiniciaron las validaciones dependientes.

### Nota (2026-11-11 16:14:37 UTC)

Requisitos importados: flujo_cb87b2b390ceaef68.con_almacen_la_guia_no_pisa_lo_que_el_producto_versiona_y_dice_del_almacen (funcional), flujo_cb87b2b390ceaef68.con_almacen_la_guia_y_la_skill_van_al_producto_sin_versionar (funcional). Los nuevos nacen SIN MEDIR; verificá cobertura antes del juicio.

### Nota (2026-11-11 16:21:22 UTC)

Medidas de flujo_cb87b2b390ceaef68.con_almacen_la_guia_no_pisa_lo_que_el_producto_versiona_y_dice_del_almacen: factory_almacen_guia.con_almacen_la_guia_no_pisa_lo_que_el_producto_versiona_y_dice_del_almacen, factory_almacen_guia.corrida_completa; propuestas por claude-code (agente, propuso, modo confirmacion). SIN MEDIR: sin límite adicional declarado. Revisión y juicio anteriores invalidados; no se declara cumplimiento ni aprobación de pertinencia.

### Nota (2026-11-11 16:21:24 UTC)

Medidas de flujo_cb87b2b390ceaef68.con_almacen_la_guia_y_la_skill_van_al_producto_sin_versionar: factory_almacen_guia.con_almacen_la_guia_y_la_skill_van_al_producto_sin_versionar, factory_almacen_guia.corrida_completa; propuestas por claude-code (agente, propuso, modo confirmacion). SIN MEDIR: sin límite adicional declarado. Revisión y juicio anteriores invalidados; no se declara cumplimiento ni aprobación de pertinencia.

### Nota (2026-11-11 17:01:39 UTC)

Medidas de flujo_cb87b2b390ceaef68.con_almacen_la_guia_no_pisa_lo_que_el_producto_versiona_y_dice_del_almacen: Brian Hollweg (persona, confirmo, modo confirmacion).

### Nota (2026-11-11 17:01:39 UTC)

Medidas de flujo_cb87b2b390ceaef68.con_almacen_la_guia_y_la_skill_van_al_producto_sin_versionar: Brian Hollweg (persona, confirmo, modo confirmacion).

### Nota (2026-11-11 18:37:56 UTC)

Revisión guiada Brian Hollweg: aprobar; registrada por Brian Hollweg (persona, confirmo, modo confirmacion; motivo: Propuesta del agente claude-code. Etapa 5a de «registros fuera del repo del producto»: la guía de agentes y la skill van al producto sin versionar. Candidato 9e4c901 (camino completo: 195 líneas y toca cli.py): evidencia verde (1436 pruebas, 6 casos de contrato). LO HICE YO, no el agente lanzado (se quedó sin cuota en las dos etapas anteriores). QUÉ HACE: con almacén aparte, agentes y skill --instalar escriben AGENTS.md (con una sección que dice que los registros viven en un almacén aparte y que se comparten con sincronizar), CLAUDE.md y la skill en el producto, y los excluyen en info/exclude del directorio común de Git del producto (vale para todos sus worktrees), salvo lo que ya ignora; nunca .gitignore ni configuración de Git; git status queda limpio. Si el producto ya versiona alguno, se niega (también con --forzar). No sigue enlaces simbólicos. Sin almacén nada cambia. ENCONTRADO EN EL CAMINO: conectar llama a init, y init escribía la guía: con este cambio la habría escrito en el producto durante conectar, que promete no tocarlo; ahora, al preparar un almacén, init sólo avisa que hay que correr agentes. MUTACIONES: 18, todas detectadas. REVISIÓN: sólo codex, 2 rondas: R1 (medio: rutas con metacaracteres de Git) NO SE REPRODUCE: las rutas excluidas son tres constantes sin metacaracteres y el patrón es relativo a la raíz del repo; lo comprobé con un producto en la carpeta 'prod a[b]*?' y quedó fijado con una prueba; propongo DESCARTARLO; la ronda 2 no trajo hallazgos. DECIDE BRIAN: (1) camino completo con un solo proveedor revisor (agy sin cuota). (2) Decisión por defecto, ya dicha en la spec: si el producto versiona su propio AGENTS.md, CLAUDE.md o la skill, Factory se niega en vez de modificarlos. (3) La única escritura en el .git del producto es info/exclude, y sólo cuando se piden agentes o skill --instalar. No edité ninguna prueba existente.); 0 abiertos derivados; commit 1cb1b0951ee75be73c2264d189c4e483be15dbec; informe tareas/20261111-161316-dd7-almacen-guia/revisiones/registro-ssf009np/informe.json; decisiones tareas/20261111-161316-dd7-almacen-guia/revisiones/registro-ssf009np/decisiones.json.
