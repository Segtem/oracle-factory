# Agy Task — 2026-10-03 23:26:54

**Tarea:** Trabajá en español. Auditoría de SOLO LECTURA para contratos aceptados en /home/workstation/Dev/factory, rama feat/20261004-005956-inicio-guiado. Root implementaCLI y agy1 guía. NO edites ningún archivo (wrapper guarda reporte en /tmp), commits/push ni corras tests mientras root edita. Leé oracle_factory/cli.py y contratos de openspec/changes/20261004-005956-inicio-guiado y 20261004-005956-elegir-medidas, y nucleo/requisito.py / proyecto.py de Oracle si sirve. Encontrá riesgos y casos de prueba necesarios para conservar archivos: preflight antes tasks new, errores parciales y reintentos sin duplicar tareas, sin_medir parcial conservado, requisito fuera cambio, medida inexistente/duplicada, sintaxis, rutas/enlaces simbólicos, cambios concurrentes, invalidación de revisión/juicio, y wheel instalado sin PATHglobalOracle/Task. No fabricar aprobaciones ni ejecutar producción. La CLI se va a extender medir con --sin-medir texto o --quitar-sin-medir explícito; default preserva límites. Aún no hay cambios implementados si lees temprano; evaluar propuesta/diseño y recomendar casos concretos en informe. Máximo 8 minutos, concentrá en invariantes importantes, no teorías hipotéticas ni prueba espejo de implementación. Tu resultado es revisión técnica de diseño, nunca aprobación humana para cierre.
**Directorio:** /home/workstation/Dev/factory
**Cuenta:** prof
**Modelo:** gemini-3.8-flash-high (esfuerzo high, timeout 8m)

---

Realizando búsqueda de `requisito.py` en segundo plano para analizar la semántica de Oracle. Mientras finaliza, preparo la auditoría técnica de los contratos.
# Informe de Auditoría Técnica de Diseño (Solo Lectura)
**Rama:** `feat/20261004-005956-inicio-guiado`
**Objetivo:** Análisis de contratos y diseño para `onboarding` (`20261004-005956-inicio-guiado`) y `measurement_choice` (`20261004-005956-elegir-medidas`).
**Alcance y Rol:** Revisión técnica de diseño sobre arquitectura, contratos e invariantes. **No constituye ni reemplaza la aprobación humana para cierre ni valida pertinencia semántica.**

---

## 1. Diagnóstico del Estado Actual y Contratos

