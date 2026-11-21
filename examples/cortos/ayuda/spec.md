# Capability: ayuda

## ADDED Requirements

### Requirement: primer paso accesible
Tipo: funcional
La página de uso DEBE enlazar el primer paso mediante una ruta relativa que exista en el proyecto.

#### Scenario: enlace presente o roto
- DADA la página uso.md
- CUANDO se sigue el enlace primer paso
- ENTONCES pasos.md existe; si el destino cambia a uno ausente, el sensor informa falla
