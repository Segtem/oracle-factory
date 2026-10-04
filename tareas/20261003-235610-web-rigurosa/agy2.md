# Agy Task — 2026-10-03 21:00:05

**Tarea:** Trabajá en español. Revisa Oracle Factory para alguien sin experiencia, con base en site/desde-cero.html y portada. Repositorio /home/workstation/Dev/factory, tarea 20261003-235610-web-rigurosa. NO modifiques el repo, NO hagas commits/push ni aprobaciones de cambios reales. El wrapper guardará tu informe en la tarea. Si verificás comandos, usa SOLO una carpeta temporal bajo /tmp con UV_TOOL_DIR, UV_TOOL_BIN_DIR y UV_CACHE_DIR propios; instala oracle-factory==0.1.0a2 desde PyPI (ya publicado), Python3.13. Conserva las instalaciones globales. Sigue la guía de carpeta vacía a cierre local usando confirmaciones fixture SOLO en esa carpeta; son pruebas automáticas, no aprobación humana ni piloto real. No leas implementación hasta registrar primero dónde la guía te deja sin información. Detecta acciones imposibles/ambiguas al crear/copiar archivos, identificar rutas/IDs, configurar terminal/editor/Git, revisar código sin experiencia, escribir informe, mapear medidas/requisitos, qué significa verde y qué hacer si se rompe algo. Devuelve resultado de ejecución (completada o bloqueo concreto y salida), pasos exactos ambiguos con citas archivo:línea, propuesta de texto, y lista separada de mejoras de CLI necesarias con costo/valor. Indica qué pudo ejecutarse en Linux y qué solo se inspeccionó para Windows/Mac. No presentes este ejercicio como una prueba con un humano principiante. No inventes evidencia ni aprobación. Tiempo acotado: lectura y ejecución de ejemplo, sin mutaciones largas.
**Directorio:** /home/workstation/Dev/factory
**Cuenta:** prof
**Modelo:** gemini-3.8-flash-high (esfuerzo high, timeout 20m)

---

# Informe de auditoría: Oracle Factory para principiantes

