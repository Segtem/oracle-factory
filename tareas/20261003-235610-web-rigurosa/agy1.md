# Agy Task — 2026-10-03 20:59:45

**Tarea:** Trabajá en español. Audita la documentación de Oracle Factory como revisor de precisión. Repositorio /home/workstation/Dev/factory, tarea 20261003-235610-web-rigurosa. NO modifiques archivos, NO hagas commits/push ni aprobaciones reales. El wrapper guardará tu respuesta en la tarea. Podés leer site/index.html, site/factory.js, site/desde-cero.html, README.md, oracle_factory/cli.py y ejemplos/tests. PyPI ya tiene oracle-factory 0.1.0a2; dependencias Oracle 0.38.1 y Oracle Task 0.2.0. Clue 0.1.0a1 prepara contexto y valida revisión externa; no genera una revisión automática con IA y no está integrado automáticamente en Factory. Contrasta TODAS las afirmaciones concretas de portada, comparación, ocho estaciones y guía con código/ejemplo real. Señala discrepancias: capacidad presente frente a visión, revisión vs evidencia, gates humanos, cobertura/vigencia, aceptación de riesgos, pruebas frente a observaciones, cierre local frente a entrega o despliegue, OpenSpec formato frente a integración de CLI. Devuelve una tabla de hallazgos con severidad, cita breve exacta + archivo:línea, evidencia de CLI archivo:línea, consecuencia, reemplazo textual propuesto. Priorizá verificables, no apreciaciones vagas. Al final sugerí estructura breve para explicar el flujo real del alpha a alguien que no sabe del tema. No ejecutes rondas largas ni edites el repo.
**Directorio:** /home/workstation/Dev/factory
**Cuenta:** principal
**Modelo:** gemini-3.8-flash-high (esfuerzo high, timeout 20m)

---

# Auditoría de Precisión de Documentación — Oracle Factory (Alpha 0.1.0a2)

