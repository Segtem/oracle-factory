# Explicar Oracle Factory de punta a punta

## Why

Oracle Factory coordina el kit para que agentes de IA puedan producir software completo con trazabilidad, mientras una persona conserva el control del alcance, los riesgos y la entrega. La CLI actual no permite entender de un vistazo ese flujo ni distinguir las herramientas y sus responsabilidades.

## What changes

Crear una web de portada en español con una escena animada de pixel art. La escena recorre el trabajo desde una idea hasta una entrega: OpenSpec convierte intención en requisitos; Trackertast organiza trabajo y bloqueos; agentes implementan y prueban; Oracle Clue revisa riesgos del cambio; Oracle evalúa evidencia contra requisitos; la persona decide en los puntos de control. La web aclara que Factory coordina el trabajo para producir el software completo, no que Clue u Oracle lo hagan por separado.

La persona debe poder avanzar, retroceder y pausar la animación, inspeccionar cada etapa y entender qué decide ella y qué hace cada herramienta. Se distinguen capacidades disponibles hoy de la visión futura.

## Out of scope

No construir automatización real de agentes, integrar APIs ni presentar las herramientas proyectadas como ya disponibles. No instalar CodeRabbit ni sustituirlo por Clue en el producto; la web describe el rol de revisión del kit. No agregar dependencias remotas para animación.

## Human decisions

La persona puede aceptar, editar, rechazar o pausar la spec; la web debe mostrar estas decisiones como parte del flujo, no como un paso ceremonial. La implementación se limita a una página estática demostrativa con controles accesibles.
