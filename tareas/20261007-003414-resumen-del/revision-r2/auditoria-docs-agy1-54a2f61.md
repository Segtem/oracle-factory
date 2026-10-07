# Auditoría de Documentación y Código: Capacidad «Resumen» (oracle-factory)

**Fecha:** 2026-10-06  
**Repositorio examinado:** `/home/workstation/Dev/_revisiones/factory-resumen-54a2f61`  
**Modalidad:** Sólo lectura (sin modificaciones en el árbol del proyecto ni commits).  
**Documentos y código auditados:**
- `docs/estructura.md` (árbol y sección «El estado actual en una lectura»)
- `oracle_factory/cli.py` (`LEEME_FACTORY`, `texto_resumen`, `comando_resumen`, `actualizar_resumen`, `cerrar`, `archivar`)
- `openspec/changes/20261007-003414-resumen-del/proposal.md`
- `openspec/changes/20261007-003414-resumen-del/design.md`
- `openspec/changes/20261007-003414-resumen-del/specs/resumen/spec.md`
- `oracle_factory/resumen.py`
- `.factory/resumen.md` (generado en el repositorio)

---

## 1. Resumen Ejecutivo

La capacidad `resumen` cumple con el objetivo medular de ofrecer una vista corta, consolidada y libre de llamadas a LLM que sintetiza lo vigente, lo abierto, los riesgos aceptados y los límites declarados. Su integración automática al cerrar y archivar es limpia, determinista y atómica.

Sin embargo, el contraste riguroso entre la especificación, la propuesta, el diseño, la documentación de usuario y el código real revela **contradicciones concretas**:
1. **Incumplimiento de contrato en la tabla de requisitos vigentes:** Tanto la spec como la propuesta exigen incluir el «requisito de Oracle» de cada ítem vigente; el código extrae el identificador pero lo omite en la salida Markdown.
2. **Enlaces relativos rotos con `--salida`:** La función `--salida RUTA` (promocionada para GitHub como `RESUMEN.md`) genera enlaces relativos rotos (`../openspec/...`) fuera de `.factory/`.
3. **Discrepancia de fuentes entre diseño e implementación:** El diseño especifica leer medidas de `registro['medidas'][rid]` y el código las lee directamente del archivo `.requisito` en disco.
4. **Engaño y ruido cognitivo para el lector:** Un lector sin conocimiento previo interpreta los veredictos «verde al cerrar el...» como un estado verde actual de todo el código en HEAD (lo cual no está garantizado), y se enfrenta a 6 cambios obsoletos presentados como «abiertos» con pendientes incompletos o engañosos.

---

## 2. Defectos y Contradicciones Concretas

Se listan a continuación los defectos normativos donde un documento contradice a otro o donde el código contradice la especificación / propuesta, con su cita y corrección propuesta.

### Defecto D-01: Omisión del requisito de Oracle en la tabla de lo vigente
- **Citas en conflicto:**
  - `openspec/changes/20261007-003414-resumen-del/specs/resumen/spec.md:7`:
    > `oracle-factory resumen SHALL escribir .factory/resumen.md con los requisitos vigentes de cada capacidad (tipo, requisito de Oracle, cambio de origen, medidas y veredicto)...`
  - `openspec/changes/20261007-003414-resumen-del/proposal.md:10`:
    > `- Lo vigente, por capacidad: cada requisito con su tipo, su requisito de Oracle, el cambio del que viene, sus medidas y el veredicto con el que se cerró ese cambio.`
  - `oracle_factory/resumen.py:58-63`:
    ```python
    58: '| Requisito | Tipo | Medidas | Veredicto | Cambio de origen |', '|---|---|---|---|---|']
    59: for nombre, req in indice['requisitos'].items():
    60:     rid = req['requisito']
    61:     cuerpo.append(f"| {_celda(nombre)} | {_tipo(req.get('cuerpo', []))} | "
    62:                   f"{_celda(', '.join(medidas.get(rid, [])) or 'sin medir')} | {_veredicto(registros.get(req['cambio']))} | "
    63:                   f"{req['cambio']} |")
    ```
  - `.factory/resumen.md:16`:
    > `| Requisito | Tipo | Medidas | Veredicto | Cambio de origen |`
