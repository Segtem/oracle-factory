# Auditoría de Contenido: Colaboración en Equipo y Agentes en Oracle Factory

**Fecha:** 7 de octubre de 2026  
**Objetivo:** Evaluar la claridad, coherencia, rigurosidad técnica y tono de la documentación sobre colaboración multi-persona con agentes en Oracle Factory, adoptando la perspectiva de quien nunca usó la herramienta.  
**Archivos auditados:**
- `site/index.html`
- `site/colaboracion.html`
- `site/desde-cero.html` (sección «Y después», líneas 47-55)
- `docs/colaboracion.md`  
**Archivos de contraste técnico:** `oracle_factory/cli.py`, `oracle_factory/modos.py`, `oracle_factory/estructura.py`, `site/factory.js`.

---

## 1. Evaluación General y Diagnóstico

Oracle Factory tiene una postura conceptual sólida y honesta: no vende "magia de agentes autónomos", no disfraza probabilidades con certezas, y recalca la primacía de la decisión humana y el registro trazable en Git. Sin embargo, para una persona recién llegada que busca entender **cómo colaborar en equipo con agentes**, el material presenta baches pedagógicos significativos:

1. **Saltos temporales y comandos faltantes:** En `site/colaboracion.html` se crea un cambio en el Paso 01 y en el Paso 03 se salta directamente a asociar medidas (`medir`), omitiendo por completo los pasos obligatorios del ciclo de vida (`aprobar-spec` e `importar`), sin los cuales `medir` falla.
2. **El problema del "huevo o la gallina" en Git:** Se muestra `oracle-factory nuevo` antes de clonar el repositorio, y el comando de clonación usa la carpeta de Ana (`notas-ana`) en un ejemplo donde supuestamente participan Ana y Bruno.
3. **Contradicciones entre la web y los documentos:** El ejemplo usa capacidades `consulta` y `pantalla` en la web, pero `api` e `interfaz` en `docs/colaboracion.md`.
4. **Promesas exageradas respecto a modos de trabajo:** En «Y después» (`desde-cero.html`) se afirma que en el modo por defecto (`confirmacion`) todas las decisiones del agente son propuestas confirmables por una persona, cuando en el código (`modos.py` y `cli.py`) el cierre por parte de un agente está terminantemente prohibido (`via == 'rechaza'`).
5. **Inconsistencias de registro lingüístico:** En `docs/colaboracion.md` conviven el plural peninsular/neutro ("ustedes"), un imperativo tuteo peninsular (`decláralo`), y fórmulas formales de "usted" (`registre`, `use`, `prepare`, `ejecute`).

---

## 2. Respuestas a los Ejes de Evaluación

### (1) ¿Se entiende cómo trabajan varias personas con sus agentes? ¿Qué paso no se entiende o falta?
- **Lo que se entiende:** Queda claro el principio de responsabilidad: Factory no orquesta agentes por red ni ejecuta modelos; cada persona corre sus herramientas en su máquina/checkout. Queda clara la distinción entre commit de producto (código, tests, spec) y commit de evidencia (hechos, informes).
- **Lo que NO se entiende o falta:**
  1. *¿Dónde se crea el cambio?* En `colaboracion.html`, Paso 01 muestra `oracle-factory nuevo ...` y Paso 02 muestra `git clone URL notas-ana`. Si Ana y Bruno están en máquinas distintas, ¿quién crea qué y en qué repositorio? Si Ana creó las dos tareas antes, ¿hizo commit y push a `main` antes de que Bruno clonara? Si Bruno clona, ¿por qué clonaría en `notas-ana`?
  2. *Pasos omitidos:* Entre `nuevo` (Paso 01) y `medir` (Paso 03) faltan `aprobar-spec` e `importar`. Un usuario nuevo que copie los comandos verá que `medir` es rechazado con error (`"primero hay que aceptar la propuesta y la spec"`). Además, el lector no sabe de dónde salió `ID_DEL_REQUISITO`.
  3. *¿Qué hace el agente realmente?* Se menciona que el agente actúa con `--agente`, pero en los snippets solo se muestra `oracle-factory --agente agente-de-ana medir ...`. No se ilustra cómo el agente propone el código, cómo se corren las pruebas o quién redacta la propuesta.
  4. *La integración real en Git:* En el Paso 06 ("Integrar una entrega por vez"), no se muestra ningún comando Git (ni `git checkout`, ni `git merge --no-ff`). Salta directo a `juzgar`.
  5. *Falta de plantillas a la vista:* Se habla repetidamente de "la plantilla de reparto", "la plantilla de relevo" y "el registro de integración", pero en `site/colaboracion.html` no se muestra su contenido ni se enlaza su ubicación directa en el repositorio.

