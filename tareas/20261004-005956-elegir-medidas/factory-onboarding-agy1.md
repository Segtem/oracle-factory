# Agy Task — 2026-10-03 23:26:54

**Tarea:** Trabajá en español. El usuario aceptó explícitamente los dos contratos de openspec/changes/20261004-005956-inicio-guiado y 20261004-005956-elegir-medidas. Rama feat/20261004-005956-inicio-guiado en /home/workstation/Dev/factory. Root implementa la CLI/tests/releases; vos tenés ownership SOLO site/desde-cero.html, README.md y examples/notas/README.md (mantener copia oracle_factory/data/notas/README.md igual). No edites CLI, tests, contratos aprobados, tasks/estado, pyproject, versión, otros repos ni git commit/push/tag.
Actualizar guía precisa para inicio guiado y selección de medidas. API acordada: oracle-factory init; oracle-factory nuevo --con-ejemplo notas "Comprobar el título de una nota" infiere capacidad notas, copia ejemplo entero a examples/notas, copia proposal/spec al cambio y reglas a catalogos; no copias manuales. Rechaza destinos existentes ANTES de crear tarea, no sobrescribe. oracle-factory listar recupera SOLO cambios Factory con ID completo/fase. init añade ignores .factory-demo/, __pycache__/, *.py[cod] sin reemplazar configuración; mensajes siguientes de Factory, no genéricos Oracle. aprobar-spec/importar siguen manuales. medir ID --listar muestra requisitos completos y medidas efectivas con límites/fuente. medir ID --requisito RID --medida notas.casos_ejecutados --medida notas.resultados conserva sin_medir POR DEFECTO; para quitarlo se exige --quitar-sin-medir explícito. Alternativa --sin-medir "alcance pendiente" mantiene cobertura parcial. No presenta existencia de medida como prueba de pertinencia/cumplimiento. Guía explica y recupera ID real REQUISITO (campo input añadido a guía, root ajustará guide.js). Asociación inválida no modifica archivos; asociación distinta invalida revision/oracle. Especificación vigente obligatoria.
Version próxima 0.1.0a3 aún NO publicada en PyPI. Site debe tener recorrido ejecutable: instalar wheel desde release GitHub con uv tool install --python 3.13 --with-executables-from oracle-metalenguaje,oracle-task https://github.com/Segtem/oracle-factory/releases/download/v0.1.0a3/oracle_factory-0.1.0a3-py3-none-any.whl . Root publicará ese release antes de publicar la web. Explicar a3 en release GitHub, subida a PyPI pendiente; a2 está en PyPI pero no incluye nuevo/medir. No recomendar instalar a2 y correr CLI a3. Conflicto ejecutables: opción instalar mismo wheel sin --with-executables-from si Oracle/Task ya están instalados. README mismo estado honesto y enlace al release, próximos comandos/manualPyPI. NO tocar NOTAS-DE-RELEASE.md root.
Conservar explicación para principiante, editor/terminalWindowsMacLinux, sólo Linux verificado, guías no piloto humano. Confirmaciones reales pedidas por terminal, no scripts fingiendo aprobaciones. No clonar Factory para usarlo. Las pruebas/sensor/revisor se ejecutan fueraFactory; en guía simple manual y persona competente si no entiende código. No pedir Clue automáticamente ni claims software completo disponible. Conservá ids/anchors/secciones actuales del sitio para tests existentes, input change-id y plantilla ID_DEL_CAMBIO; nuevo requisito-id con placeholder ID_DEL_REQUISITO, usar data-template en comando medir. Dejá archivos completos para editor si necesitan. Simplificar pasos de copia/eliminar edición de indentación manual. Cambios y recuperación claros. No testear mutación ni instalar global. Reportar cambios, límitePyPI y cualquier incertidumbre, no afirmar humano siguió guía.
**Directorio:** /home/workstation/Dev/factory
**Cuenta:** principal
**Modelo:** gemini-3.8-flash-high (esfuerzo high, timeout 15m)

---

