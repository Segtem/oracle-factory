# Autopilot: el conductor no repite el pedido a un revisor que se lanzó y no dejó resultado

- ESTADO: ABIERTA
- PRIORIDAD: 50
- ETIQUETAS: 

### Nota (2026-11-09 19:45:09 UTC)

OpenSpec: openspec/changes/20261109-194509-ylk-sin-informe. Modo de trabajo: confirmacion. Estado de factory: espera aceptación de proposal.md y spec.md.

### Nota (2026-11-09 19:45:34 UTC)

Brian Hollweg (persona, decidio, modo confirmacion) aceptó propuesta y spec openspec/changes/20261109-194509-ylk-sin-informe/specs/flujo/spec.md; se reiniciaron las validaciones dependientes.

### Nota (2026-11-09 19:45:54 UTC)

Requisitos importados: flujo_cda949385dec880b1.el_segundo_revisor_no_es_uno_que_no_dejo_resultado (funcional). Los nuevos nacen SIN MEDIR; verificá cobertura antes del juicio.

### Nota (2026-11-09 19:47:26 UTC)

Medidas de flujo_cda949385dec880b1.el_segundo_revisor_no_es_uno_que_no_dejo_resultado: factory_sin_informe.el_segundo_revisor_no_es_uno_que_no_dejo_resultado, factory_sin_informe.corrida_completa; propuestas por claude-code (agente, propuso, modo confirmacion). SIN MEDIR: sin límite adicional declarado. Revisión y juicio anteriores invalidados; no se declara cumplimiento ni aprobación de pertinencia.

### Nota (2026-11-09 19:49:11 UTC)

Medidas de flujo_cda949385dec880b1.el_segundo_revisor_no_es_uno_que_no_dejo_resultado: Brian Hollweg (persona, confirmo, modo confirmacion).

### Nota (2026-11-09 20:05:31 UTC)

Revisión guiada Brian Hollweg: aprobar; registrada por Brian Hollweg (persona, confirmo, modo confirmacion; motivo: Propuesta del agente claude-code. Candidato 925896f (camino ligero, 83 líneas de producto): evidencia verde (1346 pruebas, 3 casos de contrato), 13 mutaciones propias detectadas (4 sobrevivieron al principio y las cubrí con casos dentro de los métodos de las pruebas), codex ronda 1 sin hallazgos. QUÉ HAY QUE SABER: (1) este cambio lo construyó un agente lanzado por el conductor con claude -p (permisos acotados: leer/editar/escribir, oracle-factory, .venv/bin/python, git status/diff/log/show/add/commit; sin push, checkout, reset, config ni red); yo escribí la spec, hice las mutaciones y pedí las revisiones. Su código fue mínimo y correcto, no tocó la configuración de git ni editó tests existentes. (2) La instrucción de construir no se la dio el conductor sino yo: ante medir --listar sin pruebas ni catálogos el conductor pidió elegir medidas y el agente contestó con razón que aún no se podía; es un hueco del conductor a arreglar en otro cambio. (3) Descarta al revisor que falló por NOMBRE, no por proveedor (como dice la spec): si codex falla y existe codex2 del mismo proveedor, se ofrece codex2. (4) agy y agy2 siguen sin cuota hasta cerca del 2026-11-15: el revisor fue sólo codex, y el camino ligero alcanza con un revisor y una ronda. No edité ningún test existente.); 0 abiertos derivados; commit a7a48b59290dfae41428f0dbb2a9a037ff0141b6; informe tareas/20261109-194509-ylk-sin-informe/revisiones/registro-rtwqhmcp/informe.json; decisiones tareas/20261109-194509-ylk-sin-informe/revisiones/registro-rtwqhmcp/decisiones.json.

### Nota (2026-11-09 20:05:43 UTC)

Juicio Factory: verde; salida Oracle 0; informe .factory/cambios/20261109-194509-ylk-sin-informe/oracle-veredicto.txt.
