---
generado: oracle-factory kb
id: "procedencia_c1e221f291fd3697a.un_fallo_de_consulta_no_se_lee_como_sin_afectados"
vigente: true
---

# un fallo de consulta no se lee como sin afectados

> Generado por `oracle-factory kb` desde el registro de Factory: no se edita a mano.

- Id: `procedencia_c1e221f291fd3697a.un_fallo_de_consulta_no_se_lee_como_sin_afectados`
- Vigente: sí
- Cambio: [[cambios/20261029-164101-xux-avisososv]]
- Veredicto: cumple
- Medidas: `factory_avisos_osv.un_fallo_de_consulta_no_se_lee_como_sin_afectados`, `factory_avisos_osv.corrida_completa`
- Fuente: openspec/changes/20261029-164101-xux-avisososv/specs/procedencia/spec.md#un_fallo_de_consulta_no_se_lee_como_sin_afectados

Tipo: funcional El sistema DEBE terminar con error, indicando el motivo y sin guardar archivo, ante cualquier fallo de la consulta, y nunca informar «sin afectados» por no haber podido consultar.
