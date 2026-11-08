---
generado: oracle-factory kb
id: "ci_c2426e1a5c6ed9e1f.el_repositorio_corre_verificar_en_su_ci"
vigente: true
---

# el repositorio corre verificar en su ci

> Generado por `oracle-factory kb` desde el registro de Factory: no se edita a mano.

- Id: `ci_c2426e1a5c6ed9e1f.el_repositorio_corre_verificar_en_su_ci`
- Vigente: sí
- Cambio: [[cambios/20261108-003501-eqd-activar]]
- Veredicto: sin juicio
- Medidas: `factory_ci_activar.el_repositorio_corre_verificar_en_su_ci`, `factory_ci_activar.corrida_completa`
- Fuente: openspec/changes/20261108-003501-eqd-activar/specs/ci/spec.md#el_repositorio_corre_verificar_en_su_ci

Tipo: funcional El sistema DEBE tener un workflow de GitHub Actions que corra `oracle-factory verificar` en cada push y pull request, con permisos de sólo lectura, sin secretos y con Factory instalado desde el checkout.
