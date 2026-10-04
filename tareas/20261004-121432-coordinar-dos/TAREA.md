# Coordinar dos personas con sus agentes sin interferencias

- ESTADO: ABIERTA
- PRIORIDAD: 50
- ETIQUETAS: colaboracion, propuesta

## Objetivo

Definir y validar cómo trabajan dos personas con sus respectivos agentes sobre un producto compartido: reparto, aislamiento, relevo, revisión cruzada e integración con evidencia vigente.

## Entregable

[Guía operativa](../../docs/colaboracion.md), plantillas y demostración reproducible; piloto posterior con dos personas. Task conserva el trabajo, Clue vincula revisión a una versión, Factory controla acuerdos/gates y Oracle juzga únicamente requisitos medidos.

## Acuerdo y siguiente paso

- [Propuesta](../../openspec/changes/20261004-121432-coordinar-dos/proposal.md)
- [Spec](../../openspec/changes/20261004-121432-coordinar-dos/specs/colaboracion/spec.md)
- [Diseño, diagnóstico y casos](../../openspec/changes/20261004-121432-coordinar-dos/design.md)
- [Plan](../../openspec/changes/20261004-121432-coordinar-dos/tasks.md)

Rama de preparación: `tarea/colaboracion-personas-agentes`.
Responsables del piloto: pendientes de asignación humana; A/B son roles de ejemplo.
Propuesta/spec aceptadas en conversación mediante «Bien, continuemos.» y sus huellas registradas en Factory. La tarea permanece ABIERTA: implementación preparada, requisitos importados y medidas parciales asociadas. Próximo paso humano: asignar el piloto y revisar el candidato, incluyendo pertinencia de las medidas; todavía faltan esa experiencia, decisión de revisión y cierre.

Relacionadas: `20261004-005956-evidencia-origen` y `20261004-005956-revision-guiada`. Las referencias no implican dependencias verificadas por Task.

## Candidato y evidencia

- Candidato de implementación: `4ceb4b075a50290d014e3d7ec4714774c4417d81`.
- [Revisión preparada, pendiente de persona](revision-pendiente.md); contexto de Clue conservado en checkout separado.
- [Validación](evidencia/validacion.json): 48 pruebas de la suite; C1–C9 exitosos; seis requisitos cumplen sólo en lo medido.
- [Piloto pendiente](piloto-pendiente.md): participantes e integrador aún sin asignar.

Los documentos aceptados permanecen intactos. Las medidas parciales fueron elegidas por el agente y asociadas con la CLI; su pertinencia/suficiencia humana sigue pendiente. No se ejecutó revisión aprobada ni cierre del cambio real.

### Nota (2026-10-04 12:14:32 UTC)

OpenSpec: openspec/changes/20261004-121432-coordinar-dos. Estado de factory: espera aprobación humana de proposal.md y spec.md.

### Nota (2026-10-04 12:20:14 UTC)

Aceptación humana de proposal.md y spec.md en conversación: «Bien, continuemos.». Se registra sobre las huellas de la propuesta preparada; no implica aprobación de revisión, medidas ni cierre.

### Nota (2026-10-04 12:20:15 UTC)

Requisitos importados: colaboracion_c20a7f5e3d414985d.aislamiento_y_sincronizacion_explicitos, colaboracion_c20a7f5e3d414985d.demostracion_reproducible_con_limites, colaboracion_c20a7f5e3d414985d.integracion_serializada_y_evidencia_vigente, colaboracion_c20a7f5e3d414985d.relevo_recuperable, colaboracion_c20a7f5e3d414985d.reparto_explicito_del_trabajo, colaboracion_c20a7f5e3d414985d.revision_vinculada_a_una_version. Los nuevos nacen SIN MEDIR; verificá cobertura antes del juicio.

### Nota (2026-10-04 12:24:12 UTC)

Requisitos importados: colaboracion_c20a7f5e3d414985d.aislamiento_y_sincronizacion_explicitos, colaboracion_c20a7f5e3d414985d.demostracion_reproducible_con_limites, colaboracion_c20a7f5e3d414985d.integracion_serializada_y_evidencia_vigente, colaboracion_c20a7f5e3d414985d.relevo_recuperable, colaboracion_c20a7f5e3d414985d.reparto_explicito_del_trabajo, colaboracion_c20a7f5e3d414985d.revision_vinculada_a_una_version. Los nuevos nacen SIN MEDIR; verificá cobertura antes del juicio.

### Nota (2026-10-04 12:31:25 UTC)

Medidas de colaboracion_c20a7f5e3d414985d.aislamiento_y_sincronizacion_explicitos: factory_colaboracion.aislamiento_y_sincronizacion_explicitos, factory_colaboracion.corrida_completa. SIN MEDIR: Pilotaje en máquinas distintas y migración de dos tareas nuevas con ID colisionado sin medir; el arnés observa worktrees y clones locales divergentes.. Revisión y juicio anteriores invalidados; no se declara cumplimiento ni aprobación de pertinencia.

### Nota (2026-10-04 12:31:25 UTC)

Medidas de colaboracion_c20a7f5e3d414985d.demostracion_reproducible_con_limites: factory_colaboracion.demostracion_reproducible_con_limites, factory_colaboracion.corrida_completa. SIN MEDIR: Piloto con dos personas y sus agentes pendiente; usabilidad y productividad no medidas por el arnés.. Revisión y juicio anteriores invalidados; no se declara cumplimiento ni aprobación de pertinencia.

### Nota (2026-10-04 12:31:25 UTC)

Medidas de colaboracion_c20a7f5e3d414985d.integracion_serializada_y_evidencia_vigente: factory_colaboracion.integracion_serializada_y_evidencia_vigente, factory_colaboracion.corrida_completa. SIN MEDIR: Autoridad del integrador, resolución humana de conflictos y suficiencia del sensor del producto sin medir; aprobaciones fixture sólo en temporales.. Revisión y juicio anteriores invalidados; no se declara cumplimiento ni aprobación de pertinencia.

### Nota (2026-10-04 12:31:25 UTC)

Medidas de colaboracion_c20a7f5e3d414985d.relevo_recuperable: factory_colaboracion.relevo_recuperable, factory_colaboracion.corrida_completa. SIN MEDIR: Recepción y recuperación reales por personas sin medir; el arnés sólo simula responsables y un proceso fixture terminado.. Revisión y juicio anteriores invalidados; no se declara cumplimiento ni aprobación de pertinencia.

### Nota (2026-10-04 12:31:25 UTC)

Medidas de colaboracion_c20a7f5e3d414985d.reparto_explicito_del_trabajo: factory_colaboracion.reparto_explicito_del_trabajo, factory_colaboracion.corrida_completa. SIN MEDIR: Acuerdo real de reparto, confirmación de ambas personas y aplicación de escritor único pendientes de piloto humano.. Revisión y juicio anteriores invalidados; no se declara cumplimiento ni aprobación de pertinencia.

### Nota (2026-10-04 12:31:25 UTC)

Medidas de colaboracion_c20a7f5e3d414985d.revision_vinculada_a_una_version: factory_colaboracion.revision_vinculada_a_una_version, factory_colaboracion.corrida_completa. SIN MEDIR: Calidad y suficiencia de la revisión cruzada y de decisiones humanas sin medir; Clue valida integridad con informe fixture.. Revisión y juicio anteriores invalidados; no se declara cumplimiento ni aprobación de pertinencia.
