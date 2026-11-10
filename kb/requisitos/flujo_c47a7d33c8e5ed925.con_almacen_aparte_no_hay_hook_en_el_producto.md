---
generado: oracle-factory kb
id: "flujo_c47a7d33c8e5ed925.con_almacen_aparte_no_hay_hook_en_el_producto"
vigente: true
---

# con almacen aparte no hay hook en el producto

> Generado por `oracle-factory kb` desde el registro de Factory: no se edita a mano.

- Id: `flujo_c47a7d33c8e5ed925.con_almacen_aparte_no_hay_hook_en_el_producto`
- Vigente: sí
- Cambio: [[cambios/20261110-140719-h7t-registros-candidato]]
- Veredicto: cumple
- Medidas: `factory_registros_candidato.con_almacen_aparte_no_hay_hook_en_el_producto`, `factory_registros_candidato.corrida_completa`
- Fuente: openspec/changes/20261110-140719-h7t-registros-candidato/specs/flujo/spec.md#con_almacen_aparte_no_hay_hook_en_el_producto

Tipo: funcional El sistema DEBE, con almacén aparte, negarse a instalar con `hooks` cualquier hook en el repo del producto, con un mensaje que diga que los commits de un cambio se deducen de sus candidatos y sin escribir nada; y `log ID` DEBE mostrar los commits del cambio deducidos de sus candidatos.
