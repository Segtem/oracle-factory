---
generado: oracle-factory kb
id: "colaboracion_cac5d9b2dbb283ed3.la_hora_de_un_evento_distingue_lo_escrito_en_el_mismo_segundo"
vigente: true
---

# la hora de un evento distingue lo escrito en el mismo segundo

> Generado por `oracle-factory kb` desde el registro de Factory: no se edita a mano.

- Id: `colaboracion_cac5d9b2dbb283ed3.la_hora_de_un_evento_distingue_lo_escrito_en_el_mismo_segundo`
- Vigente: sí
- Cambio: [[cambios/20261022-115958-1jt-hora]]
- Veredicto: sin juicio
- Medidas: ninguna
- Sin medir: sin medida todavía; escenarios: «dos mensajes en el mismo segundo»
- Fuente: openspec/changes/20261022-115958-1jt-hora/specs/colaboracion/spec.md#la hora de un evento distingue lo escrito en el mismo segundo

Tipo: funcional La hora de cada evento y de cada decisión que Factory registra SHALL llevar microsegundos, en UTC, de modo que dos escrituras del mismo segundo tengan horas distintas y ordenadas. Un registro con horas en segundos SHALL seguir leyéndose, mostrándose y uniéndose sin migrarlo.
