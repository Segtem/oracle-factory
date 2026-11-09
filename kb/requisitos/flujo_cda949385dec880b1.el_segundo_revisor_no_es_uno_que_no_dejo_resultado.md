---
generado: oracle-factory kb
id: "flujo_cda949385dec880b1.el_segundo_revisor_no_es_uno_que_no_dejo_resultado"
vigente: true
---

# el segundo revisor no es uno que no dejo resultado

> Generado por `oracle-factory kb` desde el registro de Factory: no se edita a mano.

- Id: `flujo_cda949385dec880b1.el_segundo_revisor_no_es_uno_que_no_dejo_resultado`
- Vigente: sí
- Cambio: [[cambios/20261109-194509-ylk-sin-informe]]
- Veredicto: sin juicio
- Medidas: `factory_sin_informe.el_segundo_revisor_no_es_uno_que_no_dejo_resultado`, `factory_sin_informe.corrida_completa`
- Fuente: openspec/changes/20261109-194509-ylk-sin-informe/specs/flujo/spec.md#el_segundo_revisor_no_es_uno_que_no_dejo_resultado

Tipo: funcional El sistema DEBE, al calcular `segundo_revisor` en `estado --json`, descartar a un revisor que tenga un lanzamiento sin resultado sobre el candidato vigente, y ofrecer en su lugar el primero (por orden de nombre) de otro proveedor que no tenga ese problema; si no queda ninguno, `segundo_revisor` DEBE ser `null`. Un lanzamiento sin resultado sobre otro candidato, o ya cerrado por un resultado, no descarta a nadie, y el resto de las reglas del `segundo_revisor` no cambia.
