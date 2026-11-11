# Registros fuera del repo del producto, etapa 4b2: conectar desde una URL y sincronizar el almacén entre personas

- ESTADO: CERRADA
- PRIORIDAD: 50
- ETIQUETAS: 

### Nota (2026-11-11 13:55:46 UTC)

OpenSpec: openspec/changes/20261111-135546-t8q-almacen-sincronizar. Modo de trabajo: confirmacion. Estado de factory: espera aceptación de proposal.md y spec.md.

### Nota (2026-11-11 13:57:24 UTC)

Brian Hollweg (persona, decidio, modo confirmacion) aceptó propuesta y spec openspec/changes/20261111-135546-t8q-almacen-sincronizar/specs/flujo/spec.md; se reiniciaron las validaciones dependientes.

### Nota (2026-11-11 13:57:47 UTC)

Requisitos importados: flujo_c5b6a893e70e9eba0.conectar_una_url_clona_el_almacen_en_una_carpeta_del_usuario (funcional), flujo_c5b6a893e70e9eba0.sincronizar_sube_solo_si_es_una_persona_y_no_deja_nada_a_medias (funcional), flujo_c5b6a893e70e9eba0.sincronizar_une_los_registros_de_todos_sin_escribir_configuracion (funcional). Los nuevos nacen SIN MEDIR; verificá cobertura antes del juicio.

### Nota (2026-11-11 14:52:57 UTC)

Medidas de flujo_c5b6a893e70e9eba0.conectar_una_url_clona_el_almacen_en_una_carpeta_del_usuario: factory_almacen_sincronizar.conectar_una_url_clona_el_almacen_en_una_carpeta_del_usuario, factory_almacen_sincronizar.corrida_completa; propuestas por claude-code (agente, propuso, modo confirmacion). SIN MEDIR: sin límite adicional declarado. Revisión y juicio anteriores invalidados; no se declara cumplimiento ni aprobación de pertinencia.

### Nota (2026-11-11 14:52:59 UTC)

Medidas de flujo_c5b6a893e70e9eba0.sincronizar_sube_solo_si_es_una_persona_y_no_deja_nada_a_medias: factory_almacen_sincronizar.sincronizar_sube_solo_si_es_una_persona_y_no_deja_nada_a_medias, factory_almacen_sincronizar.corrida_completa; propuestas por claude-code (agente, propuso, modo confirmacion). SIN MEDIR: sin límite adicional declarado. Revisión y juicio anteriores invalidados; no se declara cumplimiento ni aprobación de pertinencia.

### Nota (2026-11-11 14:53:02 UTC)

Medidas de flujo_c5b6a893e70e9eba0.sincronizar_une_los_registros_de_todos_sin_escribir_configuracion: factory_almacen_sincronizar.sincronizar_une_los_registros_de_todos_sin_escribir_configuracion, factory_almacen_sincronizar.corrida_completa; propuestas por claude-code (agente, propuso, modo confirmacion). SIN MEDIR: sin límite adicional declarado. Revisión y juicio anteriores invalidados; no se declara cumplimiento ni aprobación de pertinencia.

### Nota (2026-11-11 14:59:47 UTC)

Medidas de flujo_c5b6a893e70e9eba0.conectar_una_url_clona_el_almacen_en_una_carpeta_del_usuario: Brian Hollweg (persona, confirmo, modo confirmacion).

### Nota (2026-11-11 14:59:48 UTC)

Medidas de flujo_c5b6a893e70e9eba0.sincronizar_sube_solo_si_es_una_persona_y_no_deja_nada_a_medias: Brian Hollweg (persona, confirmo, modo confirmacion).

### Nota (2026-11-11 14:59:48 UTC)

Medidas de flujo_c5b6a893e70e9eba0.sincronizar_une_los_registros_de_todos_sin_escribir_configuracion: Brian Hollweg (persona, confirmo, modo confirmacion).

### Nota (2026-11-11 15:50:08 UTC)

Revisión guiada Brian Hollweg: aprobar; registrada por Brian Hollweg (persona, confirmo, modo confirmacion; motivo: Propuesta del agente claude-code. Etapa 4b2 de «registros fuera del repo del producto»: conectar desde una URL y sincronizar el almacén entre personas. Candidato 1a1c920 (camino completo): evidencia verde (1430 pruebas, 14 casos de contrato). QUIÉN LO HIZO: el agente lanzado escribió las pruebas (se quedó sin cuota a los 3 minutos y dejó un error en su setUp, que corregí) y después implementó (almacenes.es_url, clonar en un temporal que se renombra, sincronizar bajo el bloqueo de la 4b1 con los drivers de unión pasados con git -c, rehacer lo generado, merge --abort y reset --hard al punto de partida si algo falla, push sólo si es una persona). Yo regeneré la ayuda del CLI, documenté conectar URL y sincronizar en docs/estructura.md (dos pruebas existentes lo exigían y la primera evidencia falló por eso), hice las mutaciones (21 sobre el código del agente, reales detectadas; equivalentes declaradas: merge --abort redundante con reset --hard, y la lista de archivos que chocaron, que igual nombra la salida de git merge; un error de mi script mutaba el bloqueo de la 4b1 en vez del de sincronizar: lo corregí) y corregí el hallazgo. REVISIÓN: sólo codex, 2 rondas: codex-01 (ALTO, real): un archivo local ignorado o sin versionar que el remoto agrega versionado se perdía porque Git lo pisa sin avisar: ahora no se une, se nombra y el almacén queda como estaba; codex-02 (medio): la subida fuera del bloqueo era un FALSO POSITIVO (el push está dentro del with): propongo DESCARTARLO; quedó fijado con una prueba que intenta tomar el bloqueo durante el push y no puede; ronda 2 sin hallazgos. PRUEBA EXISTENTE EDITADA (declarada, motivo del freno): tests/datos/ayuda-cli.json regenerado por el subcomando sincronizar y la ayuda nueva de conectar. DECIDE BRIAN: (1) camino completo con un solo proveedor revisor (agy sin cuota). (2) sincronizar no escribe configuración de Git en ningún repo; el .gitattributes del almacén sí lo escribe y commitea (es contenido versionado). (3) Con --agente, sincronizar trae y une pero no sube; el conductor lo puede correr como paso mecánico.); 0 abiertos derivados; commit 1cdd575800956974f5abb089296afdf454639f39; informe tareas/20261111-135546-t8q-almacen-sincronizar/revisiones/registro-zo3iuahp/informe.json; decisiones tareas/20261111-135546-t8q-almacen-sincronizar/revisiones/registro-zo3iuahp/decisiones.json.

### Nota (2026-11-11 15:50:25 UTC)

Juicio Factory: verde; salida Oracle 0; informe .factory/cambios/20261111-135546-t8q-almacen-sincronizar/oracle-veredicto.txt.

### Nota (2026-11-11 15:50:40 UTC)

Cierre: Brian Hollweg (persona, decidio, modo confirmacion), tras revisar el informe de código y el veredicto Oracle.
