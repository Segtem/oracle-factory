---
generado: oracle-factory kb
id: "autoproduccion_c847ea5712990b078.importar_no_trae_lo_que_la_spec_retira"
vigente: true
---

# importar no trae lo que la spec retira

> Generado por `oracle-factory kb` desde el registro de Factory: no se edita a mano.

- Id: `autoproduccion_c847ea5712990b078.importar_no_trae_lo_que_la_spec_retira`
- Vigente: sí
- Cambio: [[cambios/20261012-131420-clue-dependencia]]
- Veredicto: cumple
- Medidas: `factory_clue.importar_no_trae_lo_que_la_spec_retira`, `factory_clue.corrida_completa`
- Fuente: openspec/changes/20261012-131420-clue-dependencia/specs/autoproduccion/spec.md#importar no trae lo que la spec retira

Tipo: funcional Los requisitos de la sección `## REMOVED Requirements` de la spec de un cambio SHALL quedar fuera de su importación: `importar` no los registra entre los requisitos del cambio ni deja sus archivos en `requisitos/`, porque lo que se retira no se mide; se retiran de la spec consolidada al cerrar.
