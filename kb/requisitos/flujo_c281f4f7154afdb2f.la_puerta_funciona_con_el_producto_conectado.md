---
generado: oracle-factory kb
id: "flujo_c281f4f7154afdb2f.la_puerta_funciona_con_el_producto_conectado"
vigente: true
---

# la puerta funciona con el producto conectado

> Generado por `oracle-factory kb` desde el registro de Factory: no se edita a mano.

- Id: `flujo_c281f4f7154afdb2f.la_puerta_funciona_con_el_producto_conectado`
- Vigente: sí
- Cambio: [[cambios/20261112-121837-6bu-pmr]]
- Veredicto: cumple
- Medidas: `factory_preparar_migracion.la_puerta_funciona_con_el_producto_conectado`, `factory_preparar_migracion.corrida_completa`
- Fuente: openspec/changes/20261112-121837-6bu-pmr/specs/flujo/spec.md#la_puerta_funciona_con_el_producto_conectado

Tipo: funcional El sistema DEBE, con el producto conectado a un almacén, hacer que la puerta local de salida (`oracle-factory puerta`, la que corre el hook pre-push) busque secretos en lo que se empuja del repo del producto y corra sus verificaciones sobre los registros del almacén, y bloquee el push si encuentra un secreto o una verificación vencida.
