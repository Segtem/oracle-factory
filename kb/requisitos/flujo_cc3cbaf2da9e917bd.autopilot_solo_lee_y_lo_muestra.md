---
generado: oracle-factory kb
id: "flujo_cc3cbaf2da9e917bd.autopilot_solo_lee_y_lo_muestra"
vigente: true
---

# autopilot solo lee y lo muestra

> Generado por `oracle-factory kb` desde el registro de Factory: no se edita a mano.

- Id: `flujo_cc3cbaf2da9e917bd.autopilot_solo_lee_y_lo_muestra`
- Vigente: sí
- Cambio: [[cambios/20261108-220606-51z-autopilot]]
- Veredicto: cumple
- Medidas: `factory_autopilot.autopilot_solo_lee_y_lo_muestra`, `factory_autopilot.corrida_completa`
- Fuente: openspec/changes/20261108-220606-51z-autopilot/specs/flujo/spec.md#autopilot_solo_lee_y_lo_muestra

Tipo: funcional El sistema DEBE ofrecer `oracle-factory autopilot ID`, de solo lectura, que muestre la decisión en texto y con `--json` (acción, quién, comando, instrucción, motivo y frenos), sin escribir nada en el proyecto ni en el registro del cambio, y que falle con un error claro si el cambio no existe.
