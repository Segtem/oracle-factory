---
generado: oracle-factory kb
id: "revisores_c90ab53abb4ca96d7.el_paquete_de_revision_excluye_lo_que_no_es_producto"
vigente: true
---

# el paquete de revision excluye lo que no es producto

> Generado por `oracle-factory kb` desde el registro de Factory: no se edita a mano.

- Id: `revisores_c90ab53abb4ca96d7.el_paquete_de_revision_excluye_lo_que_no_es_producto`
- Vigente: sí
- Cambio: [[cambios/20261014-000054-paquete-producto]]
- Veredicto: cumple
- Medidas: `factory_paquete.el_paquete_de_revision_excluye_lo_que_no_es_producto`, `factory_paquete.corrida_completa`
- Fuente: openspec/changes/20261014-000054-paquete-producto/specs/revisores/spec.md#el paquete de revisión excluye lo que no es producto

Tipo: funcional `pedir-revision` SHALL preparar el paquete de Clue excluyendo `.factory/`, `tareas/` y todo otro archivo del diff que no cuente en la huella del producto. El paquete SHALL nombrar esas exclusiones y los archivos que dejaron afuera, y el pedido al revisor SHALL decir que no forman parte de lo revisado.
