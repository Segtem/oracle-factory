---
generado: oracle-factory kb
id: "20261109-201722-oja-construir-primero"
fase: "oracle_verde"
capacidad: "flujo"
---

# Autopilot: ante medir --listar sin medidas todavía el conductor delega construir primero

> Generado por `oracle-factory kb` desde el registro de Factory: no se edita a mano.

- Fase: oracle_verde
- Capacidad: flujo
- Responsable: nadie
- Spec: [openspec/changes/20261109-201722-oja-construir-primero/specs/flujo/spec.md](../../openspec/changes/20261109-201722-oja-construir-primero/specs/flujo/spec.md)

## Requisitos

- [[requisitos/flujo_c0d820474143ed460.ante_medir_listar_el_conductor_manda_construir_antes_de_elegir_medidas]] — cumple

## Decisiones

- 2026-11-09 20:17 · Cambio creado · claude-code (agente)
- 2026-11-09 20:23 · Spec aprobada · Brian Hollweg (persona)
- 2026-11-09 20:23 · Requisitos importados · claude-code (agente)
- 2026-11-09 20:26 · Medidas confirmadas · Brian Hollweg (persona)
- 2026-11-09 20:39 · Spec aprobada · Brian Hollweg (persona)
- 2026-11-09 20:40 · Requisitos importados · claude-code (agente)
- 2026-11-09 20:42 · Medidas confirmadas · Brian Hollweg (persona)
- 2026-11-09 20:55 · Revisión registrada · Brian Hollweg (persona) — aprobar: Propuesta del agente claude-code. Candidato b1a8886 (camino ligero): evidencia verde, 10 mutaciones propias detectadas sobre la redacción final, codex ronda 1 con CP1-001 (medio: «pruebas ni catálogos» ambigua; corregido) y ronda 2 sin hallazgos. DECIDIÓ BRIAN (ya aprobada la spec corregida): me aparté de mi propia spec aprobada: listaba la evidencia del candidato como parte de construir y en el flujo real va DESPUÉS de que una persona confirma las medidas; la spec cambió, aprobaste de nuevo, el requisito cambió de identificador y reconfirmaste las medidas. QUÉ HAY QUE SABER: la instrucción sigue siendo texto para un agente: no detecta con datos qué falta (pruebas, catálogos); lo decide el agente mirando el cambio. Si mañana un agente la lee mal, el conductor lo frena por sin progreso. No edité ningún test existente (el que mira medidas en la instrucción sigue pasando).
- 2026-11-09 20:55 · Juicio de Oracle · claude-code (agente)

## Riesgos aceptados

- Ninguno.

## Commits

- `e5a33e0` construir-primero: propuesta y spec (trailer)
- `65eaa2a` construir-primero: spec aprobada por Brian (trailer)
- `c53e17d` construir-primero: instrucción del conductor, pruebas y docs (trailer)
- `dfe0412` construir-primero: catálogos y propuesta de medidas (trailer)
- `cbe6500` construir-primero: medidas confirmadas por Brian (trailer)
- `b09eba3` construir-primero: evidencia del candidato (trailer)
- `23f3d51` construir-primero: hallazgo CP1-001 de codex y corrección de la spec (la evidencia va después de confirmar las medidas) (trailer)
- `3b3709c` construir-primero: spec aprobada de nuevo por Brian (trailer)
- `0f582fe` construir-primero: requisito importado de nuevo y medidas propuestas (trailer)
- `b1a8886` construir-primero: medidas confirmadas por Brian (segunda vez) (trailer)
- `d1acf6b` construir-primero: evidencia del candidato nuevo (trailer)
- `1ce02a2` construir-primero: informe de codex (ronda 2, sin hallazgos) (trailer)
- `d65c434` construir-primero: propuesta de revisión (trailer)
- Todos, también los que se deducen al integrarlo o los posteriores a la última decisión: `oracle-factory log 20261109-201722-oja-construir-primero`.

## Mensajes

- Ninguno.
