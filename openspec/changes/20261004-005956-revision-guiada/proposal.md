# Revisión guiada con pendientes y decisiones explícitas

## Why

Hoy `revision` acepta cualquier archivo no vacío y confía en el número de hallazgos aportado por el operador. Además, omitir `--hallazgos-abiertos` equivale a cero. Una plantilla con campos pendientes puede registrarse como aprobada sin que Factory detecte su falta de contenido.

Quien revisa necesita distinguir la preparación del informe, el análisis efectivamente realizado, las decisiones humanas sobre hallazgos y el registro final. Esto también facilita el relevo entre dos personas con sus agentes.

## What changes

- Agregar `revision-preparar ID`: crea dos documentos JSON en una carpeta nueva bajo la tarea, uno de informe y otro de decisiones. Captura el cambio y contexto actual, deja campos humanos pendientes y muestra cómo completarlos. No cambia gates ni asigna cero hallazgos.
- Agregar a `revision` el modo `--formato guiado --informe RUTA --decisiones RUTA`. Valida estructura, identidad de cambio, contexto, IDs y decisiones vinculadas al hash exacto del informe. Calcula hallazgos abiertos; no admite sustituirlos mediante un número manual.
- Separar observaciones del revisor y decisiones humanas. El informe tiene responsable, alcance revisado, comprobaciones, límites y hallazgos; el documento de decisiones tiene actor, motivo y resolución por ID. Un informe vacío de hallazgos exige una declaración explícita y motivada de quien revisó; no es aprobación automática.
- Mantener `--decision aprobar|cambios` y la confirmación humana. Antes de confirmar se muestran commit, tipo de revisión, completitud, límites, resoluciones y pendientes. Sólo permite aprobar una revisión declarada completa, con documentos completos y sin hallazgos abiertos.
- Archivar ambos documentos sin sobrescribir antecedentes y verificar sus hashes y el contexto al registrar y al cerrar. Una nueva revisión invalida el juicio previo. Cancelación, documentos inválidos o entradas modificadas no sustituyen una revisión vigente.
- Conservar el modo `libre` como valor por defecto por compatibilidad, rotulado como declaración humana sin validación estructural. Exigir `--hallazgos-abiertos` explícito en ese modo; eliminar el cero implícito. Los comandos existentes que ya pasan ese número siguen siendo válidos.
- Documentar el recorrido guiado y sus límites, con pruebas del contrato. Los comandos de una guía que instala una versión publicada anterior no se cambiarán por comandos aún no publicados; el nuevo recorrido indicará qué versión/checkout lo incorpora.

Clue conserva su función de preparar contexto y validar sus informes. Este corte toma su separación entre informe y triage como referencia; no introduce un segundo validador de sus schemas. Un informe de Clue o CodeRabbit puede usarse como antecedente del revisor, pero no se convierte ni se presenta como validado por Factory. Una integración automática de Clue queda fuera del corte.

## Out of scope

Generar hallazgos con IA, aprobar por ausencia de hallazgos, autenticar a los actores, demostrar que una corrección resuelve un defecto, decidir la pertinencia de medidas, ejecutar el sensor, coordinar escritores entre máquinas, modificar Oracle Task/Clue, publicar versiones y cerrar cambios reales automáticamente.

## Human decisions

El pedido «Bien vamos con la 1» selecciona esta tarea y autoriza preparar el contrato. La aceptación de esta propuesta y spec concretas queda pendiente antes de implementar.

Se recomienda el corte descrito: modo guiado optativo y modo libre compatible con cantidad explícita. La persona conserva la aprobación del alcance, el criterio de revisión, las resoluciones y el cierre. Las comprobaciones estructurales sólo acreditan consistencia del registro.
