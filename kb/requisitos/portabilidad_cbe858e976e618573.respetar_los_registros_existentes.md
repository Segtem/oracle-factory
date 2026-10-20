---
generado: oracle-factory kb
id: "portabilidad_cbe858e976e618573.respetar_los_registros_existentes"
vigente: true
---

# respetar los registros existentes

> Generado por `oracle-factory kb` desde el registro de Factory: no se edita a mano.

- Id: `portabilidad_cbe858e976e618573.respetar_los_registros_existentes`
- Vigente: sí
- Cambio: [[cambios/20261005-184427-los-registros-de]]
- Veredicto: cumple
- Medidas: `factory_portabilidad.respetar_los_registros_existentes`, `factory_portabilidad.corrida_completa`
- Fuente: openspec/changes/20261005-184427-los-registros-de/specs/portabilidad/spec.md#respetar los registros existentes

Tipo: no funcional Factory SHALL NOT reescribir registros existentes ni exigir migración, y SHALL seguir leyendo los que tienen ruta absoluta.
