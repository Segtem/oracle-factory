---
generado: oracle-factory kb
id: "flujo_c5b6a893e70e9eba0.sincronizar_une_los_registros_de_todos_sin_escribir_configuracion"
vigente: true
---

# sincronizar une los registros de todos sin escribir configuracion

> Generado por `oracle-factory kb` desde el registro de Factory: no se edita a mano.

- Id: `flujo_c5b6a893e70e9eba0.sincronizar_une_los_registros_de_todos_sin_escribir_configuracion`
- Vigente: sí
- Cambio: [[cambios/20261111-135546-t8q-almacen-sincronizar]]
- Veredicto: cumple
- Medidas: `factory_almacen_sincronizar.sincronizar_une_los_registros_de_todos_sin_escribir_configuracion`, `factory_almacen_sincronizar.corrida_completa`
- Fuente: openspec/changes/20261111-135546-t8q-almacen-sincronizar/specs/flujo/spec.md#sincronizar_une_los_registros_de_todos_sin_escribir_configuracion

Tipo: funcional El sistema DEBE, con `sincronizar` desde un producto conectado, traer lo del remoto del almacén y unirlo con lo local usando los drivers de unión de Factory pasados con `git -c` en esa misma orden y el `.gitattributes` del almacén (que DEBE escribir y commitear si falta), de modo que el registro de un mismo cambio editado por dos personas quede unido sin perder eventos de ninguna; DEBE rehacer y commitear lo generado después de unir; NO DEBE escribir ninguna configuración de Git en ningún repositorio; y DEBE hacerlo con el bloqueo del almacén tomado.
