---
generado: oracle-factory kb
id: "bloqueos_c48b34e270263f8fb.revisar_el_producto_de_un_primer_commit"
vigente: true
---

# revisar el producto de un primer commit

> Generado por `oracle-factory kb` desde el registro de Factory: no se edita a mano.

- Id: `bloqueos_c48b34e270263f8fb.revisar_el_producto_de_un_primer_commit`
- Vigente: sí
- Cambio: [[cambios/20261026-144045-3h6-bloqueos]]
- Veredicto: cumple
- Medidas: `factory_bloqueos.revisar_el_producto_de_un_primer_commit`, `factory_bloqueos.corrida_completa`
- Fuente: openspec/changes/20261026-144045-3h6-bloqueos/specs/bloqueos/spec.md#revisar el producto de un primer commit

Tipo: funcional The system SHALL accept `pedir-revision --base vacio` to build the review package against a base with no files, so that the whole product of a candidate whose code is in the first commit can be reviewed, without changing branches, history or Git configuration.
