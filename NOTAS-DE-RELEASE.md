# Oracle Factory 0.1.0a8

- **`estado` dice qué sigue y lo ofrece.** `oracle-factory estado ID` calcula el próximo paso según lo que está vigente, en el orden del flujo: archivos del cambio que faltan (se recuperan desde Git), spec aprobada (también si cambió después de aprobarla), importar, confirmar o elegir medidas, revisión válida para el producto actual (`pedir-revision`, `revisar`, o commitear lo que cambió), juicio vigente (hechos, informe y producto) y cierre. En una terminal ofrece ejecutarlo desde un menú; sin terminal, con `--agente` o con la salida redirigida, sólo lo imprime. Un paso que exige algo de la persona (corregir, recuperar un archivo, completar una ruta) se muestra y no se ofrece ejecutar.
- **Errores con causa.** Al rechazar una aprobación, la revisión nombra las comprobaciones que no cumplen, los hallazgos abiertos o que está incompleta; `revision-preparar` avisa cuando no hay candidato vigente; sin `oracle-metalenguaje` en el intérprete, un mensaje dice qué falta y cómo seguir, sin traceback.
- **`python fabrica.py` usa el entorno del clon.** Si el intérprete no tiene `oracle-metalenguaje` u `oracle-task` y el clon tiene `.venv`, se re-ejecuta con él (una sola vez).
- **`resumen --ver`** regenera el resumen y lo muestra con `glow` si está instalado, o como texto.
- La revisión independiente la hicieron Codex (GPT) y Agy (Gemini) en 16 vueltas lanzadas con `pedir-revision`; las últimas, incrementales, porque el paquete completo supera el límite de Oracle Clue. Oracle sigue en 0.38.1 y Oracle Task en 0.2.0. Python >=3.11. Verificado en Linux.

```bash
uv publish dist/oracle_factory-0.1.0a8-py3-none-any.whl dist/oracle_factory-0.1.0a8.tar.gz
```

La evidencia está en la tarea del cambio `20261008-123018-cli-humana`.

# Oracle Factory 0.1.0a7

- **Decisiones guiadas:** ya no se tipean frases como `CERRAR <id>`. Cada decisión de una persona (aprobar la spec, registrar la revisión, cerrar, cambiar de modo) se toma en un menú: qué se decide, opciones numeradas con lo que implica cada una, y se elige escribiendo el número. Enter solo o cualquier otra respuesta cancela sin registrar nada; sin terminal interactiva, ninguna decisión de persona se registra.
- **`oracle-factory revisar ID`:** la revisión del candidato vigente de punta a punta, sin editar JSON ni copiar rutas o hashes. Muestra las comprobaciones con su evidencia, pregunta por cada hallazgo (aceptar el riesgo, descartar o dejar abierto), si la revisión está completa y la decisión, y registra.
- **El motivo se elige:** el que propuso el agente (`--agente … revisar ID --decision … --motivo …`), uno armado con los datos del cambio u «Otro». El registro guarda su origen (`agente`, `armado` o `persona`), también el de cada hallazgo resuelto.
- **`medir ID --confirmar`:** lista las medidas que propuso el agente, avisa si alguna conserva `sin_medir` o si el requisito cambió después de la propuesta, y las confirma todas o de a una.
- **`pedir-revision ID --a NOMBRE`:** lanza un revisor declarado en `.factory/config.json` (`revisores`: comando con marcadores, proveedor, modelo y tope en minutos), arma su pedido desde el cambio (plantilla reemplazable con `.factory/pedido-revision.md`; `--pedir` agrega indicaciones), valida su informe con Oracle Clue y lo guarda en `revision/` del candidato. Lo que sale mal (no inicia, no deja informe, Clue lo rechaza, se pasa del tope) no se guarda como informe; el revisor no decide. `revision-preparar` muestra las vueltas anteriores como comprobaciones, sin pedir que se decidan otra vez.
- Límite conocido: el paquete de Clue de un cambio amplio puede superar 1 MB; se revisa contra una base intermedia con `pedir-revision --base`.
- La revisión independiente de estos cambios la hicieron Codex (GPT) y Agy (Gemini), lanzados desde Factory con `pedir-revision`. Oracle sigue en 0.38.1 y Oracle Task en 0.2.0. Python >=3.11. Verificado en Linux.

