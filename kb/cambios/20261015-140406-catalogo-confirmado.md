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

- `1c5881c` catalogo-confirmado: propuesta y spec (deducido)
- `0d6a482` catalogo-confirmado: spec aprobada por Brian (deducido)
- `9ba4359` catalogo-confirmado: la decisión y la propuesta de medidas guardan la huella del archivo de cada medida; si cambia, deja de valer (estado lo nombra, juzgar no la usa, --confirmar avisa); pruebas cc1–cc2, sensor y catálogos (deducido)
- `e7f5bd7` catalogo-confirmado: medidas propuestas por claude-code (deducido)
- `0e22578` catalogo-confirmado: medidas confirmadas por Brian (deducido)
- `a19bb1c` catalogo-confirmado: evidencia (deducido)
- `a81383d` catalogo-confirmado: decidir con --requisito tras un catálogo cambiado no figura como confirmación (agy-1); una propuesta sin huellas no se confirma tal cual (codex CC-001); la medida que falta o el catálogo ilegible se nombran con su archivo relativo (agy-2, agy-5); un catálogo por llamada (agy-3); pruebas de esos casos (agy-4) (deducido)
- `310b32c` catalogo-confirmado: medidas propuestas de nuevo por claude-code (los catálogos cambiaron después de la confirmación) (deducido)
- `4e12cf2` catalogo-confirmado: medidas confirmadas de nuevo por Brian (deducido)
- `4a0debd` catalogo-confirmado: evidencia del candidato nuevo (deducido)
- `3f68c51` catalogo-confirmado: un archivo que sigue ahí pero Oracle no carga no se informa como ausente (codex CC2-001); anotación de tipo (agy) (deducido)
- `9e25b3f` catalogo-confirmado: evidencia del candidato nuevo (deducido)
- `eb3899d` catalogo-confirmado: informes de la vuelta 3 (deducido)
- `cdfed85` catalogo-confirmado: revisión preparada y aprobación propuesta por claude-code (deducido)
- `3276bf0` catalogo-confirmado: revisión registrada por Brian (el bajo CC3-001 aceptado como riesgo) (deducido)
- `9662b51` catalogo-confirmado: veredicto Oracle (deducido)

## Mensajes

- Ninguno.