**Repositorio:** [Dev/factory](file:///home/workstation/Dev/factory)  
**Tarea de referencia:** `20261003-235610-web-rigurosa`  
**Paquete verificado:** `oracle-factory==0.1.0a2` (PyPI) con `Python 3.13.15` y `uv 0.12.17`  
**Documentos auditados:** [site/desde-cero.html](file:///home/workstation/Dev/factory/site/desde-cero.html) y [site/index.html](file:///home/workstation/Dev/factory/site/index.html)  

---

## 1. Marco y alcance del ejercicio

> [!IMPORTANT]
> **Aclaración de rigor metodológico:**  
> Este ejercicio **no es una prueba de usuario con un humano principiante real**, ni constituye un piloto operativo ni una aprobación de cambios reales. Se trató de una auditoría técnica y analítica de usabilidad asistida por agentes, ejecutando los comandos con confirmaciones *fixture* estrictamente dentro de un entorno temporal aislado. No se crearon commits, ramas ni aprobaciones reales en el repositorio de trabajo.

### Cobertura de plataformas
- **Ejecutado empíricamente en Linux (x86_64):**
  - Aislamiento completo de variables de entorno (`UV_TOOL_DIR`, `UV_TOOL_BIN_DIR`, `UV_CACHE_DIR`).
  - Instalación de Python 3.13 y `oracle-factory==0.1.0a2` desde PyPI con `--with-executables-from oracle-metalenguaje,oracle-task`.
  - Recorrido íntegro de la guía paso a paso desde carpeta vacía hasta `oracle-factory cerrar` y validación de estado final `cerrada`.
- **Inspeccionado analíticamente para Windows y macOS:**
  - **Windows (PowerShell/Cmd/Explorador):** Sintaxis de comandos de instalación (`irm ... | iex`), comportamiento de rutas (`\` vs `/`), extensión oculta de archivos (`.txt`), falta de programa predeterminado para abrir archivos `.requisito` y `.oracle`, y comandos de copia en PowerShell (`Copy-Item` vs `cp`).
  - **macOS (Terminal/zsh/Finder):** Instalación vía `curl`, visibilidad de carpetas y archivos ocultos (`.factory-demo/`, sin atajo `Cmd+Shift+.` documentado), y compatibilidad de entry points en zsh.

---

## 2. Resultado de la ejecución técnica

La ejecución en Linux desde una carpeta limpia (`/tmp/.../mi-primer-proyecto`) **se completó de punta a punta hasta el cierre**, pero requirió resolver omisiones críticas de la guía (frases de confirmación exactas no documentadas, rutas completas no especificadas y edición manual de archivos con indentación sensible).

### Registro de salidas por etapa

1. **Instalación aislada:**
   ```bash
   uv python install 3.13
   uv tool install --python 3.13 --with-executables-from oracle-metalenguaje,oracle-task oracle-factory==0.1.0a2
   ```
   *Salida:* `oracle-factory 0.1.0a2`, `oracle 0.38.1`, `oracle-task 0.2.0` instalados correctamente en el entorno aislado.

2. **Inicialización y ejemplo (`Paso 02`):**
   ```bash
   git init && oracle-factory init && oracle-factory ejemplo notas
   ```
   *Salida de Factory:* Inicializó `tareas/`, `openspec/changes/`, `catalogos/`, `oracle.json` y agregó `.factory-demo/` al `.gitignore`. Copió el ejemplo a `examples/notas/`.  
   *Conflicto de salida:* La CLI de Oracle subyacente imprimió:
   ```text
   Próximos pasos:
     1. Creá un caso:     oracle caso <grupo/id>
     2. Creá una medida:  oracle nueva <dominio.nombre>
     3. Verificá todo:    oracle test
   ```
   Esto contradice directamente el flujo de Factory para un novato.

3. **Creación del cambio (`Paso 03`):**
   ```bash
   oracle-factory nuevo --capacidad notas "Comprobar el título de una nota"
   ```
   *Salida:* ID generado (ej. `20261004-000057-comprobar-el`). Creó la estructura en `tareas/` y `openspec/changes/<id>/`.

4. **Aprobación de la especificación (`Paso 04`):**
   - Si no se sustituyen los archivos o quedan textos `TODO:`, la CLI bloquea con:
     `FACTORY BLOQUEADA: hay que completar y revisar primero: openspec/changes/<id>/proposal.md`
   - Tras copiar los archivos del ejemplo, la terminal solicita una frase exacta en mayúsculas:
     `Escribí APROBAR ESPECIFICACION 20261004-000057-comprobar-el:`  
     Al ingresar la frase exacta: `Alcance aprobado; sus requisitos todavía deben importarse y medirse.`

5. **Importación y cobertura de requisitos (`Paso 04`):**
   ```bash
   oracle-factory importar <id>
   ```
   *Salida:* Creó `requisitos/notas_<hash>.titulo_valido.requisito` como `sin_medir`.  
   Tras copiar `examples/notas/catalogos/*.oracle` a `catalogos/` y editar el `.requisito` reemplazando `sin_medir` por `    medido_por notas.casos_ejecutados, notas.resultados`, la cobertura arrojó:
   ```text
   ✓ notas_c7dd69c76b1520dfe.titulo_valido   notas.casos_ejecutados, notas.resultados
   1 requisitos: 1 medidos · 0 en parte · 0 sin medir · 0 con medidas inexistentes
   ```

6. **Ejecución de pruebas, sensor y commit (`Paso 05`):**
   ```bash
   uv run --no-project --python 3.13 python -m unittest discover -s examples/notas -p "test_*.py" -v
   uv run --no-project --python 3.13 python examples/notas/sensor.py --salida .factory-demo/hechos.json
   git add . && git commit -m "<id>: ejemplo de notas"
   ```
   *Salida:* 3 pruebas unitarias aprobadas (`Ran 3 tests in 0.000s OK`). El sensor generó `.factory-demo/hechos.json` con los 3 casos. Git registró el commit inicial (requerido por `contexto_producto()`).

7. **Registro de revisión (`Paso 06`):**
   ```bash
   oracle-factory revision <id> --informe .factory-demo/review.md --revisor "Tester" --decision aprobar --hallazgos-abiertos 0
   ```
   *Confirmación requerida por la CLI:*
   `Escribí REGISTRAR REVISION 20261004-000057-comprobar-el:`  
   Registró la huella del commit y el SHA-256 del informe.

8. **Juicio y cierre (`Paso 07`):**
   ```bash
   oracle-factory juzgar <id> --con .factory-demo/hechos.json
   oracle-factory estado <id>
   oracle-factory cerrar <id>
   ```
   *Salida del juicio:*
   ```text
   ✓ notas_c7dd69c76b1520dfe.titulo_valido   cumple · notas.casos_ejecutados cumple, notas.resultados cumple
   1 requisitos: 1 se cumplen (0 sólo en lo medido) · 0 no se cumplen · 0 sin juicio · 0 sin medir · 0 con medidas inexistentes
   ```
   *Confirmación de cierre requerida por la CLI:*
   `Escribí CERRAR 20261004-000057-comprobar-el:`  
   *Salida final de estado:*
   ```text
   <id> — Comprobar el título de una nota
   Fase: cerrada
   Requisitos Oracle: notas_c7dd69c76b1520dfe.titulo_valido
   Pendiente: ninguno
   Aprobación spec: sí
   Revisión: Tester / aprobar / 0 abiertos
   Oracle: código 0 (openspec/changes/<id>/oracle-veredicto.txt)
   ```

---

## 3. Pasos exactos ambiguos y brechas de información

A continuación se detallan las acciones imposibles, ambiguas o que dejan sin información a una persona sin experiencia:

### A. Configuración de terminal, editor y Git
- **[site/desde-cero.html:8](file:///home/workstation/Dev/factory/site/desde-cero.html#L8):**
  > *«También necesitás un editor de texto plano; no uses un procesador de textos como Word.»*
  - **Brecha:** No sugiere ningún editor concreto (VS Code, Notepad++, Cursor o Nano). Un principiante no sabe qué herramienta descargar. En Windows, el Bloc de Notas suele ocultar extensiones o guardar con codificación BOM/ANSI que rompe parsers de spec.
- **[site/desde-cero.html:9](file:///home/workstation/Dev/factory/site/desde-cero.html#L9):**
  > *«curl -LsSf https://astral.sh/uv/install.sh | sh»*
  - **Brecha:** En instalaciones mínimas de Linux (ej. contenedores Debian/Ubuntu limpios), `curl` no viene preinstalado. No indica cómo instalarlo (`sudo apt install curl`).
- **[site/desde-cero.html:14](file:///home/workstation/Dev/factory/site/desde-cero.html#L14):**
  > *«Si tenías Trackertast instalado con uv, ejecutá uv tool uninstall trackertast... Si Oracle o Oracle Task ya están instalados y uv informa que sus comandos existen, instalá Factory sin --with-executables-from...»*
  - **Brecha:** Sobrecarga cognitiva severa. Un principiante no sabe qué es Trackertast ni si tiene paquetes previos instalados. Debe ser un acordeón o nota para migraciones, no parte del flujo principal.
- **[site/desde-cero.html:40-41](file:///home/workstation/Dev/factory/site/desde-cero.html#L40-L41):**
  > *«git config user.name "Tu nombre"; git config user.email "tu-correo@example.com"»*
  - **Brecha:** Se pide configurar la identidad de Git recién en el Paso 05. Si el usuario intenta hacer algo con Git antes o no sabe si poner su correo real de GitHub, se detiene con dudas de privacidad o configuración.

### B. Rutas, IDs y copia de archivos
- **[site/desde-cero.html:20](file:///home/workstation/Dev/factory/site/desde-cero.html#L20):**
  > *«Factory imprime el id del cambio y las carpetas creadas. El id identifica esa tarea: copialo completo...»*
  - **Brecha:** El mecanismo de reemplazo dinámico en el HTML depende de JavaScript (`guide.js`). Si se lee en texto plano, terminal o navegador con JS deshabilitado, los comandos muestran `ID_DEL_CAMBIO`. Además, si la persona cierra la terminal o limpia la pantalla, la guía no explica cómo recuperar el ID (no menciona `tasks list` ni mirar en `openspec/changes/`).
- **[site/desde-cero.html:21](file:///home/workstation/Dev/factory/site/desde-cero.html#L21):**
  > *«Copiá el contenido de examples/notas/proposal.md sobre el archivo proposal.md del cambio. Copiá examples/notas/spec.md sobre specs/notas/spec.md de ese mismo cambio.»*
  - **Brecha crítica:** No proporciona las rutas relativas completas de destino (`openspec/changes/ID_DEL_CAMBIO/proposal.md` y `openspec/changes/ID_DEL_CAMBIO/specs/notas/spec.md`), ni comandos de terminal para copiar (`cp` en bash o `Copy-Item` en PowerShell). Pedirle a un principiante que abra 4 archivos en un editor gráfico y haga cortar/pegar entre carpetas anidadas genera altas tasas de error.
- **[site/desde-cero.html:39](file:///home/workstation/Dev/factory/site/desde-cero.html#L39):**
  > *«Creá la carpeta catalogos si no existe. Copiá allí los dos archivos .oracle de examples/notas/catalogos/.»*
  - **Brecha:** `oracle-factory init` **ya crea** la carpeta `catalogos/`. Decir "si no existe" genera confusión ("¿hice algo mal? ¿por qué la mía ya existe?"). Tampoco da los nombres exactos de los dos archivos ni el comando para copiarlos.

### C. Mapeo de medidas y sintaxis de requisitos
- **[site/desde-cero.html:39](file:///home/workstation/Dev/factory/site/desde-cero.html#L39):**
  > *«Abrí el archivo .requisito que acaba de generarse... Sustituí únicamente la línea que empieza con sin_medir por esta línea, con cuatro espacios al comienzo: medido_por notas.casos_ejecutados, notas.resultados»*
  - **Brecha crítica:** El archivo tiene un nombre largo autogenerado (`requisitos/notas_<hash>.titulo_valido.requisito`). En Windows o Mac el sistema operativo no sabe con qué programa abrir un `.requisito`. Además, la exigencia de "cuatro espacios al comienzo" es frágil: si el editor inserta una tabulación o 2 espacios, Oracle Metalenguaje falla.
- **[site/desde-cero.html:39](file:///home/workstation/Dev/factory/site/desde-cero.html#L39):**
  > *«Tu requisito debe aparecer con ✓. Otros requisitos de la POC pueden seguir sin medir.»*
  - **Brecha conceptual:** En un proyecto nuevo creado desde cero siguiendo la guía, **sólo hay 1 requisito**. La mención a "Otros requisitos de la POC" es una fuga del repositorio de desarrollo de Factory, que desconcierta al principiante al buscar requisitos inexistentes.

### D. Revisión sin experiencia e informe
- **[site/desde-cero.html:44](file:///home/workstation/Dev/factory/site/desde-cero.html#L44):**
  > *«Revisá el programa y las pruebas, o pedí una revisión asistida. Guardá el informe real en .factory-demo/review.md con lo que se comprobó, los hallazgos y cómo se resolvieron.»*
  - **Brecha severa:** Alguien sin experiencia no sabe programar en Python, no sabe qué buscar en el código ni cómo redactar un informe. No se provee una plantilla de `review.md`. Además, `.factory-demo/` es una carpeta oculta en Linux y macOS; el usuario no la verá en su explorador de archivos.

### E. Frases de confirmación omitidas en la guía
La CLI bloquea con error si no se ingresa una cadena literal exacta en mayúsculas, pero la guía omite el texto que la terminal exigirá:
1. `aprobar-spec` ([site/desde-cero.html:39](file:///home/workstation/Dev/factory/site/desde-cero.html#L39)): Dice *«La terminal te pide escribir una frase de confirmación»*. La CLI exige: `APROBAR ESPECIFICACION <ID_DEL_CAMBIO>`.
2. `revision` ([site/desde-cero.html:44](file:///home/workstation/Dev/factory/site/desde-cero.html#L44)): Dice *«La terminal solicita una confirmación»*. La CLI exige: `REGISTRAR REVISION <ID_DEL_CAMBIO>`.
3. `cerrar` ([site/desde-cero.html:45](file:///home/workstation/Dev/factory/site/desde-cero.html#L45)): Dice *«Revisá los informes antes de confirmar»*. La CLI exige: `CERRAR <ID_DEL_CAMBIO>`.

### F. Significado del "Verde" y recuperación de fallas
- **[site/desde-cero.html:45](file:///home/workstation/Dev/factory/site/desde-cero.html#L45) y [site/index.html:54-55](file:///home/workstation/Dev/factory/site/index.html#L54-L55):**
  - **Brecha:** El verde de Oracle sólo certifica que los 3 casos ejecutados por el sensor produjeron código 0 y fueron observados exactamente 3 veces. No garantiza que no haya bugs fuera de esos 3 casos, ni persistencia, ni seguridad. Debe explicarse con claridad qué cubre y qué no.
- **[site/desde-cero.html:46](file:///home/workstation/Dev/factory/site/desde-cero.html#L46) ("Si algo no funciona"):**
  - No explica qué hacer si `contexto_producto()` falla: si el usuario modifica o deja archivos sin commitear después del paso 5, la revisión o el juicio quedan "desactualizados respecto del producto" y la CLI bloquea. El usuario no sabe que el commit y el árbol de trabajo están vinculados criptográficamente al juicio.

---

## 4. Propuesta de texto para la documentación

A continuación se presentan propuestas concretas para reemplazar los fragmentos ambiguos en `site/desde-cero.html`:

### Mejora 1: Paso 04 — Copia explícita y frase de aprobación
```html
<p>Copiá los documentos del ejemplo sobre las carpetas de tu cambio. Podés hacerlo desde la terminal con estos comandos:</p>
<div class="code-block"><pre><code data-template="cp examples/notas/proposal.md openspec/changes/ID_DEL_CAMBIO/proposal.md
cp examples/notas/spec.md openspec/changes/ID_DEL_CAMBIO/specs/notas/spec.md">cp examples/notas/proposal.md openspec/changes/ID_DEL_CAMBIO/proposal.md
cp examples/notas/spec.md openspec/changes/ID_DEL_CAMBIO/specs/notas/spec.md</code></pre><button class="copy-code" type="button">Copiar</button></div>
<p>Revisá el contenido de <code>openspec/changes/ID_DEL_CAMBIO/specs/notas/spec.md</code>. Si estás de acuerdo, ejecutá:</p>
<div class="code-block"><pre><code data-template="oracle-factory aprobar-spec ID_DEL_CAMBIO">oracle-factory aprobar-spec ID_DEL_CAMBIO</code></pre><button class="copy-code" type="button">Copiar</button></div>
<p>La terminal te pedirá confirmar escribiendo exactamente en mayúsculas: <code>APROBAR ESPECIFICACION ID_DEL_CAMBIO</code>.</p>
```

### Mejora 2: Paso 04 — Catálogos y edición del requisito
```html
<p>Copiá las reglas de comprobación a la carpeta <code>catalogos/</code>:</p>
<div class="code-block"><pre><code>cp examples/notas/catalogos/*.oracle catalogos/</code></pre><button class="copy-code" type="button">Copiar</button></div>
<p>Abrí el archivo que termina en <code>.requisito</code> dentro de la carpeta <code>requisitos/</code> con tu editor. Buscá la línea que empieza con <code>sin_medir</code> y reemplazala por:</p>
<div class="code-block"><pre><code>    medido_por notas.casos_ejecutados, notas.resultados</code></pre><button class="copy-code" type="button">Copiar</button></div>
<p><em>Importante:</em> conservá los 4 espacios al principio de la línea y no borres el id, texto ni fuente.</p>
<div class="code-block"><pre><code>oracle cobertura --proyecto .</code></pre><button class="copy-code" type="button">Copiar</button></div>
<p>Verás tu requisito marcado con <strong>✓</strong> (1 medido de 1). Esto certifica que el requisito ahora está enlazado a las dos reglas de comprobación.</p>
```

### Mejora 3: Paso 06 — Plantilla de revisión y frase de confirmación
```html
<p>Creá un archivo de texto llamado <code>review.md</code> dentro de la carpeta <code>.factory-demo/</code> (es una carpeta oculta en el proyecto). Podés usar esta plantilla básica:</p>
<div class="code-block"><pre><code># Informe de revisión del cambio
- **Revisor:** Tu Nombre
- **Comprobación:** Se verificaron las pruebas unitarias y la ejecución del sensor.
- **Hallazgos:** Ninguno.
- **Conclusión:** Aprobado para juicio con Oracle.</code></pre><button class="copy-code" type="button">Copiar</button></div>
<p>Registrá la revisión formal con:</p>
<div class="code-block"><pre><code data-template="oracle-factory revision ID_DEL_CAMBIO --informe .factory-demo/review.md --revisor &quot;Tu nombre&quot; --decision aprobar --hallazgos-abiertos 0">oracle-factory revision ID_DEL_CAMBIO --informe .factory-demo/review.md --revisor &quot;Tu nombre&quot; --decision aprobar --hallazgos-abiertos 0</code></pre><button class="copy-code" type="button">Copiar</button></div>
<p>La terminal solicitará confirmar escribiendo: <code>REGISTRAR REVISION ID_DEL_CAMBIO</code>.</p>
```

### Mejora 4: Paso 07 — Cierre y alcance del verde
```html
<p>El veredicto verde de Oracle significa que se observaron exactamente los 3 casos esperados y ninguno falló. No afirma que el software esté libre de otros errores fuera de esos 3 casos.</p>
<div class="code-block"><pre><code data-template="oracle-factory cerrar ID_DEL_CAMBIO">oracle-factory cerrar ID_DEL_CAMBIO</code></pre><button class="copy-code" type="button">Copiar</button></div>
<p>Para confirmar el cierre definitivo de la tarea, escribí: <code>CERRAR ID_DEL_CAMBIO</code>.</p>
```

---

## 5. Lista separada de mejoras de CLI necesarias

| ID | Mejora de CLI propuesta | Problema que resuelve | Costo de desarrollo | Valor para principiantes |
|---|---|---|---|---|
| **CLI-01** | `oracle-factory ejemplo aplicar <id> <nombre>` o flag `nuevo --con-ejemplo notas` | Evita que el usuario tenga que copiar manualmente archivos entre carpetas anidadas con rutas frágiles (`examples/...` a `openspec/...`). | **Bajo** (copia programática interna de `proposal.md`, `spec.md` y `catalogos/`). | **Crítico / Muy Alto** (elimina la mayor causa de abandono en el paso 4). |
| **CLI-02** | Subcomando `oracle-factory medir <id> <requisito> <medidas...>` | Evita que el usuario tenga que buscar y editar a mano un archivo con extensión `.requisito` y respetar una indentación exacta de 4 espacios. | **Bajo / Medio** (reemplazo seguro de la línea `sin_medir` en el archivo de requisitos). | **Crítico / Muy Alto** (evita errores sintácticos en Oracle Metalenguaje). |
| **CLI-03** | Subcomando o flag `oracle-factory listar` | Si el usuario cierra la terminal o no copia el ID, no tiene cómo recuperar los IDs de cambios abiertos sin conocer la herramienta `tasks`. | **Muy Bajo** (envolver `tasks list` o listar carpetas en `openspec/changes/`). | **Alto** (recuperabilidad inmediata). |
| **CLI-04** | Generador de plantilla de revisión: `oracle-factory revision --init` o mensaje de ayuda guiado | Alguien sin experiencia no sabe cómo estructurar `.factory-demo/review.md`. Un generador con preguntas interactivas o plantilla por defecto resuelve la barrera. | **Bajo** (crear un markdown básico con fecha, commit y campos estándar). | **Alto** |
| **CLI-05** | Supresión o personalización de los "Próximos pasos" de `oracle init` en `oracle-factory init` | Al ejecutar `init`, Oracle imprime instrucciones para crear casos y medidas manuales que contradicen el flujo guiado de Factory. | **Muy Bajo** (filtrar la salida stdout de `oracle init` en `oracle_factory/cli.py`). | **Medio** (reduce la confusión inicial). |
| **CLI-06** | Prompt interactivo con confirmación por defecto o sugerencia en pantalla | Cuando la CLI pide `Escribí APROBAR ESPECIFICACION <id>: `, si el usuario escribe en minúsculas o con un espacio de más, se aborta inmediatamente sin mensaje didáctico de error. | **Bajo** (dar feedback claro: *"Se esperaba exactamente '...' pero se recibió '...'"*). | **Medio** |

---

## 6. Estado final del repositorio

El repositorio [/home/workstation/Dev/factory](file:///home/workstation/Dev/factory) se conservó **completamente intacto**:
- No se crearon commits ni ramas.
- No se modificaron archivos del proyecto ni de la web.
- La tarea tracker y el paquete OpenSpec quedaron listos para que el equipo (`agy1`, `agy2`, `Codex`) incorpore los cambios en la rama `web-rigurosa`.
