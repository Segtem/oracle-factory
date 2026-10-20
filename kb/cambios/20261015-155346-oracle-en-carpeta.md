---
generado: oracle-factory kb
id: "20261015-155346-oracle-en-carpeta"
fase: "cerrada"
capacidad: "estructura"
---

# El proyecto Oracle puede estar en una carpeta del proyecto

> Generado por `oracle-factory kb` desde el registro de Factory: no se edita a mano.

- Fase: cerrada
- Capacidad: estructura
- Responsable: nadie
- Spec: [openspec/changes/20261015-155346-oracle-en-carpeta/specs/estructura/spec.md](../../openspec/changes/20261015-155346-oracle-en-carpeta/specs/estructura/spec.md)

## Requisitos

- [[requisitos/estructura_c01f2e6fb0af5aed6.el_proyecto_oracle_puede_estar_en_una_carpeta]] — cumple
- [[requisitos/estructura_c01f2e6fb0af5aed6.init_adopta_un_proyecto_oracle_existente]] — cumple
- [[requisitos/estructura_c01f2e6fb0af5aed6.los_escalares_del_proyecto_se_ejecutan_solo_si_el_proyecto_lo_declara]] — cumple

## Decisiones

- 2026-10-15 15:53 · Cambio creado · claude-code (agente)
- 2026-10-15 16:15 · Spec aprobada · Brian Hollweg (persona)
- 2026-10-15 16:15 · Requisitos importados · claude-code (agente)
- 2026-10-15 16:30 · Medidas confirmadas · Brian Hollweg (persona)
- 2026-10-15 16:30 · Medidas confirmadas · Brian Hollweg (persona)
- 2026-10-15 16:30 · Medidas confirmadas · Brian Hollweg (persona)
- 2026-10-15 19:21 · Revisión registrada · Brian Hollweg (persona) — aprobar: tres vueltas de codex y agy, a la vez. La 1: dos altos (buscar ocultaba una carpeta inválida; init sin --oracle recreaba Oracle en la raíz) y tres medios; la 2: un alto (juzgar no entregaba el error de Oracle con escalares sin declarar) y tres medios (una prueba que pasaba por vacuidad, rutas de Windows). Todo corregido con pruebas que fallan sin el arreglo. La 3 no encontró nada. Suite 367 y evidencia en verde, con Oracle 0.38.2.
- 2026-10-15 19:21 · Juicio de Oracle · claude-code (agente)
- 2026-10-15 19:22 · Cerrado · Brian Hollweg (persona)
- 2026-10-15 19:22 · Archivado · Brian Hollweg (persona)

## Riesgos aceptados

- Ninguno.

## Commits

- `af991ba` oracle-en-carpeta: medidas confirmadas por Brian (deducido)
- `75bbe8a` oracle-en-carpeta: buscar no oculta una carpeta inválida (agy, codex OC-001); init respeta la carpeta ya configurada (agy); estado no se cae si los escalares no se pueden cargar y la prueba sin declararlos pasa por juzgar (agy) (deducido)
- `a38d44b` oracle-en-carpeta: juzgar entrega el error de Oracle con escalares sin declarar y el detalle de una cobertura que falla (agy, codex OC-001); la prueba ya no pasa por vacuidad; se rechazan rutas con barras invertidas o absolutas de Windows (agy) (deducido)
- Todos, también los que se deducen al integrarlo: `oracle-factory log 20261015-155346-oracle-en-carpeta`.

## Mensajes

- Ninguno.
