# Guiar la revisión con un informe pendiente y decisiones explícitas

- ESTADO: ABIERTA
- PRIORIDAD: 30
- ETIQUETAS:

## Hallazgo y alcance

Factory acepta cualquier informe no vacío y el número de hallazgos declarado. Para un principiante eso puede dar una falsa sensación de revisión. Proponer una plantilla estructurada con campos pendientes, versión, archivos/casos comprobados, hallazgos y decisiones motivadas, límites y responsable. Sin hallazgos inventados, cero por defecto ni autoaprobación. Mejorar feedback de confirmación. El análisis exige revisor competente; no presentar el registro como verificación del contenido.

Origen: auditoría 20261003-235610-web-rigurosa, informes agy1/agy2 y lectura directa de la CLI. El contrato concreto fue aceptado después por el usuario y se implementó en rama; ver registro de aceptación y evidencia. La revisión y el cierre humanos permanecen pendientes.

### Nota (2026-10-04 00:59:56 UTC)

Registrada como mejora necesaria/propuesta a partir del pedido de revisar la web para principiantes. No se implementó ni simuló aprobación del producto.

## Próximo paso

Documentos del contrato aceptado:

- [Propuesta](../../openspec/changes/20261004-005956-revision-guiada/proposal.md).
- [Spec](../../openspec/changes/20261004-005956-revision-guiada/specs/revision-guiada/spec.md).
- [Diseño y casos](../../openspec/changes/20261004-005956-revision-guiada/design.md).
- [Plan](../../openspec/changes/20261004-005956-revision-guiada/tasks.md).

El usuario seleccionó esta tarea con «Bien vamos con la 1.». Se preparó el contrato en `tarea/20261004-005956-revision-guiada`, partiendo de `6af15e4` (incluye el protocolo de colaboración anterior). El pedido no se registra como aceptación de documentos que todavía no habían sido presentados. No se duplicó la tarea ni se implementó la CLI.

## Implementación y siguiente paso actual

Después de presentar el contrato, el usuario respondió «Se acepta la propuesta.». Esa aceptación está registrada sobre las huellas de proposal/spec. Se implementaron `revision-preparar`, formato guiado, decisiones separadas, abiertos derivados y conservación/vigencia de ambas copias; el modo libre exige ahora conteo explícito.

- [Guía de uso desde el checkout](../../docs/revision-guiada.md).
- [Mapeo de medidas aplicado](../../openspec/changes/20261004-005956-revision-guiada/medicion-propuesta.md), con límites explícitos de cobertura.
- Validación: 66 pruebas de la suite, incluidos 18 casos del contrato G1–G8, pasan. No es una revisión humana del producto.

Próximo paso: revisar el candidato actualizado con una persona/revisor competente. Registrar informe, decisiones y commit revisado; juzgar y cerrar sólo si corresponde. Los siete requisitos ya tienen medidas asociadas y conservan `sin_medir` para propiedades fuera de los casos seleccionados.

## Entrega histórica previa al mapeo

- Candidato: `109e2b579ec29c3bc87ba30c92599f81c9a6a79f`.
- [Revisión preparada y pendientes](revision-pendiente.md).
- [Evidencia del candidato](evidencia/resultado.json): 66 pruebas y 18 casos específicos, sin fallas ni omisiones.
- [Cobertura Oracle](evidencia/oracle-cobertura.txt): siete requisitos sin medir; [ocho reglas propuestas](evidencia/oracle-medidas-propuestas.txt) cumplen sobre los hechos, sin asociación ni aprobación implícita.

El informe y las decisiones de la revisión real quedaron pendientes mediante `revision-preparar` en un checkout del candidato. Clue preparó un paquete sin omisiones; no generó un análisis ni decisiones. Este archivo y sus adjuntos se archivan después del commit del producto, sin atribuirles una revisión humana.

### Nota (2026-10-04 13:01:14 UTC)

Propuesta, spec y diseño preparados: revision-preparar, informe guiado y decisiones separadas; modo libre compatible con conteo explícito. Pendiente aceptación humana de los documentos antes de implementar. OpenSpec: openspec/changes/20261004-005956-revision-guiada

### Nota (2026-10-04 13:04:46 UTC)

Contrato presentado aceptado por el usuario: «Se acepta la propuesta.», en respuesta a la aceptación de proposal.md y spec.md. Huellas registradas; no implica revisión aprobada ni cierre del producto.

### Nota (2026-10-04 13:04:46 UTC)

