---
generado: oracle-factory kb
id: "flujo_cc3cbaf2da9e917bd.el_conductor_frena_ante_un_freno_o_un_paso_que_no_conoce"
vigente: true
---

# el conductor frena ante un freno o un paso que no conoce

> Generado por `oracle-factory kb` desde el registro de Factory: no se edita a mano.

- Id: `flujo_cc3cbaf2da9e917bd.el_conductor_frena_ante_un_freno_o_un_paso_que_no_conoce`
- Vigente: sí
- Cambio: [[cambios/20261108-220606-51z-autopilot]]
- Veredicto: sin juicio
- Medidas: `factory_autopilot.el_conductor_frena_ante_un_freno_o_un_paso_que_no_conoce`, `factory_autopilot.corrida_completa`
- Fuente: openspec/changes/20261108-220606-51z-autopilot/specs/flujo/spec.md#el_conductor_frena_ante_un_freno_o_un_paso_que_no_conoce

Tipo: funcional El sistema DEBE frenar, antes de cualquier otra regla, cuando el cambio tiene algún freno de `estado`, cuando el próximo paso no es uno que el conductor reconoce, o cuando faltan archivos del cambio; y DEBE decir `terminado` cuando el cambio está cerrado o abandonado y no tiene próximo paso. Frenar nunca trae un comando para actuar.
