# Capability: cli

## ADDED Requirements

### Requirement: la plantilla de un cambio nuevo trae la forma de OpenSpec
Tipo: funcional
`oracle-factory nuevo` SHALL crear una spec con `## ADDED Requirements` y un requisito con `Tipo: funcional`, y una propuesta cuyas decisiones humanas no nombran a una persona en particular. Mientras tengan TODO, `aprobar-spec` SHALL seguir rechazándolas.

#### Scenario: un cambio recién creado
- GIVEN un proyecto Factory
- WHEN se crea un cambio con nuevo
- THEN la spec trae ## ADDED Requirements y Tipo: funcional, la propuesta no nombra a Brian, y aprobar-spec la rechaza por los TODO

#### Scenario: la plantilla completada se importa
- GIVEN un cambio recién creado cuyos TODO se completaron sin tocar la estructura de la plantilla
- WHEN se aprueba la spec y se importan los requisitos
- THEN se importa un requisito funcional

### Requirement: medir dice qué medidas reemplaza
Tipo: funcional
Cuando un requisito ya tiene medidas y `medir` le asocia otras, `medir` SHALL nombrar las medidas que tenía y las nuevas, y SHALL señalar cada medida que deja de usar y que ningún otro requisito del proyecto usa.

#### Scenario: reemplazar las medidas de un requisito
- GIVEN un requisito medido con dos medidas, una de ellas usada también por otro requisito
- WHEN se le asocia una sola medida distinta
- THEN la salida nombra las dos anteriores y la nueva, y señala sin requisito sólo la que nadie más usa

#### Scenario: la primera vez no hay nada que reemplazar
- GIVEN un requisito sin medidas
- WHEN se le asocian medidas
- THEN la salida no habla de reemplazo

### Requirement: medir --listar separa las medidas del proyecto de las del catálogo base
Tipo: funcional
`medir ID --listar` SHALL mostrar primero las medidas del proyecto, con archivo, umbral, ámbito y alcance, y después, en una sección propia y una línea cada una, las del catálogo base de Oracle.

#### Scenario: un proyecto con medidas propias
- GIVEN un proyecto con medidas propias y el catálogo base de Oracle
- WHEN se lista con medir --listar
- THEN las medidas del proyecto van primero y con su detalle, y las del catálogo base van después, en su sección, una por línea
