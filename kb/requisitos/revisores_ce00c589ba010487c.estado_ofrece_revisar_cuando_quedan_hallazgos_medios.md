---
generado: oracle-factory kb
id: "revisores_ce00c589ba010487c.estado_ofrece_revisar_cuando_quedan_hallazgos_medios"
vigente: true
---

# estado ofrece revisar cuando quedan hallazgos medios

> Generado por `oracle-factory kb` desde el registro de Factory: no se edita a mano.

- Id: `revisores_ce00c589ba010487c.estado_ofrece_revisar_cuando_quedan_hallazgos_medios`
- Vigente: sí
- Cambio: [[cambios/20261014-125953-estado-revisar-medios]]
- Veredicto: cumple
- Medidas: `factory_alternativas.estado_ofrece_revisar_cuando_quedan_hallazgos_medios`, `factory_alternativas.corrida_completa`
- Fuente: openspec/changes/20261014-125953-estado-revisar-medios/specs/revisores/spec.md#estado ofrece revisar cuando quedan hallazgos medios

Tipo: funcional Con hallazgos medios o más sin aceptar en el candidato vigente, `estado` SHALL mostrar, además de corregir y pedir otra vuelta, que se pueden aceptar como riesgo o descartar con motivo con `oracle-factory revisar ID`; en una terminal, su menú SHALL ofrecer ejecutar ese comando; `estado --json` SHALL listarlo en `alternativas`, y `pedir-revision` SHALL decirlo al guardar un informe que deja medios sin aceptar. Sin medios pendientes no SHALL haber alternativa.