- **Repositorio:** `/home/workstation/Dev/factory`
- **Tarea:** `20261003-235610-web-rigurosa`
- **Alcance auditado:** [site/index.html](file:///home/workstation/Dev/factory/site/index.html), [site/factory.js](file:///home/workstation/Dev/factory/site/factory.js), [site/desde-cero.html](file:///home/workstation/Dev/factory/site/desde-cero.html), [README.md](file:///home/workstation/Dev/factory/README.md), contrastados contra la implementación real en [oracle_factory/cli.py](file:///home/workstation/Dev/factory/oracle_factory/cli.py) y ejemplos/tests.
- **Contexto verificado:** `oracle-factory 0.1.0a2` ya está publicado en PyPI; dependencias directas `oracle-metalenguaje 0.38.1` y `oracle-task 0.2.0`. `oracle-clue 0.1.0a1` solo prepara contexto y valida esquemas de informes externos (no genera revisiones con IA ni está acoplado en la CLI de Factory).

---

## 1. Análisis de Discrepancias por Ejes Clave

### 1. Capacidad presente frente a visión
* **Discrepancia:** La portada ([site/index.html:22-24](file:///home/workstation/Dev/factory/site/index.html#L22-L24)) y el simulador ([site/factory.js:9](file:///home/workstation/Dev/factory/site/factory.js#L9)) proclaman «IA QUE CONSTRUYE», «Factory coordina el kit, los agentes hacen el trabajo» y «Factory coordina la producción completa: planificar, construir, comprobar, corregir y entregar».
* **Realidad técnica:** En [oracle_factory/cli.py](file:///home/workstation/Dev/factory/oracle_factory/cli.py#L458-L502) no existe código de orquestación de agentes, llamadas a LLMs ni ejecución de compiladores/runners. Como reconoce honestamente [README.md:5](file:///home/workstation/Dev/factory/README.md#L5), «la implementación del producto y las pruebas se ejecutan por fuera de la CLI». Factory es hoy una herramienta de línea de comandos para custodiar compuertas (*gates*) y vigencia criptográfica de artefactos en Git.

### 2. Revisión vs. evidencia
* **Discrepancia:** [site/factory.js:11](file:///home/workstation/Dev/factory/site/factory.js#L11) afirma que «Clue revisará los cambios de código y señalará posibles defectos con evidencia. En nuestro ejemplo detecta que un título hecho solo de espacios se acepta».
* **Realidad técnica:** Clue 0.1.0a1 no realiza análisis estático ni razonamiento automático con IA. Factory CLI no invoca a Clue en ninguna parte de su código: el comando `oracle-factory revision` ([oracle_factory/cli.py:268-300](file:///home/workstation/Dev/factory/oracle_factory/cli.py#L268-L300)) recibe cualquier archivo de texto mediante `--informe`, valida que no esté vacío y almacena su hash SHA-256 junto con la decisión humana.

### 3. Gates humanos
* **Discrepancia:** En la barra de estaciones de la portada ([site/index.html:32](file:///home/workstation/Dev/factory/site/index.html#L32)) y en [site/factory.js:8](file:///home/workstation/Dev/factory/site/factory.js#L8), la etapa «03 Medidas» figura con rombo de decisión humana (`gate: true`, bloqueando el avance interactivo).
* **Realidad técnica:** En [oracle_factory/cli.py](file:///home/workstation/Dev/factory/oracle_factory/cli.py) **no existe un gate ni comando para aprobar medidas**. Los únicos gates humanos con prompt interactivo son:
  1. `aprobar-spec`: escribe `APROBAR ESPECIFICACION <id>` ([cli.py:231](file:///home/workstation/Dev/factory/oracle_factory/cli.py#L231)).
  2. `revision`: escribe `REGISTRAR REVISION <id>` ([cli.py:284](file:///home/workstation/Dev/factory/oracle_factory/cli.py#L284)).
  3. `cerrar`: escribe `CERRAR <id>` ([cli.py:398](file:///home/workstation/Dev/factory/oracle_factory/cli.py#L398)).
  La asociación de medidas se hace editando manualmente el archivo `.requisito` de Oracle y la CLI se limita a verificar programáticamente la cobertura durante `juzgar` ([cli.py:314-316](file:///home/workstation/Dev/factory/oracle_factory/cli.py#L314-L316)).

### 4. Cobertura y vigencia
* **Discrepancia:** La web presenta las etapas como paradas secuenciales estáticas sin advertir el costo de invalidación cruzada.
* **Realidad técnica:** [oracle_factory/cli.py:178-205](file:///home/workstation/Dev/factory/oracle_factory/cli.py#L178-L205) calcula `contexto_producto()` (HEAD y SHA-256 de todos los archivos trackeados y nuevos no ignorados). Si el producto cambia tras la revisión o el juicio, quedan inmediatamente desactualizados ([cli.py:363-369](file:///home/workstation/Dev/factory/oracle_factory/cli.py#L363-L369)). Asimismo, registrar una revisión resetea el veredicto previo de Oracle (`estado["oracle"] = None`, [cli.py:295](file:///home/workstation/Dev/factory/oracle_factory/cli.py#L295)), y re-aprobar la spec borra requisitos, revisión y juicio ([cli.py:237](file:///home/workstation/Dev/factory/oracle_factory/cli.py#L237)).

### 5. Aceptación de riesgos
* **Discrepancia:** [site/index.html:58](file:///home/workstation/Dev/factory/site/index.html#L58) dice textualmente: «03 Resolver los hallazgos: Corregir, descartar con motivo o aceptar un riesgo».
* **Realidad técnica:** En [oracle_factory/cli.py:275-276](file:///home/workstation/Dev/factory/oracle_factory/cli.py#L275-L276) el validador exige taxativamente:
  ```python
  if abiertos < 0 or (decision == "aprobar" and abiertos):
      raise FactoryError("una revisión aprobada exige cero hallazgos abiertos")
  ```
  La CLI **no tiene ningún mecanismo para aceptar riesgos con hallazgos abiertos**. Cualquier descarte o asunción de riesgo debe quedar resuelto y justificado dentro del informe de revisión Markdown, pasándose formalmente a Factory con `--hallazgos-abiertos 0`.

### 6. Pruebas frente a observaciones
* **Discrepancia:** La estación 05 se titula genéricamente «Pruebas» ([site/index.html:32](file:///home/workstation/Dev/factory/site/index.html#L32)), y en [site/factory.js:10](file:///home/workstation/Dev/factory/site/factory.js#L10) se mezclan tests unitarios con hechos observados.
* **Realidad técnica:** En la arquitectura de Oracle, las pruebas unitarias ([examples/notas/test_notas.py](file:///home/workstation/Dev/factory/examples/notas/test_notas.py)) verifican aserciones internas de código. Por separado, el sensor ([examples/notas/sensor.py](file:///home/workstation/Dev/factory/examples/notas/sensor.py)) ejecuta el sistema y genera hechos estructurados JSON (`hechos.json`). Oracle no corre tests; evalúa hechos observables contra reglas formales de catálogo ([oracle_factory/cli.py:317](file:///home/workstation/Dev/factory/oracle_factory/cli.py#L317)).

### 7. Cierre local frente a entrega o despliegue
* **Discrepancia:** [site/index.html:32](file:///home/workstation/Dev/factory/site/index.html#L32), [site/index.html:55](file:///home/workstation/Dev/factory/site/index.html#L55) y [site/factory.js:13](file:///home/workstation/Dev/factory/site/factory.js#L13) denominan a la estación final «08 Entrega», hablando de «¿Está listo para entregar?» y «Una entrega aceptada y trazable».
* **Realidad técnica:** El comando real es `oracle-factory cerrar <id>` ([oracle_factory/cli.py:392-411](file:///home/workstation/Dev/factory/oracle_factory/cli.py#L392-L411)). No compila binarios, no empaqueta, no hace push a GitHub ni despliega nada en producción. Simplemente invoca `tasks close <id>` y sella el archivo local `factory.json` en fase `cerrada`.

### 8. OpenSpec: formato frente a integración de CLI
* **Discrepancia:** [site/index.html:50](file:///home/workstation/Dev/factory/site/index.html#L50) y [site/factory.js:7](file:///home/workstation/Dev/factory/site/factory.js#L7) presentan OpenSpec como «Formato integrado» y sugieren integración de ciclo de vida completo.
* **Realidad técnica:** Factory no interactúa con la CLI de OpenSpec ([README.md:67](file:///home/workstation/Dev/factory/README.md#L67)). Solo genera una estructura de carpetas `openspec/changes/<id>/` con archivos Markdown estándar. La importación de requisitos la realiza directamente `oracle requisito importar` ([cli.py:253](file:///home/workstation/Dev/factory/oracle_factory/cli.py#L253)). Además, al cerrar la tarea, Factory **no archiva el cambio de OpenSpec** ([README.md:63](file:///home/workstation/Dev/factory/README.md#L63)), dejándolo indefinidamente en `changes/`.

---

## 2. Tabla de Hallazgos

| Severidad | Cita breve exacta (`archivo:línea`) | Evidencia en código/CLI (`archivo:línea`) | Consecuencia | Reemplazo textual propuesto |
| :--- | :--- | :--- | :--- | :--- |
| **Alta** | `site/index.html:22`<br>`"IA QUE CONSTRUYE. PERSONAS QUE DECIDEN."` | [oracle_factory/cli.py:458-502](file:///home/workstation/Dev/factory/oracle_factory/cli.py#L458-L502); [README.md:5,32](file:///home/workstation/Dev/factory/README.md#L5) | Atribuye a la herramienta actual generación de código con IA que no existe en el paquete alpha. | `GATES HUMANOS Y EVIDENCIA. VISIÓN DE FÁBRICA ASISTIDA.` |
| **Alta** | `site/index.html:24`<br>`"Factory coordina el kit, los agentes hacen el trabajo y vos decidís qué merece avanzar."` | [oracle_factory/cli.py:1-506](file:///home/workstation/Dev/factory/oracle_factory/cli.py#L1-L506); [README.md:5](file:///home/workstation/Dev/factory/README.md#L5) | Sugiere que la CLI orquesta agentes que implementan código, cuando la codificación es manual y externa. | `Factory custodia los acuerdos y la evidencia; las personas o herramientas externas construyen y vos decidís qué avanza.` |
| **Alta** | `site/index.html:48`<br>`"Factory coordina la producción completa: planificar, construir, comprobar, corregir y entregar."` | [oracle_factory/cli.py:463-483](file:///home/workstation/Dev/factory/oracle_factory/cli.py#L463-L483) | Promesa excesiva de plataforma integral; la CLI solo gestiona compuertas de verificación y estado. | `Factory verifica los puntos críticos del ciclo: acuerdos de alcance, requisitos medibles, revisión de código y evidencia reproducible.` |
| **Alta** | `site/index.html:58`<br>`"03 Resolver los hallazgos: Corregir, descartar con motivo o aceptar un riesgo."` | [oracle_factory/cli.py:275-276](file:///home/workstation/Dev/factory/oracle_factory/cli.py#L275-L276); [cli.py:347-348](file:///home/workstation/Dev/factory/oracle_factory/cli.py#L347-L348) | La CLI rechaza con error cualquier aprobación con `hallazgos_abiertos > 0`. No existe un flujo para «aceptar riesgo» con issues abiertos. | `03 Resolver los hallazgos: Corregir o justificar cada punto en el informe escrito, cerrando todos los hallazgos antes de aprobar.` |
| **Alta** | `site/factory.js:8`<br>`{tool:'ORACLE + PERSONA', maturity:'Medidas en el prototipo', ..., tracker:'Esperando criterio de medición', gate:true}` | [oracle_factory/cli.py:243-267](file:///home/workstation/Dev/factory/oracle_factory/cli.py#L243-L267); [cli.py:314-316](file:///home/workstation/Dev/factory/oracle_factory/cli.py#L314-L316) | El simulador inventa una compuerta formal interactiva («Acordar estas medidas») que no existe como comando ni gate en Factory CLI. | Cambiar a `gate:false`, `maturity:'Configuración en Oracle'` y explicar que las medidas se asocian editando los archivos `.requisito`. |
| **Alta** | `site/factory.js:11`<br>`"Clue revisará los cambios de código y señalará posibles defectos con evidencia. En nuestro ejemplo detecta que un título hecho solo de espacios se acepta."` | [oracle_factory/cli.py:268-300](file:///home/workstation/Dev/factory/oracle_factory/cli.py#L268-L300); [README.md:5](file:///home/workstation/Dev/factory/README.md#L5) | Hace creer que Clue ejecuta una auditoría de código con IA integrada, cuando Clue 0.1.0a1 no tiene IA y Factory solo recibe un archivo `--informe`. | `La revisión busca defectos en el cambio (como un título de solo espacios). En este alpha registrás el informe de un revisor externo con oracle-factory revision.` |
| **Media** | `site/index.html:52`<br>`"Implementan el producto y ejecutan pruebas. Si aparece un problema, vuelven al código con el contexto del cambio."` | [oracle_factory/cli.py:463-483](file:///home/workstation/Dev/factory/oracle_factory/cli.py#L463-L483); [README.md:32](file:///home/workstation/Dev/factory/README.md#L32) | Redactado en presente activo indicando capacidad funcional inmediata, a pesar del badge «prevista». | `En la visión de Factory, implementarán el producto y sus pruebas. En la POC actual, la implementación se realiza fuera de la CLI.` |
| **Media** | `site/index.html:61`<br>`"01 / PEDÍ ... Factory reúne el contexto y te muestra una propuesta concreta."` | [oracle_factory/cli.py:102-130](file:///home/workstation/Dev/factory/oracle_factory/cli.py#L102-L130) | `nuevo` solo genera esqueletos estáticos con comentarios `TODO:`. No analiza contexto ni genera propuestas inteligentes. | `01 / PEDÍ ... Factory inicializa la tarea y las plantillas OpenSpec para que definas el problema y su alcance.` |
| **Media** | `site/index.html:32` / `site/factory.js:13`<br>`"08 Entrega"`, `"¿Está listo para entregar?"`, `"Una entrega aceptada y trazable"` | [oracle_factory/cli.py:392-411](file:///home/workstation/Dev/factory/oracle_factory/cli.py#L392-L411); [site/desde-cero.html:45](file:///home/workstation/Dev/factory/site/desde-cero.html#L45) | Confunde el cierre formal de una tarea de seguimiento local (`tasks close`) con la entrega o despliegue (*delivery/release*) del software. | Reemplazar por `Cierre` / `Cierre de tarea`. `"¿Cumple las condiciones de cierre?"` y `"Una tarea cerrada con evidencia verificada"`. |
| **Media** | `site/factory.js:61`<br>`"Los agentes ajustan la validación para rechazar también títulos que solo contienen espacios. Se agrega una prueba para ese caso..."` | [oracle_factory/cli.py:458-502](file:///home/workstation/Dev/factory/oracle_factory/cli.py#L458-L502); [examples/notas/notas.py](file:///home/workstation/Dev/factory/examples/notas/notas.py) | Describe un bucle de corrección automática por agentes inexistente en el alpha. | `Ajustás la validación en notas.py para rechazar títulos con solo espacios y agregás la prueba. El cambio vuelve a recorrer pruebas y sensor.` |
| **Media** | `site/desde-cero.html:8`<br>`"Factory 0.1.0a2 migra a Oracle Task y está preparado para publicar en PyPI. Los comandos de esta guía requieren esa publicación."` | Contexto de release PyPI; [site/index.html:62](file:///home/workstation/Dev/factory/site/index.html#L62) | Afirma que la publicación en PyPI está pendiente, cuando `oracle-factory 0.1.0a2` ya está disponible en PyPI. | `Factory 0.1.0a2 está publicado en PyPI y migrado a Oracle Task. Los comandos de esta guía se instalan directamente con uv.` |
| **Media** | `README.md:12`<br>`"Su publicación en PyPI está pendiente; los comandos siguientes se usan después de publicarla."` | Contexto de release PyPI; [site/index.html:62](file:///home/workstation/Dev/factory/site/index.html#L62) | Documentación desactualizada respecto al estado real de PyPI. | `La versión alpha 0.1.0a2 está publicada en PyPI y migrada a Oracle Task.` |
| **Media** | `site/desde-cero.html:21`<br>`"Copiá examples/notas/spec.md sobre specs/notas/spec.md de ese mismo cambio."` | [oracle_factory/cli.py:98-101](file:///home/workstation/Dev/factory/oracle_factory/cli.py#L98-L101) | La ruta relativa al proyecto es `openspec/changes/<id>/specs/notas/spec.md`. Decir `specs/...` confunde a principiantes. | `Copiá examples/notas/spec.md sobre openspec/changes/ID_DEL_CAMBIO/specs/notas/spec.md.` |
| **Baja** | `site/index.html:61`<br>`"02 / DECIDÍ ... Un tablero de decisiones pendientes, con el motivo, la evidencia y las opciones para continuar."` | [oracle_factory/cli.py:413-423](file:///home/workstation/Dev/factory/oracle_factory/cli.py#L413-L423) | Sugiere la existencia de un dashboard o UI tipo Kanban interactivo. En la CLI solo existe `oracle-factory estado <id>`. | `02 / DECIDÍ ... La terminal te indica exactamente qué compuerta está pendiente: spec, revisión o veredicto de evidencia.` |
| **Baja** | `site/desde-cero.html:19`<br>`"Deberías ver init, ejemplo, nuevo, aprobar-spec, importar, revision, juzgar y cerrar."` | [oracle_factory/cli.py:471-474](file:///home/workstation/Dev/factory/oracle_factory/cli.py#L471-L474) | Omite el comando `estado` de la lista de comandos disponibles que imprime el parser de CLI. | `Deberías ver init, ejemplo, nuevo, aprobar-spec, importar, revision, juzgar, cerrar y estado.` |

---

## 3. Estructura Sugerida para Explicar el Flujo Real del Alpha

Para explicar Oracle Factory 0.1.0a2 a una persona que no conoce el sistema sin generar falsas expectativas ni confusiones técnicas, se sugiere estructurar la explicación en **4 momentos reales y verificables**:

### 1. El Propósito: Una compuerta de confianza en tu propio Git
> «Factory no es un bot que escribe código solo: es un auditor estricto en tu terminal que no te deja dar por terminada una tarea hasta que demuestres que hiciste lo acordado.»

### 2. Los Cuatro Pasos Reales de la CLI:
1. **Acordar qué vas a construir (`nuevo` y `aprobar-spec`)**
   * Creás una tarea vinculada a una especificación escrita en Markdown (OpenSpec).
   * Escribís los escenarios esperados y confirmás explícitamente en la terminal que ese es el alcance aceptado antes de tocar el código.
2. **Medir los requisitos (`importar` y catálogos de Oracle)**
   * Importás los requisitos de la especificación a Oracle. Nacen *sin medir*.
   * Declarás qué regla objetiva evalúa cada promesa (asociando medidas).
3. **Construir, probar y revisar fuera de Factory (Git + Tests + Sensor + `revision`)**
   * Vos o tu asistente programan la app y corren sus pruebas normales.
   * Un sensor guarda lo que pasó (`hechos.json`) y hacés un commit en Git.
   * Adjuntás un informe de revisión de código (humano o de CodeRabbit) y registrás en Factory que no quedaron problemas pendientes (`revision`).
4. **Verificar la evidencia y cerrar (`juzgar` y `cerrar`)**
   * Oracle contrasta los hechos del sensor con las reglas (`juzgar`).
   * Si todo está verde y la evidencia corresponde exactamente al commit actual, confirmás el cierre de la tarea (`cerrar`). Si algo cambió en el código tras la revisión, Factory lo detecta y exige volver a revisar.

### 3. Las Tres Reglas de Oro del Alpha:
* **El código lo hacés vos (o tu herramienta):** Factory no tiene IA propia incorporada hoy; custodia las decisiones humanas.
* **Cero hallazgos abiertos:** No se puede cerrar con advertencias ignoradas; todo descarte debe estar documentado en el informe.
* **Si el código cambia, la evidencia vence:** Cambiar un archivo invalida revisiones y juicios anteriores para evitar falsos verdes.