- **Explicación:**
  La especificación formal y la propuesta exigen explícitamente mostrar el **requisito de Oracle** (`req['requisito']`). El código en `resumen.py:60` obtiene `rid`, pero lo utiliza únicamente para consultar el diccionario `medidas.get(rid, [])`. El `rid` nunca se agrega a las columnas de la tabla. En `.factory/resumen.md`, sólo figura el título en lenguaje natural de OpenSpec (ej. `la spec de un cambio se fusiona al cerrarlo`). Si un requisito está `sin medir`, el ID de Oracle se pierde por completo para el lector.
  *(Nota: En `tests/test_resumen.py:59,66`, el test obtiene `rid = ...` pero luego hace `self.assertTrue(rid)` en lugar de assertar su presencia en el texto generado, encubriendo el defecto).*
- **Corrección propuesta:**
  En `oracle_factory/resumen.py`, agregar la columna de Oracle (o mostrarlo junto al nombre, p. ej. `Requisito de Oracle | Requisito OpenSpec | ...` o en una columna dedicada `Requisito Oracle`), o si se decide mantener 5 columnas por espacio, modificar formalmente la spec y la proposal mediante un delta que declare la decisión de omitirlo.

---

### Defecto D-02: Enlaces relativos a specs consolidadas rotos al usar `--salida RUTA`
- **Citas en conflicto:**
  - `openspec/changes/20261007-003414-resumen-del/specs/resumen/spec.md:7, 57`:
    > `... y un enlace a la spec consolidada de cada capacidad, sin copiar sus escenarios.`
    > `... y resumen --salida RUTA SHALL escribirlo en la ruta indicada dentro del proyecto.`
  - `openspec/changes/20261007-003414-resumen-del/proposal.md:15`:
    > `--salida RUTA lo escribe en otro lugar (por ejemplo un RESUMEN.md para leer en GitHub).`
  - `docs/estructura.md:109`:
    > `--salida RUTA lo escribe en otro lugar del proyecto (por ejemplo RESUMEN.md); fuera de .factory/, ese archivo sí cuenta en la huella.`
  - `oracle_factory/resumen.py:57`:
    ```python
    cuerpo += ['', f'### {cap}', '', f'Spec completa: [openspec/specs/{cap}/spec.md](../openspec/specs/{cap}/spec.md)', '',
    ```
- **Explicación:**
  El enlace a la spec consolidada está fijado como `../openspec/specs/{cap}/spec.md`. Este enlace relativo sólo es válido cuando el archivo reside en `.factory/resumen.md`. Cuando se ejecuta `oracle-factory resumen --salida RESUMEN.md` (como propone la guía y la propuesta para la raíz del repositorio), el enlace relativo apunta a `../openspec/...`, es decir, al directorio padre por fuera del repositorio Git. En GitHub o en cualquier visor Markdown local, el enlace queda roto (HTTP 404).
- **Corrección propuesta:**
  Hacer que el generador reciba la ruta destino relativa al proyecto (o la profundidad de la carpeta) para calcular la ruta relativa canónica hacia `openspec/specs/{cap}/spec.md` (`os.path.relpath`), o emitir la ruta relativa adecuada según el destino.

---

### Defecto D-03: Discrepancia sobre la fuente de las medidas (`design.md` vs `cli.py`)
- **Citas en conflicto:**
  - `openspec/changes/20261007-003414-resumen-del/design.md:6`:
    > `- Fuentes: ... registro del cambio de origen (oracle.codigo, cierre.cuando, medidas[rid]); ...`
  - `oracle_factory/cli.py:973-979`:
    ```python
    medidas = {}
    for indice in indices:
        for req in indice["requisitos"].values():
            ruta = ROOT / "requisitos" / f"{req['requisito']}.requisito"
            texto = ruta.read_text(encoding="utf-8") if ruta.is_file() else ""
            m = re.search(r"(?m)^\s+medido_por\s+(.+?)\s*$", texto)
            medidas[req["requisito"]] = [x.strip() for x in m[1].split(",")] if m else []
    ```
- **Explicación:**
  `design.md` estipula que las medidas se leen del registro del cambio de origen (`medidas[rid]` dentro de `factory.json`). En cambio, la implementación en `cli.py:texto_resumen` ignora `registro.get('medidas')` y parsea dinámicamente la directiva `medido_por` de los archivos `requisitos/<rid>.requisito` en el árbol de trabajo. Si bien esto refleja las medidas registradas en Oracle, contradice la nota de diseño sin explicación de la desviación.
