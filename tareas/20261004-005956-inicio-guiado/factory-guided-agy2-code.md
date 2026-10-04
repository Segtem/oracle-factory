# Agy Task — 2026-10-03 23:47:01

**Tarea:** Trabajá en español. Revisión técnica de SOLO LECTURA del código YA IMPLEMENTADO en /home/workstation/Dev/factory, rama feat/20261004-005956-inicio-guiado. La aceptación del usuario está registrada en factory.json/canal conversación de los dos contratos. Leé diff CLI, tests/test_guided.py y contratos; no repitas auditoría de diseño anterior. NO edites ni corras tests (root corre wheel/guía), ni commits/push, ni registro de aprobación humana. Informe en salida del wrapper, máximo 8min.
Verificar bugs concretos: nuevo --con-ejemplo plan/copia antes tasks new, destinos/enlaces seguros/no sobrescribir, copia IO parcial informa y evita crear tareas/reintentosduplicados, plantillasmanualnuevo conservan Markdown sinindentextra. medir usa oracle_metalenguaje.nucleo (namespace publicado); catálogo efectivo, requisitosexactosdelcambio, preserva comentarios/textofuente/sin_medir salvoopciones, valida antesescribir, lock entre medir, comparar requisito/registro/spec/catalogo, invalidarantesrequisitoparasierroresnollevagreen. No se promete impedir editores externos. Buscar casos de concurrencia/errores no cubiertos y falsas garantías enREADMEguía. Revisar si testsmuy dependienteso simulanaprobaciónfuera/tmp. Un hallazgo debe demostrar escenario reproducible conlíneas; clasificarbloqueantedelcontrato o mejoraopcional. Si no haybugsverificados dilo, nunca aprobado ni listo producción por esta auditoría. Root atenderá hallazgos antes publicar.
**Directorio:** /home/workstation/Dev/factory
**Cuenta:** prof
**Modelo:** gemini-3.8-flash-high (esfuerzo high, timeout 8m)

---

### Informe de Revisión Técnica (SOLO LECTURA)

**Rama:** `feat/20261004-005956-inicio-guiado`
**Repositorio:** `/home/workstation/Dev/factory`
**Estado de la auditoría:** Solo lectura. No se ejecutaron pruebas (reservadas al entorno de empaquetado/guía de root), no se editaron archivos, no se crearon commits ni ramas, ni se registraron aprobaciones humanas ni cierres de tareas.

---

### 1. Verificación de Contratos y Código Implementado

