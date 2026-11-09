---
generado: oracle-factory kb
id: "flujo_c350dc50b9b6cde6a.el_conductor_pide_el_segundo_revisor_antes_de_la_revision"
vigente: true
---

# el conductor pide el segundo revisor antes de la revision

> Generado por `oracle-factory kb` desde el registro de Factory: no se edita a mano.

- Id: `flujo_c350dc50b9b6cde6a.el_conductor_pide_el_segundo_revisor_antes_de_la_revision`
- Vigente: sí
- Cambio: [[cambios/20261109-162444-701-segundo-revisor]]
- Veredicto: sin juicio
- Medidas: ninguna
- Sin medir: sin medida todavía; escenarios: «con segundo revisor», «sin segundo revisor», «nombre inválido», «con un freno»
- Fuente: openspec/changes/20261109-162444-701-segundo-revisor/specs/flujo/spec.md#el_conductor_pide_el_segundo_revisor_antes_de_la_revision

Tipo: funcional El sistema DEBE, ante un próximo paso `revisar` con un `segundo_revisor` válido (texto no vacío de letras, dígitos, punto, guion y guion bajo), decidir `actuar` con el comando mecánico `oracle-factory pedir-revision ID --a ESE_REVISOR`, antes de delegar la propuesta de revisión o pedirle la revisión a una persona; con `segundo_revisor` ausente, `null` o inválido la decisión no cambia; y los frenos y los datos ilegibles siguen yendo primero.
