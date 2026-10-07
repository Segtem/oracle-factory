# Propuesta de Diseño: Vista «estado actual» generada (`oracle-factory resumen`)

> **Documento de diseño para:** `tareas/20261006-160411-resumen/TAREA.md`  
> **Repositorio de referencia:** `/home/workstation/Dev/factory-archivar` (rama con «archivar al cerrar»)  
> **Objetivo:** Generar una vista corta, determinista y regenerable del estado actual del proyecto desde los registros existentes, sin LLM, detectando desactualización mediante huella criptográfica (SHA-256).

---

## 1. Secciones del resumen y origen exacto de cada dato

El principio rector es **«comprimir lo que se lee, no lo que se guarda»**: los registros continúan siendo estructurados, append-only y atados a hashes; encima, `oracle-factory resumen` produce una vista Markdown derivada equivalente a un `ARCHITECTURE.md` vigente.

El documento generado se estructura en **cuatro secciones principales**, con origen de datos campo por campo:

```text
┌────────────────────────────────────────────────────────────────────────┐
│ 1. Encabezado y Metadatos de Vigencia (huella, timestamp, resumen)    │
├────────────────────────────────────────────────────────────────────────┤
│ 2. Capacidades y Requisitos Vigentes (por capacidad, medidas y veredicto)│
├────────────────────────────────────────────────────────────────────────┤
│ 3. Cambios Abiertos y Faltantes (fase actual y pendientes_actuales)    │
├────────────────────────────────────────────────────────────────────────┤
│ 4. Riesgos Aceptados y Límites Declarados (decisiones humanas y límites)│
└────────────────────────────────────────────────────────────────────────┘
```

---

### Sección 1: Encabezado y Metadatos de Vigencia

Contiene la marca de control para auditoría y la detección de desactualización:

| Dato mostrado | Campo / Origen exacto | Formato / Ejemplo |
|---|---|---|
| **Huella del resumen** | Comentario HTML de cabecera con SHA-256 canónico de las entradas | `<!-- oracle-factory resumen-hash: <sha256> generado: <iso> -->` |
| **Fecha de generación** | `ahora()` en formato ISO 8601 UTC | `2026-10-06T14:30:00+00:00` |
| **Commit del repositorio** | `git rev-parse HEAD` del proyecto | `1ed9610 (7 chars)` |
| **Totales del proyecto** | Conteo de capacidades, requisitos vigentes, cambios abiertos y cerrados | `6 capacidades · 41 requisitos vigentes · 1 cambio abierto` |

---

### Sección 2: Capacidades y Requisitos Vigentes

Agrupa por capacidad consolidada únicamente lo que rige hoy en el sistema (excluyendo lo reemplazado o dado de baja):

| Dato mostrado | Archivo y Campo exacto | Descripción / Regla |
|---|---|---|
| **Nombre de capacidad** | Archivos en `.factory/specs/<capacidad>.json` → `indice["capacidad"]` | Nombre de la capacidad consolidada (ej. `vigencia`, `estructura`, `modos`). |
| **Requisitos vigentes** | Claves del diccionario `indice["requisitos"]` en `.factory/specs/<capacidad>.json` | Cada clave es el nombre humano del requisito (ej. `vigencia por contenido del producto`). *(Nota: los reemplazados están en `indice["reemplazados"]` y no se listan aquí).* |
| **ID de Oracle** | `indice["requisitos"][nombre]["requisito"]` | ID canónico con namespace en Oracle (ej. `vigencia_c82d7f5b48fbc29ba.vigencia_por_contenido_del_producto`). |
| **Cambio de origen** | `indice["requisitos"][nombre]["cambio"]` | Identificador del cambio que lo agregó o modificó por última vez (ej. `20261005-154433-la-vigencia-de`). |
| **Tipo de requisito** | Primera línea de `indice["requisitos"][nombre]["cuerpo"]` | `funcional` o `no funcional`. |
| **Medidas asignadas** | 1. Archivo `requisitos/<rid>.requisito` → cláusula `medido_por <medidas...>`<br>2. En `.factory/cambios/<cambio>/factory.json` → evento `medidas_confirmadas` con `requisito == rid` → campo `medidas: [...]` | IDs de las medidas de Oracle asignadas y confirmadas (ej. `factory_vigencia.vigencia_por_contenido_del_producto`, `factory_vigencia.corrida_completa`). |
| **Confirmación de medida** | `.factory/cambios/<cambio>/factory.json` → `estado["medidas"][rid]` | Persona que confirmó y fecha (`actor`, `cuando`, `forma == "confirmo"`). |
| **Último veredicto Oracle** | 1. En `.factory/cambios/<cambio>/oracle-veredicto.txt`<br>2. O en `.factory/cambios/<cambio>/factory.json` → `estado["oracle"]["codigo"]` (0 es verde) | Se extrae la línea de `oracle-veredicto.txt` del cambio de origen que coincide con `^([✓◐·✗?])\s+<rid>\s+([a-záéíóú\s]+)`:<br>• Símbolo y estado: `✓ cumple`, `? sin juicio`, `· sin medir`, `✗ falla`.<br>• Se acompaña del cambio y commit donde se verificó (`cumple en 20261005-154433...`). |

