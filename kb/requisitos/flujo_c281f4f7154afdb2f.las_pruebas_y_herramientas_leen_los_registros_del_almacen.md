---
generado: oracle-factory kb
id: "flujo_c281f4f7154afdb2f.las_pruebas_y_herramientas_leen_los_registros_del_almacen"
vigente: true
---

# las pruebas y herramientas leen los registros del almacen

> Generado por `oracle-factory kb` desde el registro de Factory: no se edita a mano.

- Id: `flujo_c281f4f7154afdb2f.las_pruebas_y_herramientas_leen_los_registros_del_almacen`
- Vigente: sí
- Cambio: [[cambios/20261112-121837-6bu-pmr]]
- Veredicto: cumple
- Medidas: `factory_preparar_migracion.las_pruebas_y_herramientas_leen_los_registros_del_almacen`, `factory_preparar_migracion.corrida_completa`
- Fuente: openspec/changes/20261112-121837-6bu-pmr/specs/flujo/spec.md#las_pruebas_y_herramientas_leen_los_registros_del_almacen

Tipo: funcional El sistema DEBE, con el producto conectado a un almacén, hacer que `tools/verificar_cambio.py` lea la spec y el registro del cambio del almacén, escriba ahí los catálogos y corra las pruebas del producto, y que las pruebas de Factory que leen sus propios requisitos y catálogos (`test_portabilidad` p6 y `test_verificador_generico` vg3) los lean del almacén; sin conexión, todo DEBE seguir leyendo y escribiendo en el repo del producto como antes.
