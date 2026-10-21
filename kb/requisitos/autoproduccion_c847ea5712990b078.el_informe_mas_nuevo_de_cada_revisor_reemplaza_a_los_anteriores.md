---
generado: oracle-factory kb
id: "autoproduccion_c847ea5712990b078.el_informe_mas_nuevo_de_cada_revisor_reemplaza_a_los_anteriores"
vigente: true
---

# el informe mas nuevo de cada revisor reemplaza a los anteriores

> Generado por `oracle-factory kb` desde el registro de Factory: no se edita a mano.

- Id: `autoproduccion_c847ea5712990b078.el_informe_mas_nuevo_de_cada_revisor_reemplaza_a_los_anteriores`
- Vigente: sí
- Cambio: [[cambios/20261012-131420-clue-dependencia]]
- Veredicto: cumple
- Medidas: `factory_clue.el_informe_mas_nuevo_de_cada_revisor_reemplaza_a_los_anteriores`, `factory_clue.corrida_completa`
- Fuente: openspec/changes/20261012-131420-clue-dependencia/specs/autoproduccion/spec.md#el informe más nuevo de cada revisor reemplaza a los anteriores

Tipo: funcional Cuando un candidato tiene varios informes del mismo revisor (`<revisor>-<n>.json`), `revision-preparar` SHALL usar sólo el de mayor `n` para hallazgos y comprobaciones, y SHALL mostrar los anteriores como vueltas registradas, sin decidirse otra vez.
