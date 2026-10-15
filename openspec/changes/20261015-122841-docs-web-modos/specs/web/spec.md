# Capability: web

## ADDED Requirements

### Requirement: los modos de trabajo están explicados
Tipo: funcional
`docs/modos.md` y `site/modos.html` SHALL explicar los tres modos y cuándo conviene cada uno, quién decide cada cosa en cada modo, los requisitos funcionales y no funcionales con `tipos_obligatorios`, cómo leer en `estado` quién decidió, propuso o confirmó, cómo cambiar de modo, un ejemplo real y los límites. La portada SHALL enlazar la página desde su tarjeta de los modos y el README SHALL enlazar el documento. La página SHALL tener idioma `es`, un solo `h1` y su contenido en el HTML.

#### Scenario: la página y el documento están completos
- GIVEN el sitio y la documentación
- WHEN se leen la página y el documento de los modos
- THEN los dos tienen las secciones de modos, quién decide, tipos, estado, cambiar de modo, ejemplo y límites, la portada enlaza la página y el README enlaza el documento

#### Scenario: la página se lee sin JavaScript
- GIVEN la página de los modos
- WHEN se lee sin ejecutar scripts
- THEN está en español, tiene un solo h1 y el texto está en el HTML

### Requirement: la tabla de quién decide coincide con el código
Tipo: funcional
La tabla de quién decide de `site/modos.html` y la de `docs/modos.md` SHALL decir, para cada decisión y cada modo, lo mismo que `modos.via_agente`: que decide el agente, que el agente propone y una persona confirma, o que decide sólo una persona.

#### Scenario: las tablas dicen lo que hace el código
- GIVEN las tablas de la página y del documento
- WHEN se comparan celda por celda con modos.via_agente
- THEN coinciden todas, y no falta ninguna decisión ni ningún modo

#### Scenario: una celda equivocada se detecta
- GIVEN una tabla con una celda que contradice al código
- WHEN se compara
- THEN la comparación nombra la decisión, el modo y lo que dice el código
