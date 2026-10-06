# Auditoría de Documentación y Especificación: Archivar al Cerrar

- **Repositorio/Checkout:** `/home/workstation/Dev/_revisiones/factory-archivar-c31ef73`
- **Modo:** Sólo lectura en el repositorio (sin modificaciones de código ni commits).
- **Alcance auditado:**
  - `docs/estructura.md` (secciones del árbol, «Quién es dueño de qué», «Lo vigente de cada capacidad»).
  - `LEEME_FACTORY` en `oracle_factory/cli.py` (texto escrito por `init` en `.factory/LEEME.md`).
  - `openspec/changes/20261006-161029-archivar-al/proposal.md`.
  - `openspec/changes/20261006-161029-archivar-al/design.md`.
  - `openspec/changes/20261006-161029-archivar-al/specs/archivo/spec.md`.
  - Código real: `oracle_factory/archivo.py`; en `oracle_factory/cli.py`: `cerrar`, `archivar`, `plan_archivo`, `escribir_archivo`, `contexto_producto`, `config_proyecto`, `nuevo`; en `oracle_factory/estructura.py`: `donde`, `buscar`.
  - Directorio `openspec/specs/` y `.factory/specs/` de este repositorio.

---

## 1. Resumen Ejecutivo de la Auditoría

Se contrastaron las promesas de la documentación y los contratos de especificación frente a la implementación concreta en el código y el estado del repositorio.

Se identificaron **9 defectos concretos**, clasificados en:
1. **Afirmaciones desactualizadas sobre el orden de cierre y el motivo de exclusión de la huella.**
2. **Inexactitudes en el alcance de la huella del producto** (generalizaciones en la guía frente al filtrado condicional estricto en el código).
3. **Contradicciones en opciones de comandos de CLI** (promesa de un flag `--existentes` en `design.md` que la CLI no implementa y rechaza).
4. **Contradicción entre la promesa de atomicidad al rechazar cierre y el comportamiento real ante una spec consolidada editada a mano.**
5. **Vacíos procedimentales críticos para el operador humano** (la guía no indica cómo resolver conflictos de delta ni cómo proceder cuando una spec consolidada fue editada a mano).
6. **Omisiones en tablas de inventario y diagramas de árbol** (índices `.factory/specs/` omitidos en la tabla de propiedad; `.factory/LEEME.md` ausente en el árbol y físicamente en el checkout).
7. **Discrepancias entre los contratos exigidos por los catálogos Oracle y los escenarios formalizados en la spec.**

A continuación se detalla cada hallazgo con su cita exacta de `archivo:línea`, descripción del contraste y corrección propuesta.

---

## 2. Lista Detallada de Defectos

### Defecto 1: Justificación desactualizada de la exclusión de la huella por cambio en el orden de cierre
- **Cita:** `docs/estructura.md:96`
- **Texto actual:**
  > «La spec consolidada queda fuera de la huella del producto, como `.factory/`: se deriva de specs ya aceptadas, y si contara, un cierre interrumpido no se podría reintentar.»
- **Contraste contra el código:**
  En la versión inicial del diseño, `cerrar` fusionaba la spec antes de cerrar la tarea y el registro. Sin embargo, en el commit `8c38535` (corrección de hallazgos R2A-01 a R2A-04), el orden fue explícitamente invertido en `oracle_factory/cli.py:973-985` y documentado en `openspec/changes/20261006-161029-archivar-al/design.md:8`:
  Primero se cierra la tarea (`tasks close`) y se guarda el estado `fase: cerrada` en `factory.json`, y recién después se fusiona la spec con `escribir_archivo()`. Si el proceso se interrumpe antes del cierre, la spec consolidada nunca se tocó; si se interrumpe después, el cambio ya está cerrado y se completa con `oracle-factory archivar`.
  Por lo tanto, la justificación de que *«si contara, un cierre interrumpido no se podría reintentar»* quedó desactualizada. La razón real actual (documentada en `oracle_factory/cli.py:355-356` y `design.md:11`) es que archivar retroactivamente los cambios anteriores (`oracle-factory archivar`) modificaría la huella del árbol de archivos e invalidaría la revisión del último cambio integrado.
- **Corrección propuesta:**
  Actualizar `docs/estructura.md:96`:
  ```markdown
  - La spec consolidada generada por Factory queda fuera de la huella del producto, como `.factory/`: se deriva de specs ya aceptadas, y si contara, archivar los cambios anteriores invalidaría la revisión del último cambio integrado.
  ```