### (2) Contradicciones entre páginas y con `docs/colaboracion.md`
- **Nombres de capacidades divergentes:** `consulta` / `pantalla` en `site/colaboracion.html` vs. `api` / `interfaz` en `docs/colaboracion.md`.
- **Reglas del modo `confirmacion`:** En `site/desde-cero.html` («Y después») se dice que en el modo por defecto las decisiones del agente son propuestas que la persona confirma. En `modos.py` y `colaboracion.html` (Paso 07), el cierre (`cierre`) por un agente es rechazado de plano; no genera propuesta.
- **Texto residual en el canvas interactivo de `index.html`:** En `site/factory.js` (estación 03, medidas), el texto mostrado afirma: *"Esta pausa representa tu elección manual. No es una aprobación de medidas en la CLI de Factory"*. Esto contradice directamente a `site/index.html` (línea 58), `site/desde-cero.html` (paso 04) y la versión 0.1.0a5, donde la CLI cuenta con el comando `oracle-factory medir` precisamente para registrar y validar la elección de medidas.
- **Ruta de evidencia y hechos:** En `colaboracion.html` línea 28 se remite a `oracle-factory ruta` (que apunta a `.factory/cambios/...`), mientras que en `cli.py` (línea 756) y `docs/colaboracion.md` (línea 149) se advierte que guardar hechos en carpetas ignoradas impide que viajen por Git y se recomienda `tareas/`.

### (3) Promesas exageradas o cosas que suenan hechas y no lo están
- **"Piloto con agentes" (badging y narrativa):** El sitio luce insignias como *"Probado con agentes y en contenedores"* y narra *"Un piloto con agentes: dos agentes en frentes separados, un relevo..."*. Al contrastar con `docs/colaboracion.md` (línea 168) y el código de testing (`tools/verify_collaboration.py`), se observa que se trata de un arnés de prueba automatizado con fixtures preestablecidos (scripts que simulan actores), no de una experiencia real con agentes LLM autónomos colaborando. Debería presentarse con precisión como "comprobado mediante simulación automatizada de agentes en contenedores".
- **Yuxtaposición de Oracle Clue y Factory:** En el Paso 05 de `colaboracion.html`, se agrupan en un mismo bloque `oracle-clue preparar` y `oracle-factory revision-preparar`. Esto genera la falsa ilusión de que Factory interactúa con Clue. En realidad, Factory no llama a Clue ni valida sus esquemas; son herramientas desacopladas.

### (4) Tono y español rioplatense consistente con el resto del sitio
- El sitio (`index.html` y `desde-cero.html`) maneja un rioplatense singular pulcro, sobrio y bien cuidado ("vos", "instalá", "leé", "probá", "revisá", "cerrá").
- En `site/colaboracion.html` línea 73 aparece una discordancia a plural: `(no lo hagan: un frente, un escritor)`.
- En `docs/colaboracion.md` se rompe la unidad de estilo:
  - En la mayoría de las secciones se usa segunda persona plural neutra ("ustedes"): `copien`, `completen`, `separen`, `guarden`.
  - En la línea 44 aparece un imperativo singular de tuteo peninsular con tilde: `decláralo` (en rioplatense sería `declaralo`, o en plural `declárenlo`).
  - En las líneas 158 y 162-165 salta a un tratamiento formal singular de "usted": `Registre`, `use`, `prepare`, `Ejecute`.

