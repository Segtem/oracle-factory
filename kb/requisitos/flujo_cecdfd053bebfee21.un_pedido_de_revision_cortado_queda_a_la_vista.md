---
generado: oracle-factory kb
id: "flujo_cecdfd053bebfee21.un_pedido_de_revision_cortado_queda_a_la_vista"
vigente: true
---

# un pedido de revision cortado queda a la vista

> Generado por `oracle-factory kb` desde el registro de Factory: no se edita a mano.

- Id: `flujo_cecdfd053bebfee21.un_pedido_de_revision_cortado_queda_a_la_vista`
- Vigente: sí
- Cambio: [[cambios/20261017-135953-higiene]]
- Veredicto: cumple
- Medidas: `factory_higiene.un_pedido_de_revision_cortado_queda_a_la_vista`, `factory_higiene.corrida_completa`
- Fuente: openspec/changes/20261017-135953-higiene/specs/flujo/spec.md#un pedido de revisión cortado queda a la vista

Tipo: funcional `pedir-revision` SHALL registrar el lanzamiento del revisor (revisor y candidato) antes de correrlo y su resultado al terminar, también si se interrumpe. Mientras un lanzamiento no tenga resultado, `estado` y `estado --json` (en `avisos`) SHALL avisar qué revisor se lanzó, cuándo y sobre qué candidato, y que no dejó resultado.