---

### Defecto 2: Inexactitud en la guía sobre qué parte de `openspec/specs/` se excluye de la huella
- **Citas:** `docs/estructura.md:43` y `docs/estructura.md:96`
- **Texto actual:**
  - `docs/estructura.md:43`: «La huella de archivos del producto excluye `.factory/` entera, como ya excluye `tareas/`: agregar evidencia o un paquete de Clue no invalida una revisión. Cambiar el acuerdo, el código o las medidas sí.» *(omite mencionar `openspec/specs/`)*.
  - `docs/estructura.md:96`: «La spec consolidada queda fuera de la huella del producto, como `.factory/`: se deriva de specs ya aceptadas...»
- **Contraste contra el código:**
  En `oracle_factory/cli.py:357-360` (`contexto_producto()`), la exclusión es altamente restrictiva:
  ```python
  gestionada = (len(partes) == 4 and partes[:2] == ("openspec", "specs") and partes[3] == "spec.md"
                and (ROOT / estructura.DIR / "specs" / f"{partes[2]}.json").is_file())
  if partes[0] in ("tareas", estructura.DIR) or gestionada or ...:
      continue
  ```
  Sólo se excluye el archivo exacto `openspec/specs/<capacidad>/spec.md` **siempre que exista** su correspondiente índice `.factory/specs/<capacidad>.json`. Cualquier otro archivo dentro de `openspec/specs/` (o una spec no gestionada por Factory que carezca de índice) **sí forma parte de la huella del producto** (`design.md:11`).
  La guía es inexacta al sugerir de forma genérica que cualquier "spec consolidada" está fuera de la huella y omite esta condición en la sección general de huella (línea 43).
- **Corrección propuesta:**
  - En `docs/estructura.md:43`, agregar una mención explícita a las specs consolidadas gestionadas junto a `.factory/` y `tareas/`.
  - En `docs/estructura.md:96`, aclarar:
    ```markdown
    - Sólo la spec consolidada gestionada por Factory (la que tiene su correspondiente índice en `.factory/specs/<capacidad>.json`) queda fuera de la huella del producto; cualquier otro archivo bajo `openspec/specs/` sí cuenta en la huella y altera la vigencia de las revisiones.
    ```

---

### Defecto 3: Promesa de flag `--existentes` en `design.md` no soportado por la CLI
- **Cita:** `openspec/changes/20261006-161029-archivar-al/design.md:10`
- **Texto actual:**
  > «- **Retroactivo:** `oracle-factory archivar --existentes` (o un paso de `migrar`) archiva los cerrados que no tienen marca, en el orden de su evento de cierre. Idempotente.»
- **Contraste contra el código:**
  En `oracle_factory/cli.py:1555` y `cli.py:1608`:
  ```python
  sub.add_parser('archivar', help='fusionar en openspec/specs/ la spec de los cambios cerrados que todavía no lo están')
  ...
  elif args.comando == "archivar": archivar()
  ```
  La función `archivar()` no recibe argumentos y el parser de la CLI no define el flag `--existentes`. Si una persona ejecuta `oracle-factory archivar --existentes` siguiendo la nota de diseño, el comando falla con `argparse: error: unrecognized arguments: --existentes`.
  (Nótese que en `docs/estructura.md:95` sí se documenta correctamente la invocación sin banderas: `oracle-factory archivar`).
- **Corrección propuesta:**
  En `openspec/changes/20261006-161029-archivar-al/design.md:10`, eliminar `--existentes`:
  ```markdown
  - **Retroactivo:** `oracle-factory archivar` archiva los cerrados que no tienen marca, en el orden de su evento de cierre. Idempotente.
  ```

---

### Defecto 4: Falsa promesa de rechazo antes de modificar archivos ante spec consolidada editada a mano
- **Citas:**
  - `openspec/changes/20261006-161029-archivar-al/specs/archivo/spec.md:21`
  - `openspec/changes/20261006-161029-archivar-al/proposal.md:12`
  - `openspec/changes/20261006-161029-archivar-al/design.md:8`
  - `docs/estructura.md:92`
