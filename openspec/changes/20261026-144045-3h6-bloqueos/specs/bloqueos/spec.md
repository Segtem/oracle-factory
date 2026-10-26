# Capability: bloqueos

## ADDED Requirements

### Requirement: el próximo paso sin revisor lo explica
Tipo: funcional
The system SHALL, when the next step is to request a review and the project has no reviewer configured, state what is missing and where to declare a reviewer (with an example) instead of offering a command with an unfilled placeholder.

#### Scenario: proyecto sin revisores
- GIVEN un cambio con medidas confirmadas y sin ningún revisor en .factory/config.json
- WHEN se consulta el próximo paso
- THEN el texto explica que falta un revisor y dónde declararlo, y no contiene el hueco NOMBRE

### Requirement: revisar bloqueado dice cómo seguir
Tipo: funcional
The system SHALL, when `revisar` is blocked for lack of a current candidate, reviewer reports or evidence, name the cause and the exact command to continue, using the configured reviewer.

#### Scenario: candidato sin informes
- GIVEN un cambio con un revisor configurado y un candidato sin informes de revisores
- WHEN una persona corre revisar
- THEN el bloqueo nombra la causa y el comando pedir-revision completo con ese revisor

### Requirement: revisar el producto de un primer commit
Tipo: funcional
The system SHALL accept `pedir-revision --base vacio` to build the review package against a base with no files, so that the whole product of a candidate whose code is in the first commit can be reviewed, without changing branches, history or Git configuration.

#### Scenario: código en el primer commit
- GIVEN un proyecto cuyo código está en su primer commit
- WHEN se pide una revisión con --base vacio
- THEN el paquete incluye los archivos del producto y ninguna rama, historia ni configuración de Git cambia

### Requirement: el paquete vacío nombra la salida
Tipo: funcional
The system SHALL, when a review request fails because the package has no product changes, say that `--base vacio` reviews the whole product.

#### Scenario: paquete sin cambios de producto
- GIVEN un candidato cuya base por defecto deja el paquete sin cambios de producto
- WHEN se pide la revisión sin --base
- THEN el error nombra la opción --base vacio
