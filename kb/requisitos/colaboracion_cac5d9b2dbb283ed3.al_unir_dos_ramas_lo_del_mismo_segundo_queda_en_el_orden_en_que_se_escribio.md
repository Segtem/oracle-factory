---
generado: oracle-factory kb
id: "colaboracion_cac5d9b2dbb283ed3.al_unir_dos_ramas_lo_del_mismo_segundo_queda_en_el_orden_en_que_se_escribio"
vigente: true
---

# al unir dos ramas lo del mismo segundo queda en el orden en que se escribio

> Generado por `oracle-factory kb` desde el registro de Factory: no se edita a mano.

- Id: `colaboracion_cac5d9b2dbb283ed3.al_unir_dos_ramas_lo_del_mismo_segundo_queda_en_el_orden_en_que_se_escribio`
- Vigente: sí
- Cambio: [[cambios/20261022-115958-1jt-hora]]
- Veredicto: sin juicio
- Medidas: ninguna
- Sin medir: sin medida todavía; escenarios: «mensajes de a turnos en el mismo segundo»
- Fuente: openspec/changes/20261022-115958-1jt-hora/specs/colaboracion/spec.md#al unir dos ramas lo del mismo segundo queda en el orden en que se escribió

Tipo: funcional Al unir el registro de un cambio editado en dos ramas, los eventos SHALL quedar en el orden de sus horas aunque se hayan escrito en el mismo segundo, también si una rama tiene horas en segundos y la otra con microsegundos. El banco de concurrencia SHALL comprobarlo con mensajes de a turnos escritos en el mismo segundo, sin separar los días.
