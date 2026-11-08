---
generado: oracle-factory kb
id: "despliegue_c15d6443128edff6b.el_plan_explica_la_eleccion_y_no_ejecuta_si_no_hay_nada"
vigente: true
---

# el plan explica la eleccion y no ejecuta si no hay nada

> Generado por `oracle-factory kb` desde el registro de Factory: no se edita a mano.

- Id: `despliegue_c15d6443128edff6b.el_plan_explica_la_eleccion_y_no_ejecuta_si_no_hay_nada`
- Vigente: sí
- Cambio: [[cambios/20261108-020932-3t5-alcance]]
- Veredicto: no cumple
- Medidas: `factory_destinos_alcance.el_plan_explica_la_eleccion_y_no_ejecuta_si_no_hay_nada`, `factory_destinos_alcance.corrida_completa`
- Fuente: openspec/changes/20261108-020932-3t5-alcance/specs/despliegue/spec.md#el_plan_explica_la_eleccion_y_no_ejecuta_si_no_hay_nada

Tipo: funcional El sistema DEBE mostrar en el plan por qué entra cada destino y cuáles se omiten, y cuando ningún destino resulta afectado DEBE decir que no hay nada que desplegar y NO DEBE ejecutar nada, ni siquiera con `--autorizar`.