### (5) Qué sacar por largo o sobrecarga cognitiva
- **En `docs/colaboracion.md`:**
  - El apartado sobre colisión de IDs en clones divergentes (líneas 70-71) describe un caso hiperbólico y raro (dos personas generando el mismo timestamp exacto sin conexión) con 15 líneas de instrucciones de emergencia manual que confunden a quien recién aprende el protocolo.
  - El detalle de locks residuales de `medir` y procesos caídos (líneas 90-93).
  - La tabla completa de casos de prueba del arnés interno C1 a C9 (líneas 170-181), que es una especificación de testing interno de `verify_collaboration.py` y no aporta a un protocolo de trabajo en equipo.
- **En `site/colaboracion.html`:**
  - La sección #no-probado (líneas 66-74) entra en detalles de laboratorio ("dos máquinas en contenedores sin archivos compartidos...", "demostración automática en repositorios temporales"). Debe sintetizarse en dos líneas directas enfocadas en lo que le importa al usuario: verificado en Linux con pruebas automatizadas; pendientes pilotos con humanos y soporte de Windows/macOS.

---

## 3. Defectos Concretos (Cita, Problema y Corrección)

### Defecto 1: Orden de operaciones ambiguo y nombre del clon incoherente
- **Archivo:** `site/colaboracion.html` (Líneas 16-17 y 24-27)
- **Texto original:**
  ```html
  <div class="code-block"><pre><code>oracle-factory nuevo --capacidad consulta "Agregar consulta de notas"
  oracle-factory nuevo --capacidad pantalla "Mostrar notas en pantalla"</code></pre></div>
  ...
  <div class="code-block"><pre><code>git clone URL_DEL_REPOSITORIO notas-ana
  cd notas-ana
  git switch -c trabajo/consulta
  oracle-factory donde ID_DEL_CAMBIO</code></pre></div>
  ```
- **Problema:** En el Paso 01 se crean los cambios antes de clonar. Luego en el Paso 02 se clona en `notas-ana`. Si Ana y Bruno están en máquinas separadas (premisa del ejemplo), no se entiende quién corrió el Paso 01 ni dónde. Si Bruno está clonando, no tiene sentido que clone en `notas-ana`. Tampoco se indica que los cambios deben commitearse y pushearse a la rama compartida para que el otro los reciba al clonar.
- **Corrección propuesta:**
  Explicar claramente:
  1. Una persona (o el equipo en la rama principal) crea ambos cambios con `nuevo`, commitea la estructura base y la envía al remoto (`git push`).
  2. Luego, cada integrante clona su copia o crea su worktree (Ana en `notas-ana` hacia la rama `trabajo/consulta`; Bruno en `notas-bruno` hacia la rama `trabajo/pantalla`):
  ```bash
  # En la máquina de Ana:
  git clone URL_DEL_REPOSITORIO notas-ana
  cd notas-ana
  git switch -c trabajo/consulta

  # En la máquina de Bruno:
  git clone URL_DEL_REPOSITORIO notas-bruno
  cd notas-bruno
  git switch -c trabajo/pantalla
  ```

---

### Defecto 2: Salto metodológico entre Paso 01 y Paso 03 (omisión de `aprobar-spec` e `importar`)
- **Archivo:** `site/colaboracion.html` (Líneas 37-39)
- **Texto original:**
  ```html
  <p>En todos los modos, <code>estado</code> muestra quién propuso, quién confirmó y quién decidió cada cosa. En equipo esto importa: Bruno puede ver qué aceptó Ana y qué propuso el agente de Ana, sin preguntarle.</p>
  <div class="code-block"><pre><code>oracle-factory --agente agente-de-ana medir ID_DEL_CAMBIO --requisito ID_DEL_REQUISITO --medida consulta.casos
  oracle-factory estado ID_DEL_CAMBIO</code></pre></div>
  ```
