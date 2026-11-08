---
generado: oracle-factory kb
id: "modos_ce25b1098e45c53ae.la_autonomia_se_declara_por_etapa_y_lo_no_declarado_pide_a_una_persona"
vigente: true
---

# la autonomia se declara por etapa y lo no declarado pide a una persona

> Generado por `oracle-factory kb` desde el registro de Factory: no se edita a mano.

- Id: `modos_ce25b1098e45c53ae.la_autonomia_se_declara_por_etapa_y_lo_no_declarado_pide_a_una_persona`
- Vigente: sí
- Cambio: [[cambios/20261108-134533-o0q-etapas]]
- Veredicto: sin juicio
- Medidas: `factory_etapas.la_autonomia_se_declara_por_etapa_y_lo_no_declarado_pide_a_una_persona`, `factory_etapas.corrida_completa`
- Fuente: openspec/changes/20261108-134533-o0q-etapas/specs/modos/spec.md#la_autonomia_se_declara_por_etapa_y_lo_no_declarado_pide_a_una_persona

Tipo: funcional El sistema DEBE admitir en `.factory/config.json` una clave opcional `autonomia` con las etapas `integracion`, `publicacion` y `produccion`, cada una en `confirmacion` o `autonomo`, DEBE tratar como `confirmacion` toda etapa no declarada, DEBE rechazar con un error que nombre el archivo y el valor una etapa o un modo desconocidos, y NO DEBE cambiar nada para un proyecto sin esa clave.