- **Texto actual:**
  - `specs/archivo/spec.md:21`: «Si la fusión no es posible (agregar un requisito con un nombre que ya existe en la capacidad, o modificar o quitar uno que no existe), `cerrar` SHALL rechazarse antes de modificar cualquier archivo y SHALL nombrar el requisito en conflicto.»
  - `proposal.md:12`: «2. **Un conflicto no se resuelve solo:** si la fusión no es posible (agregar un requisito que ya existe, modificar o quitar uno que no existe), `cerrar` lo dice y no cierra.»
  - `design.md:8`: «`cerrar` calcula la fusión antes de pedir la confirmación; si hay conflicto no pregunta.»
  - `docs/estructura.md:92`: «- **Un conflicto no se resuelve solo:** agregar un requisito que ya existe, o modificar o quitar uno que no existe, rechaza el cierre antes de preguntar y nombra el requisito.»
- **Contraste contra el código:**
  El catálogo `catalogos/factory_archivo.un_conflicto_impide_cerrar.oracle` y `tools/verify_archivo.py:18-19` consideran el caso `a2_una_spec_consolidada_editada_a_mano_no_se_pisa` parte del contrato del requisito `un_conflicto_impide_cerrar`.
  Sin embargo, en `oracle_factory/cli.py`:
  1. `plan_archivo(estado)` (línea 958) sólo calcula la fusión en memoria sobre `leer_indice()` y la spec delta. **No comprueba** el archivo `spec.md` en disco (`cli.py:891-900`).
  2. Si `openspec/specs/<capacidad>/spec.md` fue editada a mano, `plan_archivo` **no falla**.
  3. `cerrar` solicita la confirmación humana interactiva (`decidir`, línea 966).
  4. `cerrar` invoca `tasks close` (línea 973), cerrando la tarea en Oracle Task.
  5. `cerrar` muta `estado["fase"] = "cerrada"` y guarda el archivo `factory.json` (línea 979).
  6. Recién en `escribir_archivo` (líneas 983 y 908-910) se compara `actual != esperado` y se lanza `FactoryError`.
  **Consecuencias:**
  - `cerrar` **SÍ modifica archivos** antes de fallar (cierra la tarea en Oracle Task y pasa `factory.json` a `fase: cerrada`).
  - El cambio queda en un estado híbrido: tarea cerrada y registro cerrado, pero **sin archivar**.
  - `test_archivo.py:170-180` enmascara este comportamiento porque prueba la spec editada a mano únicamente contra `f.archivar()`, no contra `f.cerrar()`.
- **Corrección propuesta:**
  - **En el código:** `plan_archivo` (o una comprobación previa en `cerrar`) debe validar que `actual == esperado` en `openspec/specs/<capacidad>/spec.md` antes de invocar a `decidir` y antes de cerrar la tarea.
  - **En la documentación y spec:** documentar explícitamente el caso de colisión por edición manual y asegurar que `cerrar` aborte antes de pedir confirmación ni tocar el tracker de tareas.

---

### Defecto 5: Ausencia de procedimiento para resolver conflictos en la spec delta
- **Cita:** `docs/estructura.md:92`
- **Texto actual:**
  > «- **Un conflicto no se resuelve solo:** agregar un requisito que ya existe, o modificar o quitar uno que no existe, rechaza el cierre antes de preguntar y nombra el requisito.»
- **Contraste contra el código:**
  La guía menciona el rechazo pero no indica el procedimiento de resolución que debe seguir la persona:
  1. **Tipos de conflicto en el código no mencionados en la guía:**
     - Uso de encabezados `## RENAMED Requirements` (no soportado en `archivo.py:31`: se debe eliminar y volver a agregar).
     - Nombres de requisitos duplicados dentro del mismo cambio (`archivo.py:70`).
     - Requisitos de la spec que no fueron importados en Oracle para ese cambio (`archivo.py:86`: `«{nombre}» no tiene requisito de Oracle importado en {ident}`).
  2. **Acción correctiva e invalidación de la aprobación:**
     - Si la persona edita la spec delta en `openspec/changes/<ID>/specs/<capacidad>/spec.md` para solucionar el conflicto (cambiando `ADDED` por `MODIFIED` o ajustando nombres), esto altera el hash sha256 de los documentos.
     - En `oracle_factory/cli.py:338-339` (`exigir_spec()`), cualquier cambio en la spec invalida inmediatamente la aceptación previa (`la propuesta/spec cambió o su aprobación es antigua; renová la aceptación`).
     - Por ende, la persona **debe ejecutar nuevamente `aprobar-spec`** (y eventualmente renovar revisión o juicio si la huella cambió) antes de reintentar `cerrar`. Quien sólo lea la guía no sabrá esto y se encontrará con un error de aprobación vencida.
