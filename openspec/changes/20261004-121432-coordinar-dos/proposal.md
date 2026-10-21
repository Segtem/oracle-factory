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

## Segundo corte: el banco de concurrencia (2026-10-21)

Brian pidió una prueba exhaustiva que ponga al límite que dos personas con agentes LLM trabajen sin interferirse, a la
vez o pasándose tareas a lo largo de una semana. El estado del arte dice que el aislamiento por worktree es necesario
pero no alcanza: los conflictos de agentes en paralelo son frecuentes (arXiv 2607.04697), hay cambios que pasan solos y
fallan juntos (arXiv 2609.25396), la asincronía trabaja sobre una vista vieja del estado (arXiv 2603.21489) y faltan
bancos que lo midan (arXiv 2608.18092). Factory ya aísla (clones, `tomar`, merge serializado), pero nunca se midió con
dos personas a la vez.

- Un banco que arma dos personas, cada una con su clon, su identidad de Git y un agente de prueba determinista, sobre
  un proyecto de prueba, e intercala sus acciones en un orden reproducible por una semilla, también en paralelo de
  verdad (procesos simultáneos).
- Escenarios sincrónicos: frentes en paralelo sobre archivos distintos, el mismo archivo (conflicto de texto), cambios
  que pasan solos y fallan juntos, dos `tomar` a la vez, decisiones simultáneas sobre un mismo registro, dos cambios
  creados con el mismo ID en dos clones, y los archivos que Factory genera y todos tocan (`resumen.md`, `kb/`,
  `oracle.json`, catálogos).
- Escenarios asincrónicos, en una semana simulada: un relevo que la otra persona retoma días después desde un clon
  atrasado, evidencia y revisión que quedan viejas cuando la otra integra antes, el registro de un cambio editado en dos
  ramas, mensajes del chat en paralelo, y trailers y vault en clones distintos.
- Un informe con sus métricas por escenario: si hubo conflicto y cuándo se detectó (antes, en o después del merge),
  decisiones perdidas o atribuidas a otra persona, evidencia vieja aceptada, y trabajo rehecho.
- Una corrida piloto con agentes reales (claude-code y codex) sobre el mismo proyecto, registrada aparte: no es
  reproducible y no es evidencia de Oracle, pero se compara con el banco.

Lo que el banco encuentre se corrige antes de cerrar este cambio, en él o en cambios propios.

## Out of scope

Scheduler de agentes, servicio central de locks (el banco mide sin él), sincronización automática, nuevas CLI de reserva/asignación, integración automática de Clue en Factory, cambios en oracle-task u oracle-clue, autenticación de personas, merges/publicaciones automáticos y garantía universal de ausencia de conflictos. El arnés simula participantes; no equivale a un piloto humano ni mide productividad.

## Human decisions

Brian eligió el 2026-10-21: agentes de prueba deterministas en el banco más una corrida con agentes reales registrada aparte, retomar este cambio para medirlo, y hacerlo antes del RAG.


Pendiente de aceptación de proposal.md y spec.md. La recomendación es aprobar primero este protocolo verificable antes de diseñar automatización distribuida. Para el piloto, las personas elegirán nombres reales, responsables de revisión/integración y el cambio de prueba; A y B son roles de ejemplo, no asignaciones reales.

La persona conserva alcance, aprobación de spec, pertinencia de medidas, resolución de hallazgos y cierre. Preparar esta tarea no acepta el protocolo ni autoriza implementarlo.