- **Problema:** Un lector que siga la guía no podrá ejecutar `medir`: Factory arroja error si la spec no fue aprobada previamente con `aprobar-spec`. Además, `ID_DEL_REQUISITO` no existe hasta que se ejecuta `oracle-factory importar`. Ambos comandos desaparecieron de `colaboracion.html`.
- **Corrección propuesta:**
  Incorporar explícitamente la aprobación del alcance y la importación de requisitos al final del Paso 01 o al inicio del Paso 03:
  ```html
  <p>Antes de que el agente proponga medidas, una persona debe aceptar el alcance e importar los requisitos:</p>
  <div class="code-block"><pre><code>oracle-factory aprobar-spec ID_DEL_CAMBIO
  oracle-factory importar ID_DEL_CAMBIO</code></pre></div>
  <p>Con los requisitos importados (que nacen sin medir), el agente puede proponer cómo medirlos:</p>
  <div class="code-block"><pre><code>oracle-factory --agente agente-de-ana medir ID_DEL_CAMBIO --requisito ID_DEL_REQUISITO --medida consulta.casos
  oracle-factory estado ID_DEL_CAMBIO</code></pre></div>
  ```

---

### Defecto 3: Discrepancia de nombres de capacidades entre la web y `docs/colaboracion.md`
- **Archivo:** `site/colaboracion.html` (Líneas 16-17) vs. `docs/colaboracion.md` (Líneas 18-19, 29, 99)
- **Texto en `colaboracion.html`:**
  ```bash
  oracle-factory nuevo --capacidad consulta "Agregar consulta de notas"
  oracle-factory nuevo --capacidad pantalla "Mostrar notas en pantalla"
  ```
- **Texto en `docs/colaboracion.md`:**
  ```bash
  oracle-factory --proyecto /ruta/producto nuevo --capacidad api "Agregar consulta de notas"
  oracle-factory --proyecto /ruta/producto nuevo --capacidad interfaz "Mostrar notas en pantalla"
  ```
- **Problema:** El usuario que salta de la web al markdown complementario encuentra que `consulta` pasó a ser `api`, y `pantalla` pasó a ser `interfaz`.
- **Corrección propuesta:** Unificar la nomenclatura. Se sugiere mantener `consulta` y `pantalla` en ambos documentos por ser términos más concretos y acordes al ejemplo funcional de notas.

---

### Defecto 4: Afirmación incorrecta sobre propuestas de agente en modo `confirmacion`
- **Archivo:** `site/desde-cero.html` (Línea 50, sección «Y después»)
- **Texto original:**
  ```html
  <li><strong>Modos de trabajo.</strong> Cada cambio declara cuánto decide una persona: <code>confirmacion</code> (el que usaste: la persona confirma todo), <code>funcional</code> o <code>autonomo</code>. Se elige al crearlo con <code>oracle-factory nuevo --modo</code> o después con <code>oracle-factory modo</code>. Un agente actúa con <code>oracle-factory --agente NOMBRE</code>: sus decisiones quedan registradas como de un agente y, en el modo por defecto, sólo son propuestas que una persona confirma repitiendo el comando desde su terminal.</li>
  ```
- **Problema:** En modo `confirmacion`, la decisión de `cierre` **no** puede ser propuesta por un agente (`via_agente('confirmacion', 'cierre', [])` retorna `'rechaza'` en `modos.py`). Ejecutar `oracle-factory --agente ... cerrar` falla directamente con error y no registra ninguna propuesta. La redacción actual induce a pensar que el agente puede proponer cualquier decisión, incluido el cierre.
- **Corrección propuesta:**
  Reemplazar por:
  ```html
  <li><strong>Modos de trabajo.</strong> Cada cambio declara cuánto decide una persona: <code>confirmacion</code> (el que usaste: la persona confirma todo), <code>funcional</code> o <code>autonomo</code>. Se elige al crearlo con <code>oracle-factory nuevo --modo</code> o después con <code>oracle-factory modo</code>. Un agente actúa con <code>oracle-factory --agente NOMBRE</code>: en el modo por defecto, sus acciones sobre spec, medidas y revisión quedan registradas como propuestas que una persona debe confirmar repitiendo el comando sin <code>--agente</code>; el cierre, en cambio, sólo puede ejecutarlo directamente una persona.</li>
  ```

