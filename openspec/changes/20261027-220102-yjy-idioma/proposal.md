# Elegir el idioma de la propuesta y la spec de un cambio nuevo

## Why

La plantilla que crea `oracle-factory nuevo` mezcla idiomas sin explicarlo: la promesa dice «The system SHALL TODO: write one testable promise» y los pasos «GIVEN / WHEN / THEN» en inglés, mientras el resto del proyecto, los escenarios y los mensajes están en español. En el piloto, Brian lo notó al escribir su primera spec: «el requerimiento está en inglés y los escenarios en español». Propuso un parámetro `language` o una configuración global como la de Git.

## What changes

- `.factory/config.json` acepta `"idioma": "es"` o `"en"` (por defecto `es`). Cualquier otro valor se rechaza diciendo cuáles hay.
- `oracle-factory nuevo --idioma es|en` lo elige para un cambio, por encima del proyecto.
- La propuesta, la spec, el diseño y las tareas que crea `nuevo` salen enteros en ese idioma. En español: «Por qué», «Qué cambia», «Fuera de alcance», «Decisiones humanas», «El sistema DEBE…», «DADO / CUANDO / ENTONCES». En inglés: la plantilla de OpenSpec con todo su texto en inglés.
- Lo que el formato exige no se traduce: `# Capability:`, `## ADDED Requirements`, `### Requirement:`, `#### Scenario:`, `Tipo:` y la marca `TODO:` que impide aprobar con pendientes.
- Un cambio ya creado no se toca, y `importar` acepta una spec en cualquiera de los dos idiomas.

## Out of scope

- Traducir los mensajes de la CLI, la documentación o el tablero.
- Una configuración global del usuario (tipo `git config --global`): queda para otro cambio.
- Más idiomas que `es` y `en`.

## Human decisions

- Si el idioma por defecto es `es` (propuesto: el proyecto y sus personas trabajan en español) o `en` (lo que más se parece a la plantilla actual).
- Si «Tipo:» se queda como está en inglés (propuesto: lo lee Factory, no una persona ajena al proyecto).
