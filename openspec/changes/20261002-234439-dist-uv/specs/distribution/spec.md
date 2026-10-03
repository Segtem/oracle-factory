# Capability: distribution

### Requirement: instalar y seleccionar proyecto
The system SHALL expose oracle-factory from an installable Python package and operate on the explicitly selected project or current directory without writing to its installation.

#### Scenario: persona inicia otro proyecto
- WHEN ejecuta oracle-factory --proyecto una-carpeta init
- THEN se inicializan las herramientas en esa carpeta, preservando archivos existentes

### Requirement: conservar el flujo humano instalado
The system SHALL use packaged dependencies and retain scope approval, evidence, review and closure gates outside its own checkout.

#### Scenario: instalación aislada
- GIVEN un wheel instalado sin comandos Oracle o tasks globales
- WHEN se recorre el ejemplo en una carpeta temporal
- THEN la importación, la revisión, el juicio y el cierre funcionan con las dependencias del paquete

### Requirement: entregar artefactos verificables
The system SHALL provide a versioned prerelease with wheel, source distribution, checksums and instructions for manual PyPI publication.

#### Scenario: usuario publica el corte
- WHEN consulta el release
- THEN encuentra artefactos probados e instrucciones sin afirmaciones de publicación en PyPI ya realizada
