# Capability: conocimiento

## ADDED Requirements

### Requirement: contar y listar specs
Tipo: funcional
The system SHALL answer questions of how many and which specs there are directly from the spec folders, reporting the current specs (one per capability) and the specs in open changes as separate numbers, and citing the files it read.

#### Scenario: cuántas specs hay
- GIVEN un proyecto con una spec vigente y un cambio abierto con otra spec
- WHEN se pregunta «cuántas specs hay»
- THEN la respuesta dice 1 vigente y 1 en cambios abiertos, y cita los archivos

#### Scenario: cuáles son
- GIVEN el mismo proyecto
- WHEN se pide la lista de specs
- THEN cada spec aparece con su capacidad, su estado y su ruta

### Requirement: filtro de specs no admitido
Tipo: funcional
The system SHALL reject, saying so, a question about specs that carries a filter it does not support, instead of falling back to loose passages.

#### Scenario: filtro por fecha
- GIVEN un proyecto con specs
- WHEN se pregunta «cuántas specs hay desde ayer»
- THEN la respuesta explica que ese filtro no está admitido y no lista pasajes

### Requirement: las demás preguntas no cambian
Tipo: funcional
The system SHALL keep answering questions about tasks and changes, and document questions, exactly as before.

#### Scenario: cambios abiertos
- GIVEN un proyecto con un cambio abierto
- WHEN se pregunta «cuántos cambios abiertos hay»
- THEN la respuesta sigue siendo la del registro de cambios
