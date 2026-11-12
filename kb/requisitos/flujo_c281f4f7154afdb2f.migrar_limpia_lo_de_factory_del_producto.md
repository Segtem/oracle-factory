---
generado: oracle-factory kb
id: "flujo_c281f4f7154afdb2f.migrar_limpia_lo_de_factory_del_producto"
vigente: true
---

# migrar limpia lo de factory del producto

> Generado por `oracle-factory kb` desde el registro de Factory: no se edita a mano.

- Id: `flujo_c281f4f7154afdb2f.migrar_limpia_lo_de_factory_del_producto`
- Vigente: sí
- Cambio: [[cambios/20261112-121837-6bu-pmr]]
- Veredicto: sin juicio
- Medidas: ninguna
- Sin medir: sin medida todavía; escenarios: «un producto con las líneas y los hooks de Factory», «un hook ajeno»
- Fuente: openspec/changes/20261112-121837-6bu-pmr/specs/flujo/spec.md#migrar_limpia_lo_de_factory_del_producto

Tipo: funcional El sistema DEBE, con `migrar --almacen`, sacar del `.gitignore` y del `.gitattributes` del producto exactamente las líneas que escribe Factory (y la marca de su bloque), dejando esos cambios en el índice sin commitear junto con la baja; llevar las líneas de `.gitattributes` al almacén en el mismo commit de la migración; y sacar los hooks `commit-msg`, `prepare-commit-msg`, `post-commit` y `post-merge` que tengan la marca de Factory, sin tocar un hook que no la tenga ni el `pre-push`. `--verificar` DEBE decir qué sacaría, sin escribir nada.
