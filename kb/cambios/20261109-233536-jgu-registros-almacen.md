---
generado: oracle-factory kb
id: "20261109-233536-jgu-registros-almacen"
fase: "requisitos_importados"
capacidad: "flujo"
---

# Registros fuera del repo del producto, etapa 2: el almacén y conectar

> Generado por `oracle-factory kb` desde el registro de Factory: no se edita a mano.

- Fase: requisitos_importados
- Capacidad: flujo
- Responsable: nadie
- Spec: [openspec/changes/20261109-233536-jgu-registros-almacen/specs/flujo/spec.md](../../openspec/changes/20261109-233536-jgu-registros-almacen/specs/flujo/spec.md)

## Requisitos

- [[requisitos/flujo_c92ca9731e38f72e0.con_el_producto_conectado_los_comandos_usan_el_almacen]] — sin juicio
- [[requisitos/flujo_c92ca9731e38f72e0.conectar_guarda_el_almacen_por_usuario_sin_tocar_el_producto]] — sin juicio
- [[requisitos/flujo_c92ca9731e38f72e0.conectar_sin_argumentos_y_desconectar]] — sin juicio
- [[requisitos/flujo_c92ca9731e38f72e0.un_producto_con_su_propio_factory_conectado_se_niega]] — sin juicio

## Decisiones

- 2026-11-09 23:35 · Cambio creado · claude-code (agente)
- 2026-11-09 23:36 · Spec aprobada · Brian Hollweg (persona)
- 2026-11-09 23:36 · Requisitos importados · claude-code (agente)
- 2026-11-09 23:41 · Medidas confirmadas · Brian Hollweg (persona)
- 2026-11-09 23:41 · Medidas confirmadas · Brian Hollweg (persona)
- 2026-11-09 23:41 · Medidas confirmadas · Brian Hollweg (persona)
- 2026-11-09 23:41 · Medidas confirmadas · Brian Hollweg (persona)

## Riesgos aceptados

- Ninguno.

## Commits

- `081f98f` registros-almacen: propuesta y spec (etapa 2 de 6) (trailer)
- `12a44ad` registros-almacen: spec aprobada por Brian (trailer)
- `5ee2f59` registros-almacen: pruebas, catálogos y propuesta de medidas (trailer)
- `6b2ddb6` registros-almacen: medidas confirmadas por Brian (trailer)
- Todos, también los que se deducen al integrarlo o los posteriores a la última decisión: `oracle-factory log 20261109-233536-jgu-registros-almacen`.

## Mensajes

- 2026-11-09 23:37 · claude-code: autopilot delegar\_al\_agente: elegir medidas es trabajo del agente; confirmarlas es de una persona. Instrucción: construí primero lo que falte: las pruebas de cada escenario (antes que el código) y los catálogos de medidas de los requisitos, sin correr todavía la evidencia completa; después elegí las medidas de cada requisito (oracle-factory medir ... --requisito R --medida M) y proponelas; confirmarlas es de una persona, y la evidencia se hace después de su confirmación
- 2026-11-09 23:39 · claude-code: autopilot se detuvo: confirmar las medidas es sólo de una persona. Comando para una persona: oracle-factory medir 20261109-233536-jgu-registros-almacen --confirmar
- 2026-11-09 23:49 · claude-code: autopilot delegar\_al\_agente: no hay candidato vigente: antes de revisar hay que construir. Instrucción: construí el cambio según la spec aprobada: pruebas primero, evidencia y commit del candidato; después: oracle-factory pedir-revision 20261109-233536-jgu-registros-almacen --a agy
