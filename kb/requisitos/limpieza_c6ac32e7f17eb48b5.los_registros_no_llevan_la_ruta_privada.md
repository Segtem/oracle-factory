---
generado: oracle-factory kb
id: "limpieza_c6ac32e7f17eb48b5.los_registros_no_llevan_la_ruta_privada"
vigente: true
---

# los registros no llevan la ruta privada

> Generado por `oracle-factory kb` desde el registro de Factory: no se edita a mano.

- Id: `limpieza_c6ac32e7f17eb48b5.los_registros_no_llevan_la_ruta_privada`
- Vigente: sí
- Cambio: [[cambios/20261005-193914-quitar-la-ruta]]
- Veredicto: cumple
- Medidas: `factory_limpieza.los_registros_no_llevan_la_ruta_privada`, `factory_limpieza.corrida_completa`
- Fuente: openspec/changes/20261005-193914-quitar-la-ruta/specs/limpieza/spec.md#los registros no llevan la ruta privada

Tipo: funcional Los registros que Factory lee (la fuente de los requisitos, incluidos los requisitos previos, y la ruta de los hechos en el registro de cada cambio) SHALL expresar rutas relativas a la raíz del proyecto, sin la ruta de la máquina que los escribió.