- **Corrección propuesta:**
  Actualizar `design.md` para documentar que las medidas se extraen de `requisitos/<rid>.requisito` (que es la fuente de verdad de Oracle para `medido_por`), eliminando la mención a `medidas[rid]` del registro del cambio cerrado.

---

### Defecto D-04: Código muerto y comprobación de huella no utilizada en `resumen.py`
- **Citas en conflicto:**
  - `oracle_factory/resumen.py:11`:
    ```python
    CABECERA = re.compile(r'^<!-- oracle-factory resumen sha256:([0-9a-f]{64}) -->\n')
    ```
  - `openspec/changes/20261007-003414-resumen-del/design.md:7`:
    > `...la primera línea lleva el sha256 del cuerpo para que se vea a simple vista si alguien lo editó.`
  - `oracle_factory/cli.py:989-994`:
    ```python
    if verificar:
        actual = destino.read_text(encoding="utf-8") if destino.is_file() else None
        if actual != texto:
            print(f"{destino.relative_to(ROOT)} " + ("no existe" if actual is None else "quedó viejo o se editó a mano")
                  + "; regeneralo con oracle-factory resumen.")
            raise SystemExit(1)
    ```
- **Explicación:**
  La constante `CABECERA` en `resumen.py:11` no se utiliza en ninguna parte de la base de código. `comando_resumen` en `cli.py` no parsea la cabecera ni valida el hash del cuerpo por separado; simplemente hace una comparación completa de igualdad de cadenas (`actual != texto`). La cabecera generada es meramente cosmética y la expresión regular es código muerto.
- **Corrección propuesta:**
  Eliminar `CABECERA` de `oracle_factory/resumen.py` si no se utiliza para verificar la integridad del cuerpo de forma aislada, o utilizarla en `comando_resumen` para reportar específicamente si el hash de integridad del archivo fue alterado manualmente frente a si sólo quedó desactualizado por avances en los registros.

---

### Defecto D-05: Inconsistencia normativa en la definición de determinismo («con los mismos registros»)
- **Citas en conflicto:**
  - `openspec/changes/20261007-003414-resumen-del/specs/resumen/spec.md:39`:
    > `Con los mismos registros, resumen SHALL producir los mismos bytes, sin fecha ni commit, sin red ni modelos de lenguaje; SHALL NOT modificar ningún otro archivo...`
  - `openspec/changes/20261007-003414-resumen-del/design.md:7`:
    > `«Lo que falta» de los cambios abiertos sale de pendientes_actuales y depende de la huella del producto: si un commit vence una revisión, el resumen queda viejo, y eso es correcto porque lo que muestra ya no es cierto.`
  - `oracle_factory/cli.py:966`:
    ```python
    "pendientes": pendientes_actuales(carpeta, estado)
    ```
- **Explicación:**
  La formulación en `spec.md` («Con los mismos registros, resumen SHALL producir los mismos bytes») es técnicamente incompleta o contradictoria: si los registros (`factory.json`, `specs/*.json`, `requisitos/*.requisito`) permanecen 100% inalterados, pero alguien hace un commit o modifica un archivo del producto, `pendientes_actuales()` detecta `revision/oracle desactualizado respecto del producto` (líneas 841-845). En consecuencia, `texto_resumen()` produce bytes diferentes sin que hayan cambiado los registros. El diseño (`design.md:7`) lo justifica explícitamente, pero el requisito contractual en `spec.md` omitió mencionar la huella del producto como entrada de la función.
- **Corrección propuesta:**
  Ajustar el requisito en `specs/resumen/spec.md`: «Con los mismos registros y la misma huella del producto, `resumen` SHALL producir los mismos bytes...».

---

### Defecto D-06: Inconsistencia entre `docs/estructura.md` y `spec.md` en la descripción de columnas
- **Citas en conflicto:**
  - `docs/estructura.md:104`:
    > `oracle-factory resumen escribe .factory/resumen.md: los requisitos vigentes de cada capacidad (con su tipo, sus medidas, el cambio del que vienen y el veredicto con que se cerró ese cambio)...`
  - `openspec/changes/20261007-003414-resumen-del/specs/resumen/spec.md:7`:
    > `...los requisitos vigentes de cada capacidad (tipo, requisito de Oracle, cambio de origen, medidas y veredicto)...`
