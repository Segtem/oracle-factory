---
generado: oracle-factory kb
id: "colaboracion_cf525024cf654a9ec.el_registro_de_un_cambio_editado_en_dos_ramas_se_une_sin_perder_nada"
vigente: true
---

# el registro de un cambio editado en dos ramas se une sin perder nada

> Generado por `oracle-factory kb` desde el registro de Factory: no se edita a mano.

- Id: `colaboracion_cf525024cf654a9ec.el_registro_de_un_cambio_editado_en_dos_ramas_se_une_sin_perder_nada`
- Vigente: sí
- Cambio: [[cambios/20261021-140625-unir]]
- Veredicto: sin juicio
- Medidas: ninguna
- Sin medir: sin medida todavía; escenarios: «dos ramas que dejaron mensajes en el mismo cambio»
- Fuente: openspec/changes/20261021-140625-unir/specs/colaboracion/spec.md#el registro de un cambio editado en dos ramas se une sin perder nada

Tipo: funcional Con los hooks de Factory instalados, al integrar dos ramas que editaron el registro de un mismo cambio, Git SHALL unirlo con Factory sin conflicto de texto: todos los eventos de las dos ramas SHALL quedar, sin repetirse y en orden; y lo que cambió una sola rama SHALL tomarse de esa rama.
