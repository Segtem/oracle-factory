---
generado: oracle-factory kb
id: "revision_guiada_c804320abe8bb0c1d.un_intento_de_revision_que_no_se_registro_queda_a_la_vista"
vigente: true
---

# un intento de revision que no se registro queda a la vista

> Generado por `oracle-factory kb` desde el registro de Factory: no se edita a mano.

- Id: `revision_guiada_c804320abe8bb0c1d.un_intento_de_revision_que_no_se_registro_queda_a_la_vista`
- Vigente: sí
- Cambio: [[cambios/20261016-143020-revisar-cancelada]]
- Veredicto: cumple
- Medidas: `factory_cancelada.un_intento_de_revision_que_no_se_registro_queda_a_la_vista`, `factory_cancelada.corrida_completa`
- Fuente: openspec/changes/20261016-143020-revisar-cancelada/specs/revision-guiada/spec.md#un intento de revisión que no se registró queda a la vista

Tipo: funcional Cuando `revisar` corta después de mostrar la revisión sin registrarla, SHALL guardar en el registro un evento `revision_cancelada` con la causa, el candidato y la persona, sin registrar ninguna decisión. Mientras el último intento de revisión sea uno cortado, `estado` y `estado --json` (en `avisos`) SHALL avisar que no se registró, con la causa, y SHALL decir qué hacer: volver a correr revisar o, si ya hay una revisión anterior registrada, que esa sigue valiendo.
