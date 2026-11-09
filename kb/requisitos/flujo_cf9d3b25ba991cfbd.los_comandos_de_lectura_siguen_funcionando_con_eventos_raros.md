---
generado: oracle-factory kb
id: "flujo_cf9d3b25ba991cfbd.los_comandos_de_lectura_siguen_funcionando_con_eventos_raros"
vigente: true
---

# los comandos de lectura siguen funcionando con eventos raros

> Generado por `oracle-factory kb` desde el registro de Factory: no se edita a mano.

- Id: `flujo_cf9d3b25ba991cfbd.los_comandos_de_lectura_siguen_funcionando_con_eventos_raros`
- Vigente: sí
- Cambio: [[cambios/20261109-012630-nn6-eventos]]
- Veredicto: sin juicio
- Medidas: ninguna
- Sin medir: sin medida todavía; escenarios: «estado», «kb»
- Fuente: openspec/changes/20261109-012630-nn6-eventos/specs/flujo/spec.md#los_comandos_de_lectura_siguen_funcionando_con_eventos_raros

Tipo: funcional El sistema DEBE seguir mostrando `estado`, `estado --json` y el conocimiento generado (`kb`) de un cambio cuyo registro tiene eventos que no son objetos, con los demás eventos intactos, sin fallar.
