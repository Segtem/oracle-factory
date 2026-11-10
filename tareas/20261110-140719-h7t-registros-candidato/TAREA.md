# Registros fuera del repo del producto, etapa 3: el candidato y la huella con dos fuentes

- ESTADO: ABIERTA
- PRIORIDAD: 50
- ETIQUETAS: 

### Nota (2026-11-10 14:07:19 UTC)

OpenSpec: openspec/changes/20261110-140719-h7t-registros-candidato. Modo de trabajo: confirmacion. Estado de factory: espera aceptación de proposal.md y spec.md.

### Nota (2026-11-10 14:08:13 UTC)

Brian Hollweg (persona, decidio, modo confirmacion) aceptó propuesta y spec openspec/changes/20261110-140719-h7t-registros-candidato/specs/flujo/spec.md; se reiniciaron las validaciones dependientes.

### Nota (2026-11-10 14:08:24 UTC)

Requisitos importados: flujo_c47a7d33c8e5ed925.con_almacen_aparte_el_candidato_es_el_ancestro_con_evidencia (funcional), flujo_c47a7d33c8e5ed925.con_almacen_aparte_el_ciclo_completo_funciona_sin_tocar_el_producto (funcional), flujo_c47a7d33c8e5ed925.con_almacen_aparte_la_huella_es_el_producto_y_este_cambio (funcional), flujo_c47a7d33c8e5ed925.con_almacen_aparte_no_hay_hook_en_el_producto (funcional). Los nuevos nacen SIN MEDIR; verificá cobertura antes del juicio.

### Nota (2026-11-10 14:14:33 UTC)

Medidas de flujo_c47a7d33c8e5ed925.con_almacen_aparte_el_candidato_es_el_ancestro_con_evidencia: factory_registros_candidato.con_almacen_aparte_el_candidato_es_el_ancestro_con_evidencia, factory_registros_candidato.corrida_completa; propuestas por claude-code (agente, propuso, modo confirmacion). SIN MEDIR: sin límite adicional declarado. Revisión y juicio anteriores invalidados; no se declara cumplimiento ni aprobación de pertinencia.

### Nota (2026-11-10 14:14:35 UTC)

Medidas de flujo_c47a7d33c8e5ed925.con_almacen_aparte_la_huella_es_el_producto_y_este_cambio: factory_registros_candidato.con_almacen_aparte_la_huella_es_el_producto_y_este_cambio, factory_registros_candidato.corrida_completa; propuestas por claude-code (agente, propuso, modo confirmacion). SIN MEDIR: sin límite adicional declarado. Revisión y juicio anteriores invalidados; no se declara cumplimiento ni aprobación de pertinencia.

### Nota (2026-11-10 14:14:37 UTC)

Medidas de flujo_c47a7d33c8e5ed925.con_almacen_aparte_el_ciclo_completo_funciona_sin_tocar_el_producto: factory_registros_candidato.con_almacen_aparte_el_ciclo_completo_funciona_sin_tocar_el_producto, factory_registros_candidato.corrida_completa; propuestas por claude-code (agente, propuso, modo confirmacion). SIN MEDIR: sin límite adicional declarado. Revisión y juicio anteriores invalidados; no se declara cumplimiento ni aprobación de pertinencia.

### Nota (2026-11-10 14:14:39 UTC)

Medidas de flujo_c47a7d33c8e5ed925.con_almacen_aparte_no_hay_hook_en_el_producto: factory_registros_candidato.con_almacen_aparte_no_hay_hook_en_el_producto, factory_registros_candidato.corrida_completa; propuestas por claude-code (agente, propuso, modo confirmacion). SIN MEDIR: sin límite adicional declarado. Revisión y juicio anteriores invalidados; no se declara cumplimiento ni aprobación de pertinencia.

### Nota (2026-11-10 14:52:16 UTC)

Medidas de flujo_c47a7d33c8e5ed925.con_almacen_aparte_el_candidato_es_el_ancestro_con_evidencia: Brian Hollweg (persona, confirmo, modo confirmacion).

### Nota (2026-11-10 14:52:16 UTC)

Medidas de flujo_c47a7d33c8e5ed925.con_almacen_aparte_el_ciclo_completo_funciona_sin_tocar_el_producto: Brian Hollweg (persona, confirmo, modo confirmacion).