- **Explicación:**
  La documentación en `docs/estructura.md:104` describe la tabla omitiendo «su requisito de Oracle» (alineándose accidentalmente con el código con defecto D-01), mientras que la spec formal (`spec.md:7`) y la propuesta (`proposal.md:10`) sí exigen la presencia del requisito de Oracle.
- **Corrección propuesta:**
  Alinear `docs/estructura.md:104` con la especificación contractual una vez subsanado el defecto D-01.

---

### Defecto D-07: Divergencia en el conteo de cambios abiertos y ocultamiento de cambios sin registro
- **Citas en conflicto:**
  - `openspec/changes/20261007-003414-resumen-del/proposal.md:24`:
    > `- Los 6 cambios viejos que nunca se cerraron: aparecen como abiertos, con lo que les falta.`
  - `.factory/resumen.md:246` (límite declarado de `archivar-al`):
    > `- (20261006-161029-archivar-al) Los 9 cambios que nunca se cerraron no se archivan: queda como tarea decidir si se cierran o se abandonan.`
  - `oracle_factory/cli.py:958-960`:
    ```python
    for carpeta in sorted(CHANGES.iterdir()) if CHANGES.is_dir() else []:
        if not ID_RE.fullmatch(carpeta.name) or not ruta_registro(carpeta).is_file():
            continue
    ```
- **Explicación:**
  En `openspec/changes/` existen 18 carpetas: 8 cerradas, 7 abiertas con `factory.json` (6 viejas + `resumen-del`) y 3 carpetas históricas de OpenSpec sin `factory.json` (`20261002-224749-revision-poc`, `20261003-185925-migrar-task`, `20261003-235610-web-rigurosa`).
  El límite declarado de `archivar-al` habla de **9 cambios** no cerrados (6 + 3), mientras que `proposal.md:24` dice «Los 6 cambios viejos que nunca se cerraron: aparecen como abiertos».
  La implementación en `cli.py:959` descarta silenciosamente cualquier carpeta sin archivo de registro. Esas 3 carpetas no aparecen ni como abiertas, ni cerradas, ni huérfanas, quedando invisibles para el lector de `resumen.md`.
- **Corrección propuesta:**
  En `proposal.md:24`, aclarar que de los 9 cambios históricos no cerrados, sólo los 6 que poseen registro Factory se listan como abiertos. O mejor aún, hacer que `texto_resumen` o `donde` emita una advertencia si detecta carpetas de cambios sin registro bajo `openspec/changes/`.

---

## 3. Evaluación Crítica de `.factory/resumen.md` como Lector

Al situarse en el rol de un ingeniero, revisor o decisor humano que abre `.factory/resumen.md` para entender el estado del repositorio, se desprenden las siguientes observaciones:

### A. ¿Se entiende qué está vigente?
- **Aspectos claros:**
  - La división por capacidades (`archivo`, `estructura`, `limpieza`, `modos`, `portabilidad`, `revision-guiada`, `vigencia`) es intuitiva y proporciona una vista de alto nivel del sistema.
  - La distinción de tipos (`funcional` / `no funcional`) y el enlace a la spec consolidada ayudan a no sobrecargar el resumen con escenarios BDD innecesarios.
- **Deficiencias para la comprensión:**
  - **Falta el enlace unívoco con Oracle:** Como no figura el ID del requisito de Oracle (ej. `factory_archivo.la_spec_de_un_cambio_se_fusiona_al_cerrarlo`), un usuario que quiera verificar una regla con la CLI de Oracle no puede copiar el identificador desde el resumen; tiene que ir a inspeccionar el archivo `.requisito` o la spec consolidada.
  - **Sobrecarga horizontal:** En la columna «Medidas», la concatenación de nombres completos de medidas (algunos con más de 60 caracteres) rompe el ancho de lectura estándar en terminales (`glow -p`) y tablas Markdown.

### B. ¿Se entiende qué falta?
- **Aspectos claros:**
  - Para el cambio actual (`20261007-003414-resumen-del`), la lista de pendientes es precisa e instructiva: muestra exactamente qué medidas fueron propuestas por agentes (`claude-code`) y requieren confirmación humana.
