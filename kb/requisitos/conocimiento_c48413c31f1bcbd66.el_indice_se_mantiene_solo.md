---
generado: oracle-factory kb
id: "conocimiento_c48413c31f1bcbd66.el_indice_se_mantiene_solo"
vigente: true
---

# el indice se mantiene solo

> Generado por `oracle-factory kb` desde el registro de Factory: no se edita a mano.

- Id: `conocimiento_c48413c31f1bcbd66.el_indice_se_mantiene_solo`
- Vigente: sí
- Cambio: [[cambios/20261021-235127-fjn-rag]]
- Veredicto: sin juicio
- Medidas: `factory_rag.el_indice_se_mantiene_solo`, `factory_rag.corrida_completa`
- Fuente: openspec/changes/20261021-235127-fjn-rag/specs/conocimiento/spec.md#el índice se mantiene solo

Tipo: funcional El índice SHALL vivir en `.factory/local/rag/` y SHALL actualizarse solo al preguntar cuando cambió el corpus: agrega lo nuevo, borra lo que ya no está y reusa el embedding de cada pasaje que no cambió; un modelo distinto SHALL invalidar sus embeddings. Ninguna persona SHALL tener que reconstruirlo para que las respuestas estén al día.
