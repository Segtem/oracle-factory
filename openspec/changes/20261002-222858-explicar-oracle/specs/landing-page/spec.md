# Capability: landing-page

### Requirement: explicar la producción de software con Oracle Factory
The system SHALL explain that Oracle Factory coordinates the complete software workflow, using the tool kit and AI coding agents from an approved need through implementation, tests, review, evidence, and delivery.

#### Scenario: visitante recorre el flujo
- GIVEN una persona abre la portada en español
- WHEN recorre las etapas de principio a fin
- THEN puede identificar qué produce cada herramienta, qué artefactos pasan entre ellas y en qué etapas participa la persona

### Requirement: distinguir responsabilidades y madurez de herramientas
The system SHALL distinguish the coordinating role of Factory, the requirement-evidence judgment of Oracle, and the code-risk review role of Oracle Clue, and SHALL label capabilities that remain planned.

#### Scenario: visitante consulta una herramienta aún en desarrollo
- GIVEN una herramienta del kit no está integrada todavía
- WHEN la persona abre su etapa en la web
- THEN la interfaz la marca como visión o en desarrollo y no afirma que la automatización ya existe

### Requirement: mostrar puntos de control humanos
The system SHALL make scope approval, requirement-measurement decisions, review triage, and delivery approval visible as human-controlled gates.

#### Scenario: agente llega a una decisión humana
- GIVEN el flujo alcanza una aprobación de alcance, una decisión de medición, un hallazgo o un cierre
- WHEN la etapa se muestra
- THEN el control visual se detiene y presenta opciones de inspeccionar, editar, rechazar, aceptar o pausar según corresponda

#### Scenario: visitante usa una decisión de la demostración
- GIVEN la escena muestra una aprobación humana
- WHEN la persona interactúa con el control
- THEN sólo cambia el recorrido visual, sin aprobar una spec real ni modificar tareas o código

### Requirement: ofrecer una animación accesible y controlable
The system SHALL provide pixel-art animation with keyboard-operable controls to play, pause, advance, and reverse the flow, with a reduced-motion mode and an equivalent textual explanation.

#### Scenario: visitante prefiere movimiento reducido
- GIVEN el sistema operativo solicita movimiento reducido
- WHEN la página se carga
- THEN el flujo aparece en una escena estática y cada etapa sigue siendo inspeccionable

### Requirement: funcionar como sitio estático autónomo
The system SHALL render the explanation without a backend, account, analytics, or runtime dependency fetched from a third party.

#### Scenario: visitante abre la página sin red externa
- GIVEN los archivos del sitio están servidos localmente
- WHEN el navegador carga la portada sin acceso a servicios de terceros
- THEN el texto, controles y animación propia siguen disponibles

### Requirement: comparar enfoques para visitantes sin experiencia
The system SHALL explain vibe coding, the software development lifecycle, specification-driven development and Oracle Factory using the same notes example, plain language, human responsibilities and verification methods, without presenting these approaches as mutually exclusive.

#### Scenario: visitante compara cuatro formas de crear software
- GIVEN una persona sin experiencia consulta la portada
- WHEN recorre los cuatro enfoques por ratón o teclado
- THEN encuentra el mismo pedido, los pasos, el papel humano y cómo se comprueba cada resultado

### Requirement: guiar desde cero con herramientas disponibles
The system SHALL provide a separate Spanish onboarding page covering installation with uv and published PyPI tools, the current Factory checkout and a bundled reproducible example through local human-confirmed closure, clearly separating available capabilities from planned distribution.

#### Scenario: persona sigue la guía desde cero
- GIVEN una persona dispone de una terminal y un editor de texto
- WHEN sigue la instalación y los pasos con el id real de su cambio
- THEN puede importar el acuerdo, elegir medidas, ejecutar pruebas y un sensor, registrar una revisión real, evaluar evidencia y decidir el cierre
- AND la guía no inventa un paquete Factory publicado ni aprobaciones de la persona
