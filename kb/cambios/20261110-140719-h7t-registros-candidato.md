---
generado: oracle-factory kb
id: "20261110-140719-h7t-registros-candidato"
fase: "oracle_verde"
capacidad: "flujo"
---

# Registros fuera del repo del producto, etapa 3: el candidato y la huella con dos fuentes

> Generado por `oracle-factory kb` desde el registro de Factory: no se edita a mano.

- Fase: oracle_verde
- Capacidad: flujo
- Responsable: nadie
- Spec: [openspec/changes/20261110-140719-h7t-registros-candidato/specs/flujo/spec.md](../../openspec/changes/20261110-140719-h7t-registros-candidato/specs/flujo/spec.md)

## Requisitos

- [[requisitos/flujo_c47a7d33c8e5ed925.con_almacen_aparte_el_candidato_es_el_ancestro_con_evidencia]] — cumple
- [[requisitos/flujo_c47a7d33c8e5ed925.con_almacen_aparte_el_ciclo_completo_funciona_sin_tocar_el_producto]] — cumple
- [[requisitos/flujo_c47a7d33c8e5ed925.con_almacen_aparte_la_huella_es_el_producto_y_este_cambio]] — cumple
- [[requisitos/flujo_c47a7d33c8e5ed925.con_almacen_aparte_no_hay_hook_en_el_producto]] — cumple

## Decisiones

- 2026-11-10 14:07 · Cambio creado · claude-code (agente)
- 2026-11-10 14:08 · Spec aprobada · Brian Hollweg (persona)
- 2026-11-10 14:08 · Requisitos importados · claude-code (agente)
- 2026-11-10 14:52 · Medidas confirmadas · Brian Hollweg (persona)
- 2026-11-10 14:52 · Medidas confirmadas · Brian Hollweg (persona)
- 2026-11-10 14:52 · Medidas confirmadas · Brian Hollweg (persona)
- 2026-11-10 14:52 · Medidas confirmadas · Brian Hollweg (persona)
- 2026-11-10 19:33 · Revisión registrada · Brian Hollweg (persona) — aprobar: Propuesta del agente claude-code. Etapa 3 de 6 de «registros fuera del repo del producto»: el candidato y la huella con dos fuentes. Candidato 49e4233 (camino completo): evidencia verde (1396 pruebas, 12 casos de contrato). QUIÉN LO HIZO: un agente lanzado por el conductor, por primera vez con el entorno filtrado y Python acotado (sólo -m unittest y tools/verificar\_cambio.py): escribió las 12 pruebas, implementó (cli.git\_producto con GIT\_OPTIONAL\_LOCKS=0; candidato vigente sobre la historia del producto; huella = producto + propuesta, spec, requisitos y catálogos de ESTE cambio vía almacenes.con\_el\_cambio; la base vacía se crea en el clon del revisor; hooks se niega con almacén) y produjo una primera evidencia que falló. Yo arreglé lo que faltaba, hice las mutaciones, pedí las revisiones y corregí el hallazgo. FALLAS EN EL CAMINO: (1) una prueba nueva del agente esperaba que la trazabilidad listara una prueba que sólo pierde una línea; el código hace bien en no listarla: corregí la expectativa. (2) errores de test\_guided en la primera evidencia que no se reproducen ni aislados ni en la suite completa: probablemente el agente editó archivos mientras su suite corría. (3) cli.py pasó su tope de 160000 bytes con mi arreglo: acorté comentarios, quedó en 159984 (16 bytes de margen: el próximo cambio que lo toque tiene que partirlo). PRUEBA EXISTENTE EDITADA (declarada, motivo del freno): tests/test\_registros\_raiz.py, test\_rr3: probaba que con registros aparte esos comandos se negaban con «etapa 3 de 6», y esta etapa es justamente la que los habilita; ahora prueba que sin candidato fallan sin escribir nada ni tocar el producto (el porqué está en un comentario dentro de la prueba). REVISIÓN: sólo codex (2 rondas): RCAND-1 (medio: con almacén aparte una carpeta de candidato sin evidencia contaba como candidato) corregido: sólo cuenta la carpeta con evidencia/ que no sea enlace; ronda 2 sin hallazgos. MUTACIONES: 25 sobre el código del agente más 3 sobre la corrección; reales detectadas con casos nuevos (próximo paso con la huella del cambio, base vacía, vueltas anteriores); equivalentes declaradas: exclusiones del paquete con almacén (no hay registros en el diff del producto), GIT\_OPTIONAL\_LOCKS (hoy no se corre status sobre el producto: defensa), la base vacía creada en el almacén (el clon la vuelve a crear y el producto no se toca), procedencia con --python explícito. DECIDE BRIAN: (1) camino completo con un solo proveedor revisor (agy sin cuota hasta cerca del 2026-11-15). (2) LÍMITES SIN PRUEBA: procedencia sobre un producto con uv.lock; la cabeza del paquete cuando no hay candidato; sin almacén aparte, el mismo hueco de RCAND-1 sigue (una carpeta de candidato sin evidencia cuenta): no lo toqué porque la spec pide no cambiar ese modo; queda para otro cambio. (3) cli.py está al límite de tamaño. No edité otra prueba existente.
- 2026-11-10 19:33 · Juicio de Oracle · claude-code (agente)

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
- `87d528a` registros-candidato: propuesta de revisión (trailer)
- Todos, también los que se deducen al integrarlo o los posteriores a la última decisión: `oracle-factory log 20261110-140719-h7t-registros-candidato`.

## Mensajes

- 2026-11-10 14:08 · claude-code: autopilot delegar\_al\_agente: elegir medidas es trabajo del agente; confirmarlas es de una persona. Instrucción: construí primero lo que falte: las pruebas de cada escenario (antes que el código) y los catálogos de medidas de los requisitos, sin correr todavía la evidencia completa; después elegí las medidas de cada requisito (oracle-factory medir ... --requisito R --medida M) y proponelas; confirmarlas es de una persona, y la evidencia se hace después de su confirmación
- 2026-11-10 14:15 · claude-code: autopilot se detuvo: confirmar las medidas es sólo de una persona. Comando para una persona: oracle-factory medir 20261110-140719-h7t-registros-candidato --confirmar
- 2026-11-10 14:52 · claude-code: autopilot delegar\_al\_agente: no hay candidato vigente: antes de revisar hay que construir. Instrucción: construí el cambio según la spec aprobada: pruebas primero, evidencia y commit del candidato; después: oracle-factory pedir-revision 20261110-140719-h7t-registros-candidato --a agy
- 2026-11-10 15:43 · claude-code: autopilot se detuvo: el paso falló (código 1): Implementé el cambio y commiteé el producto y la evidencia, pero hay dos cosas abiertas: \*\*la evidencia salió con \`éxito: False\` y la revisión de agy no se hizo\*\* (se le acabó la cuota). \*\*Commits\*\*…
