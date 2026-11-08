# Conductor autopilot: decide el siguiente paso por reglas (sin actuar)

- ESTADO: ABIERTA
- PRIORIDAD: 50
- ETIQUETAS: 

### Nota (2026-11-08 22:06:06 UTC)

OpenSpec: openspec/changes/20261108-220606-51z-autopilot. Modo de trabajo: confirmacion. Estado de factory: espera aceptación de proposal.md y spec.md.

### Nota (2026-11-08 22:07:43 UTC)

Brian Hollweg (persona, decidio, modo confirmacion) aceptó propuesta y spec openspec/changes/20261108-220606-51z-autopilot/specs/flujo/spec.md; se reiniciaron las validaciones dependientes.

### Nota (2026-11-08 22:07:55 UTC)

Requisitos importados: flujo_cc3cbaf2da9e917bd.autopilot_solo_lee_y_lo_muestra (funcional), flujo_cc3cbaf2da9e917bd.el_conductor_decide_el_siguiente_paso_por_reglas (funcional), flujo_cc3cbaf2da9e917bd.el_conductor_frena_ante_un_freno_o_un_paso_que_no_conoce (funcional). Los nuevos nacen SIN MEDIR; verificá cobertura antes del juicio.

### Nota (2026-11-08 22:10:09 UTC)

Medidas de flujo_cc3cbaf2da9e917bd.autopilot_solo_lee_y_lo_muestra: factory_autopilot.autopilot_solo_lee_y_lo_muestra, factory_autopilot.corrida_completa; propuestas por claude-code (agente, propuso, modo confirmacion). SIN MEDIR: sin límite adicional declarado. Revisión y juicio anteriores invalidados; no se declara cumplimiento ni aprobación de pertinencia.

### Nota (2026-11-08 22:10:11 UTC)

Medidas de flujo_cc3cbaf2da9e917bd.el_conductor_decide_el_siguiente_paso_por_reglas: factory_autopilot.el_conductor_decide_el_siguiente_paso_por_reglas, factory_autopilot.corrida_completa; propuestas por claude-code (agente, propuso, modo confirmacion). SIN MEDIR: sin límite adicional declarado. Revisión y juicio anteriores invalidados; no se declara cumplimiento ni aprobación de pertinencia.

### Nota (2026-11-08 22:10:13 UTC)

Medidas de flujo_cc3cbaf2da9e917bd.el_conductor_frena_ante_un_freno_o_un_paso_que_no_conoce: factory_autopilot.el_conductor_frena_ante_un_freno_o_un_paso_que_no_conoce, factory_autopilot.corrida_completa; propuestas por claude-code (agente, propuso, modo confirmacion). SIN MEDIR: sin límite adicional declarado. Revisión y juicio anteriores invalidados; no se declara cumplimiento ni aprobación de pertinencia.

### Nota (2026-11-08 22:11:37 UTC)

Medidas de flujo_cc3cbaf2da9e917bd.autopilot_solo_lee_y_lo_muestra: Brian Hollweg (persona, confirmo, modo confirmacion).

### Nota (2026-11-08 22:11:37 UTC)

Medidas de flujo_cc3cbaf2da9e917bd.el_conductor_decide_el_siguiente_paso_por_reglas: Brian Hollweg (persona, confirmo, modo confirmacion).

### Nota (2026-11-08 22:11:37 UTC)

Medidas de flujo_cc3cbaf2da9e917bd.el_conductor_frena_ante_un_freno_o_un_paso_que_no_conoce: Brian Hollweg (persona, confirmo, modo confirmacion).

### Nota (2026-11-08 23:19:05 UTC)

Revisión guiada Brian Hollweg: aprobar; registrada por Brian Hollweg (persona, confirmo, modo confirmacion; motivo: Tres rondas de codex sobre candidatos 92fc31a, bbd6b80 y 0ecb92e; la tercera sin hallazgos. Ronda 1, AP-1 (media): el conductor leía tokens[1] como subcomando y no reconocía el prefijo global --agente; corregido en la clase entera clasificando con el parser real de Factory (opciones globales, forma con =, abreviaturas; lo que el parser rechaza frena). Ronda 2, AP-2 (media): terminado se evaluaba antes que los frenos y los datos ilegibles; era mi interpretación y la spec aprobada dice que frenar va antes que cualquier otra regla, así que volví a la spec (un cambio cerrado con freno sale frenar). Evidencia 1310 pruebas OK, 9 casos de contrato. 28 mutaciones propias detectadas salvo una equivalente declarada (len(tokens) < 3 → < 2: un comando con un solo argumento frena igual por el último paso). Toca reglas de decisión (cli.py): camino completo. Sin pruebas existentes editadas; se regeneran tests/datos/ayuda-cli.json y AGENTS.md (la orden autopilot ID en la lista de lectura). Las decisiones de persona (aprobar-spec, medir --confirmar, revisar, cerrar, abandonar, modo, autonomia, soltar, decidir-union) salen siempre pedir_a_persona, también con --agente delante. Límites: este cambio solo observa y razona (autopilot es de solo lectura); actuar, lanzar al agente, repetir el bucle y registrar el porqué con mensaje son el cambio 3b. El conductor depende del parser real: un paso que el parser no acepta frena.); 0 abiertos derivados; commit 5ca1a61fe620282f995cbb43b551d9d8632e59d8; informe tareas/20261108-220606-51z-autopilot/revisiones/registro-_qsv5tzr/informe.json; decisiones tareas/20261108-220606-51z-autopilot/revisiones/registro-_qsv5tzr/decisiones.json.

### Nota (2026-11-08 23:19:22 UTC)

Juicio Factory: verde; salida Oracle 0; informe .factory/cambios/20261108-220606-51z-autopilot/oracle-veredicto.txt.
