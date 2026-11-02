# Capability: web

## ADDED Requirements

### Requirement: la portada explica el papel real de Clue
Tipo: funcional
La portada SHALL describir de forma coherente que Factory usa Oracle Clue para preparar el contexto de revisión y validar los informes externos. SHALL distinguir esas tareas del análisis del revisor configurado y de las decisiones de la persona según el modo del proyecto. SHALL NOT afirmar que Factory no invoca Clue ni atribuir al alpha de Clue una revisión automática con IA que no ofrece. La explicación SHALL ser consistente con la CLI y con docs/agentes.md.

#### Scenario: alguien consulta cómo funcionan las revisiones
- GIVEN la implementación de pedir-revision y la guía de agentes vigentes
- WHEN una persona lee las secciones de herramientas y revisores de la portada
- THEN ambas describen la preparación y validación con Clue sin negaciones contradictorias

#### Scenario: distinguir preparar de analizar y decidir
- GIVEN un revisor configurado en el proyecto y el alpha actual de Clue
- WHEN la portada explica el proceso de revisión
- THEN distingue el análisis externo, la preparación y validación con Clue y las decisiones de quien corresponda, sin prometer capacidades ausentes