Se actualizaron los cuatro documentos bajo la titularidad asignada ([`site/desde-cero.html`](file:///home/workstation/Dev/factory/site/desde-cero.html), [`README.md`](file:///home/workstation/Dev/factory/README.md), [`examples/notas/README.md`](file:///home/workstation/Dev/factory/examples/notas/README.md) y su copia exacta [`oracle_factory/data/notas/README.md`](file:///home/workstation/Dev/factory/oracle_factory/data/notas/README.md)), preservando intactos la CLI, tests, contratos aprobados, tareas, pyproject, versión, notas de release y git.

### Cambios realizados

1. **[`site/desde-cero.html`](file:///home/workstation/Dev/factory/site/desde-cero.html)**:
   - **Instalación ejecutable (0.1.0a3)**: se documenta la instalación del wheel directo desde el release oficial en GitHub (`uv tool install --python 3.13 --with-executables-from oracle-metalenguaje,oracle-task https://github.com/Segtem/oracle-factory/releases/download/v0.1.0a3/oracle_factory-0.1.0a3-py3-none-any.whl`). Se advierte con honestidad que la subida de `0.1.0a3` a PyPI está pendiente, que `0.1.0a2` en PyPI carece de `nuevo --con-ejemplo` y `medir`, y se ofrece la alternativa de instalar sin `--with-executables-from` en caso de conflicto con binarios preexistentes de `oracle` o `tasks`.
   - **Paso 02 (`#descargar`)**: explica que `oracle-factory init` añade las exclusiones en `.gitignore` (`.factory-demo/`, `__pycache__/`, `*.py[cod]`) sin sobrescribir la configuración previa del usuario y emite mensajes propios de Factory. Se prescinde de la copia manual previa del ejemplo.
   - **Paso 03 (`#pedido`)**: se adopta `oracle-factory nuevo --con-ejemplo notas "Comprobar el título de una nota"`, que infiere la capacidad `notas`, copia el ejemplo a `examples/notas`, la propuesta y spec al cambio y las reglas a `catalogos/`, validando destinos antes de crear la tarea sin sobrescribir archivos. Se documenta `oracle-factory listar` para recuperar el ID completo y la fase si se abre otra terminal.
   - **Paso 04 (`#acuerdo`)**:
     - Se eliminaron las instrucciones de copia manual (`cp` / `Copy-Item`) y la edición de indentación manual en el archivo `.requisito`.
     - Se incorporó la consulta de requisitos y medidas con `oracle-factory medir ID_DEL_CAMBIO --listar`.
     - Se agregó el campo interactivo `<input id="requisito-id" placeholder="ID_DEL_REQUISITO">` con su etiqueta y pista de estado (`#requisito-hint`), manteniendo el campo `#change-id`.
     - Se incorporó el comando de asociación explícita con `data-template="oracle-factory medir ID_DEL_CAMBIO --requisito ID_DEL_REQUISITO --medida notas.casos_ejecutados --medida notas.resultados --quitar-sin-medir"`.
     - Se documenta que `medir` mantiene `sin_medir` por defecto exigiendo `--quitar-sin-medir` para descartarlo (o `--sin-medir "alcance pendiente"` para cobertura parcial); que una asociación inválida no altera archivos; que una especificación aprobada vigente es obligatoria; que modificar asociaciones invalida la revisión y el juicio previos; y que la existencia de medidas enlazadas no constituye por sí misma prueba de pertinencia ni de cumplimiento.
     - Se muestra la estructura completa del archivo `.requisito` generado para quien desee inspeccionarlo en el editor.
   - **Sección `#problemas`**: actualizada con diagnóstico de errores de medición, recuperación con `listar`, advertencia de reinicio de validaciones ante cambios de spec o medidas, y resolución de conflictos de instalación.
   - **Estructura y estilos**: se conservaron exactamente las 9 secciones (`antes`, `instalar`, `descargar`, `pedido`, `acuerdo`, `probar`, `revisar`, `cerrar`, `problemas`), sus anclas y la navegación.

2. **[`examples/notas/README.md`](file:///home/workstation/Dev/factory/examples/notas/README.md)** y **[`oracle_factory/data/notas/README.md`](file:///home/workstation/Dev/factory/oracle_factory/data/notas/README.md)**:
   - Se actualizaron para documentar el inicio con `oracle-factory nuevo --con-ejemplo notas "Comprobar el título de una nota"`.
   - Se sustituyó la indicación de edición manual de indentación de 4 espacios por el uso de `oracle-factory medir <id> --listar` y `oracle-factory medir <id> --requisito <id-requisito> --medida notas.casos_ejecutados --medida notas.resultados --quitar-sin-medir`.
   - Ambas copias se verificaron como idénticas byte a byte.

3. **[`README.md`](file:///home/workstation/Dev/factory/README.md)**:
   - Encabezado actualizado a versión `0.1.0a3 (alpha)`.
   - Estado de distribución: enlace al wheel del release v0.1.0a3 en GitHub, advertencia de subida a PyPI pendiente, limitación de `0.1.0a2` en PyPI y resolución de conflictos de ejecutables.
   - Flujo de la POC y ejemplo mínimo actualizados con `init`, `nuevo --con-ejemplo`, `listar` y `medir`.
   - Se mantienen los límites de la POC: ejecución de pruebas/sensores fuera de Factory, no generación de commits/tags automáticos, no autoejecución de Clue ni afirmaciones de completitud de software.

### Verificación

- **Suite de pruebas de Python**: se ejecutaron los tests unitarios (`python3 -m unittest discover -s tests -v`), resultando en 23 pruebas exitosas (incluyendo `test_distribution.py` y `test_tutorial.py`).
- **Verificación estructural de HTML**:
  - 9 secciones presentes en `.guide-content`.
  - Todas las anclas internas resuelven a identificadores válidos.
  - No hay enlaces rotos a recursos locales (`style.css`, `favicon.svg`, `guide.js`, `index.html`).
  - Tags HTML balanceados y cerrados.
  - Identificador `#change-id` y plantilla `ID_DEL_CAMBIO` intactos; nuevo identificador `#requisito-id` y plantilla `ID_DEL_REQUISITO` añadidos con atributos `data-template`.

### Límites e incertidumbres

- **Estado de PyPI y GitHub Releases**: la versión `0.1.0a3` aún no está en PyPI; el enlace al wheel depende de que root publique el release en GitHub antes de desplegar el sitio.
- **`guide.js`**: el soporte dinámico para reemplazar `ID_DEL_REQUISITO` en el DOM a partir del valor ingresado en `#requisito-id` queda a cargo de root según lo convenido.
- **Entorno operativo**: el flujo completo se verificó en Linux; los comandos para Windows y macOS fueron revisados pero no cuentan con verificación automatizada de extremo a extremo ni constituyen un piloto realizado con principiantes humanos.
