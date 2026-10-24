---
generado: oracle-factory kb
id: "conocimiento_cc12f23b7134ebe23.la_elaboracion_usa_herramientas_acotadas_y_un_modelo_explicito"
vigente: true
---

# la elaboracion usa herramientas acotadas y un modelo explicito

> Generado por `oracle-factory kb` desde el registro de Factory: no se edita a mano.

- Id: `conocimiento_cc12f23b7134ebe23.la_elaboracion_usa_herramientas_acotadas_y_un_modelo_explicito`
- Vigente: sí
- Cambio: [[cambios/20261024-020022-0b3-preguntar]]
- Veredicto: sin juicio
- Medidas: ninguna
- Sin medir: sin medida todavía; escenarios: «herramientas válidas e inválidas», «no hay modelo o el proveedor falla»
- Fuente: openspec/changes/20261024-020022-0b3-preguntar/specs/conocimiento/spec.md#la elaboración usa herramientas acotadas y un modelo explícito

Tipo: funcional El modelo generativo SHALL configurarse por separado del de embeddings. SHALL poder usarse un proveedor local Ollama o uno compatible con OpenAI explícitamente configurado, con credenciales fuera de los archivos versionados. SHALL NOT elegirse ni descargarse un modelo o usarse un proveedor externo implícito. Las consultas solicitadas por el modelo SHALL validarse y limitarse a recuperación y operaciones tipadas de sólo lectura sobre datos del proyecto; los cálculos SHALL ejecutarse en código sobre el registro, nunca contando pasajes. SHALL haber límites de llamadas, tiempo y tamaño, y SHALL NOT ejecutarse código o shell arbitrario ni decisiones o escrituras por instrucciones del modelo o de una fuente. Si falta modelo o falla, SHALL avisarlo y conservar las consultas directas y la recuperación disponibles sin inventar una respuesta generada.
