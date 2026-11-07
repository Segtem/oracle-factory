# Verificar para CI: comprobar de solo lectura que los cambios están consistentes

- ESTADO: ABIERTA
- PRIORIDAD: 50
- ETIQUETAS: 

### Nota (2026-11-07 13:03:17 UTC)

OpenSpec: openspec/changes/20261107-130317-2vv-verificar. Modo de trabajo: confirmacion. Estado de factory: espera aceptación de proposal.md y spec.md.

### Nota (2026-11-07 13:11:37 UTC)

Brian Hollweg (persona, decidio, modo confirmacion) aceptó propuesta y spec openspec/changes/20261107-130317-2vv-verificar/specs/ci/spec.md; se reiniciaron las validaciones dependientes.

### Nota (2026-11-07 13:11:58 UTC)

Requisitos importados: ci_ceafbb528d2c1c459.hay_un_ejemplo_de_ci_y_de_hook (funcional), ci_ceafbb528d2c1c459.un_cambio_cerrado_tiene_la_decision_de_una_persona (funcional), ci_ceafbb528d2c1c459.verificar_dice_si_los_cambios_estan_consistentes (funcional), ci_ceafbb528d2c1c459.verificar_no_exige_lo_que_otra_maquina_no_tiene (funcional), ci_ceafbb528d2c1c459.verificar_solo_lee_y_no_necesita_a_nadie (funcional). Los nuevos nacen SIN MEDIR; verificá cobertura antes del juicio.

### Nota (2026-11-07 13:13:20 UTC)

Brian Hollweg (persona, decidio, modo confirmacion) aceptó propuesta y spec openspec/changes/20261107-130317-2vv-verificar/specs/ci/spec.md; se reiniciaron las validaciones dependientes.

### Nota (2026-11-07 13:13:29 UTC)

Requisitos importados: ci_c65ac59b63e44085b.hay_un_ejemplo_de_ci_y_de_hook (funcional), ci_c65ac59b63e44085b.un_cambio_cerrado_tiene_la_decision_de_una_persona (funcional), ci_c65ac59b63e44085b.verificar_dice_si_los_cambios_estan_consistentes (funcional), ci_c65ac59b63e44085b.verificar_no_exige_lo_que_otra_maquina_no_tiene (funcional), ci_c65ac59b63e44085b.verificar_solo_lee_y_no_necesita_a_nadie (funcional). Los nuevos nacen SIN MEDIR; verificá cobertura antes del juicio.

### Nota (2026-11-07 13:17:22 UTC)

Medidas de ci_c65ac59b63e44085b.verificar_dice_si_los_cambios_estan_consistentes: factory_verificar.verificar_dice_si_los_cambios_estan_consistentes, factory_verificar.corrida_completa; propuestas por claude-code (agente, propuso, modo confirmacion). SIN MEDIR: sin límite adicional declarado. Revisión y juicio anteriores invalidados; no se declara cumplimiento ni aprobación de pertinencia.

### Nota (2026-11-07 13:17:24 UTC)

Medidas de ci_c65ac59b63e44085b.verificar_solo_lee_y_no_necesita_a_nadie: factory_verificar.verificar_solo_lee_y_no_necesita_a_nadie, factory_verificar.corrida_completa; propuestas por claude-code (agente, propuso, modo confirmacion). SIN MEDIR: sin límite adicional declarado. Revisión y juicio anteriores invalidados; no se declara cumplimiento ni aprobación de pertinencia.

### Nota (2026-11-07 13:17:25 UTC)

Medidas de ci_c65ac59b63e44085b.un_cambio_cerrado_tiene_la_decision_de_una_persona: factory_verificar.un_cambio_cerrado_tiene_la_decision_de_una_persona, factory_verificar.corrida_completa; propuestas por claude-code (agente, propuso, modo confirmacion). SIN MEDIR: sin límite adicional declarado. Revisión y juicio anteriores invalidados; no se declara cumplimiento ni aprobación de pertinencia.