- **Elementos confusos y engañosos:**
  - **Ruido de cambios zombis:** Los 6 cambios del 2 y 4 de octubre ocupan 60 líneas (líneas 117-166 de `resumen.md`). Un lector pensaría que el equipo tiene 7 desarrollos concurrentes en curso.
  - **Pendientes incompletos en cambios viejos:** En `20261002-222858-explicar-oracle`, `dist-uv`, `elegir-medidas` e `inicio-guiado`, el resumen afirma que sólo falta:
    - `revisión humana aprobada y sin hallazgos abiertos`
    - `veredicto Oracle exitoso con evidencia`
    Esto es **engañoso**: ninguno de estos cambios tiene medidas asociadas en sus requisitos (`medidas: None`). Si alguien los juzgara, Oracle daría un veredicto verde vacío que, según `AGENTS.md`, «no habilita el cierre». La CLI no reporta que falte medir porque esos cambios son anteriores a los modos de trabajo (`cli.py:813`). El lector se lleva la impresión de que están listos para revisar y cerrar cuando en realidad están incompletos en su diseño.
  - **Redundancia:** En `validar-el-flujo`, se lista dos veces la misma acción con distinto redactado: `- aprobación humana de spec` y `- primero hay que aceptar la propuesta y la spec (aprobar-spec)`.

### C. ¿Se entiende qué riesgos hay y qué límites se declararon?
- **Aspectos claros:**
  - Cada riesgo aceptado identifica claramente el hallazgo (`G-03`, `M-02`, etc.), el cambio de origen, la descripción del riesgo, el decisor humano («Aceptado por Brian Hollweg») y la justificación.
  - La sección de límites declarados advierte honestamente sobre las restricciones metodológicas (sesgos de modelos, pruebas exclusivas en Linux, fixtures de contenedores).
- **Deficiencias para la comprensión:**
  - **Secciones «Históricos: Ninguno» innecesarias:** Tanto en Riesgos como en Límites, la subsección `### Históricos` dice `Ninguno.` Esto se debe a que todos los cambios cerrados hasta hoy conservan al menos un requisito vigente en la spec consolidada. Agregar una subsección vacía dos veces aporta ruido visual sin valor.
  - **Falta de estado de los riesgos aceptados diferidos:** Varios riesgos se aceptaron con el compromiso de resolverlos en una tarea futura (ej. `M-03: va a la tarea docs-web-modos`, `G-03: Se resuelve en la tarea cli-humana`). El lector no sabe si esa tarea ya se ejecutó o sigue abierta sin consultar el tracker externo.

### D. ¿Algo engaña en la lectura?
- **El veredicto «verde» reiterado genera falsa seguridad:**
  - En la tabla de lo vigente, leer 52 veces `verde al cerrar el 2026-10-06` genera un sesgo cognitivo de que «todo el sistema está verde hoy».
  - Si bien la nota en la línea 10 advierte: `El veredicto es el registrado al cerrar el cambio de origen, no una corrida nueva de Oracle`, la visualización en la tabla transmite la sensación de una suite integral aprobada. No existe un sensor consolidado que haya corrido las 52 pruebas juntas sobre el código actual.
- **La advertencia de commit posterior sin fecha/commit de anclaje:**
  - La línea 115 indica: `Lo que falta se calculó al generar este resumen; un commit posterior puede cambiarlo.`
  - Como el documento no incluye por diseño ni fecha de generación ni commit hash, un lector que lee `resumen.md` en GitHub o fuera de la CLI no tiene forma de saber si el commit que está mirando es anterior o posterior al cálculo de esos pendientes. La única manera de saberlo es ejecutando `oracle-factory resumen --verificar`.

### E. ¿Qué sobra y qué falta para que sea útil en una lectura?
- **Qué sobra:**
  - Subsecciones vacías `### Históricos \n Ninguno.`.
  - La enumeración repetitiva y desglosada de pendientes idénticos para medidas no confirmadas por agentes (líneas 173-179: 7 líneas casi idénticas que podrían sintetizarse en «7 medidas propuestas por claude-code sin confirmar»).
  - Cambios abiertos viejos no archivados ni activos, que distorsionan el panorama del trabajo en curso.
- **Qué falta:**
  - Identificador explícito del requisito de Oracle en la tabla.
  - Indicación o enlace para cambios abiertos hacia su propuesta (`openspec/changes/<ID>/proposal.md`).
  - Resolución correcta de enlaces relativos a specs consolidadas si se exporta a la raíz.

---

## 4. Sugerencias de Mejora (No Defectos)

