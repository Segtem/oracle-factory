---
generado: oracle-factory kb
id: "ci_c2426e1a5c6ed9e1f.verificar_falla_en_main_y_avisa_en_las_demas"
vigente: true
---

# verificar falla en main y avisa en las demas

> Generado por `oracle-factory kb` desde el registro de Factory: no se edita a mano.

- Id: `ci_c2426e1a5c6ed9e1f.verificar_falla_en_main_y_avisa_en_las_demas`
- Vigente: sí
- Cambio: [[cambios/20261108-003501-eqd-activar]]
- Veredicto: cumple
- Medidas: `factory_ci_activar.verificar_falla_en_main_y_avisa_en_las_demas`, `factory_ci_activar.corrida_completa`
- Fuente: openspec/changes/20261108-003501-eqd-activar/specs/ci/spec.md#verificar_falla_en_main_y_avisa_en_las_demas

Tipo: funcional El sistema DEBE hacer fallar el workflow cuando `verificar` encuentra un cambio inconsistente en la rama `main`, y DEBE avisar sin fallar, con una anotación de advertencia, en cualquier otra rama o pull request.
