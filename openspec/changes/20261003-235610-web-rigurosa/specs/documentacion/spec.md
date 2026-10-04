# Documentación del alpha publicado

## ADDED Requirements

### Requirement: Correspondencia con el producto
La web MUST distinguir el flujo disponible en Factory 0.1.0a2 de las capacidades previstas.

#### Scenario: conocer el alcance
- GIVEN una persona visita la portada y recorre la escena
- WHEN lee las responsabilidades y salidas
- THEN reconoce qué ejecuta Factory, qué hacen herramientas externas y qué decide una persona.

### Requirement: Guía reproducible
La guía MUST describir cada comando, archivo y confirmación necesarios para el ejemplo local.

#### Scenario: proyecto vacío
- GIVEN el kit publicado instalado con uv en un entorno aislado
- WHEN se ejecutan los pasos de la guía en una carpeta nueva
- THEN el ejemplo se puede completar hasta el cierre fixture sin inventar aprobaciones reales.

### Requirement: Límites de la evidencia
La web MUST explicar el alcance de medidas, pruebas, revisión y cierre local.

#### Scenario: interpretación del verde
- GIVEN Oracle confirma las medidas del ejemplo
- WHEN una persona lee el resultado
- THEN entiende qué propiedades y observaciones lo sostienen y qué no se verificó.
