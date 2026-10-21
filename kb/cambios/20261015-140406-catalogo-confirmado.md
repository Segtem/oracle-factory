---
generado: oracle-factory kb
id: "20261015-140406-catalogo-confirmado"
fase: "cerrada"
capacidad: "modos"
---

# Una medida confirmada cuyo catálogo cambia vuelve a pedir decisión

> Generado por `oracle-factory kb` desde el registro de Factory: no se edita a mano.

- Fase: cerrada
- Capacidad: modos
- Responsable: nadie
- Spec: [openspec/changes/20261015-140406-catalogo-confirmado/specs/modos/spec.md](../../openspec/changes/20261015-140406-catalogo-confirmado/specs/modos/spec.md)

## Requisitos

- [[requisitos/modos_cfcd50c150324f5bc.una_decision_de_medidas_deja_de_valer_si_cambia_el_catalogo]] — cumple
- [[requisitos/modos_cfcd50c150324f5bc.una_propuesta_de_medidas_no_se_confirma_si_cambio_el_catalogo]] — cumple

## Decisiones

- 2026-10-15 14:04 · Cambio creado · claude-code (agente)
- 2026-10-15 14:13 · Spec aprobada · Brian Hollweg (persona)
- 2026-10-15 14:13 · Requisitos importados · claude-code (agente)
- 2026-10-15 14:23 · Medidas confirmadas · Brian Hollweg (persona)
- 2026-10-15 14:23 · Medidas confirmadas · Brian Hollweg (persona)
- 2026-10-15 14:50 · Medidas confirmadas · Brian Hollweg (persona)
- 2026-10-15 14:50 · Medidas confirmadas · Brian Hollweg (persona)
- 2026-10-15 15:40 · Revisión registrada · Brian Hollweg (persona) — aprobar: tres vueltas de codex y agy, a la vez. La 1: un alto (decidir con --requisito tras un catálogo cambiado figuraba como confirmación de la propuesta), cuatro medios y un bajo; todos corregidos con pruebas que fallan sin el arreglo. La 2: un medio (un archivo presente que Oracle no carga se informaba como ausente), corregido. La 3: agy nada, codex un bajo (el mismo caso para una medida del catálogo base). Las medidas de este cambio se reconfirmaron porque sus catálogos cambiaron: el propio cambio lo detectó. Suite 361 y evidencia en verde.
- 2026-10-15 15:41 · Juicio de Oracle · claude-code (agente)
- 2026-10-15 15:43 · Cerrado · Brian Hollweg (persona)
- 2026-10-15 15:43 · Archivado · Brian Hollweg (persona)

## Riesgos aceptados

- `oracle_factory/cli.py`: Una medida del catálogo base omitida por Oracle se informa como ausente — aceptado por Brian Hollweg: Acepto el riesgo: Una medida del catálogo base omitida por Oracle se informa como ausente

## Commits

- `0e22578` catalogo-confirmado: medidas confirmadas por Brian (deducido)
- `4e12cf2` catalogo-confirmado: medidas confirmadas de nuevo por Brian (deducido)
- `3f68c51` catalogo-confirmado: un archivo que sigue ahí pero Oracle no carga no se informa como ausente (codex CC2-001); anotación de tipo (agy) (deducido)
- Todos, también los que se deducen al integrarlo o los posteriores a la última decisión: `oracle-factory log 20261015-140406-catalogo-confirmado`.

## Mensajes

- Ninguno.
