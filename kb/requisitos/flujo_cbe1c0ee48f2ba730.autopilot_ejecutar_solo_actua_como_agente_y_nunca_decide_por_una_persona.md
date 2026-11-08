---
generado: oracle-factory kb
id: "flujo_cbe1c0ee48f2ba730.autopilot_ejecutar_solo_actua_como_agente_y_nunca_decide_por_una_persona"
vigente: true
---

# autopilot ejecutar solo actua como agente y nunca decide por una persona

> Generado por `oracle-factory kb` desde el registro de Factory: no se edita a mano.

- Id: `flujo_cbe1c0ee48f2ba730.autopilot_ejecutar_solo_actua_como_agente_y_nunca_decide_por_una_persona`
- Vigente: sí
- Cambio: [[cambios/20261108-233304-ywj-actua]]
- Veredicto: sin juicio
- Medidas: `factory_conductor.autopilot_ejecutar_solo_actua_como_agente_y_nunca_decide_por_una_persona`, `factory_conductor.corrida_completa`
- Fuente: openspec/changes/20261108-233304-ywj-actua/specs/flujo/spec.md#autopilot_ejecutar_solo_actua_como_agente_y_nunca_decide_por_una_persona

Tipo: funcional El sistema DEBE ofrecer `oracle-factory autopilot ID --ejecutar` solo con `--agente`: sin él, DEBE fallar con un error claro sin correr ni escribir nada. El bucle NUNCA DEBE correr un comando de decisión de una persona (`aprobar-spec`, `medir --confirmar`, `revisar`, `cerrar`, `abandonar`, `modo`, `autonomia`, `soltar`, `decidir-union`), aunque la decisión llegue mal clasificada; y DEBE detenerse sin ejecutar nada cuando la decisión es `terminado`, `frenar` o `pedir_a_persona`, mostrando en el último caso el comando listo para pegar.