---

### Defecto 5: Texto desactualizado en la escena interactiva de `site/index.html`
- **Archivo:** `site/factory.js` (Línea 43, asociada a la etapa 3 / estación 03 de `site/index.html`)
- **Texto original:**
  ```javascript
  "why": "Esta pausa representa tu elección manual. No es una aprobación de medidas en la CLI de Factory. Contar tres filas no demuestra que sean tres casos distintos."
  ```
- **Problema:** Esta frase proviene de versiones alfa anteriores a 0.1.0a5. En 0.1.0a5, la CLI incorporó formalmente `oracle-factory medir`, que registra explícitamente las medidas y las confirmaciones humanas en `factory.json` y en las notas de la tarea. Decir al usuario que *"No es una aprobación de medidas en la CLI de Factory"* contradice a la propia versión actual y a `site/index.html` (línea 58).
- **Corrección propuesta:**
  Actualizar en `site/factory.js`:
  ```javascript
  "why": "Esta pausa representa la elección de medidas con oracle-factory medir. Una persona evalúa y confirma la pertinencia de las reglas; contar tres filas no demuestra por sí solo que sean tres casos distintos."
  ```

---

### Defecto 6: Imperativo de tuteo peninsular desalineado en `docs/colaboracion.md`
- **Archivo:** `docs/colaboracion.md` (Línea 44)
- **Texto original:**
  ```markdown
  Dos sensores que emiten la misma relación son un solapamiento que Git no ve: decláralo en el reparto como interfaz.
  ```
- **Problema:** Uso de `decláralo` (tuteo peninsular / neutro con tilde esdrújula) en un texto donde el resto de las instrucciones están formuladas en segunda persona plural (`detengan`, `acuerden`, `copien`), y el resto del proyecto usa rioplatense (`declaralo` o `declará`).
- **Corrección propuesta:** Cambiar a segunda persona plural consistente con el documento:
  ```markdown
  Dos sensores que emiten la misma relación son un solapamiento que Git no ve: declárenlo en el reparto como interfaz.
  ```

---

### Defecto 7: Salto a tratamiento formal ("usted") en `docs/colaboracion.md`
- **Archivo:** `docs/colaboracion.md` (Líneas 158 y 162-165)
- **Texto original:**
  ```markdown
  Registre ambos en la entrega sin presentarlos como idénticos.
  ...
  Desde un checkout de Factory, use un Python con sus dependencias fijadas... Por ejemplo, prepare un entorno local... Ejecute:
  ```
- **Problema:** Salto injustificado al tratamiento formal en singular ("usted": `Registre`, `use`, `prepare`, `Ejecute`). Las secciones anteriores usan "ustedes" (`copien`, `designen`, `separen`, `úsenlo`).
- **Corrección propuesta:**
  Ajustar a plural homogéneo con el resto del archivo:
  ```markdown
  Registren ambos en la entrega sin presentarlos como idénticos.
  ...
  Desde un checkout de Factory, usen un Python con sus dependencias fijadas... Por ejemplo, preparen un entorno local... Ejecuten:
  ```

---

### Defecto 8: Salto a segunda persona plural en `site/colaboracion.html`
- **Archivo:** `site/colaboracion.html` (Línea 73)
- **Texto original:**
  ```html
  También queda fuera que dos personas modifiquen a la vez el registro de un mismo cambio (no lo hagan: un frente, un escritor) y Windows y macOS, que no se probaron.
  ```