A diferencia de los defectos normativos de la sección 2, aquí se recopilan propuestas de optimización de diseño y experiencia de usuario:

1. **S-01: Ocultar o colapsar subsecciones históricas vacías:**
   En `oracle_factory/resumen.py:89`, si `filas` está vacío para el bloque `Históricos`, se podría omitir la subsección completa en lugar de imprimir `### Históricos \n\n Ninguno.`
2. **S-02: Agrupar advertencias repetitivas de medidas en cambios abiertos:**
   Cuando un cambio tiene 5 o 7 requisitos con la misma situación de medida (ej. «propuestas por claude-code, sin confirmar por una persona»), resumirlo como:
   `- 7 requisitos con medidas propuestas por claude-code, sin confirmar por una persona`
   Esto reduciría el tamaño del resumen y facilitaría la lectura en una sola pantalla.
3. **S-03: Incorporar el comando de verificación en el pie del documento:**
   Recordar al final del archivo cómo comprobar si el resumen está vigente:
   `Para comprobar si este resumen coincide con el estado actual del repositorio, ejecutá: oracle-factory resumen --verificar.`
4. **S-04: Marcar en `donde` o `listar` las carpetas de cambio huérfanas:**
   Si existen directorios en `openspec/changes/` que no tienen `factory.json`, `listar` o `donde` deberían alertar sobre su estado no gestionado en lugar de ignorarlos silenciosamente.
5. **S-05: Incorporar `oracle-factory resumen` en la tabla de comandos de `docs/estructura.md`:**
   En la sección `## Encontrar las cosas` (tabla de líneas 67-73 de `docs/estructura.md`), incluir `oracle-factory resumen` y `--verificar` junto a `donde`, `ruta`, `buscar` y `listar`.

---

## 5. Matriz de Trazabilidad y Estado de Conformidad

| Requisito / Compromiso | Documento de origen | Estado en Código (`oracle_factory/`) | Estado en `.factory/resumen.md` | Veredicto |
|---|---|---|---|---|
| Requisitos vigentes con tipo | `spec.md:7`, `proposal.md:10` | Implementado (`resumen.py:61`) | Presente | **Conforme** |
| Requisito de Oracle en tabla | `spec.md:7`, `proposal.md:10` | Extraído pero omitido en salida (`resumen.py:60-63`) | Ausente | **DEFECTO (D-01)** |
| Cambio de origen en tabla | `spec.md:7`, `proposal.md:10` | Implementado (`resumen.py:63`) | Presente | **Conforme** |
| Medidas en tabla | `spec.md:7`, `proposal.md:10` | Implementado (`cli.py:979`, `resumen.py:62`) | Presente | **Conforme** |
| Veredicto de cierre con fecha | `spec.md:30`, `proposal.md:17` | Implementado (`resumen.py:27-30`) | Presente | **Conforme** |
| Enlace a spec consolidada sin escenarios | `spec.md:7`, `proposal.md:10` | Implementado (`resumen.py:57`) | Presente (pero roto con `--salida`) | **DEFECTO (D-02)** |
| Cambios abiertos con fase, modo y pendientes | `spec.md:7`, `proposal.md:11` | Implementado (`cli.py:964-966`, `resumen.py:70-72`) | Presente | **Conforme** |
| Riesgos aceptados vigentes vs históricos | `spec.md:21`, `proposal.md:12` | Implementado (`resumen.py:75-89`) | Presente | **Conforme** |
| Límites declarados vigentes vs históricos | `spec.md:21`, `proposal.md:13` | Implementado (`resumen.py:75-89`) | Presente | **Conforme** |
| Determinismo y sin fecha ni commit | `spec.md:39`, `proposal.md:14` | Implementado (`resumen.py:90-91`) | Presente | **Conforme** |
| Verificación con `--verificar` sin escribir | `spec.md:48`, `proposal.md:15` | Implementado (`cli.py:989-996`) | N/A | **Conforme** |
| Actualización automática en `cerrar` y `archivar` | `spec.md:57`, `proposal.md:16` | Implementado (`cli.py:1005, 1022, 1031, 1068`) | N/A | **Conforme** |
| `--salida RUTA` en cualquier ruta del proyecto | `spec.md:57`, `proposal.md:15` | Implementado (`cli.py:983-984, 998`) | N/A (enlaces internos rotos) | **DEFECTO (D-02)** |
