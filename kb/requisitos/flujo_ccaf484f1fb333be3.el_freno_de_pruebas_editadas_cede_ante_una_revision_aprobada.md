---
generado: oracle-factory kb
id: "flujo_ccaf484f1fb333be3.el_freno_de_pruebas_editadas_cede_ante_una_revision_aprobada"
vigente: true
---

# el freno de pruebas editadas cede ante una revision aprobada

> Generado por `oracle-factory kb` desde el registro de Factory: no se edita a mano.

- Id: `flujo_ccaf484f1fb333be3.el_freno_de_pruebas_editadas_cede_ante_una_revision_aprobada`
- Vigente: sí
- Cambio: [[cambios/20261109-125752-r6d-freno-visto]]
- Veredicto: cumple
- Medidas: `factory_freno_visto.el_freno_de_pruebas_editadas_cede_ante_una_revision_aprobada`, `factory_freno_visto.corrida_completa`
- Fuente: openspec/changes/20261109-125752-r6d-freno-visto/specs/flujo/spec.md#el_freno_de_pruebas_editadas_cede_ante_una_revision_aprobada

Tipo: funcional El sistema DEBE dejar de declarar el freno `prueba_existente_editada` cuando hay una revisión aprobada y vigente del cambio (decisión `aprobar`, del mismo producto que el candidato actual y sin problemas), y declararlo cuando hay tests existentes editados y no la hay; los avisos de tests editados siguen mostrándose en ambos casos, y los demás frenos no cambian.
