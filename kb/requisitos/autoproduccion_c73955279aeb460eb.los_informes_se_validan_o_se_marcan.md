---
generado: oracle-factory kb
id: "autoproduccion_c73955279aeb460eb.los_informes_se_validan_o_se_marcan"
vigente: true
---

# los informes se validan o se marcan

> Generado por `oracle-factory kb` desde el registro de Factory: no se edita a mano.

- Id: `autoproduccion_c73955279aeb460eb.los_informes_se_validan_o_se_marcan`
- Vigente: sí
- Cambio: [[cambios/20261007-150043-autoproduccion]]
- Veredicto: cumple
- Medidas: `factory_autoproduccion.los_informes_se_validan_o_se_marcan`, `factory_autoproduccion.corrida_completa`
- Fuente: openspec/changes/20261007-150043-autoproduccion/specs/autoproduccion/spec.md#los informes se validan o se marcan

Tipo: funcional Si `oracle-clue` está disponible, cada informe de revisor SHALL validarse contra su paquete antes de usarse; si no lo está, SHALL usarse marcado «sin validar» con un aviso; un informe ilegible, inválido o de otro candidato SHALL avisarse y no usarse.
