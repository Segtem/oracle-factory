# Un camino ligero de revisión para los cambios chicos

- ESTADO: ABIERTA
- PRIORIDAD: 50
- ETIQUETAS: 

### Nota (2026-11-02 22:12:11 UTC)

OpenSpec: openspec/changes/20261102-221210-70x-caminoligero. Modo de trabajo: confirmacion. Estado de factory: espera aceptación de proposal.md y spec.md.

### Nota (2026-11-02 22:20:28 UTC)

Brian Hollweg (persona, decidio, modo confirmacion) aceptó propuesta y spec openspec/changes/20261102-221210-70x-caminoligero/specs/practicas/spec.md; se reiniciaron las validaciones dependientes.

### Nota (2026-11-02 22:20:38 UTC)

Requisitos importados: practicas_cbb21b20e98f56a94.el_camino_ligero_no_cambia_ninguna_decision_ni_paso_pendiente (funcional), practicas_cbb21b20e98f56a94.el_estado_dice_si_el_candidato_califica_para_el_camino_ligero (funcional), practicas_cbb21b20e98f56a94.la_guia_para_agentes_explica_el_camino_ligero (funcional). Los nuevos nacen SIN MEDIR; verificá cobertura antes del juicio.

### Nota (2026-11-02 22:24:09 UTC)

Medidas de practicas_cbb21b20e98f56a94.el_estado_dice_si_el_candidato_califica_para_el_camino_ligero: factory_camino_ligero.el_estado_dice_si_el_candidato_califica_para_el_camino_ligero, factory_camino_ligero.corrida_completa; propuestas por claude-code (agente, propuso, modo confirmacion). SIN MEDIR: sin límite adicional declarado. Revisión y juicio anteriores invalidados; no se declara cumplimiento ni aprobación de pertinencia.

### Nota (2026-11-02 22:24:11 UTC)

Medidas de practicas_cbb21b20e98f56a94.el_camino_ligero_no_cambia_ninguna_decision_ni_paso_pendiente: factory_camino_ligero.el_camino_ligero_no_cambia_ninguna_decision_ni_paso_pendiente, factory_camino_ligero.corrida_completa; propuestas por claude-code (agente, propuso, modo confirmacion). SIN MEDIR: sin límite adicional declarado. Revisión y juicio anteriores invalidados; no se declara cumplimiento ni aprobación de pertinencia.

### Nota (2026-11-02 22:24:12 UTC)

Medidas de practicas_cbb21b20e98f56a94.la_guia_para_agentes_explica_el_camino_ligero: factory_camino_ligero.la_guia_para_agentes_explica_el_camino_ligero, factory_camino_ligero.corrida_completa; propuestas por claude-code (agente, propuso, modo confirmacion). SIN MEDIR: sin límite adicional declarado. Revisión y juicio anteriores invalidados; no se declara cumplimiento ni aprobación de pertinencia.

### Nota (2026-11-02 22:27:42 UTC)

Medidas de practicas_cbb21b20e98f56a94.el_camino_ligero_no_cambia_ninguna_decision_ni_paso_pendiente: Brian Hollweg (persona, confirmo, modo confirmacion).

### Nota (2026-11-02 22:27:42 UTC)

Medidas de practicas_cbb21b20e98f56a94.el_estado_dice_si_el_candidato_califica_para_el_camino_ligero: Brian Hollweg (persona, confirmo, modo confirmacion).

### Nota (2026-11-02 22:27:43 UTC)

Medidas de practicas_cbb21b20e98f56a94.la_guia_para_agentes_explica_el_camino_ligero: Brian Hollweg (persona, confirmo, modo confirmacion).

### Nota (2026-11-02 23:55:00 UTC)

Brian Hollweg (persona, decidio, modo confirmacion) aceptó propuesta y spec openspec/changes/20261102-221210-70x-caminoligero/specs/practicas/spec.md; se reiniciaron las validaciones dependientes.

