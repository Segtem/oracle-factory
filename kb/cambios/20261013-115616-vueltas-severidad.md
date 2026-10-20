---
generado: oracle-factory kb
id: "20261013-115616-vueltas-severidad"
fase: "cerrada"
capacidad: "revisores"
---

# Vueltas de revisión proporcionales y riesgos aceptados que persisten

> Generado por `oracle-factory kb` desde el registro de Factory: no se edita a mano.

- Fase: cerrada
- Capacidad: revisores
- Responsable: nadie
- Spec: [openspec/changes/20261013-115616-vueltas-severidad/specs/revisores/spec.md](../../openspec/changes/20261013-115616-vueltas-severidad/specs/revisores/spec.md)

## Requisitos

- [[requisitos/revisores_c54735f6bdc173577.el_corte_de_vueltas_sigue_la_severidad]] — cumple
- [[requisitos/revisores_c54735f6bdc173577.revisar_reconoce_un_riesgo_ya_aceptado]] — cumple
- [[requisitos/revisores_c54735f6bdc173577.un_riesgo_aceptado_persiste_entre_vueltas]] — cumple

## Decisiones

- 2026-10-13 11:56 · Cambio creado · claude-code (agente)
- 2026-10-13 11:59 · Spec aprobada · Brian Hollweg (persona)
- 2026-10-13 12:02 · Requisitos importados · claude-code (agente)
- 2026-10-13 12:12 · Medidas confirmadas · Brian Hollweg (persona)
- 2026-10-13 12:12 · Medidas confirmadas · Brian Hollweg (persona)
- 2026-10-13 12:12 · Medidas confirmadas · Brian Hollweg (persona)
- 2026-10-13 15:18 · Revisión registrada · Brian Hollweg (persona) — aprobar: tres vueltas de codex y agy: la 1 trajo 5 hallazgos (2 altos, 3 medios) y la 2, 4 (1 alto, 2 medios, 1 bajo), todos corregidos con una aserción que falla en el código anterior dentro de los mismos 10 casos del contrato; la 3 dejó un solo hallazgo bajo, decidido en esta revisión, y el corte nuevo dijo que no hacía falta otra vuelta. El F-03 de la vuelta 1 (el escenario de severidad desconocida no se alcanza por pedir-revision porque Clue rechaza el informe) queda como límite declarado en la evidencia; ajustar la spec va aparte. Suite 320 y evidencia en verde.
- 2026-10-13 15:18 · Juicio de Oracle · claude-code (agente)
- 2026-10-13 15:19 · Cerrado · Brian Hollweg (persona)
- 2026-10-13 15:19 · Archivado · Brian Hollweg (persona)

## Riesgos aceptados

- `oracle_factory/preparacion.py`: La ubicación ambigua trunca archivos cuyo nombre termina en dos puntos y dígitos — aceptado por Brian Hollweg: Acepto el riesgo: La ubicación ambigua trunca archivos cuyo nombre termina en dos puntos y dígitos

## Commits

- `43f9d4d` vueltas-severidad: medidas confirmadas por Brian (deducido)
- `0dda62b` vueltas-severidad: firma sin puntuación ni títulos vacíos, un aceptado por firma y aviso si no hay corte (deducido)
- `6d60612` vueltas-severidad: un hallazgo repetido se decide una vez, la firma conserva los símbolos y se guarda el aceptado sin firma (deducido)
- Todos, también los que se deducen al integrarlo: `oracle-factory log 20261013-115616-vueltas-severidad`.

## Mensajes

- Ninguno.
