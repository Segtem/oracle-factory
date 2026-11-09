# Registros fuera del repo del producto, etapa 1: dos raíces (producto y registros)

- ESTADO: CERRADA
- PRIORIDAD: 50
- ETIQUETAS: 

### Nota (2026-11-09 21:22:25 UTC)

OpenSpec: openspec/changes/20261109-212224-xo0-registros-raiz. Modo de trabajo: confirmacion. Estado de factory: espera aceptación de proposal.md y spec.md.

### Nota (2026-11-09 21:25:00 UTC)

Brian Hollweg (persona, decidio, modo confirmacion) aceptó propuesta y spec openspec/changes/20261109-212224-xo0-registros-raiz/specs/flujo/spec.md; se reiniciaron las validaciones dependientes.

### Nota (2026-11-09 21:25:10 UTC)

Requisitos importados: flujo_ce4aba0f609f14b30.con_registros_aparte_el_repo_del_producto_queda_limpio (funcional), flujo_ce4aba0f609f14b30.con_registros_aparte_lo_que_necesita_candidato_no_inventa_uno (funcional), flujo_ce4aba0f609f14b30.sin_registros_aparte_nada_cambia (funcional). Los nuevos nacen SIN MEDIR; verificá cobertura antes del juicio.

### Nota (2026-11-09 21:26:52 UTC)

Medidas de flujo_ce4aba0f609f14b30.sin_registros_aparte_nada_cambia: factory_registros_raiz.sin_registros_aparte_nada_cambia, factory_registros_raiz.corrida_completa; propuestas por claude-code (agente, propuso, modo confirmacion). SIN MEDIR: sin límite adicional declarado. Revisión y juicio anteriores invalidados; no se declara cumplimiento ni aprobación de pertinencia.

### Nota (2026-11-09 21:26:54 UTC)

Medidas de flujo_ce4aba0f609f14b30.con_registros_aparte_el_repo_del_producto_queda_limpio: factory_registros_raiz.con_registros_aparte_el_repo_del_producto_queda_limpio, factory_registros_raiz.corrida_completa; propuestas por claude-code (agente, propuso, modo confirmacion). SIN MEDIR: sin límite adicional declarado. Revisión y juicio anteriores invalidados; no se declara cumplimiento ni aprobación de pertinencia.

### Nota (2026-11-09 21:26:56 UTC)

Medidas de flujo_ce4aba0f609f14b30.con_registros_aparte_lo_que_necesita_candidato_no_inventa_uno: factory_registros_raiz.con_registros_aparte_lo_que_necesita_candidato_no_inventa_uno, factory_registros_raiz.corrida_completa; propuestas por claude-code (agente, propuso, modo confirmacion). SIN MEDIR: sin límite adicional declarado. Revisión y juicio anteriores invalidados; no se declara cumplimiento ni aprobación de pertinencia.

### Nota (2026-11-09 21:31:52 UTC)

Medidas de flujo_ce4aba0f609f14b30.con_registros_aparte_el_repo_del_producto_queda_limpio: Brian Hollweg (persona, confirmo, modo confirmacion).

### Nota (2026-11-09 21:31:52 UTC)

Medidas de flujo_ce4aba0f609f14b30.con_registros_aparte_lo_que_necesita_candidato_no_inventa_uno: Brian Hollweg (persona, confirmo, modo confirmacion).

### Nota (2026-11-09 21:31:52 UTC)

Medidas de flujo_ce4aba0f609f14b30.sin_registros_aparte_nada_cambia: Brian Hollweg (persona, confirmo, modo confirmacion).

### Nota (2026-11-09 23:09:56 UTC)

Revisión guiada Brian Hollweg: aprobar; registrada por Brian Hollweg (persona, confirmo, modo confirmacion; motivo: Propuesta del agente claude-code. Etapa 1 de 6 de «registros fuera del repo del producto». Candidato 19e963a (camino completo: toca cli.py): evidencia verde (1354 pruebas, 6 casos de contrato). QUIÉN LO HIZO: lo construyó un agente lanzado por el conductor (autopilot --ejecutar --lanzar con claude -p y permisos acotados: leer/editar/escribir, oracle-factory, .venv/bin/python, git status/diff/log/show/add/commit; sin push, checkout, reset, config ni red) en dos pasos: 1) pruebas, catálogos y propuesta de medidas (te frenó en medir --confirmar); 2) implementación y evidencia (se frenó por el freno de pruebas editadas). Yo escribí la spec, hice las mutaciones, pedí las revisiones y arreglé los hallazgos. IDEA: ROOT sigue significando «dónde están los registros» (así sus ~220 usos no cambian) y una variable nueva PRODUCTO guarda la raíz del producto sólo con --registros distinto; main la fija y la suelta; CON_CANDIDATO rechaza pedir-revision, revision-preparar, revision, revisar, juzgar y cerrar (etapa 3); verificar_en_proceso y ofrecer_siguiente pasan ambas raíces. PRUEBA EXISTENTE EDITADA (declarada, motivo del freno): tests/datos/ayuda-cli.json se regeneró porque se agregó la opción --registros (es un archivo de datos con la ayuda del CLI; el diff es sólo esa opción); ninguna prueba existente se quitó ni aflojó. REVISIÓN: sólo codex (3 rondas): RRAIZ-1 (medio: un almacén dentro del producto, o al revés, ensuciaba el repo del producto; corregido con un rechazo en main por is_relative_to y pruebas con tres rutas y un hermano de prefijo igual) y RRAIZ-2 (medio: un enlace simbólico dentro del almacén haría escribir en el producto) que NO SE REPRODUCE: probé enlaces en catalogos, requisitos, macros, corpus, diferencial, relaciones, oracle.json, tareas, openspec, .factory, .gitignore y kb, antes y después de init, y el producto nunca cambió (ruta_segura y la validación de .factory ya lo bloquean); propongo DESCARTARLO con ese motivo y lo dejé fijado con pruebas; la ronda 3 no trajo hallazgos. DECIDE BRIAN: (1) este es un cambio de camino completo con un solo proveedor revisor (agy y agy2 siguen sin cuota hasta cerca del 2026-11-15); la etapa 1 es chica y de bajo riesgo (la opción es experimental y nadie la usa hasta la etapa 2), pero lo digo. (2) 15 mutaciones propias reales detectadas; equivalentes declaradas: la asignación de tupla PRODUCTO, ROOT = ROOT, registros evaluada en otro orden es idéntica, y el reinicio de PRODUCTO al principio de main es redundante con el finally (el finally sí está probado). LÍMITES para las etapas siguientes: las llamadas a git siguen con cwd=ROOT, o sea en el almacén, y la etapa 3 tiene que apuntarlas al producto; REGISTROS es un alias de ROOT. No edité ninguna otra prueba existente.); 0 abiertos derivados; commit 410b673bc823a19a271325f90a4f8fd1fd3c3534; informe tareas/20261109-212224-xo0-registros-raiz/revisiones/registro-2slk0e9f/informe.json; decisiones tareas/20261109-212224-xo0-registros-raiz/revisiones/registro-2slk0e9f/decisiones.json.

### Nota (2026-11-09 23:10:04 UTC)

Juicio Factory: verde; salida Oracle 0; informe .factory/cambios/20261109-212224-xo0-registros-raiz/oracle-veredicto.txt.

### Nota (2026-11-09 23:12:23 UTC)

Cierre: Brian Hollweg (persona, decidio, modo confirmacion), tras revisar el informe de código y el veredicto Oracle.
