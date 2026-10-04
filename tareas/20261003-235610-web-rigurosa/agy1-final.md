# Agy Task — 2026-10-03 21:52:57

**Tarea:** Revisión final de documentación, en español. Tu primera auditoría está en tareas/20261003-235610-web-rigurosa/agy1.md. Revisá SOLO site/index.html, site/factory.js y site/desde-cero.html actuales contra oracle_factory/cli.py y el ejemplo. No edites nada ni hagas aprobaciones/commits. Busca contradicciones residuales: capacidades presentes/futuras, simulación vs ejemplo, huellas vs procedencia de evidencia, cierre vs entrega, y afirmaciones sobre los casos y revisión. La pausa en medidas es elección humana manual, no un gate de la CLI: debe quedar explícito. Devolvé solo defectos concretos restantes con cita y corrección, o ninguna contradicción encontrada con límites de auditoría. No repitas propuestas ya aplicadas. No es piloto humano. Tiempo acotado; lectura, sin instalación ni tests.
**Directorio:** /home/workstation/Dev/factory
**Cuenta:** principal
**Modelo:** gemini-3.8-flash-high (esfuerzo high, timeout 6m)

---

# Auditoría Final de Documentación de Oracle Factory

**Alcance revisado:** Únicamente [site/index.html](file:///home/workstation/Dev/factory/site/index.html), [site/factory.js](file:///home/workstation/Dev/factory/site/factory.js) y [site/desde-cero.html](file:///home/workstation/Dev/factory/site/desde-cero.html), contrastados contra la implementación real en [oracle_factory/cli.py](file:///home/workstation/Dev/factory/oracle_factory/cli.py) y los archivos del ejemplo en [examples/notas/](file:///home/workstation/Dev/factory/examples/notas/).  
**Condiciones de la auditoría:** Solo lectura; sin edición de archivos, sin aprobaciones ni commits; sin ejecución de tests ni instalaciones de dependencias. Se excluyen propuestas ya aplicadas en la primera auditoría ([tareas/20261003-235610-web-rigurosa/agy1.md](file:///home/workstation/Dev/factory/tareas/20261003-235610-web-rigurosa/agy1.md)).

---

## 1. Estado de los Ejes Temáticos Auditados

1. **Capacidades presentes frente a futuras:** Las descripciones generales, la grilla del kit y los avisos de alcance diferencian adecuadamente lo disponible hoy de lo previsto. Persiste únicamente una divergencia en el HTML estático de carga inicial de la estación 01 ([site/index.html:35-36](file:///home/workstation/Dev/factory/site/index.html#L35-L36)), donde no se sincronizaron las aclaraciones de [site/factory.js:10,12,14](file:///home/workstation/Dev/factory/site/factory.js#L10-L14).
2. **Simulación vs. ejemplo:** Queda explícito que la escena animada contiene un ciclo ilustrativo de hallazgo y corrección (títulos con espacios), mientras que el código publicado en `examples/notas/notas.py` ya incluye `bool(titulo.strip())` y satisface los 3 casos desde el inicio.
3. **Huellas vs. procedencia de evidencia:** La documentación en JS y la guía explican correctamente que Factory calcula y valida *hashes* SHA-256 para detectar modificaciones posteriores en los hechos o en el producto, pero que no ejecuta el sensor ni valida de dónde provino el JSON de hechos (responsabilidad humana).
4. **Cierre vs. entrega:** La distinción entre cerrar localmente una tarea (`tasks close`, sellar `factory.json`) y desplegar o publicar un producto fue incorporada con coherencia en las tres páginas.
5. **Afirmaciones sobre los casos y revisión:** Tanto en la guía como en el script se explicita con exactitud técnica que el catálogo de Oracle solo cuenta filas de hechos (`contar(1) == 3` y `codigo != 0 <= 0`), por lo que Oracle no distingue por sí mismo los casos evaluados ni verifica la calidad técnica del informe de revisión.
6. **La pausa en medidas como elección humana manual y no un gate de la CLI:** En [site/factory.js:37](file:///home/workstation/Dev/factory/site/factory.js#L37) se introdujo la aclaración explícita (`"Esta pausa representa tu elección manual. No es una aprobación de medidas en la CLI de Factory"`). Sin embargo, **esta distinción aún no es explícita en la portada HTML ([site/index.html:32,58](file:///home/workstation/Dev/factory/site/index.html#L32)) ni en la guía paso a paso ([site/desde-cero.html:38](file:///home/workstation/Dev/factory/site/desde-cero.html#L38))**, donde la estación 03 se sigue rotulando con el símbolo de gate humano `◆` y agrupando con los gates reales de la terminal sin aclarar que la CLI carece de compuerta para ello.

---

## 2. Defectos Concretos Restantes

### Defecto 1: La pausa en medidas se presenta visualmente como compuerta sin explicitar en la portada que no es un gate de la CLI
* **Cita exacta 1:** [site/index.html:32](file:///home/workstation/Dev/factory/site/index.html#L32)
  ```html
  <button data-stage="2"><span>03</span>Medidas <i aria-label="Decisión humana">◆</i></button>
  ```
* **Cita exacta 2:** [site/index.html:58](file:///home/workstation/Dev/factory/site/index.html#L58)
  ```html
  <li><span>02</span><div><h3>Acordar la evidencia</h3><p>Qué podemos medir y qué juicio sigue siendo humano.</p></div></li>
  ```
* **Evidencia en CLI:** [oracle_factory/cli.py:243-267, 314-316](file:///home/workstation/Dev/factory/oracle_factory/cli.py#L243-L267)  
  En la CLI no existe ningún comando interactivo ni compuerta para acordar o aprobar medidas (a diferencia de `aprobar-spec`, `revision` y `cerrar`, que exigen confirmaciones escritas explícitas). `importar` deja los requisitos como `sin_medir` y `juzgar` solo verifica programáticamente la salida de `oracle cobertura`. Asociar las reglas es una edición manual del archivo `.requisito`.
* **Consecuencia:** El lector deduce que la CLI de Factory contiene un comando o compuerta formal ("acordar medidas") análogo a los otros tres gates interactivos.
* **Corrección propuesta:**
  * En [site/index.html:32](file:///home/workstation/Dev/factory/site/index.html#L32): retirar el rombo de gate de la botonera o aclarar su naturaleza manual:
    ```html
    <button data-stage="2"><span>03</span>Medidas</button>
    ```
  * En [site/index.html:58](file:///home/workstation/Dev/factory/site/index.html#L58): explicitar en la descripción de la parada 02 que es una elección manual y no un gate de la CLI:
    ```html
    <li><span>02</span><div><h3>Acordar la evidencia</h3><p>Elección humana manual de reglas y límites en Oracle; no es un gate en la CLI de Factory.</p></div></li>
    ```

---

### Defecto 2: Falta de explicitud sobre la ausencia de un gate de medidas en la guía práctica
* **Cita exacta:** [site/desde-cero.html:38](file:///home/workstation/Dev/factory/site/desde-cero.html#L38)
  ```html
  <p>Esperamos <strong>1 requisito medido, 0 sin medir</strong>, con ✓. Esa marca informa un enlace a medidas existentes; todavía no demuestra que el programa cumpla. Elegir esas medidas es una decisión humana sobre su pertinencia y sus límites.</p>
  ```
* **Evidencia en CLI:** [oracle_factory/cli.py:243-267, 471-477](file:///home/workstation/Dev/factory/oracle_factory/cli.py#L243-L267)  
  El usuario viene de usar `oracle-factory aprobar-spec` (con frase interactiva) y luego `oracle-factory importar`. Para las medidas, edita a mano el archivo y corre `oracle cobertura --proyecto .`. No hay intervención de la CLI de Factory.
* **Consecuencia:** Un lector que recorre la guía esperando los gates anunciados en la portada busca un comando inexistente para registrar o acordar las medidas en Factory.
* **Corrección propuesta:**
  Reemplazar el cierre del párrafo en [site/desde-cero.html:38](file:///home/workstation/Dev/factory/site/desde-cero.html#L38) por:
  ```html
  <p>Esperamos <strong>1 requisito medido, 0 sin medir</strong>, con ✓. Esa marca informa un enlace a medidas existentes; todavía no demuestra que el programa cumpla. Elegir esas medidas en el archivo .requisito es una decisión humana manual: la CLI de Factory no tiene un gate para aprobar medidas y solo comprueba la cobertura durante el juicio.</p>
  ```

---

### Defecto 3: Contradicción residual en el contenido estático de fallback de la estación 01 frente a la CLI y `factory.js`
* **Cita exacta:** [site/index.html:35-36](file:///home/workstation/Dev/factory/site/index.html#L35-L36)
  ```html
  <article class="explanation" aria-live="polite" aria-atomic="true"><div class="stage-heading"><p id="stage-tool" class="eyebrow">PERSONA + FACTORY</p><span id="stage-maturity" class="maturity">Disponible hoy</span></div><h3 id="stage-title">Todo empieza por una necesidad.</h3><p id="stage-copy">“Quiero guardar notas y que ninguna tenga el título vacío.” La persona trae el problema; vos aportás el contexto y Factory crea una tarea y documentos iniciales para el cambio.</p><dl class="artifacts"><div><dt>ENTRA</dt><dd id="stage-input">Una idea y su contexto</dd></div><div><dt>SALE</dt><dd id="stage-output">Un pedido con responsable</dd></div></dl></article>
  <aside class="decision" id="decision-panel"><p class="eyebrow" id="decision-label">LO QUE IMPORTA ACÁ</p><h4 id="decision-title">Primero, entender el problema.</h4><p id="decision-copy">Todavía no se escribe código. Acordar para quién construimos evita producir algo que nadie necesita.</p><div id="decision-actions"></div><p id="decision-feedback" role="status"></p></aside>
  ```
* **Evidencia en CLI y simulador:** [oracle_factory/cli.py:88-155](file:///home/workstation/Dev/factory/oracle_factory/cli.py#L88-L155); [site/factory.js:10,12,14](file:///home/workstation/Dev/factory/site/factory.js#L10-L14)  
  1. `cli.py:nuevo` no asigna ni recibe ningún campo de "responsable"; crea una tarea y esqueletos OpenSpec. En `factory.js:12` se corrigió la salida a `"Una tarea y plantillas por completar"`, pero el HTML estático de [site/index.html:35](file:///home/workstation/Dev/factory/site/index.html#L35) quedó desincronizado con `"Un pedido con responsable"`.
  2. `factory.js:10` retiró `"Quiero guardar notas"` para ser fiel a [site/index.html:38](file:///home/workstation/Dev/factory/site/index.html#L38) (*"sin guardado de notas"*), pero `index.html:35` aún lo mantiene.
  3. `factory.js:14` agregó la aclaración de presente `"Factory no redacta el acuerdo por vos"`, ausente en `index.html:36`.
* **Consecuencia:** Antes de la hidratación de JavaScript o con lectores que no ejecutan scripts, la página presenta un artefacto de salida ficticio ("responsable") y promesas no ajustadas.
* **Corrección propuesta:**
  Sincronizar el contenido estático de [site/index.html:35-36](file:///home/workstation/Dev/factory/site/index.html#L35-L36) con [site/factory.js:10,12,14](file:///home/workstation/Dev/factory/site/factory.js#L10-L14):
  ```html
  <article class="explanation" aria-live="polite" aria-atomic="true"><div class="stage-heading"><p id="stage-tool" class="eyebrow">PERSONA + FACTORY</p><span id="stage-maturity" class="maturity">Disponible hoy</span></div><h3 id="stage-title">Todo empieza por una necesidad.</h3><p id="stage-copy">“Quiero que ninguna nota tenga el título vacío.” Vos aportás el contexto y Factory crea una tarea y documentos iniciales para el cambio.</p><dl class="artifacts"><div><dt>ENTRA</dt><dd id="stage-input">Una idea y su contexto</dd></div><div><dt>SALE</dt><dd id="stage-output">Una tarea y plantillas por completar</dd></div></dl></article>
  <aside class="decision" id="decision-panel"><p class="eyebrow" id="decision-label">LO QUE IMPORTA ACÁ</p><h4 id="decision-title">Primero, entender el problema.</h4><p id="decision-copy">Acordar para quién construimos evita producir algo que nadie necesita. Factory no redacta el acuerdo por vos.</p><div id="decision-actions"></div><p id="decision-feedback" role="status"></p></aside>
  ```

---

### Defecto 4: Desalineación entre la rotulación de la estación 07 en el canvas de Pixel Art y el resto de la interfaz
* **Cita exacta:** [site/factory.js:288](file:///home/workstation/Dev/factory/site/factory.js#L288)
  ```javascript
  const labels=['PEDIDO','SPEC','MEDIDAS','CÓDIGO','PRUEBAS','REVISIÓN','ORACLE','CIERRE'];
  ```
* **Evidencia en código y accesibilidad:** [site/index.html:28, 32](file:///home/workstation/Dev/factory/site/index.html#L28)  
  En el botón de navegación de [site/index.html:32](file:///home/workstation/Dev/factory/site/index.html#L32) la estación 07 se llama `"07 Evidencia"`, y en el `aria-label` del canvas ([site/index.html:28](file:///home/workstation/Dev/factory/site/index.html#L28)) se lista como `"evidencia"`. Las demás 7 estaciones del canvas coinciden palabra por palabra con los botones. Rotular la estación como `ORACLE` en el dibujo confunde el nombre de la etapa del flujo con la herramienta que lo evalúa.
* **Consecuencia:** Inconsistencia terminológica entre lo que lee el usuario en pantalla/accesibilidad y lo dibujado en la cinta del taller.
* **Corrección propuesta:**
  En [site/factory.js:288](file:///home/workstation/Dev/factory/site/factory.js#L288), cambiar `'ORACLE'` por `'EVIDENCIA'`:
  ```javascript
  const labels=['PEDIDO','SPEC','MEDIDAS','CÓDIGO','PRUEBAS','REVISIÓN','EVIDENCIA','CIERRE'];
  ```

---

## 3. Conclusión de la Auditoría

Fuera de los 4 defectos concretos señalados (donde destaca la necesidad de explicitar tanto en [site/index.html](file:///home/workstation/Dev/factory/site/index.html) como en [site/desde-cero.html](file:///home/workstation/Dev/factory/site/desde-cero.html) que la pausa en medidas es una elección y edición humana manual sin compuerta en la CLI), los textos actuales de los tres archivos reflejan con fidelidad técnica el comportamiento real de `oracle-factory 0.1.0a2`, la estructura del ejemplo `notas` y los límites criptográficos y operacionales del sistema.
