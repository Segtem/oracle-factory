---
generado: oracle-factory kb
id: "flujo_cbe1c0ee48f2ba730.el_bucle_tiene_topes_y_se_frena_solo"
vigente: true
---

# el bucle tiene topes y se frena solo

> Generado por `oracle-factory kb` desde el registro de Factory: no se edita a mano.

- Id: `flujo_cbe1c0ee48f2ba730.el_bucle_tiene_topes_y_se_frena_solo`
- Vigente: sí
- Cambio: [[cambios/20261108-233304-ywj-actua]]
- Veredicto: cumple
- Medidas: `factory_conductor.el_bucle_tiene_topes_y_se_frena_solo`, `factory_conductor.corrida_completa`
- Fuente: openspec/changes/20261108-233304-ywj-actua/specs/flujo/spec.md#el_bucle_tiene_topes_y_se_frena_solo

Tipo: funcional El sistema DEBE detener el bucle cuando se llega al tope de pasos o de minutos (10 y 120 por defecto, `--max-pasos` y `--max-minutos`), cuando la misma decisión con el mismo comando se repite dos veces seguidas (sin progreso), cuando un comando o el agente lanzado terminan con error o no arrancan, o cuando los datos no se pueden leer; en todos los casos DEBE decir el motivo y no volver a actuar.
