# Frenos: el de pruebas editadas deja de frenar cuando una persona aprobó la revisión

- ESTADO: CERRADA
- PRIORIDAD: 50
- ETIQUETAS: 

### Nota (2026-11-09 12:57:52 UTC)

OpenSpec: openspec/changes/20261109-125752-r6d-freno-visto. Modo de trabajo: confirmacion. Estado de factory: espera aceptación de proposal.md y spec.md.

### Nota (2026-11-09 13:02:42 UTC)

Brian Hollweg (persona, decidio, modo confirmacion) aceptó propuesta y spec openspec/changes/20261109-125752-r6d-freno-visto/specs/flujo/spec.md; se reiniciaron las validaciones dependientes.

### Nota (2026-11-09 13:09:57 UTC)

Brian Hollweg (persona, decidio, modo confirmacion) aceptó propuesta y spec openspec/changes/20261109-125752-r6d-freno-visto/specs/flujo/spec.md; se reiniciaron las validaciones dependientes.

### Nota (2026-11-09 13:10:08 UTC)

Requisitos importados: flujo_ccaf484f1fb333be3.el_freno_de_pruebas_editadas_cede_ante_una_revision_aprobada (funcional). Los nuevos nacen SIN MEDIR; verificá cobertura antes del juicio.

### Nota (2026-11-09 13:10:52 UTC)

Medidas de flujo_ccaf484f1fb333be3.el_freno_de_pruebas_editadas_cede_ante_una_revision_aprobada: factory_freno_visto.el_freno_de_pruebas_editadas_cede_ante_una_revision_aprobada, factory_freno_visto.corrida_completa; propuestas por claude-code (agente, propuso, modo confirmacion). SIN MEDIR: sin límite adicional declarado. Revisión y juicio anteriores invalidados; no se declara cumplimiento ni aprobación de pertinencia.

### Nota (2026-11-09 13:32:39 UTC)

Medidas de flujo_ccaf484f1fb333be3.el_freno_de_pruebas_editadas_cede_ante_una_revision_aprobada: Brian Hollweg (persona, confirmo, modo confirmacion).

### Nota (2026-11-09 15:44:13 UTC)

Revisión guiada Brian Hollweg: aprobar; registrada por Brian Hollweg (persona, confirmo, modo confirmacion; motivo: Propuesta del agente claude-code. Candidato f575a13: evidencia verde (1339 pruebas, 3 casos de contrato), 14 mutaciones propias detectadas, agy ronda 1 con FRV-001 y FRV-002 (medios, huecos de prueba: corregidos) y codex ronda 2 sin hallazgos. DECIDE BRIAN: (1) FRV-004 (informativo): en modo funcional con requisitos no funcionales, o en modo autonomo, un agente puede registrar una revision aprobada, y con eso el freno prueba_existente_editada se levanta sin que una persona haya mirado los tests editados; solo corregi la redaccion (comentario y docs/tests.md), la regla no cambia. En este proyecto (confirmacion) la revision siempre es de una persona, asi que no aplica aqui; si queres, un cambio siguiente exige tipo_actor persona. (2) FRV-003 (baja) aceptado: el ayudante de EstadoReal usa una lista de editados fija en las aserciones intermedias; el estado real con Git se prueba aparte. No edite ningun test existente.); 0 abiertos derivados; commit 5e176a3fa41f95b854e6c230b724f0e8190dc60c; informe tareas/20261109-125752-r6d-freno-visto/revisiones/registro-_p9n74kx/informe.json; decisiones tareas/20261109-125752-r6d-freno-visto/revisiones/registro-_p9n74kx/decisiones.json.

### Nota (2026-11-09 15:44:23 UTC)

Juicio Factory: verde; salida Oracle 0; informe .factory/cambios/20261109-125752-r6d-freno-visto/oracle-veredicto.txt.

### Nota (2026-11-09 15:44:54 UTC)

Cierre: Brian Hollweg (persona, decidio, modo confirmacion), tras revisar el informe de código y el veredicto Oracle.
