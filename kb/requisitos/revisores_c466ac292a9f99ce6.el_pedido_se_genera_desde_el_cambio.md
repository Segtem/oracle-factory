---
generado: oracle-factory kb
id: "revisores_c466ac292a9f99ce6.el_pedido_se_genera_desde_el_cambio"
vigente: true
---

# el pedido se genera desde el cambio

> Generado por `oracle-factory kb` desde el registro de Factory: no se edita a mano.

- Id: `revisores_c466ac292a9f99ce6.el_pedido_se_genera_desde_el_cambio`
- Vigente: sí
- Cambio: [[cambios/20261007-192608-revisores]]
- Veredicto: cumple
- Medidas: `factory_revisores.el_pedido_se_genera_desde_el_cambio`, `factory_revisores.corrida_completa`
- Fuente: openspec/changes/20261007-192608-revisores/specs/revisores/spec.md#el pedido se genera desde el cambio

Tipo: funcional El pedido SHALL generarse desde una plantilla versionada con la propuesta, la spec, el paquete, el checkout, el formato de informe esperado y las vueltas anteriores del cambio; un proyecto SHALL poder reemplazar la plantilla con `.factory/pedido-revision.md`, y `--pedir` SHALL agregar indicaciones al final.