- **Problema:** El paréntesis salta a plural apelativo `(no lo hagan)`, rompiendo la convención del sitio web que siempre interpela en singular rioplatense ("vos") o en tercera persona neutral.
- **Corrección propuesta:**
  Cambiar a rioplatense singular o fórmula impersonal:
  ```html
  También queda fuera que dos personas modifiquen a la vez el registro de un mismo cambio (no lo hagas: un frente, un escritor) y Windows y macOS, que no se probaron.
  ```

---

### Defecto 9: Yuxtaposición confusa de comandos de Clue y Factory
- **Archivo:** `site/colaboracion.html` (Líneas 46-51)
- **Texto original:**
  ```html
  <p>Lo ideal es que revise alguien distinto de quien escribió: otra persona, u otro agente de una familia de modelo distinta a la del que escribió el código. Oracle Clue prepara el contexto de un candidato y valida el informe del revisor; Factory deja preparada la revisión guiada:</p>
  <div class="code-block"><pre><code>oracle-clue preparar --repo . --base BASE_DE_REVISION --salida /ruta/fuera/del/repo/contexto.json
  oracle-factory revision-preparar ID_DEL_CAMBIO</code></pre></div>
  <p>El revisor completa el informe con lo que realmente revisó, sus comprobaciones y sus límites; una persona decide cada hallazgo —corregido, descartado o riesgo aceptado— en un documento aparte, y registra la revisión:</p>
  <div class="code-block"><pre><code>oracle-factory revision ID_DEL_CAMBIO --formato guiado --informe RUTA_INFORME --decisiones RUTA_DECISIONES --revisor "Bruno" --decision aprobar</code></pre></div>
  ```
- **Problema:** Colocar `oracle-clue preparar` y `oracle-factory revision-preparar` juntos en un mismo bloque sin explicar qué produce cada uno hace pensar que están encadenados. Un principiante no sabrá si `revision-preparar` consume `contexto.json`. Además, Clue nunca vuelve a mencionarse (se omite `oracle-clue validar`), por lo que su comando queda como un paso fantasma.
- **Corrección propuesta:**
  Separar con claridad el rol auxiliar de Clue del flujo interno de Factory:
  ```html
  <p>Lo ideal es que revise alguien distinto de quien escribió. Si usás Oracle Clue, podés extraer el contexto para que lo analice un modelo externo:</p>
  <div class="code-block"><pre><code>oracle-clue preparar --repo . --base BASE_DE_REVISION --salida /tmp/contexto.json</code></pre></div>
  <p>Por su parte, Factory genera las plantillas del informe y de decisiones dentro de la tarea del cambio:</p>
  <div class="code-block"><pre><code>oracle-factory revision-preparar ID_DEL_CAMBIO</code></pre></div>
  <p>El revisor completa <code>informe.json</code>; una persona documenta la resolución de cada hallazgo en <code>decisiones.json</code> y registra la revisión:</p>
  <div class="code-block"><pre><code>oracle-factory revision ID_DEL_CAMBIO --formato guiado --informe RUTA_INFORME --decisiones RUTA_DECISIONES --revisor "Bruno" --decision aprobar</code></pre></div>
  ```

---

### Defecto 10: Referencia abstracta a la plantilla de integración
- **Archivo:** `site/colaboracion.html` (Línea 54)
- **Texto original:**
  ```html
  El registro de la integración va en la tarea del primer cambio integrado y la otra lo referencia (Oracle Task sólo acepta IDs de tareas, no carpetas sueltas).
  ```
- **Problema:** Mientras que en los pasos 01 y 04 se alude explícitamente a "la plantilla de reparto" y "la plantilla de relevo", aquí se habla de "el registro de la integración" sin indicar el nombre del archivo ni dónde encontrarlo.
- **Corrección propuesta:**
  Nombrarlo de forma simétrica:
  ```html
  El integrador copia la plantilla de integración (<code>integracion.md</code>) a la tarea del primer cambio que integra, y la otra tarea lo referencia con una nota.
  ```

---

