---
generado: oracle-factory kb
id: "limpieza_c6ac32e7f17eb48b5.limpieza_repetible_y_verificable"
vigente: true
---

# limpieza repetible y verificable

> Generado por `oracle-factory kb` desde el registro de Factory: no se edita a mano.

- Id: `limpieza_c6ac32e7f17eb48b5.limpieza_repetible_y_verificable`
- Vigente: sí
- Cambio: [[cambios/20261005-193914-quitar-la-ruta]]
- Veredicto: cumple
- Medidas: `factory_limpieza.limpieza_repetible_y_verificable`, `factory_limpieza.corrida_completa`
- Fuente: openspec/changes/20261005-193914-quitar-la-ruta/specs/limpieza/spec.md#limpieza repetible y verificable

Tipo: no funcional La herramienta SHALL ser idempotente, y un verificador SHALL comprobar que ningún registro conserva la ruta, que `tareas/` no cambió y que el estado de cada cambio es el mismo antes y después.
