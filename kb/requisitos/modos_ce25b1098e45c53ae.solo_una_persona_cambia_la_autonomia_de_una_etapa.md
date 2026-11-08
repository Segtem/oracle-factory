---
generado: oracle-factory kb
id: "modos_ce25b1098e45c53ae.solo_una_persona_cambia_la_autonomia_de_una_etapa"
vigente: true
---

# solo una persona cambia la autonomia de una etapa

> Generado por `oracle-factory kb` desde el registro de Factory: no se edita a mano.

- Id: `modos_ce25b1098e45c53ae.solo_una_persona_cambia_la_autonomia_de_una_etapa`
- Vigente: sí
- Cambio: [[cambios/20261108-134533-o0q-etapas]]
- Veredicto: cumple
- Medidas: `factory_etapas.solo_una_persona_cambia_la_autonomia_de_una_etapa`, `factory_etapas.corrida_completa`
- Fuente: openspec/changes/20261108-134533-o0q-etapas/specs/modos/spec.md#solo_una_persona_cambia_la_autonomia_de_una_etapa

Tipo: funcional El sistema DEBE permitir cambiar la autonomía de una etapa con `oracle-factory autonomia ETAPA MODO` únicamente a una persona desde su terminal, con una confirmación, y DEBE negárselo a un agente con `--agente`, sin modificar el archivo; el cambio DEBE conservar el resto de la configuración.
