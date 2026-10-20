---
generado: oracle-factory kb
id: "flujo_c3eeedacc969eee2a.dos_sensores_no_emiten_la_misma_relacion"
vigente: true
---

# dos sensores no emiten la misma relacion

> Generado por `oracle-factory kb` desde el registro de Factory: no se edita a mano.

- Id: `flujo_c3eeedacc969eee2a.dos_sensores_no_emiten_la_misma_relacion`
- Vigente: sí
- Cambio: [[cambios/20261017-023151-hechos-varios]]
- Veredicto: cumple
- Medidas: `factory_hechos.dos_sensores_no_emiten_la_misma_relacion`, `factory_hechos.corrida_completa`
- Fuente: openspec/changes/20261017-023151-hechos-varios/specs/flujo/spec.md#dos sensores no emiten la misma relación

Tipo: funcional Si dos archivos de hechos traen la misma relación, `juzgar` SHALL NOT registrar un veredicto y SHALL mostrar el error de Oracle, que nombra la relación y los dos archivos.
