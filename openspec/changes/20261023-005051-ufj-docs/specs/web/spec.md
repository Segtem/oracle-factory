# Capability: web

## ADDED Requirements

### Requirement: la documentación cuenta lo que Factory hace hoy
Tipo: funcional
El README SHALL describir Factory tal como está (sin presentarla como una prueba de concepto ni decir que no coordina agentes o que el análisis con IA está pendiente) y SHALL tener un apartado por herramienta con su enlace a una guía; `docs/` SHALL tener guías del tablero y el trabajo de a dos, del conocimiento del proyecto y de los agentes, y las guías existentes SHALL usar `oracle-factory` en lugar de `fabrica.py`. La portada de la web SHALL presentar como disponible lo que ya está disponible y enlazar esas guías.

#### Scenario: alguien llega al proyecto
- GIVEN el README, docs/ y la portada de la web
- WHEN se leen buscando cómo usar el tablero, preguntar, el MCP y la guía para agentes
- THEN cada uno tiene su apartado y su guía enlazada, y ninguno de los textos dice que Factory es una POC, que no coordina agentes o que esas herramientas están por venir

### Requirement: la documentación se comprueba contra la CLI
Tipo: funcional
Una comprobación automática SHALL fallar si un subcomando de la CLI no aparece en el README ni en `docs/`, si el README, `docs/` o la web nombran un `oracle-factory X` que no es un subcomando, o si nombran una versión de Factory distinta de la de `pyproject.toml` (salvo en las notas de versión y en el historial de versiones del README).

#### Scenario: un comando nuevo sin documentar, y uno que ya no existe
- GIVEN la documentación al día
- WHEN se agrega un subcomando sin mencionarlo, o un texto nombra oracle-factory un-comando-que-no-existe, o una página dice otra versión
- THEN la comprobación falla nombrando el comando o la versión y el archivo, y con la documentación al día pasa
