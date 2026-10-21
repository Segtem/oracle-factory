---
generado: oracle-factory kb
id: "limpieza_c6ac32e7f17eb48b5.las_decisiones_conservan_su_integridad"
vigente: true
---

# las decisiones conservan su integridad

> Generado por `oracle-factory kb` desde el registro de Factory: no se edita a mano.

- Id: `limpieza_c6ac32e7f17eb48b5.las_decisiones_conservan_su_integridad`
- Vigente: sí
- Cambio: [[cambios/20261005-193914-quitar-la-ruta]]
- Veredicto: cumple
- Medidas: `factory_limpieza.las_decisiones_conservan_su_integridad`, `factory_limpieza.corrida_completa`
- Fuente: openspec/changes/20261005-193914-quitar-la-ruta/specs/limpieza/spec.md#las decisiones conservan su integridad

Tipo: funcional Cuando la limpieza cambia el contenido de un requisito con una decisión de medidas registrada, SHALL actualizar el hash de esa decisión y dejar un evento que registre el hash anterior y el nuevo, de modo que `estado` no muestre pendientes que antes no tenía.
