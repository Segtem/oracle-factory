# Capability: notas

## ADDED Requirements

### Requirement: titulo valido
The system SHALL reject empty or whitespace-only titles and accept titles containing text.

#### Scenario: título vacío
- WHEN el título es una cadena vacía
- THEN no se puede guardar la nota

#### Scenario: título con espacios
- WHEN el título contiene solo espacios
- THEN no se puede guardar la nota

#### Scenario: título con texto
- WHEN el título es Mi nota
- THEN se puede guardar la nota
