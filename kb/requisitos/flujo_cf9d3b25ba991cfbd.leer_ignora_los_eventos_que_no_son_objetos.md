---
generado: oracle-factory kb
id: "flujo_cf9d3b25ba991cfbd.leer_ignora_los_eventos_que_no_son_objetos"
vigente: true
---

# leer ignora los eventos que no son objetos

> Generado por `oracle-factory kb` desde el registro de Factory: no se edita a mano.

- Id: `flujo_cf9d3b25ba991cfbd.leer_ignora_los_eventos_que_no_son_objetos`
- Vigente: sí
- Cambio: [[cambios/20261109-012630-nn6-eventos]]
- Veredicto: sin juicio
- Medidas: ninguna
- Sin medir: sin medida todavía; escenarios: «un evento que no es un objeto», «eventos que no es una lista», «un registro sano», «leer no escribe»
- Fuente: openspec/changes/20261109-012630-nn6-eventos/specs/flujo/spec.md#leer_ignora_los_eventos_que_no_son_objetos

Tipo: funcional El sistema DEBE ignorar, al leer el registro de un cambio, los elementos de `eventos` que no son objetos y tratar un `eventos` que no es una lista como vacío; DEBE avisar una vez por cambio, por la salida de error, cuántos ignoró; NO DEBE tocar el archivo al leer; y para un registro sano NO DEBE cambiar nada ni avisar.
