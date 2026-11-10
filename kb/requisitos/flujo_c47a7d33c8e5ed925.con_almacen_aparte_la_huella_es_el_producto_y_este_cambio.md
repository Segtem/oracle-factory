---
generado: oracle-factory kb
id: "flujo_c47a7d33c8e5ed925.con_almacen_aparte_la_huella_es_el_producto_y_este_cambio"
vigente: true
---

# con almacen aparte la huella es el producto y este cambio

> Generado por `oracle-factory kb` desde el registro de Factory: no se edita a mano.

- Id: `flujo_c47a7d33c8e5ed925.con_almacen_aparte_la_huella_es_el_producto_y_este_cambio`
- Vigente: sí
- Cambio: [[cambios/20261110-140719-h7t-registros-candidato]]
- Veredicto: sin juicio
- Medidas: `factory_registros_candidato.con_almacen_aparte_la_huella_es_el_producto_y_este_cambio`, `factory_registros_candidato.corrida_completa`
- Fuente: openspec/changes/20261110-140719-h7t-registros-candidato/specs/flujo/spec.md#con_almacen_aparte_la_huella_es_el_producto_y_este_cambio

Tipo: funcional El sistema DEBE, con almacén aparte, calcular la huella que decide si la revisión y el juicio de un cambio siguen vigentes a partir del repo del producto (su HEAD y sus archivos no ignorados) y de los archivos de ese cambio en el almacén (su propuesta y su spec, sin los registros que Factory genera, sus requisitos y los catálogos de las medidas que tiene elegidas); un cambio en el producto o en esos archivos DEBE dejar vieja la revisión y el juicio, y un cambio en archivos de otro cambio del almacén NO DEBE dejarlos viejos; sin almacén aparte la huella DEBE seguir calculándose como hasta ahora.