```bash
uv publish dist/oracle_factory-0.1.0a7-py3-none-any.whl dist/oracle_factory-0.1.0a7.tar.gz
```

La evidencia está en las tareas de los cambios `20261007-192608-revisores` y `20261007-223645-decisiones-guiadas`.

# Oracle Factory 0.1.0a6

- **Resumen del estado actual:** `oracle-factory resumen` escribe `.factory/resumen.md` con los requisitos vigentes de cada capacidad (tipo, requisito de Oracle, medidas, veredicto con que se cerró su cambio), los cambios abiertos con lo que les falta, los riesgos aceptados y los límites declarados. Es determinista y queda fuera de la huella del producto; `cerrar` y `archivar` lo regeneran, `--verificar` dice si quedó viejo y `--salida RUTA` lo escribe en otro lugar. Se lee con formato con `glow -p .factory/resumen.md`.
- **`nuevo --sufijo`:** el ID de un cambio termina, por defecto, en su capacidad (antes, en los primeros 16 caracteres del título, que cortaban la frase); `--sufijo` permite elegirlo.
- **La web y las guías al día:** una página nueva, [Factory en equipo](https://segtem.github.io/oracle-factory/colaboracion.html), para trabajar entre varias personas con sus agentes; la portada y la guía desde cero cuentan los modos, la revisión guiada, `.factory/`, la spec consolidada y el resumen; la guía de colaboración v2 corrige las fricciones del piloto con agentes. Una prueba comprueba que cada comando y opción que nombran el sitio y las guías existe en la CLI.
- La revisión independiente de estos cambios la hicieron Codex (GPT) y Agy (Gemini). Oracle sigue en 0.38.1 y Oracle Task en 0.2.0. Python >=3.11. Verificado en Linux.

```bash
uv publish dist/oracle_factory-0.1.0a6-py3-none-any.whl dist/oracle_factory-0.1.0a6.tar.gz
```

La evidencia está en las tareas de los cambios `20261007-003414-resumen-del` y `20261007-115805-web-y-docs`.

# Oracle Factory 0.1.0a5

- **Lo vigente de cada capacidad:** al cerrar un cambio, su spec delta (`ADDED`, `MODIFIED`, `REMOVED`; sin encabezados cuenta como `ADDED`) se fusiona en `openspec/specs/<capacidad>/spec.md`, con un índice en `.factory/specs/<capacidad>.json`. Cada requisito vigente dice de qué cambio y de qué requisito de Oracle viene. Para saber qué hace el sistema hoy se lee esa spec, no todas las propuestas.
- **Un conflicto impide cerrar:** agregar un requisito que ya existe, modificar o quitar uno que no existe, repetir un nombre o usar `RENAMED` rechaza el cierre antes de preguntar. Una spec consolidada editada a mano tampoco se pisa.
- **Nada de lo cerrado se mueve:** la carpeta del cambio queda en `openspec/changes/<ID>/` y los requisitos de Oracle no se reimportan; `estado` de un cambio archivado dice cuáles de sus requisitos siguen vigentes y cuáles reemplazó otro cambio.
- **`archivar`:** fusiona los cambios cerrados antes de esta versión, en el orden en que se cerraron; es repetible y completa un archivo interrumpido.
- **Alias de capacidades** en `.factory/config.json` (`capacidades`), para que una capacidad con dos nombres tenga una sola spec; `nuevo` avisa cuando se usa un alias.
- `listar` marca los cambios archivados, `donde` muestra la spec consolidada y `buscar` busca también en `openspec/specs/`.
- El registro de cada cambio se guarda con reemplazo atómico (un corte no lo trunca) y no se reemplaza si es de sólo lectura.
- La revisión independiente de este corte la hizo otra familia de modelo (Codex, GPT) en cuatro vueltas, más una auditoría de documentación (Agy, Gemini). Oracle sigue en 0.38.1 y Oracle Task en 0.2.0. Python >=3.11. Verificado en Linux.

```bash
uv publish dist/oracle_factory-0.1.0a5-py3-none-any.whl dist/oracle_factory-0.1.0a5.tar.gz
```

La evidencia está en la tarea del cambio `20261006-161029-archivar-al`.

# Oracle Factory 0.1.0a4

- **Modos de trabajo** (`nuevo --modo`, `modo`): `autonomo`, `funcional` o `confirmacion` (por defecto) según quién decide los requisitos funcionales y no funcionales. Un agente propone con `--agente`; las decisiones humanas se confirman desde una terminal interactiva y cada evento registra quién, cómo y en qué modo.
- **Revisión guiada** (`revision-preparar`, `revision --formato guiado`): informe y decisiones en archivos separados, con hallazgos abiertos calculados a partir de las decisiones.
- **Vigencia por contenido:** una revisión o un veredicto siguen vigentes mientras no cambien los archivos del producto, aunque cambie HEAD por commits que sólo archivan registros o evidencia.
- **Portabilidad entre máquinas:** los registros guardan rutas relativas al proyecto (hechos y fuente de los requisitos), y un cambio juzgado en una máquina se cierra desde otra. Avisa si los hechos quedan fuera del proyecto o ignorados por Git.
- **Carpeta `.factory/`:** el estado de cada cambio (`factory.json`, `review.md`, `oracle-veredicto.txt`) vive en `.factory/cambios/<ID>/`, la configuración en `.factory/config.json` y lo producido sobre cada candidato en `.factory/cambios/<ID>/candidatos/<sha7>/`; `.factory/local/` queda fuera de Git. En `openspec/changes/<ID>/` queda sólo el acuerdo. Los comandos buscan la raíz del proyecto subiendo desde la carpeta actual, como Git.
- **Comandos nuevos:** `donde` (cada artefacto de un cambio y el gate que respalda), `ruta` (dónde guardar evidencia, paquetes de Clue o checkouts), `buscar` y filtros de `listar` (`--abiertos`, `--cerrados`, `--fase`).
- **`migrar`:** pasa un proyecto creado con una versión anterior a `.factory/`, sin cambiar el contenido de los registros salvo las rutas que citan los archivos movidos; es repetible, se recupera de una interrupción y no sigue enlaces simbólicos. Hasta migrarlo, el proyecto sigue funcionando y Factory avisa.
- Oracle sigue en 0.38.1 y Oracle Task en 0.2.0. Python >=3.11. Verificado en Linux; sin pruebas en Windows ni macOS.

## Distribución y publicación

El release de GitHub adjunta wheel, sdist y SHA256SUMS; los mismos archivos se suben a PyPI:

```bash
uv publish dist/oracle_factory-0.1.0a4-py3-none-any.whl dist/oracle_factory-0.1.0a4.tar.gz
```

La evidencia de cada parte está en las tareas de sus cambios (`20261005-105331-modos-de-trabajo`, `20261004-005956-revision-guiada`, `20261005-154433-la-vigencia-de`, `20261005-184427-los-registros-de`, `20261005-132144-jerarquia-de`, `20261006-004456-fase-2-de-la`), cada uno cerrado por una persona después de una revisión independiente. La 0.1.0a3 no se subió a PyPI; esta versión la reemplaza allí.

# Oracle Factory 0.1.0a3

- Inicio guiado: `nuevo --con-ejemplo notas` prepara ejemplo, propuesta, spec y reglas; rechaza destinos existentes antes de crear una tarea.
- `listar` recupera IDs completos y fases de cambios Factory.
- `medir ID --listar` consulta requisitos y medidas; `--requisito` y `--medida` hacen asociaciones explícitas validadas por el Oracle publicado.
- Se conserva `sin_medir` por defecto; `--sin-medir` declara un límite y `--quitar-sin-medir` lo retira explícitamente. Cambiar asociaciones invalida revisión y juicio anteriores.
- Conserva archivos ante sintaxis/medidas inválidas, usa reemplazo atómico y detecta cambios de entradas antes del guardado. El bloqueo coordina operaciones medir de Factory; no bloquea editores externos.
- `init` conserva configuración/ignores propios y explica el siguiente paso de Factory. Guía sin copias ni edición de indentación, con IDs de cambio/requisito recuperados de la CLI.
- Oracle sigue en 0.38.1 y Oracle Task en 0.2.0. Python >=3.11.

## Distribución y publicación

El release de GitHub adjunta wheel, sdist y SHA256SUMS. La subida de 0.1.0a3 a PyPI queda a cargo del mantenedor. El sitio usa el wheel del release para que el recorrido nuevo funcione mientras esa subida está pendiente.

```bash
uv publish dist/oracle_factory-0.1.0a3-py3-none-any.whl dist/oracle_factory-0.1.0a3.tar.gz
```

La evidencia exacta de pruebas, wheel instalado y guía se guarda en las tareas `20261004-005956-inicio-guiado` y `20261004-005956-elegir-medidas`. Confirmaciones de pruebas son fixtures en proyectos temporales; no aprueban el cierre de estos cambios reales. Verificación en Linux, sin piloto humano ni ejecución de Windows/macOS.

# Oracle Factory 0.1.0a2

- Migra la dependencia a `oracle-task==0.2.0` y resuelve el comando `tasks` desde esa distribución.
- Conserva IDs, carpetas de tareas y decisiones humanas. Actualiza la portada y la guía desde cero.
- Oracle continúa fijado en 0.38.1; no hace falta esperar otro paquete para instalar este corte.
- Publicado en PyPI; hashes wheel/sdist verificados contra el release y ejemplo completo probado desde una instalación nueva. Factory 0.1.0a1 depende del paquete antiguo. Trackertast se archivó, sin borrar sus versiones; para instalaciones nuevas usar Oracle Task y Factory 0.1.0a2 o posterior.

```bash
uv publish dist/oracle_factory-0.1.0a2-py3-none-any.whl dist/oracle_factory-0.1.0a2.tar.gz
```

La tarea `20261003-185925-migrar-task` registra la validación del corte.

# Oracle Factory 0.1.0a1

Primer corte alpha instalable, preparado para publicación manual en PyPI.

- Comando `oracle-factory`, Python >=3.11; Oracle 0.38.1 y Trackertast 0.1.0 como dependencias del mismo entorno.
- `--proyecto` selecciona la carpeta de trabajo; por defecto usa el directorio actual.
- `init` inicializa sin reemplazar configuración; `ejemplo notas` copia los recursos incluidos sin sobrescribir.
- Conserva aprobación de alcance, importación, revisión humana, evidencia vigente y cierre humano.
- Web pixel art y guía desde cero, con capacidades disponibles y futuras diferenciadas.

## Validación

Suite Python y ejemplo completo mediante el wheel instalado, fuera del checkout y sin ejecutables globales Oracle/Trackertast. Validación de wheel/sdist, metadata y recursos. Los resultados exactos del corte se registran en la tarea `20261002-234439-dist-uv`.

## Límites

Alpha: no genera productos ni coordina agentes automáticamente. Clue es independiente y todavía no está integrado. Las confirmaciones registran al operador; no autentican por sí solas su identidad. La prueba de instalación se realiza en Linux. Las decisiones humanas reales no se simulan para cerrar las tareas de este proyecto.

## Publicación manual en PyPI

El release adjunta wheel, sdist y SHA256SUMS. Descargar esos artefactos y comprobar sus hashes antes de publicar. Desde este checkout, los mismos archivos probados quedan en `dist/`:

```bash
uv publish dist/oracle_factory-0.1.0a1-py3-none-any.whl dist/oracle_factory-0.1.0a1.tar.gz
```

El comando usa las credenciales que configure el mantenedor. Este release no implica que la versión ya esté disponible en PyPI. Tras subirla, comprobar `uvx --from oracle-factory==0.1.0a1 oracle-factory --version` en un entorno limpio.
