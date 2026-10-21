---
generado: oracle-factory kb
id: "revisores_c54735f6bdc173577.el_corte_de_vueltas_sigue_la_severidad"
vigente: true
---

# el corte de vueltas sigue la severidad

> Generado por `oracle-factory kb` desde el registro de Factory: no se edita a mano.

- Id: `revisores_c54735f6bdc173577.el_corte_de_vueltas_sigue_la_severidad`
- Vigente: sí
- Cambio: [[cambios/20261013-115616-vueltas-severidad]]
- Veredicto: cumple
- Medidas: `factory_vueltas.el_corte_de_vueltas_sigue_la_severidad`, `factory_vueltas.corrida_completa`
- Fuente: openspec/changes/20261013-115616-vueltas-severidad/specs/revisores/spec.md#el corte de vueltas sigue la severidad

Tipo: funcional Después de guardar un informe, `pedir-revision` SHALL mostrar cuántos hallazgos trae por severidad. Si entre los informes del candidato vigente no queda ningún hallazgo de severidad media o alta sin un riesgo aceptado que coincida, SHALL decir que no hace falta otra vuelta y que los bajos los decide una persona en `revisar`; si queda alguno, SHALL pedir corregirlo y pedir otra vuelta. Una severidad desconocida o ausente SHALL contar como media. `estado` SHALL sugerir el mismo próximo paso.
