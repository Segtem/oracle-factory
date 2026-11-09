# Autopilot: la propuesta de revisión es trabajo del agente, antes de pedírsela a la persona

- ESTADO: CERRADA
- PRIORIDAD: 50
- ETIQUETAS: 

### Nota (2026-11-09 03:03:59 UTC)

OpenSpec: openspec/changes/20261109-030359-8e4-revprop. Modo de trabajo: confirmacion. Estado de factory: espera aceptación de proposal.md y spec.md.

### Nota (2026-11-09 03:07:22 UTC)

Brian Hollweg (persona, decidio, modo confirmacion) aceptó propuesta y spec openspec/changes/20261109-030359-8e4-revprop/specs/flujo/spec.md; se reiniciaron las validaciones dependientes.

### Nota (2026-11-09 03:07:33 UTC)

Requisitos importados: flujo_c7819789b58cf6ed1.el_conductor_delega_la_propuesta_antes_de_pedir_la_revision (funcional), flujo_c7819789b58cf6ed1.estado_dice_la_ultima_propuesta_de_revision_de_un_agente (funcional). Los nuevos nacen SIN MEDIR; verificá cobertura antes del juicio.

### Nota (2026-11-09 03:12:12 UTC)

Medidas de flujo_c7819789b58cf6ed1.el_conductor_delega_la_propuesta_antes_de_pedir_la_revision: factory_revprop.el_conductor_delega_la_propuesta_antes_de_pedir_la_revision, factory_revprop.corrida_completa; propuestas por claude-code (agente, propuso, modo confirmacion). SIN MEDIR: sin límite adicional declarado. Revisión y juicio anteriores invalidados; no se declara cumplimiento ni aprobación de pertinencia.

### Nota (2026-11-09 03:12:14 UTC)

Medidas de flujo_c7819789b58cf6ed1.estado_dice_la_ultima_propuesta_de_revision_de_un_agente: factory_revprop.estado_dice_la_ultima_propuesta_de_revision_de_un_agente, factory_revprop.corrida_completa; propuestas por claude-code (agente, propuso, modo confirmacion). SIN MEDIR: sin límite adicional declarado. Revisión y juicio anteriores invalidados; no se declara cumplimiento ni aprobación de pertinencia.

### Nota (2026-11-09 03:20:40 UTC)

Medidas de flujo_c7819789b58cf6ed1.el_conductor_delega_la_propuesta_antes_de_pedir_la_revision: Brian Hollweg (persona, confirmo, modo confirmacion).

### Nota (2026-11-09 03:20:40 UTC)

Medidas de flujo_c7819789b58cf6ed1.estado_dice_la_ultima_propuesta_de_revision_de_un_agente: Brian Hollweg (persona, confirmo, modo confirmacion).

### Nota (2026-11-09 12:33:22 UTC)

Revisión guiada Brian Hollweg: aprobar; registrada por Brian Hollweg (persona, confirmo, modo confirmacion; motivo: Tres rondas de codex sobre candidatos 04048bb, c16e67d y ef342fd; la tercera sin hallazgos. Ronda 1, REVPROP-1 (media): ultima_propuesta aceptaba una propuesta de quien no era un agente; ahora exige tipo_actor == agente. Ronda 2, REVPROP-2 (media): el conductor aceptaba una propuesta incompleta o con un candidato con basura; ahora cuenta sólo con decision aprobar o cambios, candidato hexadecimal de 7 a 40 caracteres que coincide con el vigente en los 7 primeros, y actor y fecha presentes. Las dos de la clase qué cuenta como propuesta válida. Evidencia 1336 pruebas OK, 7 casos de contrato. 35 mutaciones propias, todas detectadas. Toca reglas de decisión (cli.py no, pero autopilot.py decide qué se le pide a una persona): camino completo por el tamaño y por el freno. DECLARO DOS PRUEBAS EXISTENTES EDITADAS (la guarda de docs/tests.md; por eso estado marca el freno prueba_existente_editada y el conductor se frena solo): sólo sus ayudantes, de forma aditiva: el decidir() de tests/test_autopilot.py y el datos() de tests/test_conductor.py dejan por defecto una propuesta completa y válida del candidato vigente, porque ahora revisar sin propuesta pasa a delegar_al_agente y sin eso los casos que esperan pedir_a_persona dejarían de probar lo que decían. Ningún caso se quitó ni se aflojó; codex miró la edición y no objetó. Con datos reales de este cambio, sin el freno, el conductor decide delegar la propuesta al agente en vez de pedir revisar. Límites: el conductor no pide una segunda ronda con otro revisor (estado sólo sugiere uno); un freno ya declarado en la revisión sigue frenando al conductor durante todo el cambio, por eso hoy el paso se hace a mano; la validación de la propuesta está en el conductor y estado muestra lo que hay. La decisión de revisar es siempre de una persona.); 0 abiertos derivados; commit ad22abc03e63146973ed7d8a40f7a756617fd496; informe tareas/20261109-030359-8e4-revprop/revisiones/registro-w7wy4j8t/informe.json; decisiones tareas/20261109-030359-8e4-revprop/revisiones/registro-w7wy4j8t/decisiones.json.

### Nota (2026-11-09 12:33:32 UTC)

Juicio Factory: verde; salida Oracle 0; informe .factory/cambios/20261109-030359-8e4-revprop/oracle-veredicto.txt.

### Nota (2026-11-09 12:37:24 UTC)

Cierre: Brian Hollweg (persona, decidio, modo confirmacion), tras revisar el informe de código y el veredicto Oracle.
