# Corregir la descripción de Oracle Clue en la portada

## Why

La portada dice «Factory no invoca Clue», aunque pedir-revision lo usa para preparar paquetes y validar informes. En la misma página se describe correctamente ese flujo más abajo. Quien llega al proyecto recibe dos explicaciones incompatibles. Brian pidió priorizar terminar Factory actual y dejar las migraciones en diferido.

## What changes

Explicar de manera consistente que Factory invoca Oracle Clue para preparar contexto y validar informes; el análisis lo hace el revisor configurado y las decisiones corresponden a la persona según el modo. Conservar el límite del alpha de Clue: no hace por sí mismo la revisión automática con IA. Contrastar la portada con la CLI y docs/agentes.md.

## Out of scope

No agregar agentes, herramientas de escritura MCP ni integración con harnesses. No cambiar el flujo de revisión, versiones de dependencias, modos, medidas de otros cambios ni configuración Git. Factory Go y Oracle Rust quedan diferidos. Pushes, tag y release de 0.1.0a14 siguen reservados a Brian.

## Human decisions

Brian aprueba esta spec antes de implementar y confirma medidas, revisión y cierre por el flujo habitual. La comprobación lingüística tiene alcance limitado: no acredita comprensión de una persona principiante.