#### A. Inicio Guiado (`nuevo --con-ejemplo`)
* **Planificación y copia previa a `tasks new`:**
  En [`oracle_factory/cli.py`](file:///home/workstation/Dev/factory/oracle_factory/cli.py#L101-L106), `plan_ejemplo()` inspecciona y planifica todos los destinos antes de invocar `tasks new`. `preparar_ejemplo(plan)` ejecuta la copia física de los archivos del ejemplo (`examples/notas/` y `catalogos/`) antes de que se ejecute la llamada de creación de tarea de `oracle-task` (línea 104).
* **Destinos y enlaces seguros sin sobrescritura:**
  [`ruta_segura()`](file:///home/workstation/Dev/factory/oracle_factory/cli.py#L499-L513) verifica que ninguna ruta escape de `ROOT`, rechaza componentes relativos ambiguos (`.` y `..`) y comprueba que ningún segmento del camino sea un enlace simbólico (`actual.is_symlink()`). En `plan_ejemplo()` (líneas 554-562), si cualquier archivo de destino existe o si algún directorio intermedio es un archivo regular, se aborta con [`FactoryError`](file:///home/workstation/Dev/factory/oracle_factory/cli.py#L27-L28). En `preparar_ejemplo()` (líneas 571-573), la apertura se realiza con modo `'xb'` (`O_CREAT | O_EXCL`), impidiendo a nivel del sistema operativo cualquier sobrescritura.
* **Copia parcial de E/S y prevención de tareas duplicadas:**
  En [`preparar_ejemplo()`](file:///home/workstation/Dev/factory/oracle_factory/cli.py#L575-L579), ante un `OSError`, se captura la excepción, se detalla el destino fallido y se listan todos los archivos copiados hasta ese instante (`Archivos copiados: ...`). Como la tarea de `tasks new` no fue creada, no queda una tarea huérfana en el tracker. Si el usuario reintenta `nuevo --con-ejemplo notas`, `plan_ejemplo()` detectará los archivos copiados en el intento previo y rechazará la operación antes de interactuar con `oracle-task`, evitando tareas duplicadas.
* **Plantillas manuales de `nuevo` sin indentación espuria:**
  En [`nuevo()`](file:///home/workstation/Dev/factory/oracle_factory/cli.py#L116-L154), las cadenas multilínea para [`proposal.md`](file:///home/workstation/Dev/factory/oracle_factory/cli.py#L116-L133), [`spec.md`](file:///home/workstation/Dev/factory/oracle_factory/cli.py#L134-L143), [`design.md`](file:///home/workstation/Dev/factory/oracle_factory/cli.py#L144) y [`tasks.md`](file:///home/workstation/Dev/factory/oracle_factory/cli.py#L145-L154) inician en la columna 0. No arrastran indentación de bloque de Python.

---

#### B. Elección de Medidas (`medir`)
* **Uso del namespace publicado `oracle_metalenguaje.nucleo`:**
  En [`oracle_factory/cli.py`](file:///home/workstation/Dev/factory/oracle_factory/cli.py#L633-L634) y [`cli.py`](file:///home/workstation/Dev/factory/oracle_factory/cli.py#L690-L691), se importan:
  - `from oracle_metalenguaje.nucleo import requisito`
  - `from oracle_metalenguaje.nucleo.proyecto import resolver, catalogo_efectivo`
  - `from oracle_metalenguaje.nucleo.forma import error_forma`
  Se verificó contra `oracle-metalenguaje==0.38.1` donde `_compat.py` expone y puentea de forma estable `oracle_metalenguaje.nucleo`.
* **Catálogo efectivo y requisitos exactos del cambio:**
  - [`inventario_medidas()`](file:///home/workstation/Dev/factory/oracle_factory/cli.py#L631-L648) consulta el proyecto mediante `resolver(['--proyecto', str(ROOT)])` y extrae `catalogo_efectivo(proyecto)`.
  - La selección de requisitos se limita estrictamente a los identificadores presentes en `estado.get('requisitos', [])` (línea 637).
  - En la línea 678, se rechaza cualquier requisito ajeno al cambio (`if requisito_id not in requisitos`).
* **Preservación de comentarios, texto fuente y `sin_medir`:**
  En las líneas 706-727, se analiza el archivo línea por línea (`keepends=True`). Se sustituye o inserta `medido_por` inmediatamente antes de `sin_medir` (respetando la gramática canónica de Oracle: `texto`, `fuente`, `medido_por`, `sin_medir`). Las líneas de comentarios `#`, `texto`, `fuente` o líneas intermedias no se reescriben ni alteran. Por defecto se conserva el valor preexistente de `sin_medir` a menos que se especifique `--sin-medir` o `--quitar-sin-medir`.
* **Validación previa a la escritura:**
  Antes de cualquier operación de escritura:
  1. Se verifica la aprobación vigente de la especificación (`exigir_spec`, línea 658).
  2. Se validan medidas duplicadas (línea 682) e inexistentes (línea 684).
  3. Se valida la coherencia de límites de `--sin-medir` (línea 687).
  4. Se verifica que el AST del resultado sea idéntico si no hubo cambios (`nuevo_r == r`, línea 703), saliendo sin invalidar revisiones.
  5. Se valida el parseo con `requisito.leer(datos)` y la forma canónica con `error_forma(...)` (líneas 728-734).
* **Bloqueo de concurrencia y comparación de 4 dimensiones:**
  - [`bloqueo_medidas(identificador)`](file:///home/workstation/Dev/factory/oracle_factory/cli.py#L616-L629) adquiere un bloqueo exclusivo mediante creación atómica de archivo (`.factory-demo/locks/{id}.medir.lock` con `os.O_CREAT | os.O_EXCL`).
  - Dentro del bloqueo (líneas 738-746), se verifican las 4 dimensiones contra lo leído inicialmente:
    1. Requisito (`ruta.read_bytes() == original`).
    2. Registro (`factory.json` == `registro_original`).
    3. Documentos de la spec aprobada (`documentos(...) == doc_original`).
    4. Catálogo efectivo (`actual_sha == catalogo_sha`).
* **Invalidación previa para evitar verdes espurios:**
  En las líneas 748-751, se actualiza e invalida primero `factory.json` (`revision=None, oracle=None, fase='requisitos_importados'`) mediante [`escribir_atomico`](file:///home/workstation/Dev/factory/oracle_factory/cli.py#L516-L534). Si la escritura posterior del archivo `.requisito` fallara (por disco lleno, desconexión o fallo de E/S), el estado en `factory.json` ya habrá revocado la revisión y el juicio previo, asegurando que un fallo de escritura nunca deje un veredicto verde anterior vigente.
* **Editores externos:**
  El diseño no promete impedir que un usuario modifique archivos externamente con un editor de texto; no obstante, [`escribir_atomico`](file:///home/workstation/Dev/factory/oracle_factory/cli.py#L528-L530) valida el contenido esperado (`esperado=original`) previo al reemplazo con `os.replace`, abortando si un editor externo alteró el archivo en ese intervalo.

---

### 2. Revisión de Documentación y Guía (`README.md`, `site/desde-cero.html`)

* **Garantías y límites de la evidencia:**
  Se revisaron las advertencias en [`README.md`](file:///home/workstation/Dev/factory/README.md#L45-L65), [`examples/notas/README.md`](file:///home/workstation/Dev/factory/examples/notas/README.md#L20-L32) y [`site/desde-cero.html`](file:///home/workstation/Dev/factory/site/desde-cero.html#L30-L32). No se encontraron falsas garantías:
  - Se explicita reiteradamente que "enlazar medidas no prueba pertinencia ni cumplimiento".
  - Se aclara que un veredicto verde de Oracle demuestra únicamente la observación de los casos provistos por el sensor (sin certificar la corrección intrínseca del sensor ni probar propiedades fuera de dichos casos).
  - Se aclara que `medir` no evalúa cumplimiento y que la decisión de pertinencia es humana.
  - Se deja constancia de que la versión `0.1.0a3` está disponible como wheel en el release de GitHub y que su publicación en PyPI está pendiente (evitando confusión con la `0.1.0a2` de PyPI).

---

### 3. Revisión de Pruebas y Aislamiento (`tests/test_guided.py`, etc.)

* **Aislamiento en `/tmp`:**
  En [`tests/test_guided.py`](file:///home/workstation/Dev/factory/tests/test_guided.py#L13-L24), la clase base `ProyectoTemporal` inicializa un directorio temporal aislado (`tempfile.TemporaryDirectory()`), y parchea `f.ROOT` y `f.CHANGES`.
* **Simulación de aprobaciones:**
  Todas las confirmaciones simuladas (`APROBAR ESPECIFICACION ...`) se inyectan mediante `unittest.mock.patch('builtins.input')` dentro del entorno de pruebas bajo `/tmp`. No modifican el repositorio principal, ni las tareas activas de `tareas/`, ni los acuerdos de `openspec/changes/`.
* **Independencia de tests:**
  La clase `EleccionMedidas` (línea 128) hereda directamente de `ProyectoTemporal` y no de `InicioGuiado`, evitando duplicación de ejecuciones o dependencias encadenadas entre contratos.

---

### 4. Hallazgos Técnicos

#### A. Bugs Bloqueantes del Contrato
* **Ninguno verificado.** El código implementado cumple rigurosamente con los escenarios, precondiciones y postcondiciones estipuladas en las especificaciones [`onboarding/spec.md`](file:///home/workstation/Dev/factory/openspec/changes/20261004-005956-inicio-guiado/specs/onboarding/spec.md) y [`measurement_choice/spec.md`](file:///home/workstation/Dev/factory/openspec/changes/20261004-005956-elegir-medidas/specs/measurement_choice/spec.md).

#### B. Mejoras Opcionales (No Bloqueantes)

1. **Resiliencia ante eliminación externa del archivo de bloqueo en `bloqueo_medidas`:**
   - **Archivo:** [`oracle_factory/cli.py`](file:///home/workstation/Dev/factory/oracle_factory/cli.py#L628)
   - **Línea:** 628 (`ruta.unlink()`)
   - **Escenario reproducible:** Si durante una operación `medir` prolongada un proceso o usuario externo elimina el archivo de lock `.factory-demo/locks/<id>.medir.lock`, al salir del bloque contextual, `ruta.unlink()` lanza un `FileNotFoundError` (subclase de `OSError`). Aunque `main()` (línea 811) lo captura y muestra `FACTORY BLOQUEADA: [Errno 2] No such file or directory`, la operación de medición ya se completó con éxito.
   - **Sugerencia:** Utilizar `ruta.unlink(missing_ok=True)` para tolerar que el lockfile haya sido retirado externamente durante el `finally`.
   - **Clasificación:** *Mejora opcional*.

2. **Captura de `OSError` en recálculo concurrente del catálogo:**
   - **Archivo:** [`oracle_factory/cli.py`](file:///home/workstation/Dev/factory/oracle_factory/cli.py#L742-L745)
   - **Líneas:** 742-745
   - **Escenario reproducible:** En `with bloqueo_medidas(identificador):`, la llamada a `inventario_medidas(estado)` lee los archivos del catálogo (`read_bytes()`). Si un archivo del catálogo fuera eliminado externamente durante la ejecución de `medir`, se lanza `FileNotFoundError` (`OSError`). Actualmente solo se captura `except ValueError as e:`. La excepción `FileNotFoundError` sube al manejador global de `main()`.
   - **Sugerencia:** Capturar `except (ValueError, OSError) as e:` en la línea 743 para homogeneizar el mensaje de error: `raise FactoryError(f'el catálogo cambió durante la operación: {e}') from e`.
   - **Clasificación:** *Mejora opcional*.

---

### Conclusión

No se hallaron bugs bloqueantes en la implementación de la rama `feat/20261004-005956-inicio-guiado`. Las operaciones de copia, validación sintáctica, concurrencia, invalidación de estado y no sobrescritura respetan estrictamente los contratos vigentes.

> **Aviso de auditoría:** Esta revisión técnica es estrictamente de solo lectura y **no constituye aprobación de producción ni cierre de tareas**. Corresponde al usuario/root atender las mejoras opcionales y realizar la verificación del wheel y la guía previa a la publicación.
