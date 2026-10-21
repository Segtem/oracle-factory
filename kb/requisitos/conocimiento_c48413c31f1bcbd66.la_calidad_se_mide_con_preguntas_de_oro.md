---
generado: oracle-factory kb
id: "conocimiento_c48413c31f1bcbd66.la_calidad_se_mide_con_preguntas_de_oro"
vigente: true
---

# la calidad se mide con preguntas de oro

> Generado por `oracle-factory kb` desde el registro de Factory: no se edita a mano.

- Id: `conocimiento_c48413c31f1bcbd66.la_calidad_se_mide_con_preguntas_de_oro`
- Vigente: sí
- Cambio: [[cambios/20261021-235127-fjn-rag]]
- Veredicto: sin juicio
- Medidas: ninguna
- Sin medir: sin medida todavía; escenarios: «evaluar el RAG de Factory»
- Fuente: openspec/changes/20261021-235127-fjn-rag/specs/conocimiento/spec.md#la calidad se mide con preguntas de oro

Tipo: funcional `oracle-factory preguntar --evaluar --salida CARPETA` SHALL correr las preguntas de `kb/preguntas-de-oro.json` y dejar, para Oracle, por pregunta si algún archivo esperado quedó entre los cinco primeros y en qué puesto, y por corrida los aciertos, el MRR, el modo (con o sin embeddings) y el modelo. Factory SHALL tener sus propias preguntas de oro, aprobadas por una persona, y medir con ellas su RAG.