Requisitos importados: revision_guiada_c5794e24f22c4deb6.conservar_evidencia_y_comprobar_vigencia, revision_guiada_c5794e24f22c4deb6.derivar_pendientes_de_decisiones_separadas, revision_guiada_c5794e24f22c4deb6.explicar_y_verificar_los_limites_del_recorrido, revision_guiada_c5794e24f22c4deb6.mantener_formato_libre_con_declaracion_explicita, revision_guiada_c5794e24f22c4deb6.preparar_documentos_pendientes_sin_aprobar, revision_guiada_c5794e24f22c4deb6.registrar_confirmacion_humana_informada, revision_guiada_c5794e24f22c4deb6.validar_informe_guiado_y_su_alcance_declarado. Los nuevos nacen SIN MEDIR; verificá cobertura antes del juicio.

### Nota (2026-10-04 17:54:24 UTC)

Medidas de revision_guiada_c5794e24f22c4deb6.conservar_evidencia_y_comprobar_vigencia: factory_revision_guiada.conservar_evidencia_y_comprobar_vigencia, factory_revision_guiada.corrida_completa. SIN MEDIR: Casos seleccionados G1–G8 en Linux; no mide calidad del análisis ni autenticación o competencia de los actores.. Revisión y juicio anteriores invalidados; no se declara cumplimiento ni aprobación de pertinencia.

### Nota (2026-10-04 17:54:24 UTC)

Medidas de revision_guiada_c5794e24f22c4deb6.derivar_pendientes_de_decisiones_separadas: factory_revision_guiada.derivar_pendientes_de_decisiones_separadas, factory_revision_guiada.corrida_completa. SIN MEDIR: Casos seleccionados G1–G8 en Linux; no mide calidad del análisis ni autenticación o competencia de los actores.. Revisión y juicio anteriores invalidados; no se declara cumplimiento ni aprobación de pertinencia.

### Nota (2026-10-04 17:54:24 UTC)

Medidas de revision_guiada_c5794e24f22c4deb6.explicar_y_verificar_los_limites_del_recorrido: factory_revision_guiada.explicar_y_verificar_los_limites_del_recorrido, factory_revision_guiada.corrida_completa. SIN MEDIR: Casos seleccionados G1–G8 en Linux; no mide calidad del análisis ni autenticación o competencia de los actores. Claridad para principiantes pendiente de observación humana.. Revisión y juicio anteriores invalidados; no se declara cumplimiento ni aprobación de pertinencia.

### Nota (2026-10-04 17:54:24 UTC)

Medidas de revision_guiada_c5794e24f22c4deb6.mantener_formato_libre_con_declaracion_explicita: factory_revision_guiada.mantener_formato_libre_con_declaracion_explicita, factory_revision_guiada.corrida_completa. SIN MEDIR: Casos seleccionados G1–G8 en Linux; no mide calidad del análisis ni autenticación o competencia de los actores.. Revisión y juicio anteriores invalidados; no se declara cumplimiento ni aprobación de pertinencia.

### Nota (2026-10-04 17:54:24 UTC)

Medidas de revision_guiada_c5794e24f22c4deb6.preparar_documentos_pendientes_sin_aprobar: factory_revision_guiada.preparar_documentos_pendientes_sin_aprobar, factory_revision_guiada.corrida_completa. SIN MEDIR: Casos seleccionados G1–G8 en Linux; no mide calidad del análisis ni autenticación o competencia de los actores.. Revisión y juicio anteriores invalidados; no se declara cumplimiento ni aprobación de pertinencia.

### Nota (2026-10-04 17:54:24 UTC)

Medidas de revision_guiada_c5794e24f22c4deb6.registrar_confirmacion_humana_informada: factory_revision_guiada.registrar_confirmacion_humana_informada, factory_revision_guiada.corrida_completa. SIN MEDIR: Casos seleccionados G1–G8 en Linux; no mide calidad del análisis ni autenticación o competencia de los actores.. Revisión y juicio anteriores invalidados; no se declara cumplimiento ni aprobación de pertinencia.

### Nota (2026-10-04 17:54:24 UTC)

Medidas de revision_guiada_c5794e24f22c4deb6.validar_informe_guiado_y_su_alcance_declarado: factory_revision_guiada.validar_informe_guiado_y_su_alcance_declarado, factory_revision_guiada.corrida_completa. SIN MEDIR: Casos seleccionados G1–G8 en Linux; no mide calidad del análisis ni autenticación o competencia de los actores.. Revisión y juicio anteriores invalidados; no se declara cumplimiento ni aprobación de pertinencia.

### Nota (2026-10-04 17:54:48 UTC)

Continuación solicitada por el usuario: «Bien, sigamos entonces.». Se aplicó mediante fabrica.py medir el mapeo G1–G8 previamente presentado: medida del requisito y corrida_completa, conservando límites sin_medir. Esto no registra aprobación de revisión ni confirmación de cierre. Se prepara un nuevo candidato con cobertura parcial.
