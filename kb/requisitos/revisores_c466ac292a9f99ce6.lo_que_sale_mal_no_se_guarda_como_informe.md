---
generado: oracle-factory kb
id: "revisores_c466ac292a9f99ce6.lo_que_sale_mal_no_se_guarda_como_informe"
vigente: true
---

# lo que sale mal no se guarda como informe

> Generado por `oracle-factory kb` desde el registro de Factory: no se edita a mano.

- Id: `revisores_c466ac292a9f99ce6.lo_que_sale_mal_no_se_guarda_como_informe`
- Vigente: sí
- Cambio: [[cambios/20261007-192608-revisores]]
- Veredicto: cumple
- Medidas: `factory_revisores.lo_que_sale_mal_no_se_guarda_como_informe`, `factory_revisores.corrida_completa`
- Fuente: openspec/changes/20261007-192608-revisores/specs/revisores/spec.md#lo que sale mal no se guarda como informe

Tipo: funcional Si el revisor no deja informe, si Clue lo rechaza o si se pasa del tope, `pedir-revision` SHALL terminar con error sin guardar nada en `revision/`, conservando la salida del revisor para inspeccionar; y si el producto tiene cambios sin commit SHALL rechazarse antes de lanzar al revisor.