### Nota (2026-11-07 13:17:27 UTC)

Medidas de ci_c65ac59b63e44085b.verificar_no_exige_lo_que_otra_maquina_no_tiene: factory_verificar.verificar_no_exige_lo_que_otra_maquina_no_tiene, factory_verificar.corrida_completa; propuestas por claude-code (agente, propuso, modo confirmacion). SIN MEDIR: sin límite adicional declarado. Revisión y juicio anteriores invalidados; no se declara cumplimiento ni aprobación de pertinencia.

### Nota (2026-11-07 13:17:29 UTC)

Medidas de ci_c65ac59b63e44085b.hay_un_ejemplo_de_ci_y_de_hook: factory_verificar.hay_un_ejemplo_de_ci_y_de_hook, factory_verificar.corrida_completa; propuestas por claude-code (agente, propuso, modo confirmacion). SIN MEDIR: sin límite adicional declarado. Revisión y juicio anteriores invalidados; no se declara cumplimiento ni aprobación de pertinencia.

### Nota (2026-11-07 13:18:17 UTC)

Medidas de ci_c65ac59b63e44085b.hay_un_ejemplo_de_ci_y_de_hook: Brian Hollweg (persona, confirmo, modo confirmacion).

### Nota (2026-11-07 13:18:17 UTC)

Medidas de ci_c65ac59b63e44085b.un_cambio_cerrado_tiene_la_decision_de_una_persona: Brian Hollweg (persona, confirmo, modo confirmacion).

### Nota (2026-11-07 13:18:17 UTC)

Medidas de ci_c65ac59b63e44085b.verificar_dice_si_los_cambios_estan_consistentes: Brian Hollweg (persona, confirmo, modo confirmacion).

### Nota (2026-11-07 13:18:18 UTC)

Medidas de ci_c65ac59b63e44085b.verificar_no_exige_lo_que_otra_maquina_no_tiene: Brian Hollweg (persona, confirmo, modo confirmacion).

### Nota (2026-11-07 13:18:18 UTC)

Medidas de ci_c65ac59b63e44085b.verificar_solo_lee_y_no_necesita_a_nadie: Brian Hollweg (persona, confirmo, modo confirmacion).

### Nota (2026-11-07 13:56:39 UTC)

Revisión guiada Brian Hollweg: aprobar; registrada por Brian Hollweg (persona, confirmo, modo confirmacion; motivo: Dos rondas de codex, ambas sin hallazgos (la segunda, tras reforzar una prueba). Codex revisó de forma estática: no pudo correr las pruebas en su entorno. Las corrí yo: evidencia de 1211 pruebas y 11 casos de contrato en éxito, y 14 mutaciones de verificar.py y de la plantilla, las 14 muertas (para matar la de contexto_producto reforcé test_ci2). Declarado: dos pruebas existentes editadas de forma aditiva (tests/datos/ayuda-cli.json suma el subcomando verificar; tests/test_web_paginas.py pasa de 13 a 14 guías por docs/ci.md), más tools/sitio_paginas.py y site/documentacion.html. Límites: sin prueba propia para un registro ilegible, un cambio abandonado ni un proyecto sin commits con cambios que necesitan compararse; verificar no está en la puerta local ni activado como workflow en este repo (decisiones de Brian). agy no revisó: su modelo configurado ya no existe.); 0 abiertos derivados; commit 38c0e8fea4baec8337c7374e788480f0cf687325; informe tareas/20261107-130317-2vv-verificar/revisiones/registro-fhco7oqd/informe.json; decisiones tareas/20261107-130317-2vv-verificar/revisiones/registro-fhco7oqd/decisiones.json.

### Nota (2026-11-07 13:56:52 UTC)

Juicio Factory: verde; salida Oracle 0; informe .factory/cambios/20261107-130317-2vv-verificar/oracle-veredicto.txt.
