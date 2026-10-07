# Capability: web

## ADDED Requirements

### Requirement: la web explica cómo trabajar entre varias personas con sus agentes
Tipo: funcional
El sitio SHALL tener una página, enlazada desde la portada, que explique el trabajo entre varias personas con sus agentes: reparto del trabajo, un checkout o una máquina por persona, quién decide qué según el modo, relevos, revisión independiente, integración con evidencia vigente y cierre por una persona; y SHALL decir qué no se probó todavía con personas reales.

#### Scenario: una persona llega a la portada
- GIVEN la portada del sitio
- WHEN busca cómo trabajar en equipo
- THEN encuentra un enlace a la página de colaboración, y la página tiene una sección para cada uno de esos temas y una sección de lo no probado

### Requirement: el sitio cuenta lo que trae la versión publicada
Tipo: funcional
La portada y la guía desde cero SHALL instalar la versión publicada en PyPI y SHALL presentar los modos de trabajo y `--agente`, la revisión guiada, la carpeta `.factory/`, la spec consolidada y el resumen del estado actual.

#### Scenario: quien instala desde la guía
- GIVEN la guía desde cero
- WHEN la lee de principio a fin
- THEN instala la versión publicada y sabe que existen los modos, la revisión guiada, la spec consolidada y el resumen, y cómo leer el resumen con formato

### Requirement: lo que la web nombra existe
Tipo: no funcional
Cada subcomando y cada opción de `oracle-factory` que nombran el sitio y las guías de `docs/` SHALL existir en la CLI, y cada enlace interno del sitio SHALL apuntar a un archivo o a un ancla que existe.

#### Scenario: un comando que la CLI no tiene
- GIVEN una página que menciona `oracle-factory comando-inexistente`
- WHEN se corren las comprobaciones del sitio
- THEN fallan nombrando la página y el comando

### Requirement: guía de colaboración sin las fricciones del piloto
Tipo: funcional
`docs/colaboracion.md` SHALL resolver las fricciones 2, 3, 4, 5, 9 y 10 del piloto con agentes: archivos compartidos por diseño, commit de producto y commit de evidencia, actualización del reparto tras un relevo, registro de una integración de varios cambios, revisión de riesgos aceptados contra el candidato integrado y uso de `oracle cobertura --con` como verificación previa.

#### Scenario: una persona prepara un relevo
- GIVEN la guía de colaboración
- WHEN una persona busca qué commitear y qué actualizar al pasar el trabajo a otra
- THEN la guía lo dice en una sección propia, sin contradecir las plantillas

### Requirement: el ID de un cambio termina en un sufijo legible
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
Tipo: no funcional
Los comandos de la guía desde cero SHALL seguir funcionando de punta a punta con el paquete instalado, y la página nueva SHALL tener idioma declarado, un solo `h1`, navegación de vuelta a la portada y su contenido legible sin JavaScript.

#### Scenario: arnés de la guía
- GIVEN el paquete construido e instalado en un entorno limpio
- WHEN se corre el arnés de la guía
- THEN todos sus comandos funcionan
