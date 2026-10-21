---
generado: oracle-factory kb
id: "conocimiento_c48413c31f1bcbd66.los_embeddings_son_configurables_y_locales_por_defecto"
vigente: true
---

# los embeddings son configurables y locales por defecto

> Generado por `oracle-factory kb` desde el registro de Factory: no se edita a mano.

- Id: `conocimiento_c48413c31f1bcbd66.los_embeddings_son_configurables_y_locales_por_defecto`
- Vigente: sí
- Cambio: [[cambios/20261021-235127-fjn-rag]]
- Veredicto: sin juicio
- Medidas: ninguna
- Sin medir: sin medida todavía; escenarios: «un proyecto sin configuración y otro con un proveedor externo»
- Fuente: openspec/changes/20261021-235127-fjn-rag/specs/conocimiento/spec.md#los embeddings son configurables y locales por defecto

Tipo: funcional Sin configuración, `preguntar` SHALL pedir los embeddings a Ollama en la máquina local con `qwen3-embedding:0.6b`. `.factory/config.json` SHALL poder elegir otro modelo, otra URL, un proveedor compatible con la API de OpenAI (con la clave en la variable de entorno que nombre) o ninguno, y ningún texto del proyecto SHALL salir de la máquina a una URL que el proyecto no configuró.
