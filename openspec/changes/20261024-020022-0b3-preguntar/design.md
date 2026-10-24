# Design

## Diagnóstico

`rag.py:preguntar` fusiona rankings y devuelve hasta ocho pasajes con puntuación positiva. RRF ordena candidatos: su
puntuación no es probabilidad de que respondan. El corpus no agrega registros; `evaluar` sólo busca rutas esperadas
entre los cinco primeros. Se reutilizará la clasificación vigente de `listar`/`tablero`, sin inferir fases de la prosa.

## Resolución

1. Aceptar preguntas abiertas sobre el proyecto. Un camino directo resuelve consultas simples de cantidad/listado sin
   modelo; un modelo configurado interpreta preguntas más amplias y combina información mediante herramientas validadas.
   No se promete comprensión universal. Una pregunta ambigua provoca aclaración, no la elección silenciosa de un filtro.
2. Para el registro, leer el estado en cada consulta y dar resultado exacto, filtro y fuentes/IDs comprobables, incluso
   cuando el resultado sea cero. No usar embeddings ni contar pasajes.
3. Para conocimiento, conservar corpus vigente, exclusiones y configuración de embeddings; recuperar fuentes y permitir
   consultas adicionales antes de redactar. Cada afirmación verificable debe llevar respaldo en las fuentes usadas.
   Aplicar un criterio explícito de respaldo, calibrado con positivos y negativos; RRF no es confianza. Si falta respaldo,
   decir «no encontré respaldo suficiente», sin prometer detectar universalmente preguntas sin respuesta.
4. Un filtro de estado fuera del alcance se comunica como no admitido. No usar similitudes documentales para afirmar
   datos del registro. Si se ofrecen pasajes, rotularlos como candidatos.

## Modelo y herramientas

El modelo generativo se configura aparte de los embeddings. Se contemplan Ollama local y un servicio compatible con
OpenAI elegido explícitamente, con claves en variables de entorno. No hay modelo generativo implícito, descarga automática
ni servicio externo de respaldo. Sin configuración o ante fallo se conserva la consulta directa al registro y la búsqueda
documental, avisando que no hubo elaboración generativa. Elegir el modelo de la medición real es una decisión posterior.

El modelo puede pedir recuperación documental y consultas tipadas del registro (listar/filtrar, contar/agrupar, estado,
decisiones, requisitos y trazabilidad). Se validan argumentos y se calculan agregados en código. Una operación no admitida
devuelve un límite explícito. El ciclo tiene límites de llamadas, tiempo y tamaño; una llamada inválida o un proveedor
fallido no habilitan shell, código arbitrario ni una escritura. Documentos y resultados son datos, no instrucciones para
cambiar esas reglas. Se registra qué fuentes y herramientas respaldan el resultado, sin guardar claves ni obligar a
versionar las conversaciones.

## Clientes y contrato

La respuesta distingue `registro`, `respuesta_elaborada`, `documentos`, `sin_respaldo` y `requiere_aclaracion` o
`consulta_no_admitida`, con pregunta, respuesta, filtros, fuentes, herramientas usadas y pasajes candidatos. Informa por
separado los modelos generativo y de embeddings, además de modo/aportes y notas por revisar. Si cambia el
contrato del JSON actual, se declara un esquema nuevo y se actualizan sus consumidores juntos. CLI, MCP y VS Code
usan el mismo resultado, sin tres lógicas de respuesta ni escrituras nuevas en el proyecto.

## Medición

Fixtures con abiertos, cerrados archivados, abandonados y proyecto vacío comprueban conteos, variantes, fuentes,
actualización tras un cierre e independencia de Ollama. Fixtures documentales separan respuesta relevante, coincidencia
casual y falta de respaldo. Se agregan preguntas abiertas que requieran combinar fuentes y herramientas, con variantes
reservadas para evaluación, respuestas mínimas esperadas y citas justificadas. Un modelo falso permite probar el flujo,
pero no acredita calidad generativa real. Una corrida con el modelo elegido mide esa calidad y sus límites.
Se conservan las 22 preguntas y el umbral humano ≥18/22 con embeddings. Los nuevos grupos informan errores, fidelidad de
citas y abstenciones por separado; sus medidas se proponen a Brian. Las pruebas deterministas no requieren red; la
medición real informa ambos modelos y límites. No se baja el umbral ni se oculta un grupo con el promedio de otros.

Cada arreglo tendrá regresión contra el código viejo y mutaciones detectadas. `tools/verify_preguntar.py` producirá
evidencia por contrato y suite completa con fuentes quietas, con catálogos por requisito más corrida completa.
La revisión usará agy y agy2 después de integrar la configuración autorizada en docs.
