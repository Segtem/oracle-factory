---
generado: oracle-factory kb
id: "practicas_cbb21b20e98f56a94.el_estado_dice_si_el_candidato_califica_para_el_camino_ligero"
vigente: true
---

# el estado dice si el candidato califica para el camino ligero

> Generado por `oracle-factory kb` desde el registro de Factory: no se edita a mano.

- Id: `practicas_cbb21b20e98f56a94.el_estado_dice_si_el_candidato_califica_para_el_camino_ligero`
- Vigente: sí
- Cambio: [[cambios/20261102-221210-70x-caminoligero]]
- Veredicto: cumple
- Medidas: `factory_camino_ligero.el_estado_dice_si_el_candidato_califica_para_el_camino_ligero`, `factory_camino_ligero.corrida_completa`
- Fuente: openspec/changes/20261102-221210-70x-caminoligero/specs/practicas/spec.md#el_estado_dice_si_el_candidato_califica_para_el_camino_ligero

Tipo: funcional El sistema DEBE decir en el estado de un cambio, y en su JSON, si el candidato vigente califica para el camino ligero: cuando agrega 150 líneas de producto o menos y no toca ninguna regla de decisión. Cuando no califica DEBE decir por qué, y cuando no se puede calcular DEBE decirlo en vez de afirmar un camino.
