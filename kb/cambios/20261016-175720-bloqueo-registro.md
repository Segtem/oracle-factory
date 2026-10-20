---
generado: oracle-factory kb
id: "20261016-175720-bloqueo-registro"
fase: "cerrada"
capacidad: "flujo"
---

# Dos procesos que escriben el mismo registro no se pisan

> Generado por `oracle-factory kb` desde el registro de Factory: no se edita a mano.

- Fase: cerrada
- Capacidad: flujo
- Responsable: nadie
- Spec: [openspec/changes/20261016-175720-bloqueo-registro/specs/flujo/spec.md](../../openspec/changes/20261016-175720-bloqueo-registro/specs/flujo/spec.md)

## Requisitos

- [[requisitos/flujo_c467adb55cba3c0a6.dos_procesos_que_escriben_el_mismo_registro_no_se_pisan]] — cumple

## Decisiones

- 2026-10-16 17:57 · Cambio creado · claude-code (agente)
- 2026-10-16 18:01 · Spec aprobada · Brian Hollweg (persona)
- 2026-10-16 18:01 · Requisitos importados · claude-code (agente)
- 2026-10-16 18:07 · Medidas confirmadas · Brian Hollweg (persona)
- 2026-10-16 19:55 · Revisión registrada · Brian Hollweg (persona) — aprobar: tres vueltas de codex y agy: la 1 marcó un alto y tres medios (la primera escritura sin leer no quedaba protegida, un archivo borrado daba un error crudo, bl2 no enfrentaba dos escrituras de Factory) y la 2 un medio (bl1 no aislaba la lectura), corregidos con pruebas que fallan sobre el código anterior y mutaciones; la 3 no encontró nada; quedan bajas de la vuelta 2 sobre el alcance del catálogo, el sensor y el flock en carpetas compartidas
- 2026-10-16 19:55 · Juicio de Oracle · claude-code (agente)
- 2026-10-16 19:57 · Cerrado · Brian Hollweg (persona)
- 2026-10-16 19:57 · Archivado · Brian Hollweg (persona)

## Riesgos aceptados

- Ninguno.

## Commits

- `8b84fcc` bloqueo-registro: medidas confirmadas por Brian (deducido)
- `d1b1f6e` bloqueo-registro: guardar anota lo que escribió aunque no lo haya leído antes (agy-1, codex BLQ-1); un archivo borrado entretanto es un archivo que cambió (agy-2); bl2 enfrenta dos guardar de Factory, demorado entre comparar y reemplazar (agy-3); límites y docs más precisos (agy-4, agy-6) (deducido)
- `f72807d` bloqueo-registro: bl1 y bl2 parten de un proceso que no escribió el registro, así que prueban que leer fija la base (agy-1 de la vuelta 2) (deducido)
- Todos, también los que se deducen al integrarlo: `oracle-factory log 20261016-175720-bloqueo-registro`.

## Mensajes

- Ninguno.