---

### Sección 3: Cambios Abiertos y Faltantes

Muestra la cola de trabajo en progreso y los impedimentos exactos que bloquean su avance o cierre:

| Dato mostrado | Archivo y Campo exacto | Descripción / Regla |
|---|---|---|
| **ID y Título** | `.factory/cambios/<id>/factory.json` → `estado["id"]` y `estado["titulo"]` | Identificador del cambio abierto (ej. `20261006-161029-archivar-al`) y su título. |
| **Capacidad destino** | `.factory/cambios/<id>/factory.json` → `estado["capacidad"]` pasada por `capacidad_destino()` | Capacidad efectiva donde se fusionará al cerrar (resolviendo alias según `.factory/config.json`). |
| **Modo de trabajo** | `modo_de(estado)` (de `estado["modo"]` o `.factory/config.json["modo_por_defecto"]`) | `confirmacion`, `estricto`, `ejecutable`, etc. |
| **Fase actual** | `.factory/cambios/<id>/factory.json` → `estado["fase"]` | Ej. `requisitos_importados`, `spec_aprobada`, `revision_aprobada`, `oracle_verde`. |
| **Lo que le falta (Pendientes)** | Salida de la función `pendientes_actuales(carpeta, estado)` de [oracle_factory/cli.py](file:///home/workstation/Dev/factory-archivar/oracle_factory/cli.py#L829) | Lista exacta de faltantes que rechazan el cierre:<br>• Faltantes de fase (`pendientes(estado)`): ej. *«revisión pendiente»*, *«oracle pendiente»*.<br>• Medidas sin decisión (`medidas_sin_decision(estado)`).<br>• Spec no aprobada o desactualizada (`exigir_spec(carpeta, estado)`).<br>• Producto desactualizado (`revision/oracle desactualizado respecto del producto`).<br>• Integridad de informes (`informe de revisión cambiado o sin huella`, `hechos ausentes`).<br>• Validaciones de revisión guiada (`revisión guiada sin decisiones vinculadas`). |
| **Avisos de HEAD** | Salida de `avisos_head(estado)` de [oracle_factory/cli.py](file:///home/workstation/Dev/factory-archivar/oracle_factory/cli.py#L395) | Aviso si el HEAD actual difiere del commit donde se registró la revisión u Oracle, con producto idéntico. |

---

### Sección 4: Riesgos Aceptados y Límites Declarados

Esta sección consolida las decisiones humanas conscientes de compromiso técnico y los límites declarados del aseguramiento:

#### 4.1. Riesgos Aceptados (Decisiones Humanas)
Provienen de las decisiones de revisión registradas en cambios cerrados:
- **Origen primario:** `.factory/cambios/<cambio>/factory.json` → `estado["revision"]["decisiones"]` (ruta a `decisiones.json`) y su hash de integridad `decisiones_sha256`.
- **Estructura en `decisiones.json`:** Array `decisiones`:
  - Se filtran los elementos donde `decision["estado"] == "riesgo_aceptado"`.
  - **Campos extraídos:**
    - `decision["hallazgo_id"]`: ID del hallazgo (ej. `R2V-03`, `R2V-05`, `R2X-01`).
    - `decision["motivo"]`: Justificación textual dada por la persona (ej. *«Mismo mensaje: dato informativo que no condiciona nada»*, *«En repositorios SHA-256 se pierde el dato de auditoría head_preparacion; la vigencia no cambia»*).
    - `decision["actor"]`: Nombre de la persona que aceptó el riesgo (ej. `Brian Hollweg`).
    - `decision["fecha"]`: Timestamp de la decisión.
- **Cruce con el informe (`informe.json`):**
  - En `estado["revision"]["informe"]` (`informe.json`), se busca en el array `hallazgos` el objeto con `id == decision["hallazgo_id"]`.
  - **Campos complementarios:**
    - `hallazgo["descripcion"]`: Descripción técnica del problema aceptado.
    - `hallazgo["ubicacion"]`: Archivo y línea (ej. `oracle_factory/cli.py:569`).

#### 4.2. Límites Declarados
Se distinguen dos fuentes independientes y complementarias:
1. **Límites metodológicos de las revisiones guiadas:**
   - **Origen:** `estado["revision"]["informe"]` (`informe.json` de cambios cerrados).
   - **Campo exacto:** Array `"limites"` (`list[str]`).
   - **Contenido:** Declaraciones de límites del análisis (ej. *«El autor es un agente (Claude Code) y R2 es otra sesión de la misma familia de modelo»*, *«La vigencia por contenido mide que el producto no cambió, no que lo revisado fuera correcto»*, *«Factory no autentica actores»*).
2. **Límites de cobertura de pruebas / Oracle (`sin_medir`):**
   - **Origen:** Archivos `requisitos/<rid>.requisito` correspondientes a los **requisitos vigentes**.
   - **Campo exacto:** Cláusula `sin_medir "<texto>"`.
   - **Contenido:** Declaración explícita de lo que las pruebas automáticas no cubren (ej. *«Pilotaje en máquinas distintas y colisión de un cambio Factory... sin medir»*, *«Autoridad del integrador y resolución humana de conflictos sin medir»*).

---

## 2. Dónde se escribe y cómo se detecta que quedó viejo

### Ubicación del archivo
**Ubicación recomendada:** `.factory/resumen.md`.

**Fundamentación técnica:**
1. **Protección de la huella del producto:**
   En [oracle_factory/cli.py](file:///home/workstation/Dev/factory-archivar/oracle_factory/cli.py#L359), la función `contexto_producto()` excluye explícitamente `partes[0] in ("tareas", estructura.DIR)`. Dado que `estructura.DIR == ".factory"`, cualquier archivo dentro de `.factory/` **no forma parte de `archivos_sha256`**.
   Por tanto, regenerar o actualizar `.factory/resumen.md` **nunca invalida** una revisión vigente ni un veredicto de Oracle en curso.
2. Si una persona deseara exponerlo en la raíz del repositorio como `RESUMEN.md` (o `ARCHITECTURE.md`), la regla de `contexto_producto()` requeriría excluir explícitamente ese nombre de archivo (análogo a como ya se excluyen las specs gestionadas de `openspec/specs/`). Por ello, `.factory/resumen.md` es la ubicación canónica y segura.

### Cálculo del hash de entradas (Huella de lo que resume)
Para detectar de forma determinista si el resumen quedó desactualizado respecto a los registros, se calcula un **hash canónico de entradas**:

```python
entradas = {
    "specs": {
        cap: sha256(ruta_indice(cap).read_bytes())
        for cap in sorted(capacidades_existentes())
    },
    "cambios": {
        cid: sha256(ruta_registro(cid).read_bytes())
        for cid in sorted(cambios_existentes())
    },
    "requisitos_vigentes": {
        rid: sha256((ROOT / "requisitos" / f"{rid}.requisito").read_bytes())
        for rid in sorted(requisitos_vigentes_ids())
        if (ROOT / "requisitos" / f"{rid}.requisito").is_file()
    },
    "contexto_producto": contexto_producto()["archivos_sha256"],
    "head": contexto_producto()["head"],
}
resumen_hash = sha256(json.dumps(entradas, sort_keys=True).encode("utf-8"))
```

### Incrustación y detección de desactualización
1. **Al generar el archivo:**
   En la cabecera de `.factory/resumen.md`, se escribe:
   ```markdown
   <!-- oracle-factory resumen-hash: 8f3c7e... generado: 2026-10-06T14:30:00+00:00 -->
   ```
2. **Al verificar (`oracle-factory resumen --verificar`):**
   - Si `.factory/resumen.md` no existe → estado **AUSENTE** (código de salida `1`).
   - Se extrae el hash del comentario HTML de cabecera.
   - Se recalcula `resumen_hash` sobre el estado actual del repositorio.
   - Si `hash_guardado == resumen_hash` → estado **VIGENTE** (código de salida `0`).
   - Si `hash_guardado != resumen_hash` → estado **DESACTUALIZADO** (código de salida `1`).
3. **Al consultar `oracle-factory estado`:**
   Muestra un aviso informativo si el resumen está desactualizado respecto a los registros, indicando que puede regenerarse con `oracle-factory resumen`.

---

## 3. Preguntas de diseño para decisión humana (con recomendación)

| # | Pregunta de diseño | Alternativas consideradas | Recomendación y Fundamento |
|---|---|---|---|
| **1** | **¿Dónde se guarda el archivo y cómo se expone?** | **A:** `.factory/resumen.md` únicamente.<br>**B:** `RESUMEN.md` en la raíz (modificando `contexto_producto` para excluirlo).<br>**C:** `.factory/resumen.md` por defecto, con opción `--salida RUTA` para volcarlo donde el usuario prefiera. | **Recomendación: Alternativa C.**<br>Mantiene `.factory/resumen.md` como el artefacto canónico fuera de la huella del producto (cero riesgo de invalidar revisiones), permitiendo redirigir o copiar a `RESUMEN.md` si un humano o pipeline CI lo desea explícitamente. |
| **2** | **¿Cuándo se actualiza el resumen?** | **A:** Sólo manualmente con `oracle-factory resumen --guardar`.<br>**B:** Automáticamente en `cerrar` y `archivar`.<br>**C:** En cada comando mutador (`medir`, `aprobar-spec`, `juzgar`, `cerrar`). | **Recomendación: Alternativa B.**<br>`cerrar` y `archivar` son los puntos canónicos donde el estado consolidado del proyecto muta de forma definitiva. Hacerlo en cada comando intermedio generaría ruido innecesario en Git; hacerlo automáticamente en `cerrar` y `archivar` garantiza que el repositorio nunca quede con un resumen desfasado tras integrar un cambio. |
| **3** | **¿Cuál es el alcance de los Riesgos Aceptados a listar?** | **A:** Riesgos de TODOS los cambios cerrados históricamente.<br>**B:** Sólo riesgos de cambios cuyos requisitos sigan vigentes hoy.<br>**C:** Todos los riesgos cerrados, pero agrupados separando «Vigentes» de «Reemplazados/Históricos». | **Recomendación: Alternativa C.**<br>Un riesgo aceptado es un compromiso de auditoría humana. Si el cambio que lo introdujo sigue en el código pero sus requisitos fueron renombrados o sustituidos, el riesgo técnico subyacente puede persistir. Agruparlos distinguiendo la vigencia de su cambio evita perder memoria técnica sin confundir al lector. |
| **4** | **¿Qué veredicto de Oracle se muestra para cada requisito vigente?** | **A:** El veredicto obtenido en la corrida del cambio que cerró el requisito.<br>**B:** El veredicto de la última corrida de Oracle en el repo (que para requisitos viejos suele dar `? sin juicio` por falta de sensor acumulado).<br>**C:** Ambos: veredicto de cierre del requisito + veredicto en la última corrida global. | **Recomendación: Alternativa A.**<br>En Factory, cada cambio se cierra con sus pruebas específicas pasando (`✓ cumple`). Mostrar la última corrida global diría erróneamente `? sin juicio` porque el arnés del cambio más reciente sólo corre sus propios hechos. Mostrar `✓ cumple (en cambio <ID>)` refleja la verdad comprobada del registro. |
| **5** | **¿Qué nivel de detalle deben tener los requisitos vigentes?** | **A:** Resumen conciso tabular (Nombre, Tipo, ID Oracle, Medidas, Veredicto).<br>**B:** Volcado íntegro de todos los escenarios GIVEN/WHEN/THEN.<br>**C:** Formato conciso por defecto, con `--completo` para incluir escenarios. | **Recomendación: Alternativa C.**<br>El objetivo expreso de la tarea es «comprimir lo que se lee». Incluir 41+ requisitos con todos sus escenarios transformaría el resumen en un documento inmanejable de más de 1000 líneas. La vista corta debe caber en una pantalla o página de lectura ágil. |

---

## 4. Requisitos en formato OpenSpec (Capacidad: `resumen`)

A continuación se presentan 7 requisitos formales para la capacidad `resumen`, con tipos funcional y no funcional, redactados bajo la convención RFC 2119 y escenarios GIVEN/WHEN/THEN verificables mediante pruebas unitarias y de integración.

---

### Requirement: generacion determinista del resumen
Tipo: funcional  
Factory SHALL generar una vista en formato Markdown (`oracle-factory resumen`) exclusivamente a partir de los registros estructurados del proyecto (`.factory/specs/*.json`, `.factory/cambios/*/factory.json`, `requisitos/*.requisito` e informes vinculados), sin invocar modelos de lenguaje ni servicios externos, produciendo una salida byte a byte idéntica ante entradas idénticas.

#### Scenario: dos ejecuciones consecutivas sin cambios
- GIVEN un proyecto Factory con capacidades consolidadas y registros existentes
- WHEN se ejecuta `oracle-factory resumen` dos veces consecutivas sin modificar el repositorio
- THEN ambas salidas estándar son idénticas carácter por carácter

#### Scenario: generación sin conexión de red ni dependencias de IA
- GIVEN un entorno sin acceso a red ni proveedores de LLM configurados
- WHEN se ejecuta `oracle-factory resumen`
- THEN el comando finaliza con código 0 y produce el documento completo

---

### Requirement: agrupacion de capacidades y requisitos vigentes
Tipo: funcional  
El resumen SHALL listar todas las capacidades consolidadas presentes en `.factory/specs/`, y para cada una SHALL listar exclusivamente sus requisitos vigentes, indicando para cada uno su identificador de Oracle, cambio de origen, medidas confirmadas y último veredicto registrado, omitiendo los requisitos marcados como reemplazados.

#### Scenario: requisito vigente con medidas y veredicto
- GIVEN una capacidad con un requisito vigente que tiene medidas confirmadas y veredicto verde en su cambio de origen
- WHEN se genera el resumen
- THEN el requisito figura bajo su capacidad con su ID de Oracle, las medidas confirmadas asociadas y la marca de cumplimiento («cumple»)

#### Scenario: exclusión de requisitos reemplazados
- GIVEN una capacidad donde un requisito original fue modificado o reemplazado por un cambio posterior
- WHEN se genera el resumen
- THEN el requisito anterior no aparece en la lista de requisitos vigentes y sólo figura el nuevo

---

### Requirement: inventario de cambios abiertos y sus faltantes
Tipo: funcional  
El resumen SHALL listar cada cambio cuyo estado no sea «cerrada», indicando su identificador, título, modo de trabajo, fase actual y la lista exhaustiva de motivos pendientes devuelta por `pendientes_actuales`.

#### Scenario: cambio abierto con pendientes
- GIVEN un cambio en fase `requisitos_importados` con medidas pendientes de confirmación
- WHEN se genera el resumen
- THEN la sección de cambios abiertos incluye el cambio y detalla exactamente que faltan decisiones de medidas y juicio de Oracle

#### Scenario: repositorio sin cambios abiertos
- GIVEN un proyecto donde todos los cambios registrados están cerrados
- WHEN se genera el resumen
- THEN la sección de cambios abiertos indica explícitamente «No hay cambios abiertos»

---

### Requirement: consolidacion de riesgos aceptados y limites
Tipo: funcional  
El resumen SHALL recopilar y listar todos los hallazgos de revisión donde una persona registró una decisión con estado `riesgo_aceptado` (mostrando ID del hallazgo, motivo y actor), los límites metodológicos declarados en los informes guiados (`limites`), y los límites de medición declarados en los requisitos vigentes (`sin_medir`).

#### Scenario: cambio cerrado con riesgo aceptado
- GIVEN un cambio cerrado con un hallazgo de revisión resuelto como «riesgo_aceptado» por una persona
- WHEN se genera el resumen
- THEN la sección de riesgos aceptados muestra el ID del hallazgo, el actor responsable y el motivo textual registrado

#### Scenario: requisitos con límites sin_medir
- GIVEN un requisito vigente con una declaración `sin_medir` en su archivo de Oracle
- WHEN se genera el resumen
- THEN dicho límite aparece en la sección de límites declarados asociado al requisito

---

### Requirement: deteccion de desactualizacion por huella de registros
Tipo: funcional  
Factory SHALL calcular una huella criptográfica SHA-256 de todas las fuentes de registro resumidas, SHALL incrustarla en el documento generado, y mediante la opción `--verificar` SHALL comprobar si el archivo de resumen guardado coincide con el estado actual del repositorio, retornando código 0 si está al día y código 1 si está desactualizado o ausente.

#### Scenario: verificación de resumen al día
- GIVEN un archivo `.factory/resumen.md` recién generado con su huella incrustada
- WHEN se ejecuta `oracle-factory resumen --verificar`
- THEN el comando reporta que el resumen está vigente y finaliza con código 0

#### Scenario: cambio posterior en un registro
- GIVEN un archivo de resumen vigente y un cambio posterior en un `factory.json` o spec
- WHEN se ejecuta `oracle-factory resumen --verificar`
- THEN el comando avisa que el resumen está desactualizado y finaliza con código 1

---

### Requirement: preservacion de la huella del producto
Tipo: no funcional  
La escritura, actualización o verificación del archivo de resumen SHALL NOT alterar la huella de archivos del producto calculada por `contexto_producto`, garantizando que regenerar el resumen nunca invalide una revisión vigente ni un veredicto de Oracle registrado.

#### Scenario: regeneración sin invalidación de revisión
- GIVEN un cambio con revisión y veredicto de Oracle registrados y vigentes
- WHEN se genera o sobrescribe `.factory/resumen.md`
- THEN `oracle-factory estado` comprueba que la revisión y el veredicto continúan plenamente vigentes

---

### Requirement: regeneracion automatica al cerrar o archivar
Tipo: funcional  
Al ejecutar con éxito `oracle-factory cerrar` o `oracle-factory archivar`, Factory SHALL actualizar automáticamente `.factory/resumen.md` con el nuevo estado consolidado del proyecto y su nueva huella calculada, de forma atómica.

#### Scenario: cierre exitoso de un cambio
- GIVEN un cambio listo para cerrar con todas sus condiciones satisfechas
- WHEN la persona confirma el cierre del cambio
- THEN el cambio queda cerrado, archivado en su spec consolidada, y `.factory/resumen.md` queda actualizado reflejando el nuevo estado verificado

---
