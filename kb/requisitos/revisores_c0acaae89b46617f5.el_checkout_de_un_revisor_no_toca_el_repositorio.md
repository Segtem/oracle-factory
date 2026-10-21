---
generado: oracle-factory kb
id: "revisores_c0acaae89b46617f5.el_checkout_de_un_revisor_no_toca_el_repositorio"
vigente: true
---

# el checkout de un revisor no toca el repositorio

> Generado por `oracle-factory kb` desde el registro de Factory: no se edita a mano.

- Id: `revisores_c0acaae89b46617f5.el_checkout_de_un_revisor_no_toca_el_repositorio`
- Vigente: sí
- Cambio: [[cambios/20261020-200030-aislar]]
- Veredicto: cumple
- Medidas: `factory_aislar.el_checkout_de_un_revisor_no_toca_el_repositorio`, `factory_aislar.corrida_completa`
- Fuente: openspec/changes/20261020-200030-aislar/specs/revisores/spec.md#el checkout de un revisor no toca el repositorio

Tipo: funcional `pedir-revision` SHALL darle a cada revisor un checkout del candidato que sea un repositorio aparte, sin copiar objetos: lo que el revisor haga con git en ese checkout (cambiar su configuración, crear ramas, hacer commits) SHALL NOT cambiar la configuración, las ramas ni el HEAD del repositorio del proyecto ni de sus worktrees, y su informe SHALL validarse como siempre.
