# Tasks

- [x] Registrar el caso real y preparar propuesta, diseño y spec sin implementar.

- [x] Persona: revisar y aceptar proposal.md + spec.md.
- [x] Persona: renovar la aprobación por el alcance ampliado de preguntas abiertas y respuestas elaboradas.
- [x] Agente: importar requisitos Oracle y señalar lo aún sin medir.
- [ ] Persona + agente: acordar medidas y evidencia para cada requisito.
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
quedaron registrados. Tras corregirlos pasan 15 pruebas específicas y se detectan 29 mutaciones;
se reproponen medidas por el control adicional del respaldo documental de producción y la corrida reforzada.
Faltan su confirmación por Brian, la evidencia actualizada, una vuelta independiente limpia y las decisiones finales.
