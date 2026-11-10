---
generado: oracle-factory kb
id: "20261110-140719-h7t-registros-candidato"
fase: "requisitos_importados"
capacidad: "flujo"
---

# Registros fuera del repo del producto, etapa 3: el candidato y la huella con dos fuentes

> Generado por `oracle-factory kb` desde el registro de Factory: no se edita a mano.

- Fase: requisitos_importados
- Capacidad: flujo
- Responsable: nadie
- Spec: [openspec/changes/20261110-140719-h7t-registros-candidato/specs/flujo/spec.md](../../openspec/changes/20261110-140719-h7t-registros-candidato/specs/flujo/spec.md)

## Requisitos

- [[requisitos/flujo_c47a7d33c8e5ed925.con_almacen_aparte_el_candidato_es_el_ancestro_con_evidencia]] — sin juicio
- [[requisitos/flujo_c47a7d33c8e5ed925.con_almacen_aparte_el_ciclo_completo_funciona_sin_tocar_el_producto]] — sin juicio
- [[requisitos/flujo_c47a7d33c8e5ed925.con_almacen_aparte_la_huella_es_el_producto_y_este_cambio]] — sin juicio
- [[requisitos/flujo_c47a7d33c8e5ed925.con_almacen_aparte_no_hay_hook_en_el_producto]] — sin juicio

## Decisiones

- 2026-11-10 14:07 · Cambio creado · claude-code (agente)
- 2026-11-10 14:08 · Spec aprobada · Brian Hollweg (persona)
- 2026-11-10 14:08 · Requisitos importados · claude-code (agente)
- 2026-11-10 14:52 · Medidas confirmadas · Brian Hollweg (persona)
- 2026-11-10 14:52 · Medidas confirmadas · Brian Hollweg (persona)
- 2026-11-10 14:52 · Medidas confirmadas · Brian Hollweg (persona)
- 2026-11-10 14:52 · Medidas confirmadas · Brian Hollweg (persona)

## Riesgos aceptados

- Ninguno.

## Commits

- `be185e6` registros-candidato: propuesta y spec (etapa 3 de 6) (trailer)
- `e05007e` registros-candidato: spec aprobada por Brian (trailer)
- `a19f159` registros-candidato: pruebas rc1-rc4, catálogos y propuesta de medidas (trailer)
- `7ec1a31` registros-candidato: medidas confirmadas por Brian (trailer)
- `82f9fb9` registros-candidato: el candidato y la huella con dos fuentes (etapa 3 de 6) (trailer)
- `cde755d` registros-candidato: evidencia del candidato 82f9fb9 (trailer)
- `d21a4ee` registros-candidato: la trazabilidad no lista una prueba que sólo pierde una línea (expectativa corregida) (trailer)
- `4cef61f` registros-candidato: casos de las mutaciones propias (próximo paso con la huella del cambio, base vacía, vueltas anteriores) (trailer)
- `76ca0a1` registros-candidato: evidencia del candidato (trailer)
- `e682db5` registros-candidato: con almacén aparte sólo es candidato la carpeta con su evidencia (hallazgo RCAND-1 de codex) (trailer)
- `ddce6d2` registros-candidato: evidencia del candidato tras RCAND-1 (trailer)
- `49e4233` registros-candidato: cli.py vuelve bajo su tope de tamaño (comentarios más cortos) (trailer)
- `84bfe8a` registros-candidato: evidencia del candidato tras el tope de cli.py (trailer)
- `7ae8b1a` registros-candidato: informe de codex (ronda 2, sin hallazgos) (trailer)
- Todos, también los que se deducen al integrarlo o los posteriores a la última decisión: `oracle-factory log 20261110-140719-h7t-registros-candidato`.

## Mensajes

- 2026-11-10 14:08 · claude-code: autopilot delegar\_al\_agente: elegir medidas es trabajo del agente; confirmarlas es de una persona. Instrucción: construí primero lo que falte: las pruebas de cada escenario (antes que el código) y los catálogos de medidas de los requisitos, sin correr todavía la evidencia completa; después elegí las medidas de cada requisito (oracle-factory medir ... --requisito R --medida M) y proponelas; confirmarlas es de una persona, y la evidencia se hace después de su confirmación
- 2026-11-10 14:15 · claude-code: autopilot se detuvo: confirmar las medidas es sólo de una persona. Comando para una persona: oracle-factory medir 20261110-140719-h7t-registros-candidato --confirmar
- 2026-11-10 14:52 · claude-code: autopilot delegar\_al\_agente: no hay candidato vigente: antes de revisar hay que construir. Instrucción: construí el cambio según la spec aprobada: pruebas primero, evidencia y commit del candidato; después: oracle-factory pedir-revision 20261110-140719-h7t-registros-candidato --a agy
- 2026-11-10 15:43 · claude-code: autopilot se detuvo: el paso falló (código 1): Implementé el cambio y commiteé el producto y la evidencia, pero hay dos cosas abiertas: \*\*la evidencia salió con \`éxito: False\` y la revisión de agy no se hizo\*\* (se le acabó la cuota). \*\*Commits\*\*…
