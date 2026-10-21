---
generado: oracle-factory kb
id: "trazabilidad_c03c40840efaaab69.cada_commit_nuevo_dice_de_que_cambio_es"
vigente: true
---

# cada commit nuevo dice de que cambio es

> Generado por `oracle-factory kb` desde el registro de Factory: no se edita a mano.

- Id: `trazabilidad_c03c40840efaaab69.cada_commit_nuevo_dice_de_que_cambio_es`
- Vigente: sí
- Cambio: [[cambios/20261019-182313-commits]]
- Veredicto: cumple
- Medidas: `factory_commits.cada_commit_nuevo_dice_de_que_cambio_es`, `factory_commits.corrida_completa`
- Fuente: openspec/changes/20261019-182313-commits/specs/trazabilidad/spec.md#cada commit nuevo dice de qué cambio es

Tipo: funcional `oracle-factory init` y `oracle-factory hooks` SHALL instalar un hook `prepare-commit-msg` que agregue el trailer `Cambio: <ID>` a cada commit hecho en un checkout con exactamente un cambio abierto, sin tocar los otros trailers ni un `Cambio:` que ya esté; con cero o más de un cambio abierto SHALL NOT agregar nada. Si en la carpeta de hooks ya hay un `prepare-commit-msg` ajeno, SHALL NOT pisarlo y SHALL decir cómo encadenarlo. El hook SHALL NOT impedir un commit, tampoco si falta el intérprete de Factory.
