---
generado: oracle-factory kb
id: "ide_c1d15db0ac698d5a4.la_vista_de_factory_muestra_los_cambios_abiertos"
vigente: true
---

# la vista de factory muestra los cambios abiertos

> Generado por `oracle-factory kb` desde el registro de Factory: no se edita a mano.

- Id: `ide_c1d15db0ac698d5a4.la_vista_de_factory_muestra_los_cambios_abiertos`
- Vigente: sí
- Cambio: [[cambios/20261016-101007-vscode]]
- Veredicto: cumple
- Medidas: `factory_vscode.la_vista_de_factory_muestra_los_cambios_abiertos`, `factory_vscode.corrida_completa`
- Fuente: openspec/changes/20261016-101007-vscode/specs/ide/spec.md#la vista de Factory muestra los cambios abiertos

Tipo: funcional La extensión de VS Code SHALL mostrar, en una vista «Factory», los cambios abiertos del proyecto, y bajo cada uno sus requisitos con sus medidas, la decisión que las respalda y el veredicto, su revisión y su próximo paso, tomados de `resumen --json` y `estado ID --json`. Sin un proyecto de Factory en la carpeta abierta SHALL decirlo, y si la CLI falla SHALL mostrar su error en vez de una vista vacía.
