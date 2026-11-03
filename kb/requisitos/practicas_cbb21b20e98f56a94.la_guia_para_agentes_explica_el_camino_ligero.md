---
generado: oracle-factory kb
id: "practicas_cbb21b20e98f56a94.la_guia_para_agentes_explica_el_camino_ligero"
vigente: true
---

# la guia para agentes explica el camino ligero

> Generado por `oracle-factory kb` desde el registro de Factory: no se edita a mano.

- Id: `practicas_cbb21b20e98f56a94.la_guia_para_agentes_explica_el_camino_ligero`
- Vigente: sí
- Cambio: [[cambios/20261102-221210-70x-caminoligero]]
- Veredicto: cumple
- Medidas: `factory_camino_ligero.la_guia_para_agentes_explica_el_camino_ligero`, `factory_camino_ligero.corrida_completa`
- Fuente: openspec/changes/20261102-221210-70x-caminoligero/specs/practicas/spec.md#la_guia_para_agentes_explica_el_camino_ligero

Tipo: funcional El sistema DEBE explicar en la guía para agentes que el camino ligero consiste en un revisor y una ronda, con los dos umbrales y la lista de reglas de decisión tal como están en el código, y que si esa ronda trae hallazgos medios o altos el cambio sigue el camino completo; y DEBE detectar con `agentes --verificar` que la guía quedó vieja si cambian esos datos.