### Nota (2026-11-10 14:52:16 UTC)

Medidas de flujo_c47a7d33c8e5ed925.con_almacen_aparte_la_huella_es_el_producto_y_este_cambio: Brian Hollweg (persona, confirmo, modo confirmacion).

### Nota (2026-11-10 14:52:16 UTC)

Medidas de flujo_c47a7d33c8e5ed925.con_almacen_aparte_no_hay_hook_en_el_producto: Brian Hollweg (persona, confirmo, modo confirmacion).

### Nota (2026-11-10 19:33:18 UTC)

Revisión guiada Brian Hollweg: aprobar; registrada por Brian Hollweg (persona, confirmo, modo confirmacion; motivo: Propuesta del agente claude-code. Etapa 3 de 6 de «registros fuera del repo del producto»: el candidato y la huella con dos fuentes. Candidato 49e4233 (camino completo): evidencia verde (1396 pruebas, 12 casos de contrato). QUIÉN LO HIZO: un agente lanzado por el conductor, por primera vez con el entorno filtrado y Python acotado (sólo -m unittest y tools/verificar_cambio.py): escribió las 12 pruebas, implementó (cli.git_producto con GIT_OPTIONAL_LOCKS=0; candidato vigente sobre la historia del producto; huella = producto + propuesta, spec, requisitos y catálogos de ESTE cambio vía almacenes.con_el_cambio; la base vacía se crea en el clon del revisor; hooks se niega con almacén) y produjo una primera evidencia que falló. Yo arreglé lo que faltaba, hice las mutaciones, pedí las revisiones y corregí el hallazgo. FALLAS EN EL CAMINO: (1) una prueba nueva del agente esperaba que la trazabilidad listara una prueba que sólo pierde una línea; el código hace bien en no listarla: corregí la expectativa. (2) errores de test_guided en la primera evidencia que no se reproducen ni aislados ni en la suite completa: probablemente el agente editó archivos mientras su suite corría. (3) cli.py pasó su tope de 160000 bytes con mi arreglo: acorté comentarios, quedó en 159984 (16 bytes de margen: el próximo cambio que lo toque tiene que partirlo). PRUEBA EXISTENTE EDITADA (declarada, motivo del freno): tests/test_registros_raiz.py, test_rr3: probaba que con registros aparte esos comandos se negaban con «etapa 3 de 6», y esta etapa es justamente la que los habilita; ahora prueba que sin candidato fallan sin escribir nada ni tocar el producto (el porqué está en un comentario dentro de la prueba). REVISIÓN: sólo codex (2 rondas): RCAND-1 (medio: con almacén aparte una carpeta de candidato sin evidencia contaba como candidato) corregido: sólo cuenta la carpeta con evidencia/ que no sea enlace; ronda 2 sin hallazgos. MUTACIONES: 25 sobre el código del agente más 3 sobre la corrección; reales detectadas con casos nuevos (próximo paso con la huella del cambio, base vacía, vueltas anteriores); equivalentes declaradas: exclusiones del paquete con almacén (no hay registros en el diff del producto), GIT_OPTIONAL_LOCKS (hoy no se corre status sobre el producto: defensa), la base vacía creada en el almacén (el clon la vuelve a crear y el producto no se toca), procedencia con --python explícito. DECIDE BRIAN: (1) camino completo con un solo proveedor revisor (agy sin cuota hasta cerca del 2026-11-15). (2) LÍMITES SIN PRUEBA: procedencia sobre un producto con uv.lock; la cabeza del paquete cuando no hay candidato; sin almacén aparte, el mismo hueco de RCAND-1 sigue (una carpeta de candidato sin evidencia cuenta): no lo toqué porque la spec pide no cambiar ese modo; queda para otro cambio. (3) cli.py está al límite de tamaño. No edité otra prueba existente.); 0 abiertos derivados; commit 87d528a6a55bcfb9377297eacac8e41c46585a70; informe tareas/20261110-140719-h7t-registros-candidato/revisiones/registro-8dzzyxgy/informe.json; decisiones tareas/20261110-140719-h7t-registros-candidato/revisiones/registro-8dzzyxgy/decisiones.json.

### Nota (2026-11-10 19:33:44 UTC)

Juicio Factory: verde; salida Oracle 0; informe .factory/cambios/20261110-140719-h7t-registros-candidato/oracle-veredicto.txt.
