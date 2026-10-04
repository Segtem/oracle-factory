# Capability: measurement_choice

## ADDED Requirements

### Requirement: asociacion explicita y valida
The system SHALL only associate explicitly selected existing measurements with a requirement imported by the current approved change.

#### Scenario: requisito ajeno
- GIVEN un requisito perteneciente a otro cambio
- WHEN se intenta asociarlo con medir
- THEN se rechaza sin modificar requisitos ni registros

### Requirement: preservar requisito ante error
The system SHALL preserve the original requirement when a selected measurement is missing, the requirement is invalid or writing fails.

#### Scenario: medida inexistente
- WHEN se elige una medida que no está en el catálogo
- THEN se informa el error y el archivo conserva sus bytes originales

### Requirement: invalidar evidencia anterior
The system SHALL invalidate the change review and judgement when its measurement associations change, while retaining requirement identity, source and text.

#### Scenario: cambio de medida
- GIVEN una revisión y juicio previos
- WHEN la persona modifica la asociación explícitamente
- THEN se requiere nueva revisión y juicio, sin cierre automático
