# Capability: web

<!-- Generada por Oracle Factory al cerrar cada cambio: no se edita a mano. -->

## Requirements

### Requirement: la web explica cómo trabajar entre varias personas con sus agentes
Origen: 20261007-115805-web-y-docs · web_c5a0a7128a6a24b88.la_web_explica_como_trabajar_entre_varias_personas_con_sus_agentes
Tipo: funcional
El sitio SHALL tener una página, enlazada desde la portada, que explique el trabajo entre varias personas con sus agentes: reparto del trabajo, un checkout o una máquina por persona, quién decide qué según el modo, relevos, revisión independiente, integración con evidencia vigente y cierre por una persona; y SHALL decir qué no se probó todavía con personas reales.

#### Scenario: una persona llega a la portada
- GIVEN la portada del sitio
- WHEN busca cómo trabajar en equipo
- THEN encuentra un enlace a la página de colaboración, y la página tiene una sección para cada uno de esos temas y una sección de lo no probado

### Requirement: el sitio cuenta lo que trae la versión publicada
Origen: 20261007-115805-web-y-docs · web_c5a0a7128a6a24b88.el_sitio_cuenta_lo_que_trae_la_version_publicada
Tipo: funcional
La portada y la guía desde cero SHALL instalar la versión publicada en PyPI y SHALL presentar los modos de trabajo y `--agente`, la revisión guiada, la carpeta `.factory/`, la spec consolidada y el resumen del estado actual.

#### Scenario: quien instala desde la guía
- GIVEN la guía desde cero
- WHEN la lee de principio a fin
- THEN instala la versión publicada y sabe que existen los modos, la revisión guiada, la spec consolidada y el resumen, y cómo leer el resumen con formato

### Requirement: lo que la web nombra existe
Origen: 20261007-115805-web-y-docs · web_c5a0a7128a6a24b88.lo_que_la_web_nombra_existe
Tipo: no funcional
Cada subcomando y cada opción de `oracle-factory` que nombran el sitio y las guías de `docs/` SHALL existir en la CLI, y cada enlace interno del sitio SHALL apuntar a un archivo o a un ancla que existe.

#### Scenario: un comando que la CLI no tiene
- GIVEN una página que menciona `oracle-factory comando-inexistente`
- WHEN se corren las comprobaciones del sitio
- THEN fallan nombrando la página y el comando

### Requirement: guía de colaboración sin las fricciones del piloto
Origen: 20261007-115805-web-y-docs · web_c5a0a7128a6a24b88.guia_de_colaboracion_sin_las_fricciones_del_piloto
Tipo: funcional
`docs/colaboracion.md` SHALL resolver las fricciones 2, 3, 4, 5, 9 y 10 del piloto con agentes: archivos compartidos por diseño, commit de producto y commit de evidencia, actualización del reparto tras un relevo, registro de una integración de varios cambios, revisión de riesgos aceptados contra el candidato integrado y uso de `oracle cobertura --con` como verificación previa.

#### Scenario: una persona prepara un relevo
- GIVEN la guía de colaboración
- WHEN una persona busca qué commitear y qué actualizar al pasar el trabajo a otra
- THEN la guía lo dice en una sección propia, sin contradecir las plantillas

### Requirement: el ID de un cambio termina en un sufijo legible
Origen: 20261007-115805-web-y-docs · web_c5a0a7128a6a24b88.el_id_de_un_cambio_termina_en_un_sufijo_legible
Tipo: funcional
`nuevo` SHALL terminar el ID del cambio en la capacidad, o en el sufijo de `--sufijo` si se indica, y SHALL rechazar antes de crear nada un sufijo que no sea de minúsculas, números y guiones, empezando con letra y de hasta 40 caracteres.

#### Scenario: sin sufijo
- GIVEN un proyecto Factory
- WHEN se crea un cambio con capacidad `notas` sin `--sufijo`
- THEN su ID termina en `-notas`

#### Scenario: sufijo inválido
- GIVEN un proyecto Factory
- WHEN se crea un cambio con `--sufijo Con_Mayusculas`
- THEN se rechaza sin crear tarea ni archivos

### Requirement: la guía desde cero sigue funcionando
Origen: 20261007-115805-web-y-docs · web_c5a0a7128a6a24b88.la_guia_desde_cero_sigue_funcionando
Tipo: no funcional
Los comandos de la guía desde cero SHALL seguir funcionando de punta a punta con el paquete instalado, y la página nueva SHALL tener idioma declarado, un solo `h1`, navegación de vuelta a la portada y su contenido legible sin JavaScript.

#### Scenario: arnés de la guía
- GIVEN el paquete construido e instalado en un entorno limpio
- WHEN se corre el arnés de la guía
- THEN todos sus comandos funcionan

### Requirement: los modos de trabajo están explicados
Origen: 20261015-122841-docs-web-modos · web_cd28e54c150c790c2.los_modos_de_trabajo_estan_explicados
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
Origen: 20261015-122841-docs-web-modos · web_cd28e54c150c790c2.la_tabla_de_quien_decide_coincide_con_el_codigo
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
