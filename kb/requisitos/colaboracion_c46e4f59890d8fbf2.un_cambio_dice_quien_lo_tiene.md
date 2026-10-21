---
generado: oracle-factory kb
id: "colaboracion_c46e4f59890d8fbf2.un_cambio_dice_quien_lo_tiene"
vigente: true
---

# un cambio dice quien lo tiene

> Generado por `oracle-factory kb` desde el registro de Factory: no se edita a mano.

- Id: `colaboracion_c46e4f59890d8fbf2.un_cambio_dice_quien_lo_tiene`
- Vigente: sí
- Cambio: [[cambios/20261019-232444-quien]]
- Veredicto: cumple
- Medidas: `factory_quien.un_cambio_dice_quien_lo_tiene`, `factory_quien.corrida_completa`
- Fuente: openspec/changes/20261019-232444-quien/specs/colaboracion/spec.md#un cambio dice quién lo tiene

Tipo: funcional `oracle-factory tomar ID` SHALL registrar como responsable a la persona que lo corre desde su terminal, con los agentes que declara con `--con`, y `soltar ID` SHALL liberarlo. Si otra persona ya es responsable, `tomar` SHALL NOT reemplazarla salvo con `--relevo`, que SHALL dejar constancia de quién lo tenía. Un agente con `--agente` SHALL NOT quedar como responsable: SHALL quedar sumado como agente del cambio. Sin terminal ni `--agente`, `tomar` SHALL negarse.
