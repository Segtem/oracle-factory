---
generado: oracle-factory kb
id: "revisores_c54735f6bdc173577.un_riesgo_aceptado_persiste_entre_vueltas"
vigente: true
---

# un riesgo aceptado persiste entre vueltas

> Generado por `oracle-factory kb` desde el registro de Factory: no se edita a mano.

- Id: `revisores_c54735f6bdc173577.un_riesgo_aceptado_persiste_entre_vueltas`
- Vigente: sí
- Cambio: [[cambios/20261013-115616-vueltas-severidad]]
- Veredicto: cumple
- Medidas: `factory_vueltas.un_riesgo_aceptado_persiste_entre_vueltas`, `factory_vueltas.corrida_completa`
- Fuente: openspec/changes/20261013-115616-vueltas-severidad/specs/revisores/spec.md#un riesgo aceptado persiste entre vueltas

Tipo: funcional Cuando una persona acepta un riesgo en `revisar`, el registro del cambio SHALL guardarlo con su archivo, título, motivo, persona, fecha y candidato, aunque la revisión termine pidiendo cambios. `pedir-revision` SHALL incluir los riesgos aceptados vigentes del cambio en el pedido a cada revisor. Un hallazgo medio o alto que coincide con un riesgo aceptado SHALL NOT pedir otra vuelta.
