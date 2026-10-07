# La web y la documentación al día con la 0.1.0a5, y trabajar entre varias personas con sus agentes

## Why

La 0.1.0a5 está en PyPI, pero la web pública no menciona nada de lo que trae desde la 0.1.0a3: los modos de trabajo y `--agente` (quién decide cada cosa), la revisión guiada, la carpeta `.factory/`, la spec consolidada y el resumen. Quien instala desde PyPI no tiene cómo enterarse. Brian lo aceptó como riesgo (M-03) al cerrar los modos, con la tarea `docs-web-modos` para resolverlo.

Además, Brian pidió una página sobre cómo se trabaja con Factory entre varias personas, cada una con sus propios agentes (tarea `web-colaboracion`), y la guía de colaboración tiene seis fricciones del piloto con agentes sin corregir (tarea `guia-v2`). Las tres cosas cuentan lo mismo y se hacen juntas.

De paso, este cambio estrena `nuevo --sufijo`: el ID de un cambio termina en la capacidad (o en un sufijo elegido) en vez de en los primeros 16 caracteres del título, que cortaban la frase (`…-resumen-del`, `…-archivar-al`). Este es el primer cambio con un ID así.

## What changes

1. **Página nueva `site/colaboracion.html`**, enlazada desde la portada: cómo trabajan varias personas, cada una con sus agentes. Reparto del trabajo, un checkout o una máquina por persona, quién decide qué según el modo, relevos, revisión independiente (con otra familia de modelo cuando se puede), integración con evidencia vigente y cierre por una persona. Dice explícitamente qué no se probó todavía con personas reales.
2. **El sitio al día con la 0.1.0a5:** la portada y la guía desde cero cuentan los modos y `--agente`, la revisión guiada, `.factory/`, la spec consolidada y el resumen (y cómo leerlo con `glow -p`), sin anunciar como hoy lo que no existe.
3. **Guía de colaboración v2** (`docs/colaboracion.md`): corrige las fricciones 2, 3, 4, 5, 9 y 10 del piloto con agentes y se pone al día con los modos, `.factory/` y la revisión independiente.
4. **`nuevo --sufijo`**: el ID termina, por defecto, en la capacidad; `--sufijo` permite elegirlo; un sufijo inválido se rechaza antes de crear nada.
5. **Comprobaciones automáticas** de que cada comando y opción que la web y las guías nombran existe en la CLI, de que los enlaces internos resuelven y de que la guía desde cero sigue funcionando con el paquete instalado.

## Out of scope

- El piloto de colaboración con personas reales (lo que la página promete se limita a lo probado con agentes y contenedores).
- Una versión del sitio en inglés.
- Cambiar los IDs de los cambios existentes.

## Human decisions

Brian, 2026-10-07: hacer primero la web y la documentación (incluida la página de colaboración que pidió) y después el objetivo «Factory se construye a sí misma»; estrenar el sufijo en este cambio.

Decidido por el agente, a revisar con la spec: la página nueva es estática, en español y sin JavaScript para el contenido, con el estilo del sitio; el ejemplo de colaboración usa dos personas ficticias (Ana y Bruno), como la prueba entre máquinas.
