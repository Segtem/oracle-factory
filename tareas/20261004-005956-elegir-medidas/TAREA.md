# Asociar medidas a requisitos sin editar indentación manualmente

- ESTADO: ABIERTA
- PRIORIDAD: 20
- ETIQUETAS:

## Hallazgo y alcance

La guía requiere abrir un .requisito generado y reemplazar sin_medir con cuatro espacios. Una persona principiante puede romper sintaxis o elegir otro requisito. Proponer un comando que liste requisitos/medidas y haga un enlace validado y atómico, conservando texto/fuente/ID. La pertinencia de las medidas sigue siendo decisión humana: no medir por defecto ni aprobar por existencia.

Origen: auditoría 20261003-235610-web-rigurosa, informes agy1/agy2 y lectura directa de la CLI. Esta tarea es una propuesta pendiente, no autorización para implementar una funcionalidad nueva.

### Nota (2026-10-04 00:59:56 UTC)

Registrada como mejora necesaria/propuesta a partir del pedido de revisar la web para principiantes. No se implementó ni simuló aprobación del producto.

### Nota (2026-10-04 01:32:56 UTC)

Contrato concreto preparado en openspec/changes/20261004-005956-elegir-medidas. Sin cambios de CLI ni aprobaciones terminal ficticias. La aceptación de propuesta/spec que exige AGENTS.md queda pendiente.

### Nota (2026-10-04 02:26:52 UTC)

Aceptación explícita del usuario: “Dale para el inicio guiado y elección de medidas”. Se registra el canal real conversación y las huellas de proposal.md/spec.md; no se simula una confirmación terminal ni una revisión de producto. Implementación en rama feat/20261004-005956-inicio-guiado.


### Nota (2026-10-04 02:31:41 UTC)

Requisitos importados: measurement_choice_cd6122f3d28654919.asociacion_explicita_y_valida, measurement_choice_cd6122f3d28654919.invalidar_evidencia_anterior, measurement_choice_cd6122f3d28654919.preservar_requisito_ante_error. Los nuevos nacen SIN MEDIR; verificá cobertura antes del juicio.

### Nota (2026-10-04 02:58:05 UTC)

Medidas de measurement_choice_cd6122f3d28654919.asociacion_explicita_y_valida: factory_guiada.asociacion_explicita_y_valida. SIN MEDIR: sin límite adicional declarado. Revisión y juicio anteriores invalidados; no se declara cumplimiento ni aprobación de pertinencia.

### Nota (2026-10-04 02:58:05 UTC)

Medidas de measurement_choice_cd6122f3d28654919.invalidar_evidencia_anterior: factory_guiada.invalidar_evidencia_anterior. SIN MEDIR: sin límite adicional declarado. Revisión y juicio anteriores invalidados; no se declara cumplimiento ni aprobación de pertinencia.

### Nota (2026-10-04 02:58:05 UTC)

Medidas de measurement_choice_cd6122f3d28654919.preservar_requisito_ante_error: factory_guiada.preservar_requisito_ante_error. SIN MEDIR: sin límite adicional declarado. Revisión y juicio anteriores invalidados; no se declara cumplimiento ni aprobación de pertinencia.

### Nota (2026-10-04 02:58:05 UTC)

El agente propuso y asoció medidas explícitas para los casos enumerados de tools/verify_contracts.py; retiró el marcador inicial sin medida. Cada alcance limita la interpretación a esos casos en Linux. La pertinencia/suficiencia quedan para revisión humana; esto no registra aprobación ni cierre.

- Adjunto: [factory-guided-validation.json](factory-guided-validation.json)

- Adjunto: [factory-guided-oracle.txt](factory-guided-oracle.txt)

- Adjunto: [factory-guided-facts.json](factory-guided-facts.json)

- Adjunto: [factory-guided-facts.manifest.json](factory-guided-facts.manifest.json)

- Adjunto: [factory-guided-guide.json](factory-guided-guide.json)

- Adjunto: [factory-guided-browser.json](factory-guided-browser.json)

- Adjunto: [factory-onboarding-agy1.md](factory-onboarding-agy1.md)

- Adjunto: [factory-onboarding-agy2.md](factory-onboarding-agy2.md)

- Adjunto: [factory-guided-agy2-code.md](factory-guided-agy2-code.md)

- Adjunto: [SHA256SUMS](SHA256SUMS)

### Nota (2026-10-04 03:04:36 UTC)

Implementado contrato aceptado y guía actualizada. 43 tests OK; wheel/sdist twine PASSED; wheel instalado con dependencias aisladas OK; 22 comandos del HTML OK; 11 controles Chromium OK. Oracle: seis requisitos nuevos cumplen sus medidas, trece previos sin medir. Agy1 actualizó guía y agy2 auditó diseño/código; sin bugs bloqueantes verificados. Se prepara corte 0.1.0a3, PyPI a cargo del mantenedor. Evidencia y hashes adjuntos; no hubo aprobación humana de revisión ni cierre real.

## Próximo paso

Revisar el commit de implementación, el informe técnico y la pertinencia/suficiencia de las seis medidas. Registrar la decisión humana con Factory, correr juzgar con hechos regenerados en ese commit y confirmar cierre sólo si corresponde. El corte alpha 0.1.0a3 queda preparado para publicación manual en PyPI; el agente no simula esos gates.
