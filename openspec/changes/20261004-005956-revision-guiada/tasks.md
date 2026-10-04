# Tasks

- [x] Recuperar tarea existente e inspeccionar revisión actual, gates, tests y formato de Clue.
- [x] Preparar propuesta/spec/diseño en rama propia, sin duplicar la tarea ni implementar.
- [x] Verificar enlaces/integridad y lectura de la spec con Oracle 0.38.1 en modo sin escritura: siete requisitos reconocidos; ninguno importado todavía.
- [x] Persona: aceptar proposal.md y spec.md presentados. Respuesta del usuario: «Se acepta la propuesta.»; canal y huellas registrados.
- [x] Agente: importar con `fabrica.py importar`; los siete requisitos nacieron sin medir.
- [x] Persona + agente: aplicar el mapeo presentado tras «Bien, sigamos entonces.»; siete requisitos con medidas asociadas y límites explícitos sin medir.
- [x] Agente: preparar reglas y mapeo propuesto, verificados con Oracle sin asociarlos a los requisitos reales.
- [x] Agente: implementar preparación de documentos pendientes y validación del formato guiado.
- [x] Agente: separar decisiones, derivar abiertos y mejorar confirmación/archivo/vigencia.
- [x] Agente: mantener modo libre e históricos rotulados y exigir conteo explícito para nuevos registros libres.
- [x] Agente: documentar recorrido de checkout y compatibilidad de versiones; 66 pruebas, incluidos 18 casos de G1–G8, pasan.
- [x] Agente: registrar candidato `109e2b579ec29c3bc87ba30c92599f81c9a6a79f`; guardar evidencia y contexto de Clue en checkout estable, sin omisiones.
- [x] Agente: preparar informe/decisiones pendientes sobre ese candidato mediante la nueva CLI, sin completar campos humanos.
- [ ] Revisor: guardar informe; persona: resolver hallazgos y registrar decisión sobre el commit efectivamente revisado.
- [x] Agente: ejecutar Oracle sobre evidencia: ocho reglas propuestas pasan; siete requisitos reales continúan sin medir, sin gate verde de Factory.
- [ ] Persona: confirmar por escrito el cierre si corresponde.

Implementación lista para revisión. El mapeo está aplicado con cobertura parcial; la revisión humana y el cierre siguen pendientes. Las ejecuciones y candidatos anteriores que se enumeran arriba conservan su alcance histórico. La claridad del recorrido no se mide con fixtures.

- [x] Continuación: mapeo aplicado en `5b54dc8`, nueva ejecución estable de 66 pruebas/18 casos, cobertura parcial de los siete requisitos y dossier actualizado con documentos pendientes. Clue dividido en implementación y mapeo por su límite de tamaño; alcance explicado en el dossier.
