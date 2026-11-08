---
generado: oracle-factory kb
id: "modos_ce25b1098e45c53ae.desplegar_autorizar_respeta_la_autonomia_de_produccion"
vigente: true
---

# desplegar autorizar respeta la autonomia de produccion

> Generado por `oracle-factory kb` desde el registro de Factory: no se edita a mano.

- Id: `modos_ce25b1098e45c53ae.desplegar_autorizar_respeta_la_autonomia_de_produccion`
- Vigente: sí
- Cambio: [[cambios/20261108-134533-o0q-etapas]]
- Veredicto: sin juicio
- Medidas: `factory_etapas.desplegar_autorizar_respeta_la_autonomia_de_produccion`, `factory_etapas.corrida_completa`
- Fuente: openspec/changes/20261108-134533-o0q-etapas/specs/modos/spec.md#desplegar_autorizar_respeta_la_autonomia_de_produccion

Tipo: funcional El sistema DEBE permitir que un agente ejecute `desplegar --autorizar` solo cuando la etapa `produccion` está en `autonomo`, registrando la autorización a nombre del agente, y DEBE seguir negándoselo en cualquier otro caso con el mismo mensaje de hoy; el plan, la puerta y la simulación se siguen exigiendo igual.
