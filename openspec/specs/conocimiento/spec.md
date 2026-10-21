# Capability: conocimiento

<!-- Generada por Oracle Factory al cerrar cada cambio: no se edita a mano. -->

## Requirements

### Requirement: el vault se genera del registro y no se desfasa
Origen: 20261020-140603-kb · conocimiento_cfa7b831bdad34a61.el_vault_se_genera_del_registro_y_no_se_desfasa
Tipo: funcional
`oracle-factory kb` SHALL escribir en `kb/` una nota por cambio (título, fase, responsable, requisitos con su veredicto, decisiones con quién, cuándo y su motivo, riesgos aceptados, commits y mensajes), una por requisito (texto, medidas, cambio que lo trajo y si está vigente) y un índice, enlazadas con wikilinks de Obsidian, con un texto que no depende de cuándo se genera. `kb --verificar` SHALL fallar, sin escribir, si `kb/` no coincide con el registro, y el vault SHALL regenerarse solo en cada decisión que cambia el estado de un cambio.

#### Scenario: un proyecto con un cambio cerrado y otro abierto
- GIVEN un proyecto con un cambio cerrado con revisión, veredicto y un riesgo aceptado, y otro abierto con un responsable
- WHEN se corre oracle-factory kb y después kb --verificar
- THEN hay una nota por cambio y por requisito con esos datos y enlaces que resuelven, y la verificación pasa

#### Scenario: el vault queda viejo
- GIVEN un vault generado
- WHEN una persona aprueba la spec de un cambio, y alguien edita a mano una nota generada
- THEN el vault se regeneró con la aprobación, y kb --verificar falla por la nota editada sin tocarla

### Requirement: una nota humana vence cuando cambian sus fuentes
Origen: 20261020-140603-kb · conocimiento_cfa7b831bdad34a61.una_nota_humana_vence_cuando_cambian_sus_fuentes
Tipo: funcional
Una nota en `kb/notas/` con `fuentes:` en su frontmatter SHALL quedar «por revisar» cuando cambia el contenido de alguna fuente desde que se marcó revisada; `kb --verificar` SHALL listarla y fallar, y `estado` SHALL avisarla en los cambios abiertos que tocaron esa fuente. `oracle-factory kb revisada NOTA` SHALL marcarla revisada sólo desde la terminal de una persona, y una fuente que no existe SHALL ser un error que nombra la nota.

#### Scenario: una guía cuyo archivo cambió
- GIVEN una nota con fuente oracle_factory/cli.py marcada revisada
- WHEN un cambio abierto modifica ese archivo
- THEN kb --verificar falla nombrando la nota y la fuente, estado del cambio lo avisa, y después de kb revisada (persona) pasa

#### Scenario: revisar sin terminal o una fuente que no existe
- GIVEN una nota con una fuente que no existe, y otra por revisar
- WHEN un agente corre kb revisada sobre la segunda, y se pide kb --verificar
- THEN la marca se niega, y la verificación nombra la nota con la fuente inexistente

### Requirement: por qué existe una línea
Origen: 20261020-140603-kb · conocimiento_cfa7b831bdad34a61.por_que_existe_una_linea
Tipo: funcional
`oracle-factory por-que ARCHIVO:LÍNEA` (y `--json`) SHALL ir del commit que escribió esa línea a su cambio (por el trailer, o deducido de sus commits) y SHALL mostrar sus requisitos con su veredicto, las decisiones con quién, cuándo y su motivo, los riesgos aceptados y hallazgos sobre ese archivo, y las notas humanas que lo tienen como fuente; si la línea no es de ningún cambio, SHALL decirlo con su commit. La extensión de VS Code SHALL mostrarlo para la línea del cursor sin modificar nada.

#### Scenario: una línea escrita en un cambio cerrado
- GIVEN un archivo con una línea agregada por un commit de un cambio cerrado que tiene un riesgo aceptado sobre ese archivo, y una nota humana con ese archivo como fuente
- WHEN se pide oracle-factory por-que ARCHIVO:LÍNEA --json, y el comando de VS Code sobre esa línea
- THEN aparecen el commit, el cambio, sus requisitos con veredicto, la aprobación de la spec con quién y cuándo, el riesgo aceptado con su motivo y la nota

#### Scenario: una línea que no es de ningún cambio
- GIVEN una línea escrita por un commit sin trailer y fuera de los commits de cualquier cambio
- WHEN se pide oracle-factory por-que ARCHIVO:LÍNEA
- THEN dice que esa línea no es de ningún cambio de Factory y nombra su commit
