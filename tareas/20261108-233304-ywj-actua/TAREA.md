# Autopilot que actúa: corre lo mecánico, delega lo creativo, con topes y rastro

- ESTADO: ABIERTA
- PRIORIDAD: 50
- ETIQUETAS: 

### Nota (2026-11-08 23:33:04 UTC)

OpenSpec: openspec/changes/20261108-233304-ywj-actua. Modo de trabajo: confirmacion. Estado de factory: espera aceptación de proposal.md y spec.md.

### Nota (2026-11-08 23:34:42 UTC)

Brian Hollweg (persona, decidio, modo confirmacion) aceptó propuesta y spec openspec/changes/20261108-233304-ywj-actua/specs/flujo/spec.md; se reiniciaron las validaciones dependientes.

### Nota (2026-11-08 23:34:51 UTC)

Requisitos importados: flujo_cbe1c0ee48f2ba730.autopilot_ejecutar_solo_actua_como_agente_y_nunca_decide_por_una_persona (funcional), flujo_cbe1c0ee48f2ba730.cada_paso_deja_su_porque_en_el_registro (funcional), flujo_cbe1c0ee48f2ba730.el_bucle_observa_decide_actua_y_vuelve_a_observar (funcional), flujo_cbe1c0ee48f2ba730.el_bucle_tiene_topes_y_se_frena_solo (funcional). Los nuevos nacen SIN MEDIR; verificá cobertura antes del juicio.

### Nota (2026-11-08 23:42:32 UTC)

Medidas de flujo_cbe1c0ee48f2ba730.autopilot_ejecutar_solo_actua_como_agente_y_nunca_decide_por_una_persona: factory_conductor.autopilot_ejecutar_solo_actua_como_agente_y_nunca_decide_por_una_persona, factory_conductor.corrida_completa; propuestas por claude-code (agente, propuso, modo confirmacion). SIN MEDIR: sin límite adicional declarado. Revisión y juicio anteriores invalidados; no se declara cumplimiento ni aprobación de pertinencia.

### Nota (2026-11-08 23:42:34 UTC)

Medidas de flujo_cbe1c0ee48f2ba730.cada_paso_deja_su_porque_en_el_registro: factory_conductor.cada_paso_deja_su_porque_en_el_registro, factory_conductor.corrida_completa; propuestas por claude-code (agente, propuso, modo confirmacion). SIN MEDIR: sin límite adicional declarado. Revisión y juicio anteriores invalidados; no se declara cumplimiento ni aprobación de pertinencia.

### Nota (2026-11-08 23:42:35 UTC)

Medidas de flujo_cbe1c0ee48f2ba730.el_bucle_observa_decide_actua_y_vuelve_a_observar: factory_conductor.el_bucle_observa_decide_actua_y_vuelve_a_observar, factory_conductor.corrida_completa; propuestas por claude-code (agente, propuso, modo confirmacion). SIN MEDIR: sin límite adicional declarado. Revisión y juicio anteriores invalidados; no se declara cumplimiento ni aprobación de pertinencia.

### Nota (2026-11-08 23:42:37 UTC)

Medidas de flujo_cbe1c0ee48f2ba730.el_bucle_tiene_topes_y_se_frena_solo: factory_conductor.el_bucle_tiene_topes_y_se_frena_solo, factory_conductor.corrida_completa; propuestas por claude-code (agente, propuso, modo confirmacion). SIN MEDIR: sin límite adicional declarado. Revisión y juicio anteriores invalidados; no se declara cumplimiento ni aprobación de pertinencia.

### Nota (2026-11-09 00:04:48 UTC)

Medidas de flujo_cbe1c0ee48f2ba730.autopilot_ejecutar_solo_actua_como_agente_y_nunca_decide_por_una_persona: Brian Hollweg (persona, confirmo, modo confirmacion).

### Nota (2026-11-09 00:04:48 UTC)

Medidas de flujo_cbe1c0ee48f2ba730.cada_paso_deja_su_porque_en_el_registro: Brian Hollweg (persona, confirmo, modo confirmacion).

### Nota (2026-11-09 00:04:48 UTC)

Medidas de flujo_cbe1c0ee48f2ba730.el_bucle_observa_decide_actua_y_vuelve_a_observar: Brian Hollweg (persona, confirmo, modo confirmacion).

### Nota (2026-11-09 00:04:48 UTC)

Medidas de flujo_cbe1c0ee48f2ba730.el_bucle_tiene_topes_y_se_frena_solo: Brian Hollweg (persona, confirmo, modo confirmacion).

### Nota (2026-11-09 01:12:56 UTC)

Revisión guiada Brian Hollweg: aprobar; registrada por Brian Hollweg (persona, confirmo, modo confirmacion; motivo: Cuatro rondas de codex sobre candidatos a690c89, d90883c, aa012ae y 18e9e86; la cuarta sin hallazgos. Ronda 1, ACTUA-001 (media): el plazo de un paso se calculaba antes de dejar el porqué, que gasta tiempo del tope; ahora cada proceso toma su plazo del reloj justo antes de correr. Ronda 2, ACTUA-002 (media): _proceso estiraba cualquier plazo a 1 s y el mensaje final tenía 60 s fijos; ahora el plazo es exacto, sin tiempo no arranca, y el mensaje final tiene un plazo propio de 10 s (PLAZO_FINAL) FUERA del tope, decisión explícita y documentada en docs/modos.md: el rastro del motivo lo exige la spec aunque el tiempo se haya agotado y dejarlo no es actuar. Ronda 3, ACTUA-003 (media): el código de salida no reflejaba que faltara el mensaje final; ahora el resultado trae fallo (un paso, el porqué, el mensaje final o la lectura del estado) y el código sale de ahí. Evidencia 1326 pruebas OK, 16 casos de contrato. 47 mutaciones propias, 45 detectadas y 2 equivalentes declaradas (len(nombre) < 3 y la verificación final del subcomando en argumentos_mecanicos: defensas redundantes con el parser, que rechaza antes esos casos). Toca reglas de decisión (cli.py): camino completo. Sin pruebas existentes editadas; se regenera tests/datos/ayuda-cli.json. Las decisiones de persona nunca se corren, ni mal clasificadas (se verifica con el comando por separado de autopilot.argumentos_mecanicos); integración, publicación y producción siguen en confirmacion. Límites: --lanzar ejecuta lo que se le pase con los permisos del usuario y no se guarda en la configuración; qué agente lanzar y con qué permisos lo decide la persona en cada corrida; el agente lanzado hace lo que haga y se verifica con la evidencia, Oracle y la revisión de siempre; el plazo del mensaje final (10 s) queda fuera del tope por diseño; el conductor depende del parser real. Un freno de este cambio es el que da el cambio 2 (frenos).); 0 abiertos derivados; commit b2cb6fc2d91b42cd2ff0173d1b7670bfe1c16e1f; informe tareas/20261108-233304-ywj-actua/revisiones/registro-r4hama_3/informe.json; decisiones tareas/20261108-233304-ywj-actua/revisiones/registro-r4hama_3/decisiones.json.

### Nota (2026-11-09 01:13:06 UTC)

Juicio Factory: verde; salida Oracle 0; informe .factory/cambios/20261108-233304-ywj-actua/oracle-veredicto.txt.