### Nota (2026-11-02 23:55:12 UTC)

Requisitos importados: practicas_cbb21b20e98f56a94.el_camino_ligero_no_cambia_ninguna_decision_ni_paso_pendiente (funcional), practicas_cbb21b20e98f56a94.el_estado_dice_si_el_candidato_califica_para_el_camino_ligero (funcional), practicas_cbb21b20e98f56a94.la_guia_para_agentes_explica_el_camino_ligero (funcional). Los nuevos nacen SIN MEDIR; verificá cobertura antes del juicio.

### Nota (2026-11-02 23:55:14 UTC)

Medidas de practicas_cbb21b20e98f56a94.el_estado_dice_si_el_candidato_califica_para_el_camino_ligero propuestas por claude-code (agente, modo confirmacion); no cuentan hasta que una persona las confirme.

### Nota (2026-11-02 23:55:16 UTC)

Medidas de practicas_cbb21b20e98f56a94.el_camino_ligero_no_cambia_ninguna_decision_ni_paso_pendiente propuestas por claude-code (agente, modo confirmacion); no cuentan hasta que una persona las confirme.

### Nota (2026-11-02 23:55:17 UTC)

Medidas de practicas_cbb21b20e98f56a94.la_guia_para_agentes_explica_el_camino_ligero propuestas por claude-code (agente, modo confirmacion); no cuentan hasta que una persona las confirme.

### Nota (2026-11-02 23:56:36 UTC)

Medidas de practicas_cbb21b20e98f56a94.el_camino_ligero_no_cambia_ninguna_decision_ni_paso_pendiente: Brian Hollweg (persona, confirmo, modo confirmacion).

### Nota (2026-11-02 23:56:36 UTC)

Medidas de practicas_cbb21b20e98f56a94.el_estado_dice_si_el_candidato_califica_para_el_camino_ligero: Brian Hollweg (persona, confirmo, modo confirmacion).

### Nota (2026-11-02 23:56:37 UTC)

Medidas de practicas_cbb21b20e98f56a94.la_guia_para_agentes_explica_el_camino_ligero: Brian Hollweg (persona, confirmo, modo confirmacion).

### Nota (2026-11-03 01:02:15 UTC)

Revisión guiada Brian Hollweg: aprobar; registrada por Brian Hollweg (persona, confirmo, modo confirmacion; motivo: Dos rondas con revisores independientes (agy2-flash y codex): ronda 1, 7 hallazgos (6 de flash, 1 de codex); ronda 2, 0 y 0 sobre el candidato 02f195b. De la ronda 1: alarmas.py faltaba entre las reglas de decisión (se sumó por decisión de Brian, con reaprobación de la spec), la prueba de la guía era tautológica (ahora hay otra con literales), docs/agentes.md no tenía prueba (hay una) y cuatro huecos de cómputo (binarios, borrados, renombres puros de pruebas a producto y copias sin origen modificado) se declararon como límites conocidos en docs/agentes.md; los revisores de la ronda 2 los vieron y no los objetaron. Evidencia con éxito, producida por tools/verificar_cambio.py: 1062 pruebas y 21 casos de contrato. Mutaciones en tres tandas; los mutantes que sobrevivían se cerraron con pruebas y el equivalente (la condición de abandonado, redundante porque un cambio abandonado no tiene candidato) se eliminó simplificando el código. Declarado: tests/datos/cli_texto/estado.txt, la referencia de texto de estado, recibió una línea nueva sin quitar ninguna; ambos revisores la vieron. Es una orientación, no un gate: los pasos pendientes, el próximo paso y quién decide no cambian (hay una prueba).); 0 abiertos derivados; commit 7b087e11b79c30aba53a1eadf955e176d7bea459; informe tareas/20261102-221210-70x-caminoligero/revisiones/registro-jib_gwno/informe.json; decisiones tareas/20261102-221210-70x-caminoligero/revisiones/registro-jib_gwno/decisiones.json.
