---
generado: oracle-factory kb
id: "ci_ceafbb528d2c1c459.verificar_dice_si_los_cambios_estan_consistentes"
vigente: true
---

# verificar dice si los cambios estan consistentes

> Generado por `oracle-factory kb` desde el registro de Factory: no se edita a mano.

- Id: `ci_ceafbb528d2c1c459.verificar_dice_si_los_cambios_estan_consistentes`
- Vigente: sí
- Cambio: ninguno registrado
- Veredicto: sin juicio
- Medidas: ninguna
- Sin medir: sin medida todavía; escenarios: «todo consistente», «una revisión que ya no corresponde», «un informe tocado después de aprobarse»
- Fuente: openspec/changes/20261107-130317-2vv-verificar/specs/ci/spec.md#verificar_dice_si_los_cambios_estan_consistentes

Tipo: funcional El sistema DEBE ofrecer `oracle-factory verificar`, que recorre los cambios del proyecto y sale con 0 si todos están consistentes y con 1 si alguno no lo está, nombrando el cambio y qué falta, y DEBE ofrecer lo mismo con `--json` en un objeto con esquema versionado.