- **Corrección propuesta:**
  Añadir en `docs/estructura.md` bajo "Lo vigente de cada capacidad" las instrucciones para destrabar un conflicto:
  ```markdown
  - **Cómo resolver un conflicto:**
    - Si el requisito ya existía y se buscaba actualizarlo, cambiá su sección a `## MODIFIED Requirements`.
    - Si se buscaba darlo de baja, usá `## REMOVED Requirements`.
    - `RENAMED` no está soportado: quitalo y agregalo con el nombre nuevo.
    - Si falta importar en Oracle, ejecutá `fabrica.py importar`.
    - **Importante:** Corregir la spec del cambio modifica el acuerdo y anula la aprobación previa; deberás renovar la aceptación con `oracle-factory aprobar-spec` antes de volver a cerrar.
  ```

---

### Defecto 6: Ausencia de procedimiento ante una spec consolidada editada a mano
- **Cita:** `docs/estructura.md:32`
- **Texto actual:**
  > `| openspec/specs/<capacidad>/ | Factory (formato OpenSpec) | La spec consolidada: los requisitos vigentes de la capacidad. Se genera; no se edita a mano |`
- **Contraste contra el código:**
  La guía afirma que la spec "no se edita a mano", pero no describe qué ocurre si alguien o alguna herramienta la edita, ni cómo recuperarse:
  1. El código en `oracle_factory/cli.py:908-910` arroja:
     `FactoryError: <ruta> no es la que generó Factory (se editó a mano o no tiene índice en <indice>); restaurala o movela antes de fusionar`.
  2. `oracle-factory` **no posee ningún subcomando para regenerar** `openspec/specs/<capacidad>/spec.md` a partir del índice `.factory/specs/<capacidad>.json`.
  3. La única forma de resolverlo es mediante control de versiones (`git checkout openspec/specs/<capacidad>/spec.md`) o eliminando el archivo desincronizado para permitir que Factory lo escriba de nuevo.
- **Corrección propuesta:**
  Explicar en `docs/estructura.md`:
  ```markdown
  - **Si se edita una spec consolidada a mano:** Factory se negará a cerrarla o archivarla para no pisar cambios externos. Para destrabarla, restaurá el archivo al contenido que Factory espera con `git checkout openspec/specs/<capacidad>/spec.md` o movelo fuera de la carpeta antes de ejecutar `oracle-factory archivar`.
  ```

---

### Defecto 7: Omisión de `.factory/specs/` en la tabla «Quién es dueño de qué»
- **Cita:** `docs/estructura.md:28-35`
- **Texto actual:**
  Fila `.factory/`:
  `| .factory/ | Factory | El estado de cada cambio, la configuración, lo que se produce sobre un candidato y lo propio de cada máquina |`
- **Contraste contra el código:**
  En el árbol de directorios (`docs/estructura.md:9`), sí figura:
  `specs/<capacidad>.json # índice de la spec consolidada: de qué cambio viene cada requisito y qué reemplazó`.
  Sin embargo, en la tabla conceptual "Quién es dueño de qué" (línea 30), se omiten por completo los índices de las specs consolidadas (`.factory/specs/`), a pesar de ser artefactos clave de Factory que definen la vigencia de los requisitos y gobiernan la exclusión de la huella del producto.
- **Corrección propuesta:**
  Completar la celda en `docs/estructura.md:30`:
  ```markdown
  | `.factory/` | Factory | El estado de cada cambio, la configuración, los índices de specs consolidadas (`specs/`), lo que se produce sobre un candidato y lo propio de cada máquina |
  ```

---

### Defecto 8: Inconsistencia con `.factory/LEEME.md` (árbol vs. texto vs. repositorio)
- **Citas:**
  - `docs/estructura.md:6-24` (árbol)
  - `docs/estructura.md:42` (texto)
  - `oracle_factory/cli.py:1187-1189` (`inicializar()`)
  - Estado del checkout actual en disco
- **Texto actual:**
  - `docs/estructura.md:42`: «Git no versiona carpetas vacías, así que `init` deja un archivo, `.factory/LEEME.md`, que explica la carpeta y hace que un clon la tenga.»
  - `docs/estructura.md:6-24`: El diagrama del árbol omite `.factory/LEEME.md`.
