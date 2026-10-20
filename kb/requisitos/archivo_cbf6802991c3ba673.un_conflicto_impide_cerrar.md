---
generado: oracle-factory kb
id: "archivo_cbf6802991c3ba673.un_conflicto_impide_cerrar"
vigente: true
---

# un conflicto impide cerrar

> Generado por `oracle-factory kb` desde el registro de Factory: no se edita a mano.

- Id: `archivo_cbf6802991c3ba673.un_conflicto_impide_cerrar`
- Vigente: sí
- Cambio: [[cambios/20261006-161029-archivar-al]]
- Veredicto: cumple
- Medidas: `factory_archivo.un_conflicto_impide_cerrar`, `factory_archivo.corrida_completa`
- Fuente: openspec/changes/20261006-161029-archivar-al/specs/archivo/spec.md#un conflicto impide cerrar

Tipo: funcional Si la fusión no es posible (agregar un requisito con un nombre que ya existe en la capacidad, modificar o quitar uno que no existe, repetir un nombre en la spec del cambio o usar `RENAMED`), o si la spec consolidada en disco no es la que generó Factory, `cerrar` SHALL rechazarse antes de pedir la confirmación y de modificar cualquier archivo, y SHALL nombrar el requisito o el archivo en conflicto.