En el repositorio local no se han realizado modificaciones a [`oracle_factory/cli.py`](file:///home/workstation/Dev/factory/oracle_factory/cli.py). Las propuestas y especificaciones en `openspec/changes/` definen dos extensiones clave:
1. **Inicio guiado (`onboarding`):** extensión de `nuevo` con `--con-ejemplo notas`, `listar` para recuperar tareas/fases sin adivinar IDs, y preflights de no colisión.
2. **Elección de medidas (`measurement_choice`):** comando `medir` (`--listar` o asociación explícita `--requisito ... --medida ...`), con flags `--sin-medir <texto>` y `--quitar-sin-medir` (preservando límites por defecto), validación canónica de Oracle e invalidación de gates ante modificaciones.

---

## 2. Invariantes Críticas y Matriz de Riesgos

### A. Preflight estricto antes de `tasks new`
* **Riesgo:** [`cli.py:nuevo()`](file:///home/workstation/Dev/factory/oracle_factory/cli.py#L88-L101) invoca `tasks new` **antes** de preparar el directorio y los archivos. Si `--con-ejemplo notas` intenta copiar archivos a `catalogos/notas.*.oracle` y alguno ya existe, o si la capacidad no coincide con `notas`, la tarea ya quedó registrada en `oracle-task`.
* **Invariante:** Cero invocaciones a `oracle-task new` si algún destino ya existe o si los argumentos de ejemplo son incompatibles.
* **Casos de prueba necesarios:**
  * `test_nuevo_ejemplo_colision_catalogo_no_toca_tracker`: crear previamente `catalogos/notas.casos_ejecutados.oracle`. Invocar `nuevo --con-ejemplo notas "Titulo"`. Debe fallar con error descriptivo y verificar que `tasks new` jamás fue ejecutado.
  * `test_nuevo_ejemplo_capacidad_incompatible_no_crea_tarea`: invocar `nuevo --capacidad demo --con-ejemplo notas`. Debe rechazar la discrepancia sin llamar a `tasks new`.

### B. Errores parciales y reintentos sin duplicar tareas
* **Riesgo:** Si ocurre una falla de I/O o interrupción tras recibir el ID de `tasks new` pero antes de escribir [`factory.json`](file:///home/workstation/Dev/factory/openspec/changes/20261004-005956-inicio-guiado/factory.json), el cambio queda a medio crear. Si el usuario reintenta, creará otra tarea duplicada.
* **Invariante:** Preparación atómica del paquete. Si la escritura falla tras la creación de la tarea, debe reportarse la ruta exacta y el ID creado con instrucciones explícitas de diagnóstico, sin forzar una tarea huérfana oculta.
* **Caso de prueba:** `test_nuevo_falla_io_reporta_id_creado`: simular fallo de permisos en `openspec/changes` tras `tasks new` y verificar que el error explica el estado exacto sin inconsistencias.

### C. Preservación por defecto de `sin_medir` parcial
* **Riesgo:** En Oracle ([`nucleo/requisito.py:66-68`](file:///home/workstation/Dev/oracle/nucleo/requisito.py#L66-L68)), un requisito con `medido_por` y `sin_medir` tiene cobertura `"parcial"`. Si `medir` asocia una regla y elimina silenciosamente `sin_medir`, el requisito pasa a `"total"`, ocultando falsamente el alcance descubierto.
* **Invariante:** Por defecto, `medir` conserva intacto el `sin_medir` existente. Solo se altera con `--sin-medir <texto>` explícito o se remueve con `--quitar-sin-medir`. Si un requisito nacía `"sin_medir"`, asociar una medida sin `--quitar-sin-medir` lo convierte en `"parcial"` (comportamiento seguro y honesto).
* **Casos de prueba necesarios:**
  * `test_medir_preserva_sin_medir_por_defecto`: asociar `--medida m1` a un requisito que tiene `sin_medir "falta caso B"`. El `.requisito` final debe contener tanto `medido_por m1` como `sin_medir "falta caso B"`.
  * `test_medir_quitar_sin_medir_explicito`: asociar `--medida m1 --quitar-sin-medir`. Debe eliminar la cláusula y quedar en cobertura total.
  * `test_medir_flags_excluyentes`: rechazar invocaciones que pasen simultáneamente `--sin-medir` y `--quitar-sin-medir`.

### D. Requisito fuera del cambio (Aislamiento de Scope)
* **Riesgo:** Un comando `medir ID --requisito <req_id>` podría intentar alterar requisitos de otro cambio, requisitos huérfanos o utilizar trayectorias con `../` para editar archivos arbitrarios.
* **Invariante:** El `req_id` debe cumplir el regex de identificador de Oracle (`[a-z][a-z0-9_]*(?:\.[a-z][a-z0-9_]*)+`) y debe pertenecer estrictamente a la lista `estado["requisitos"]` del cambio activo en [`factory.json`](file:///home/workstation/Dev/factory/openspec/changes/20261004-005956-elegir-medidas/factory.json).
* **Casos de prueba necesarios:**
  * `test_medir_rechaza_requisito_de_otro_cambio`: pasar un requisito de otro dominio o no listado en `factory.json`; debe fallar con `FactoryError` sin modificar archivos en disco.
  * `test_medir_rechaza_path_traversal`: intentar pasar cadenas con rutas (`../`) o identificadores mal formados.

### E. Medidas inexistentes o duplicadas
* **Riesgo:**
  1. Si se asocian medidas duplicadas (ej. `--medida m1 --medida m1`), Oracle falla con [`RequisitoMalDeclarado: medido_por repite una medida`](file:///home/workstation/Dev/oracle/nucleo/requisito.py#L90).
  2. Si se asocia una medida inexistente en los catálogos del proyecto o perfiles, Oracle fallará en cobertura o juicio.
* **Invariante:** Validación previa de existencia en el catálogo y descarte de duplicados. Ante cualquier error, el archivo original conserva sus bytes íntegros.
* **Casos de prueba necesarios:**
  * `test_medir_medida_inexistente_preserva_bytes`: intentar asociar una medida que no existe en `catalogos/`. Debe informar error y verificar que el hash SHA-256 del `.requisito` original no cambió.
  * `test_medir_rechaza_duplicados`: pasar medidas repetidas y comprobar rechazo previo a la escritura.

### F. Sintaxis canónica, orden estricto y escritura atómica
* **Riesgo:** [`nucleo/requisito.py:163`](file:///home/workstation/Dev/oracle/nucleo/requisito.py#L163) ejecuta `error_forma(ruta, texto, imprimir(datos))`. Cualquier desvío de indentación (4 espacios), orden de cláusulas (`requisito`, `texto`, `fuente`, `medido_por`, `sin_medir`) o espaciado genera rechazo sintáctico. Asimismo, una escritura directa interrumpida dejaría el archivo corrupto.
* **Invariante:** Uso estricto de la función de serialización canónica de Oracle (`imprimir(r.a_datos())`). La escritura en disco debe ser atómica mediante archivo temporal en el mismo directorio y reemplazo con `os.replace`.
* **Caso de prueba:** `test_medir_genera_sintaxis_canonica`: asociar medidas y validar que el archivo resultante sea leído exitosamente por `oracle.nucleo.requisito.cargar(ruta)`.

### G. Rutas y enlaces simbólicos (Symlinks)
* **Riesgo:** [`nucleo/requisito.py:180`](file:///home/workstation/Dev/oracle/nucleo/requisito.py#L180) rechaza expresamente requisitos que sean symlinks (`un requisito no puede ser symlink`). Igualmente, `oracle.json` no puede ser symlink.
* **Invariante:** Rechazar la modificación o lectura si `requisitos/<id>.requisito` o los catálogos destino son symlinks (`p.is_symlink()`).
* **Caso de prueba:** `test_medir_rechaza_requisito_symlink`: verificar que si el requisito objetivo es un symlink, `medir` aborta con error de seguridad sin modificar el destino enlazado.

### H. Detección de cambios concurrentes
* **Riesgo:** Si un usuario o proceso externo modifica el `.requisito` o la spec aprobada mientras se procesa `medir`, se podrían sobreescribir ediciones o dejar inconsistente la base.
* **Invariante:** Verificar `exigir_spec()` y comparar la huella SHA-256 del archivo `.requisito` leída en memoria contra el disco inmediatamente antes de aplicar el reemplazo atómico.
* **Caso de prueba:** `test_medir_aborta_si_archivo_cambio_concurrentemente`: alterar el archivo en disco antes del guardado; el comando debe fallar sin sobrescribir los cambios externos.

### I. Invalidación de revisión y juicio previo
* **Riesgo:** Si un cambio ya tenía revisión aprobada (`estado["revision"]`) o veredicto de Oracle (`estado["oracle"]`), una modificación en las medidas altera la cobertura y deja sin sustento la evidencia anterior.
* **Invariante:** Toda asociación que altere el estado previo debe resetear obligatoriamente:
  * `estado["revision"] = None`
  * `estado["oracle"] = None`
  * `estado["fase"] = "requisitos_importados"`
  * Registrar nota en `oracle-task` y evento en `estado["eventos"]`.
  * Si la invocación a `medir` no altera nada (idempotente), no debe invalidar.
* **Casos de prueba necesarios:**
  * `test_medir_invalida_revision_y_oracle`: dado un cambio con revisión y veredicto registrados, ejecutar `medir` con nueva regla. Verificar que ambos campos vuelven a `None` y que [`pendientes_actuales()`](file:///home/workstation/Dev/factory/oracle_factory/cli.py#L355) bloquea el cierre.
  * `test_medir_idempotente_conserva_gates`: si las medidas y `sin_medir` no varían, no resetear evidencia.

### J. Ejecución con wheel instalado sin PATH global
* **Riesgo:** Al instalarse con `uv tool install dist/*.whl`, los binarios `oracle` y `tasks` no están en el `PATH` global del usuario. La función [`ejecutar()`](file:///home/workstation/Dev/factory/oracle_factory/cli.py#L63-L79) resuelve esto invocando el entry point a través de `sys.executable -c ...`. Si la nueva implementación de `medir` o `nuevo` llama directamente a `subprocess.run(["oracle", ...])` o hace `import oracle_metalenguaje` a nivel de módulo sin contemplar entornos donde solo existe el CLI externo, fallará.
* **Invariante:** Todas las interacciones delegadas con Oracle y Task deben realizarse a través de `ejecutar()` o resolviendo los entry points del intérprete actual.
* **Caso de prueba:** `test_medir_funciona_sin_oracle_en_path`: ejecutar en un entorno con `PATH` sanitizado (sin binarios de oracle) verificando que `ejecutar()` resuelve los entry points empaquetados.

---

## 3. Recomendaciones Específicas de Diseño para Root y agy1

1. **En `oracle_factory/cli.py:nuevo`:**
   - Extraer una función de preflight pura: `validar_destinos_nuevo(proyecto, capacidad, con_ejemplo)`.
   - Si `con_ejemplo == "notas"`: inferir capacidad `notas` si no fue dada, o verificar `capacidad == "notas"`; chequear existencia previa de `catalogos/notas.*.oracle`.
   - Llamar a `ejecutar(["tasks", "new", ...])` **únicamente** tras superar todas las validaciones de destino.

2. **En el subcomando `medir`:**
   - Implementar `--listar` como consulta de solo lectura que imprima tabla de requisitos del cambio, medidas vinculadas, `sin_medir` y catálogo de medidas disponibles en el proyecto, sin tocar archivos.
   - En la asociación (`--requisito ... --medida ...`):
     - Exigir spec vigente con [`exigir_spec()`](file:///home/workstation/Dev/factory/oracle_factory/cli.py#L170).
     - Validar pertenencia del requisito en `estado["requisitos"]`.
     - Validar que el requisito no sea symlink.
     - Cargar y parsear con la lógica canónica de Oracle.
     - Modificar el objeto y serializarlo canónicamente.
     - Comparar contra el contenido actual; si hubo cambios, aplicar reemplazo atómico e invalidar `revision` y `oracle`.
     - Dejar asentada la nota en `oracle-task`.

3. **En el subcomando `listar`:**
   - Iterar sobre `openspec/changes/*/factory.json` resolviendo IDs completos y fases actuales, sin confundir tareas de `oracle-task` que no correspondan a cambios de Factory.

*Este informe concluye la revisión técnica de diseño de solo lectura para la rama `feat/20261004-005956-inicio-guiado`.*
