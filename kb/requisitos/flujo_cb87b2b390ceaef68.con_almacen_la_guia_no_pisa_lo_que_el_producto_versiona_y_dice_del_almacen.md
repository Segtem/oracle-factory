---
generado: oracle-factory kb
id: "flujo_cb87b2b390ceaef68.con_almacen_la_guia_no_pisa_lo_que_el_producto_versiona_y_dice_del_almacen"
vigente: true
---

# con almacen la guia no pisa lo que el producto versiona y dice del almacen

> Generado por `oracle-factory kb` desde el registro de Factory: no se edita a mano.

- Id: `flujo_cb87b2b390ceaef68.con_almacen_la_guia_no_pisa_lo_que_el_producto_versiona_y_dice_del_almacen`
- Vigente: sí
- Cambio: [[cambios/20261111-161316-dd7-almacen-guia]]
- Veredicto: sin juicio
- Medidas: ninguna
- Sin medir: sin medida todavía; escenarios: «el producto ya tiene su AGENTS.md», «la guía dice del almacén»
- Fuente: openspec/changes/20261111-161316-dd7-almacen-guia/specs/flujo/spec.md#con_almacen_la_guia_no_pisa_lo_que_el_producto_versiona_y_dice_del_almacen

Tipo: funcional El sistema DEBE, con almacén aparte, negarse a modificar `AGENTS.md`, `CLAUDE.md` o la skill si el producto ya los versiona, diciendo cuál y sin escribir nada; y DEBE incluir en la guía, con almacén aparte, que los registros viven en un almacén aparte y que se comparten con `oracle-factory sincronizar`.
