---
generado: oracle-factory kb
id: "20261111-135546-t8q-almacen-sincronizar"
fase: "cerrada"
capacidad: "flujo"
---

# Registros fuera del repo del producto, etapa 4b2: conectar desde una URL y sincronizar el almacén entre personas

> Generado por `oracle-factory kb` desde el registro de Factory: no se edita a mano.

- Fase: cerrada
- Capacidad: flujo
- Responsable: nadie
- Spec: [openspec/changes/20261111-135546-t8q-almacen-sincronizar/specs/flujo/spec.md](../../openspec/changes/20261111-135546-t8q-almacen-sincronizar/specs/flujo/spec.md)

## Requisitos

- [[requisitos/flujo_c5b6a893e70e9eba0.conectar_una_url_clona_el_almacen_en_una_carpeta_del_usuario]] — cumple
- [[requisitos/flujo_c5b6a893e70e9eba0.sincronizar_sube_solo_si_es_una_persona_y_no_deja_nada_a_medias]] — cumple
- [[requisitos/flujo_c5b6a893e70e9eba0.sincronizar_une_los_registros_de_todos_sin_escribir_configuracion]] — cumple

## Decisiones

- 2026-11-11 13:55 · Cambio creado · claude-code (agente)
- 2026-11-11 13:57 · Spec aprobada · Brian Hollweg (persona)
- 2026-11-11 13:57 · Requisitos importados · claude-code (agente)
- 2026-11-11 14:59 · Medidas confirmadas · Brian Hollweg (persona)
- 2026-11-11 14:59 · Medidas confirmadas · Brian Hollweg (persona)
- 2026-11-11 14:59 · Medidas confirmadas · Brian Hollweg (persona)
- 2026-11-11 15:50 · Revisión registrada · Brian Hollweg (persona) — aprobar: Propuesta del agente claude-code. Etapa 4b2 de «registros fuera del repo del producto»: conectar desde una URL y sincronizar el almacén entre personas. Candidato 1a1c920 (camino completo): evidencia verde (1430 pruebas, 14 casos de contrato). QUIÉN LO HIZO: el agente lanzado escribió las pruebas (se quedó sin cuota a los 3 minutos y dejó un error en su setUp, que corregí) y después implementó (almacenes.es\_url, clonar en un temporal que se renombra, sincronizar bajo el bloqueo de la 4b1 con los drivers de unión pasados con git -c, rehacer lo generado, merge --abort y reset --hard al punto de partida si algo falla, push sólo si es una persona). Yo regeneré la ayuda del CLI, documenté conectar URL y sincronizar en docs/estructura.md (dos pruebas existentes lo exigían y la primera evidencia falló por eso), hice las mutaciones (21 sobre el código del agente, reales detectadas; equivalentes declaradas: merge --abort redundante con reset --hard, y la lista de archivos que chocaron, que igual nombra la salida de git merge; un error de mi script mutaba el bloqueo de la 4b1 en vez del de sincronizar: lo corregí) y corregí el hallazgo. REVISIÓN: sólo codex, 2 rondas: codex-01 (ALTO, real): un archivo local ignorado o sin versionar que el remoto agrega versionado se perdía porque Git lo pisa sin avisar: ahora no se une, se nombra y el almacén queda como estaba; codex-02 (medio): la subida fuera del bloqueo era un FALSO POSITIVO (el push está dentro del with): propongo DESCARTARLO; quedó fijado con una prueba que intenta tomar el bloqueo durante el push y no puede; ronda 2 sin hallazgos. PRUEBA EXISTENTE EDITADA (declarada, motivo del freno): tests/datos/ayuda-cli.json regenerado por el subcomando sincronizar y la ayuda nueva de conectar. DECIDE BRIAN: (1) camino completo con un solo proveedor revisor (agy sin cuota). (2) sincronizar no escribe configuración de Git en ningún repo; el .gitattributes del almacén sí lo escribe y commitea (es contenido versionado). (3) Con --agente, sincronizar trae y une pero no sube; el conductor lo puede correr como paso mecánico.
- 2026-11-11 15:50 · Juicio de Oracle · claude-code (agente)
- 2026-11-11 15:50 · Cerrado · Brian Hollweg (persona)
- 2026-11-11 15:50 · Archivado · Brian Hollweg (persona)

## Riesgos aceptados

- Ninguno.

## Commits

- `d5468da` almacen-sincronizar: propuesta y spec (etapa 4b2) (trailer)
- `397687f` almacen-sincronizar: spec aprobada por Brian (trailer)
- `808e7ba` almacen-sincronizar: requisitos importados (trailer)
- `e76535d` almacen-sincronizar: pruebas de los escenarios (del agente, completadas: el setUp usaba un nombre que el módulo borra al final), catálogos y propuesta de medidas (trailer)
- `0e8166c` almacen-sincronizar: medidas confirmadas por Brian (trailer)
- `e750cae` almacen-sincronizar: conectar URL clona el almacén y sincronizar lo une con el remoto (trailer)
- `afa8956` almacen-sincronizar: ayuda del CLI regenerada (subcomando sincronizar y conectar URL) (trailer)
- `a9b2605` almacen-sincronizar: casos de las mutaciones propias (qué es una URL, producto sin almacén, remoto vacío, el conductor) (trailer)
- `6d1aaf1` almacen-sincronizar: evidencia del candidato (trailer)
- `3e8cf90` almacen-sincronizar: docs/estructura.md explica conectar URL y sincronizar (trailer)
- `1704447` almacen-sincronizar: evidencia del candidato (trailer)
- `1a1c920` almacen-sincronizar: no une si lo que trae el remoto pisaría un archivo local ignorado o sin versionar (hallazgo codex-01); prueba de que el push corre con el bloqueo tomado (codex-02, falso positivo) (trailer)
- `50b3444` almacen-sincronizar: evidencia del candidato tras codex-01 (trailer)
- `493bf6a` almacen-sincronizar: informe de codex (ronda 2, sin hallazgos) (trailer)
- `1cdd575` almacen-sincronizar: propuesta de revisión (trailer)
- `9321f66` almacen-sincronizar: revisión aprobada por Brian y veredicto de Oracle (trailer)
- Todos, también los que se deducen al integrarlo o los posteriores a la última decisión: `oracle-factory log 20261111-135546-t8q-almacen-sincronizar`.

## Mensajes

- 2026-11-11 13:57 · claude-code: autopilot delegar\_al\_agente: elegir medidas es trabajo del agente; confirmarlas es de una persona. Instrucción: construí primero lo que falte: las pruebas de cada escenario (antes que el código) y los catálogos de medidas de los requisitos, sin correr todavía la evidencia completa; después elegí las medidas de cada requisito (oracle-factory medir ... --requisito R --medida M) y proponelas; confirmarlas es de una persona, y la evidencia se hace después de su confirmación
- 2026-11-11 14:01 · claude-code: autopilot se detuvo: el paso falló (código 1): You've hit your 5-hour limit · resets 11:50am (America/Argentina/Salta)
- 2026-11-11 15:00 · claude-code: autopilot delegar\_al\_agente: no hay candidato vigente: antes de revisar hay que construir. Instrucción: construí el cambio según la spec aprobada: pruebas primero, evidencia y commit del candidato; después: oracle-factory pedir-revision 20261111-135546-t8q-almacen-sincronizar --a agy
- 2026-11-11 15:06 · claude-code: autopilot se detuvo: se llegó al tope de 1 pasos
