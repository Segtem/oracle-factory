---
generado: oracle-factory kb
id: "20261014-000054-paquete-producto"
fase: "cerrada"
capacidad: "revisores"
---

# El paquete de revisión deja fuera lo que no es producto

> Generado por `oracle-factory kb` desde el registro de Factory: no se edita a mano.

- Fase: cerrada
- Capacidad: revisores
- Responsable: nadie
- Spec: [openspec/changes/20261014-000054-paquete-producto/specs/revisores/spec.md](../../openspec/changes/20261014-000054-paquete-producto/specs/revisores/spec.md)

## Requisitos

- [[requisitos/revisores_c90ab53abb4ca96d7.el_paquete_de_revision_excluye_lo_que_no_es_producto]] — cumple
- [[requisitos/revisores_c90ab53abb4ca96d7.factory_comprueba_las_exclusiones_del_paquete]] — cumple

## Decisiones

- 2026-10-14 00:00 · Cambio creado · claude-code (agente)
- 2026-10-14 00:02 · Spec aprobada · Brian Hollweg (persona)
- 2026-10-14 00:02 · Requisitos importados · claude-code (agente)
- 2026-10-14 00:12 · Medidas confirmadas · Brian Hollweg (persona)
- 2026-10-14 00:12 · Medidas confirmadas · Brian Hollweg (persona)
- 2026-10-14 10:03 · Revisión registrada · Brian Hollweg (persona) — aprobar: dos vueltas de codex y agy, con paquetes ya armados sin los registros de Factory: la 1 trajo un alto (el diff sin producto metía los registros en el paquete), tres medios y dos bajos; todos corregidos con aserciones que fallan en el código anterior, en los mismos 4 casos. La 2 no encontró nada (agy, reintentado tras un 503 del servicio). Suite 336 y evidencia en verde.
- 2026-10-14 10:03 · Juicio de Oracle · claude-code (agente)
- 2026-10-14 10:04 · Cerrado · Brian Hollweg (persona)
- 2026-10-14 10:04 · Archivado · Brian Hollweg (persona)

## Riesgos aceptados

- Ninguno.

## Commits

- `7339a78` 20261014-000054-paquete-producto: propuesta, spec y diseño; oracle-clue fijado en 0.1.0a2 (deducido)
- `161768a` paquete-producto: spec aprobada por Brian (deducido)
- `cfe6c39` paquete-producto: pedir-revision excluye del paquete de Clue lo que no es producto y Factory comprueba las exclusiones (deducido)
- `477c21a` paquete-producto: medidas propuestas por claude-code (deducido)
- `eef8ecc` paquete-producto: medidas confirmadas por Brian (deducido)
- `9812988` paquete-producto: evidencia del candidato (deducido)
- `e919597` paquete-producto: siempre se excluyen los registros; sin producto, pedir-revision explica cómo revisar con --base; estado avisa (deducido)
- `dbcf80a` paquete-producto: informes de la vuelta 1 y evidencia del candidato nuevo (deducido)
- `2a9f4ae` paquete-producto: informes de la vuelta 2 (codex y agy sin hallazgos; agy reintentado tras un 503) (deducido)
- `247f5f9` paquete-producto: revisión preparada y aprobación propuesta por claude-code (deducido)
- `2a44fda` paquete-producto: revisión registrada por Brian (deducido)
- `e188dd0` paquete-producto: veredicto Oracle (deducido)

## Mensajes

- Ninguno.
