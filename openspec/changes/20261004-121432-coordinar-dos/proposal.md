# Coordinar dos personas con sus agentes sin interferencias

## Why

Dos personas deben poder avanzar con sus respectivos agentes sobre un mismo producto sin pisarse archivos, duplicar trabajo, perder decisiones ni reutilizar revisiones de otra versión. Separar ramas ayuda, pero no asigna responsabilidades, no sincroniza tareas entre clones ni resuelve la vigencia de evidencia al integrar.

Oracle Task conserva el trabajo y sus referencias; Oracle Clue prepara y valida el contexto de revisión; Factory coordina acuerdos, medidas y gates humanos. Falta un protocolo común que explique quién escribe, sobre qué versión, cuándo entrega y quién integra.

## What changes

Primer corte propuesto: una guía operativa en Factory, plantillas de asignación/relevo/integración y un ejercicio reproducible con dos participantes simulados, seguido por un piloto con dos personas y sus agentes. Se emplean las CLI existentes y Git; las reglas humanas se distinguen de las comprobaciones automáticas.

- Una tarea y paquete OpenSpec por cambio; un responsable humano y un único escritor activo de sus registros. Si dos frentes son independientes, cada uno tiene su cambio y referencias explícitas de dependencia.
- Una rama y checkout propios por frente activo: worktrees en una máquina o clones en máquinas distintas. Ambos leen el contexto común, pero no comparten directorio de escritura ni índice.
- Contrato de reparto: persona, agente/sesión, ID completo, base Git, rama, checkout, alcance/rutas, dependencias, responsable de revisión e integración y próximo paso. El alcance incluye interfaces compartidas, no sólo archivos.
- Relevo explícito al cambiar de persona o agente, y detención del frente afectado ante superposición; el otro frente independiente puede continuar.
- Revisión cruzada sobre commits identificados. Clue conserva paquete e informe vinculados y triage humano separado; Factory registra la decisión humana y evalúa evidencia del candidato de integración.
- Una persona serializa las integraciones y las mutaciones de Factory del candidato. Tras integrar se comprueba el estado resultante y se renuevan revisión/juicio cuando cambia su contexto.
- Matriz de casos observables y límites de las herramientas, incluyendo conflictos, interrupción, trabajo sin sincronizar y evidencia obsoleta.

El entregable será una guía enlazada desde README, plantillas y un arnés local de demostración. Los nombres de archivos y el detalle del arnés se concretarán al implementar el contrato aceptado. Las carencias que requieran cambios en las CLI se registrarán para propuestas posteriores en el repositorio dueño, sin inventar comandos existentes.

## Out of scope

Scheduler de agentes, servicio central de locks, sincronización automática, nuevas CLI de reserva/asignación, integración automática de Clue en Factory, cambios en oracle-task u oracle-clue, autenticación de personas, merges/publicaciones automáticos y garantía universal de ausencia de conflictos. El arnés simula participantes; no equivale a un piloto humano ni mide productividad.

## Human decisions

Pendiente de aceptación de proposal.md y spec.md. La recomendación es aprobar primero este protocolo verificable antes de diseñar automatización distribuida. Para el piloto, las personas elegirán nombres reales, responsables de revisión/integración y el cambio de prueba; A y B son roles de ejemplo, no asignaciones reales.

La persona conserva alcance, aprobación de spec, pertinencia de medidas, resolución de hallazgos y cierre. Preparar esta tarea no acepta el protocolo ni autoriza implementarlo.
