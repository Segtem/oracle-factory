# Tasks

- [x] Registrar el caso real y preparar propuesta, diseño y spec sin implementar.

- [x] Persona: revisar y aceptar proposal.md + spec.md.
- [x] Persona: renovar la aprobación por el alcance ampliado de preguntas abiertas y respuestas elaboradas.
- [x] Agente: importar requisitos Oracle y señalar lo aún sin medir.
- [x] Persona + agente: acordar medidas y evidencia para cada requisito.
- [ ] Agente: implementar y correr las pruebas del producto.
- [x] Agente: comprobar regresiones y mutaciones para consultas, respaldo documental y clientes.
- [x] Agente: actualizar evaluación por grupos, JSON, MCP, VS Code y documentación.
- [x] Agente: implementar elaboración de respuestas con modelo configurable y herramientas de sólo lectura.
- [x] Persona: elegir proveedor/modelo para la medición generativa real; agente configura sólo lo autorizado.
- [ ] Agente: crear verify_preguntar.py, proponer medidas y generar evidencia después de su confirmación humana.
- [ ] Revisor: revisar el diff; registrar y resolver hallazgos.
- [ ] Agente: correr Oracle sobre hechos observados.
- [ ] Persona: revisar el informe y decidir si se cierra.
- [ ] Persona: elegir integración y push.

Primera evidencia conservada en el candidato `beb247d`: 474 pruebas sin fallas, documental 21/22,
registro 6/6, negativas 3/3, generativa real 2/4 (insuficiente). Brian eligió Ollama con `qwen2.5:14b`
para la medición; no se configuró por defecto en el proyecto. Los informes iniciales de agy y agy2
quedaron registrados. Tras corregirlos pasan 15 pruebas específicas y se detectan 37 mutaciones;
se reproponen medidas por el control adicional del respaldo documental de producción y la corrida reforzada.
Faltan su confirmación por Brian, la evidencia actualizada, una vuelta independiente limpia y las decisiones finales.

Segunda revisión independiente: agy-2 y agy2-2, paquete incremental desde `beb247d` porque el diff completo supera el límite de Clue. Se añadieron regresiones adversariales de respaldo, antecedentes normativos, ejemplos numéricos, ordinales/versiones y contexto acumulado. Los hechos distinguen explícitamente ranking y respuesta con respaldo. Diagnóstico posterior: documental 21/22, registro 6/6, negativas 3/3, generativa real 2/4 con qwen2.5:14b. La calidad generativa sigue pendiente y no se propone aprobar. El catálogo de corrida ahora exige todas las mutaciones declaradas (37 actuales); las medidas fueron repropuestas y requieren nueva confirmación de Brian.

Tras comparar modelos se añadieron selección inicial de fuentes actuales, recuperación por alcance sin descartar embeddings de otros alcances, separación de exclusiones con cita literal y control explícito de pensamiento de Ollama. Pasan las 15 pruebas específicas y las 45 mutaciones declaradas. El catálogo y sus umbrales permanecen iguales a los confirmados por Brian el 2026-10-24 a las 18:25 UTC. Falta evidencia del candidato nuevo y revisión independiente.

Comparación solicitada por Brian: Qwen3.5:9b descargado (6,6 GB, digest 56671c2ab938), qwen2.5:14b y qwen3-coder:30b ya instalado. Con las mismas fuentes y citas por fragmento: 80,1 / 109,2 / 187,1 segundos para las 35 preguntas; los tres dieron 20/22 documental, 6/6 registro, 3/3 negativas y 3/4 generativa. Los modelos 9B y 30B omitieron la renovación de revisión; el 14B respondió esa parte y el control léxico no reconoció configuración/configuraciones. Se corrige el evaluador de conceptos positivos para tildes y plurales de -ción/-sión, con regresiones; no se cambian los casos de oro ni los umbrales. Las citas generativas ahora seleccionan fragmentos identificados y Factory copia sus textos consultados, rechazando IDs desconocidos o contradictorios. La primera corrida detectó 48/49 mutaciones: la prueba del contexto acumulado admitía un cierre posterior que ocultaba entregar fuentes sin presupuesto. Se reforzó para comprobar que esa entrega se rechaza antes de registrarse como exitosa; la corrida posterior detectó 49/49, con fuentes restauradas. Pasan 15 pruebas específicas. Sin cambio del modelo elegido ni del predeterminado del proyecto. Pendientes: evidencia formal y revisión independiente del candidato actual.

Evidencia 49369fc preservada y exitosa: 474 pruebas (10 omitidas), documental 20/22, registro 6/6, abiertas 4/4, negativas 3/3, fuentes estables. Se pidió la tercera revisión de agy y agy2 desde la base 4aba166. La inspección manual detectó una conclusión no respaldada sobre catálogos y vigencia que los conceptos mínimos no rechazaban: se suma esa expresión incorrecta a exclusiones de evaluación y se limita la instrucción a la pregunta y al respaldo explícito, incluidas negaciones. El diagnóstico real del mismo modelo deja de producirla. También se conserva la puntuación en los conceptos para no confundir C++ con C. Pruebas específicas 15 OK y 50/50 mutaciones detectadas. Falta nueva evidencia con estos controles reforzados y revisión limpia.

Tercera vuelta: ambos revisores identificaron el conteo en cláusula secundaria (AGY-PREGUNTAR-15 y GENERACION-ELABORAR-CONTEO-CLAUSULA-SECUNDARIA-OMITE-REGISTRO). Se inspeccionan todas las cláusulas reconocidas y se exige cada cálculo, no sólo el primero. La nueva regresión falló con el código anterior (ValueError not raised); cubre orden inverso y abiertos/cerrados en una pregunta. Un primer intento dejó una aserción de llamadas desactualizada (9 != 4); se preserva el log y no se usa su corrida de mutaciones. Tras ajustar la comprobación para las consultas originales: 15 pruebas OK y mutaciones-preguntar-17 con 51/51 detectadas y fuentes restauradas. Spec y medidas siguen confirmadas por Brian y no hay revisores corriendo. Pendiente evidencia final y nueva vuelta limpia.
