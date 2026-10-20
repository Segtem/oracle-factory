---
generado: oracle-factory kb
id: "decisiones_c59754a250f5b3593.confirmar_las_medidas_propuestas_de_una_vez"
vigente: true
---

# confirmar las medidas propuestas de una vez

> Generado por `oracle-factory kb` desde el registro de Factory: no se edita a mano.

- Id: `decisiones_c59754a250f5b3593.confirmar_las_medidas_propuestas_de_una_vez`
- Vigente: sí
- Cambio: [[cambios/20261007-223645-decisiones-guiadas]]
- Veredicto: cumple
- Medidas: `factory_decisiones.confirmar_las_medidas_propuestas_de_una_vez`, `factory_decisiones.corrida_completa`
- Fuente: openspec/changes/20261007-223645-decisiones-guiadas/specs/decisiones/spec.md#confirmar las medidas propuestas de una vez

Tipo: funcional `medir ID --confirmar` SHALL listar, por requisito, las medidas que propuso el agente y si propuso quitar `sin_medir`, y ofrecer confirmarlas todas, decidir de a una o cancelar; confirmar SHALL dar el mismo resultado que repetir cada comando propuesto sin `--agente`.
