---
generado: oracle-factory kb
id: "20261103-113909-oen-contratojson"
fase: "cerrada"
capacidad: "ide"
---

# Pruebas de contrato entre la CLI y la extensión de VS Code

> Generado por `oracle-factory kb` desde el registro de Factory: no se edita a mano.

- Fase: cerrada
- Capacidad: ide
- Responsable: nadie
- Spec: [openspec/changes/20261103-113909-oen-contratojson/specs/ide/spec.md](../../openspec/changes/20261103-113909-oen-contratojson/specs/ide/spec.md)

## Requisitos

- [[requisitos/ide_cc0ded3b7b46b23f7.el_documento_explica_como_actualizar_el_contrato]] — cumple
- [[requisitos/ide_cc0ded3b7b46b23f7.la_cli_entrega_cada_clave_declarada_con_un_tipo_permitido]] — cumple
- [[requisitos/ide_cc0ded3b7b46b23f7.la_extension_solo_lee_de_los_json_de_la_cli_lo_que_el_contrato_declara]] — cumple

## Decisiones

- 2026-11-03 11:39 · Cambio creado · claude-code (agente)
- 2026-11-03 11:56 · Spec aprobada · Brian Hollweg (persona)
- 2026-11-03 11:56 · Requisitos importados · claude-code (agente)
- 2026-11-03 12:02 · Medidas confirmadas · Brian Hollweg (persona)
- 2026-11-03 12:02 · Medidas confirmadas · Brian Hollweg (persona)
- 2026-11-03 12:02 · Medidas confirmadas · Brian Hollweg (persona)
- 2026-11-03 12:35 · Medidas confirmadas · Brian Hollweg (persona)
- 2026-11-03 12:35 · Medidas confirmadas · Brian Hollweg (persona)
- 2026-11-03 12:35 · Medidas confirmadas · Brian Hollweg (persona)
- 2026-11-03 14:58 · Medidas confirmadas · Brian Hollweg (persona)
- 2026-11-03 14:58 · Medidas confirmadas · Brian Hollweg (persona)
- 2026-11-03 14:58 · Medidas confirmadas · Brian Hollweg (persona)
- 2026-11-03 15:46 · Medidas confirmadas · Brian Hollweg (persona)
- 2026-11-03 15:46 · Medidas confirmadas · Brian Hollweg (persona)
- 2026-11-03 15:46 · Medidas confirmadas · Brian Hollweg (persona)
- 2026-11-03 16:20 · Revisión registrada · Brian Hollweg (persona) — aprobar: Cuatro rondas con revisores independientes (agy2-flash y codex), la última con 0 y 0 sobre el candidato 0a8e4fd. Hallazgos por ronda, sumando los dos revisores: 14, 10, 1 y 0. La mayoría de las rondas 1 y 2 fueron de cobertura del contrato (el primer contrato salió sólo de lo que los estados de prueba hacían leer a la extensión): se enriquecieron los estados (cerrado con revisión, abierto con candidato y hallazgos de dos revisores, con propuesta de un agente, sin avanzar, con responsable y mensajes, abandonado), se completó el contrato con tipos tomados del código de la CLI y una nota donde son más anchos de lo observado, se agregó una revisión estática del texto de modelo.js y tablero.js por archivo y por comando (con accesos encadenados y nombres de archivo con o sin carpetas), el registrador intercepta in y lee varias instantáneas, y esperando y sesion se tratan como cosas de la extensión. Evidencia con éxito, producida por tools/verificar\_cambio.py: 1082 pruebas y 20 casos de contrato. En cada ronda se corrió una tanda de mutaciones sobre los arreglos; los sobrevivientes se cerraron con pruebas o se simplificó el código si eran equivalentes. Límite declarado en docs/tablero.md: la revisión estática compara por nombre, no por ruta, así que una clave con un nombre ya declarado bajo otro padre puede pasar sin que su ruta esté declarada.
- 2026-11-03 16:21 · Juicio de Oracle · claude-code (agente)
- 2026-11-03 16:25 · Cerrado · Brian Hollweg (persona)
- 2026-11-03 16:25 · Archivado · Brian Hollweg (persona)

## Riesgos aceptados

- Ninguno.

## Commits

- `ab51e23` contrato-json: propuesta, diseño y spec (trailer)
- `e59b707` contrato-json: aprobación de la spec e importación de requisitos (trailer)
- `3f0f9ae` contrato-json: contrato, registrador en node, comprobaciones, pruebas, documento y catálogos (trailer)
- `512202e` contrato-json: proponer las medidas (trailer)
- `eea6c47` contrato-json: registrar la confirmación de medidas por Brian (trailer)
- `7850cc0` contrato-json: estados más ricos, contrato completo con notas, revisión estática del código, trampa has, documento (hallazgos de la ronda 1) (trailer)
- `07a7aac` contrato-json: proponer de nuevo las medidas (trailer)
- `58363a1` contrato-json: registrar la confirmación de medidas por Brian (trailer)
- `e3ca20e` contrato-json: contrato completo por ruta, revisión estática por archivo y por comando, accesos encadenados (hallazgos de la ronda 2) (trailer)
- `49f728d` contrato-json: proponer de nuevo las medidas (trailer)
- `fb5bdf2` contrato-json: registrar la confirmación de medidas por Brian (trailer)
- `7d20747` contrato-json: el archivo se identifica por su nombre y uno desconocido falla (hallazgo de la ronda 3) (trailer)
- `67405cd` contrato-json: proponer de nuevo las medidas (trailer)
- `0a8e4fd` contrato-json: registrar la confirmación de medidas por Brian (trailer)
- `bd90ed8` contrato-json: registrar la cuarta ronda de revisiones y la evidencia (trailer)
- `c21f250` contrato-json: proponer la aprobación de la revisión (trailer)
- `b1bfe34` contrato-json: proponer la aprobación de la revisión (motivo corregido) (trailer)
- `d17b6ee` contrato-json: registrar la revisión aprobada por Brian (trailer)
- `7e41e3f` contrato-json: veredicto de Oracle (trailer)
- Todos, también los que se deducen al integrarlo o los posteriores a la última decisión: `oracle-factory log 20261103-113909-oen-contratojson`.

## Mensajes

- Ninguno.
