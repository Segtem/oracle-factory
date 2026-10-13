# Capability: onboarding

<!-- Generada por Oracle Factory al cerrar cada cambio: no se edita a mano. -->

## Requirements

### Requirement: preparar ejemplo sin aprobacion
Origen: 20261004-005956-inicio-guiado · onboarding_ca007f9416d32e171.preparar_ejemplo_sin_aprobacion
The system SHALL prepare an example-backed change with complete editable documents and catalogs, without approving the specification or assigning measurements.

#### Scenario: primer cambio
- GIVEN proyecto inicializado y destinos libres
- WHEN la persona crea un cambio con --con-ejemplo notas
- THEN recibe el ID completo y rutas exactas, y el cambio espera aprobación humana

### Requirement: preservar archivos existentes
Origen: 20261004-005956-inicio-guiado · onboarding_ca007f9416d32e171.preservar_archivos_existentes
The system SHALL reject conflicting example destinations before creating a new task, without overwriting existing files.

#### Scenario: catalogo ya existe
- GIVEN un catálogo de notas existente
- WHEN solicita crear otro cambio con el ejemplo
- THEN recibe la ruta conflictiva y se conservan los archivos y tareas anteriores

### Requirement: recuperar cambios y siguiente paso
Origen: 20261004-005956-inicio-guiado · onboarding_ca007f9416d32e171.recuperar_cambios_y_siguiente_paso
The system SHALL list existing Factory changes with full IDs and current phases, and explain the next manual action after setup.

#### Scenario: terminal nueva
- WHEN la persona ejecuta listar desde el proyecto
- THEN puede recuperar un ID real sin crear otra tarea ni adivinarlo
