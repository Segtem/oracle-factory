---
generado: oracle-factory kb
id: "autoproduccion_c847ea5712990b078.los_informes_de_revisores_siempre_se_validan"
vigente: true
---

# los informes de revisores siempre se validan

> Generado por `oracle-factory kb` desde el registro de Factory: no se edita a mano.

- Id: `autoproduccion_c847ea5712990b078.los_informes_de_revisores_siempre_se_validan`
- Vigente: sí
- Cambio: [[cambios/20261012-131420-clue-dependencia]]
- Veredicto: cumple
- Medidas: `factory_clue.los_informes_de_revisores_siempre_se_validan`, `factory_clue.corrida_completa`
- Fuente: openspec/changes/20261012-131420-clue-dependencia/specs/autoproduccion/spec.md#los informes de revisores siempre se validan

Tipo: funcional Cada informe de revisor SHALL validarse con Clue contra su paquete antes de usarse; un informe ilegible, inválido, de otro candidato o que no se puede validar (por ejemplo, porque falta su paquete o su checkout) SHALL avisarse y no usarse. No hay informes «sin validar».