- **Contraste contra el código y repositorio:**
  - `inicializar()` en `oracle_factory/cli.py:1188` crea `.factory/LEEME.md` a partir de `LEEME_FACTORY`.
  - En el checkout `/home/workstation/Dev/_revisiones/factory-archivar-c31ef73`, el archivo `.factory/LEEME.md` **no existe físicamente** en `.factory/` (sólo están `cambios/`, `config.json` y `specs/`).
  - En el árbol de `docs/estructura.md`, no está documentado dentro de `.factory/`.
- **Corrección propuesta:**
  - Añadir `LEEME.md` al diagrama de árbol de `docs/estructura.md`.
  - Crear e incluir el archivo `.factory/LEEME.md` en el repositorio para que coincida con lo prometido por `init` y la guía.

---

### Defecto 9: Discrepancia entre los escenarios de `specs/archivo/spec.md` y el catálogo de Oracle
- **Citas:**
  - `openspec/changes/20261006-161029-archivar-al/specs/archivo/spec.md:19-27`
  - `catalogos/factory_archivo.un_conflicto_impide_cerrar.oracle:4`
  - `tools/verify_archivo.py:18-19`
- **Texto actual en spec:**
  ```markdown
  ### Requirement: un conflicto impide cerrar
  Tipo: funcional
  Si la fusión no es posible (agregar un requisito con un nombre que ya existe en la capacidad, o modificar o quitar uno que no existe), `cerrar` SHALL rechazarse antes de modificar cualquier archivo y SHALL nombrar el requisito en conflicto.

  #### Scenario: agregar un requisito que ya existe
  - GIVEN una capacidad con el requisito «X» y un cambio que agrega «X»
  - WHEN la persona intenta cerrarlo
  - THEN el cierre se rechaza nombrando «X», y ni el registro ni la spec consolidada cambian
  ```
- **Contraste contra el catálogo y pruebas:**
  El catálogo `factory_archivo.un_conflicto_impide_cerrar.oracle` establece:
  `umbral == 4 segun contrato porque "deben pasar los 4 casos enumerados para este requisito en tools/verify_archivo.py; asociar junto a corrida_completa"`.
  Los 4 casos son:
  1. `a2_agregar_un_requisito_que_ya_existe`
  2. `a2_modificar_un_requisito_que_no_existe`
  3. `a2_una_spec_consolidada_editada_a_mano_no_se_pisa`
  4. `a2_secciones_mayusculas_y_nombres_repetidos`
  La spec sólo contiene un escenario (`agregar un requisito que ya existe`), omitiendo en el contrato formal los otros 3 escenarios exigidos por Oracle y las pruebas unitarias.
- **Corrección propuesta:**
  Completar en `specs/archivo/spec.md` los 3 escenarios faltantes (`modificar un requisito que no existe`, `spec consolidada editada a mano`, `secciones y mayúsculas`).

---

## 3. Estado de `openspec/specs/` en este Repositorio

En el repositorio auditado:
- Existen 6 capacidades consolidadas: `estructura`, `limpieza`, `modos`, `portabilidad`, `revision-guiada`, `vigencia`.
- En `.factory/specs/`, existen sus 6 índices JSON homónimos.
- Los 7 cambios cerrados del proyecto están debidamente archivados:
  - `20261004-005956-revision-guiada` → `revision-guiada`
  - `20261005-105331-modos-de-trabajo` → `modos`
  - `20261005-132144-jerarquia-de` → `estructura`
  - `20261005-154433-la-vigencia-de` → `vigencia`
  - `20261005-184427-los-registros-de` → `portabilidad`
  - `20261005-193914-quitar-la-ruta` → `limpieza`
  - `20261006-004456-fase-2-de-la` → `estructura` (mediante el alias `estructura2` en `.factory/config.json`)
- Cada archivo `spec.md` contiene el banner estándar de no editar a mano y la atribución `Origen: <ID> · <requisito_oracle>` para cada requisito.
- La spec de la capacidad `archivo` (cambio `20261006-161029-archivar-al`) no está en `openspec/specs/` porque el cambio aún está abierto, lo cual es coherente con el contrato de la herramienta.

---

## 4. Límites de la Auditoría

- Auditoría puramente estática de lectura de especificaciones, documentación y código fuente.
- No se instalaron dependencias ni se ejecutaron pruebas durante esta inspección.
- La verificación de comportamiento dinámico se basó en el código fuente de `oracle_factory/`, las pruebas de contrato en `tests/test_archivo.py` y el verificador `tools/verify_archivo.py`.
