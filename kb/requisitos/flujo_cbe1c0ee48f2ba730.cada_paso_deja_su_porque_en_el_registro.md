---
generado: oracle-factory kb
id: "flujo_cbe1c0ee48f2ba730.cada_paso_deja_su_porque_en_el_registro"
vigente: true
---

# cada paso deja su porque en el registro

> Generado por `oracle-factory kb` desde el registro de Factory: no se edita a mano.

- Id: `flujo_cbe1c0ee48f2ba730.cada_paso_deja_su_porque_en_el_registro`
- Vigente: sí
- Cambio: [[cambios/20261108-233304-ywj-actua]]
- Veredicto: sin juicio
- Medidas: ninguna
- Sin medir: sin medida todavía; escenarios: «el porqué», «el final»
- Fuente: openspec/changes/20261108-233304-ywj-actua/specs/flujo/spec.md#cada_paso_deja_su_porque_en_el_registro

Tipo: funcional El sistema DEBE dejar, antes de cada paso, un `mensaje` en el registro del cambio, a nombre del agente, con la acción, el motivo y el comando o la instrucción; y al final, otro con el motivo de la detención, y DEBE mostrar un resumen de los pasos (en texto y con `--json`) con el resultado de cada uno.
