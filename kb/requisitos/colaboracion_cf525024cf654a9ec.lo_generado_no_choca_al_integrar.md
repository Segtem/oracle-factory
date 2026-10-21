---
generado: oracle-factory kb
id: "colaboracion_cf525024cf654a9ec.lo_generado_no_choca_al_integrar"
vigente: true
---

# lo generado no choca al integrar

> Generado por `oracle-factory kb` desde el registro de Factory: no se edita a mano.

- Id: `colaboracion_cf525024cf654a9ec.lo_generado_no_choca_al_integrar`
- Vigente: sí
- Cambio: [[cambios/20261021-140625-unir]]
- Veredicto: cumple
- Medidas: `factory_unir.lo_generado_no_choca_al_integrar`, `factory_unir.corrida_completa`
- Fuente: openspec/changes/20261021-140625-unir/specs/colaboracion/spec.md#lo generado no choca al integrar

Tipo: funcional Al integrar dos ramas, `.factory/resumen.md` y las notas generadas de `kb/` SHALL NOT dejar conflictos de texto: Factory SHALL rehacerlos después del merge, de modo que `resumen --verificar` y `kb --verificar` pasen sin editar nada a mano.
