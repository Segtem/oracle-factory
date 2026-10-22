---
generado: oracle-factory kb
id: "flujo_cbbf375bdcabddbc9.la_guia_dice_lo_que_hace_la_cli"
vigente: true
---

# la guia dice lo que hace la cli

> Generado por `oracle-factory kb` desde el registro de Factory: no se edita a mano.

- Id: `flujo_cbbf375bdcabddbc9.la_guia_dice_lo_que_hace_la_cli`
- Vigente: sí
- Cambio: [[cambios/20261022-215347-y70-agentes]]
- Veredicto: cumple
- Medidas: `factory_agentes.la_guia_dice_lo_que_hace_la_cli`, `factory_agentes.corrida_completa`
- Fuente: openspec/changes/20261022-215347-y70-agentes/specs/flujo/spec.md#la guía dice lo que hace la CLI

Tipo: funcional Cada comando que la guía presenta como decisión de una persona SHALL negarse cuando lo corre un agente con `--agente`, o dejar sólo una propuesta sin decidir; y cada comando que presenta como de un agente SHALL aceptar `--agente`. Una prueba SHALL recorrer la lista de la guía y comprobarlo, de modo que la guía no pueda prometer algo que la CLI no hace.