### Defecto 11: Desconexión entre texto explicativo y bloque de código en Paso 06
- **Archivo:** `site/colaboracion.html` (Líneas 56-58)
- **Texto original:**
  ```html
  <p>Antes de registrar nada, cada uno puede verificarse sin dejar rastro con <code>oracle cobertura --con HECHOS</code>: muestra qué requisitos se cumplen con esos hechos sin registrar un veredicto.</p>
  <div class="code-block"><pre><code>oracle-factory juzgar ID_DEL_CAMBIO --con RUTA_DE_LOS_HECHOS
  oracle-factory estado ID_DEL_CAMBIO</code></pre></div>
  ```
- **Problema:** La frase introduce el comando de verificación previa `oracle cobertura`, pero el bloque de código muestra `oracle-factory juzgar`. El comando mencionado en la prosa queda huérfano.
- **Corrección propuesta:**
  Incluir el comando previo o separar el párrafo de juicio formal:
  ```html
  <p>Antes de registrar el juicio, podés comprobar el resultado sin dejar rastro en el historial:</p>
  <div class="code-block"><pre><code>oracle cobertura --proyecto . --con RUTA_DE_LOS_HECHOS</code></pre></div>
  <p>Cuando la evidencia sea definitiva, registrá el veredicto oficial con Factory:</p>
  <div class="code-block"><pre><code>oracle-factory juzgar ID_DEL_CAMBIO --con RUTA_DE_LOS_HECHOS
  oracle-factory estado ID_DEL_CAMBIO</code></pre></div>
  ```

---

## 4. Sugerencias de Mejora

1. **Incorporar un esquema visual mínimo del flujo multi-máquina:**  
   En `site/colaboracion.html`, la topología entre la máquina de Ana, la de Bruno y la rama de integración se beneficiaría enormemente de un diagrama sintético:
   ```text
   [Máquina Ana: trabajo/consulta] ──> [Git Remoto] <── [Máquina Bruno: trabajo/pantalla]
                                             │
                                     [Integración limpia]
                                             │
                                  oracle-factory cerrar
                                             │
                                   openspec/specs/ (vigente)
   ```
2. **Mostrar explícitamente el par "Propuesta del agente / Confirmación de la persona":**  
   En la sección 3 ("Quién decide qué"), el bloque de código solo muestra el comando ejecutado por el agente (`oracle-factory --agente ... medir ...`). Para que un principiante entienda la confirmación humana, conviene mostrar el comando inmediato que corre la persona para ratificarlo:
   ```bash
   # 1. El agente propone:
   oracle-factory --agente agente-de-ana medir ID_DEL_CAMBIO --requisito ID_REQ --medida consulta.casos

   # 2. La persona confirma desde su terminal (mismo comando sin --agente):
   oracle-factory medir ID_DEL_CAMBIO --requisito ID_REQ --medida consulta.casos --quitar-sin-medir
   ```
3. **Ofrecer extractos breves de las plantillas de trabajo:**  
   En lugar de solo nombrar `reparto.md`, `relevo.md` e `integracion.md`, incluir un desplegable `<details>` con un ejemplo de 5 líneas de cada uno. Esto quita la sensación de "caja negra" sin obligar al usuario a abandonar la lectura para navegar por el repositorio en GitHub.
4. **Incluir comandos Git concretos de integración en Paso 06:**  
   El Paso 06 dice *"Una persona integra, desde un checkout limpio..."*, pero no ilustra cómo. Sugerimos agregar:
   ```bash
   git switch main
   git merge --no-ff trabajo/consulta
   # ejecutar sensor sobre el candidato integrado
   oracle-factory juzgar ID_CAMBIO_CONSULTA --con tareas/.../hechos.json
   ```
5. **Podar detalles de laboratorio y arneses internos en `docs/colaboracion.md`:**  
   Mover la tabla de casos C1 a C9 y la explicación de colisiones teóricas de identificadores a un apéndice técnico (por ejemplo, `docs/verificacion-colaboracion.md`), manteniendo `docs/colaboracion.md` como una guía operativa clara, directa y orientada a desarrolladores reales.
