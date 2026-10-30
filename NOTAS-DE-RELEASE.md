# Oracle Factory 0.1.0a16

- **Procedencia de las dependencias.** `oracle-factory procedencia ID` guarda en el candidato un inventario CycloneDX de las dependencias de Python (del `uv.lock`, con origen y hashes, y de lo instalado); `--buscar` dice qué cambios y candidatos usaron una dependencia y `--auditar --avisos` los cruza con un archivo de avisos OSV. Reconoce las versiones corregidas por Lightwell (sufijo `rhlw`).
- **Avisos de OSV.dev, con tu permiso.** `procedencia --consultar-osv --red` baja de OSV.dev los avisos de las dependencias de los inventarios guardados, los guarda en `.factory/local/` y audita. Sin `--red` no se conecta; sólo salen nombre, versión y ecosistema, y un fallo nunca se lee como «sin afectados».
- **El `uv.lock` de Factory viaja con el repositorio** y una prueba exige que coincida con `pyproject.toml`; un paquete del lock que el entorno no instala se marca y no invalida el inventario.
- **El código de la CLI, en módulos.** `cli.py` se repartió en `parser`, `flujo_revision`, `flujo_medidas` y `lecturas` para alejarlo del límite de tamaño de la revisión; los comandos y su ayuda no cambian.
- **Textos al día.** Las notas declaran publicada la 0.1.0a15, con su tag y su release.
- **Publicada.** En PyPI como `oracle-factory==0.1.0a16` y en GitHub con su tag `v0.1.0a16` (pre-release); los archivos de PyPI tienen el mismo contenido que el wheel que se comprobó instalado en un entorno nuevo, y se instalaron desde PyPI en un entorno limpio.
- Factory usa Oracle 0.39.0, Oracle Task 0.2.0 y Oracle Clue 0.1.0a2. Python >=3.11. Verificado en Linux. La extensión de VS Code sigue en 0.5.0 y se arma con `python3 editores/vscode/empaquetar.py`.

# Oracle Factory 0.1.0a15

- **El tablero dice qué hacer.** Cada cambio muestra «Qué falta» con una frase en lenguaje común y quién lo hace (vos o un agente); cuando lo que sigue lo corre un agente, dice «Ahora no te toca nada». Si el cambio lo tiene otra persona, la decisión se rotula «LA DECIDE ANA» en vez de «TE NECESITA», y «Actividad reciente» lista los últimos diez eventos de los cambios abiertos. `oracle-factory tablero --json` suma `yo`, `faltan` y `actividad`.
- **La terminal de Factory espera a estar lista.** Al escribir un comando desde el tablero en una terminal nueva, la extensión espera a que el shell avise (hasta `factory.esperaTerminalMs`, 3000 por defecto). Otra extensión que active el entorno de Python con su propio Enter puede seguir pisando el comando: en ese caso conviene desactivar su activación automática.
- **`preguntar` cuenta y lista las specs.** «¿Cuántas specs hay?» responde desde el inventario, con las vigentes y las de cambios abiertos; un filtro que no admite (fechas, estados) se rechaza diciéndolo, en vez de devolver pasajes sueltos.
- **El idioma de la plantilla.** `"idioma": "es"` o `"en"` en `.factory/config.json`, o `nuevo --idioma`, elige en qué idioma se escribe la propuesta, la spec, el diseño y las tareas de un cambio nuevo; ya no se mezclan. Por defecto, español.
- **Bloqueos que explican su causa.** El próximo paso sin revisor configurado dice qué falta y dónde declararlo; `pedir-revision --base vacio` revisa un producto cuyo código está en el primer commit; y `aprobar-spec` nombra de cada archivo la línea con la marca de pendiente y cuántas quedan, o dice qué archivo falta.
- **Publicada.** En PyPI como `oracle-factory==0.1.0a15` y en GitHub con su tag `v0.1.0a15` (pre-release); los archivos de PyPI tienen el mismo contenido que el wheel que se comprobó instalado en un entorno nuevo.
- Factory usa Oracle 0.39.0, Oracle Task 0.2.0 y Oracle Clue 0.1.0a2. Python >=3.11. Verificado en Linux. La extensión de VS Code sigue en 0.5.0 y se arma con `python3 editores/vscode/empaquetar.py`.

# Oracle Factory 0.1.0a14

- **Distribución verificable y consultas del proyecto.** Preparación y comprobación del wheel 0.1.0a14 instalado en un entorno nuevo y ejecutado fuera del checkout, verificando origen de importación y versión sin depender del entorno de desarrollo.
- **Consultas de registro y elaboración con límites.** `oracle-factory preguntar` responde a consultas directas del registro (contar cerrados archivados, abiertos y abandonados con fuentes de inventario), y elabora con RAG documental y proveedores configurados. Sin modelo configurado no descarga ni elige modelos implícitos; ante un proveedor simulado que intenta llamadas de escritura, Factory rechaza la operación sin tocar el disco ni el registro, conserva fuentes y distingue la simulación de una medición real.
- **Documentación al día.** Metadatos del paquete, CLI, guías y textos de la web sincronizados con 0.1.0a14.
- **Publicada.** En PyPI como `oracle-factory==0.1.0a14` y en GitHub con su tag `v0.1.0a14` (pre-release); el wheel es el mismo que se comprobó instalado en un entorno nuevo. Se conservan la versión 0.1.0a13 y sus artefactos.
- Factory usa Oracle 0.39.0, Oracle Task 0.2.0 y Oracle Clue 0.1.0a2. Python >=3.11. Verificado en Linux.

# Oracle Factory 0.1.0a13

- **El tablero de comando en VS Code.** `oracle-factory tablero --json` y el panel de la extensión: qué te necesita a vos, la línea de tiempo de cada cambio con quién decidió qué, los hallazgos por severidad y las métricas del proyecto. Cada commit dice de qué cambio es (hooks que agregan `Cambio: ID`; `oracle-factory log ID`), y `tomar`/`soltar` dicen quién trabaja en qué, con su persona y sus agentes.
- **De a dos.** El tablero en pair programming con Live Share: presencia, el tablero compartido y el chat guardado en el cambio; compartir, copiar el enlace y unirse desde el tablero.
- **El conocimiento del proyecto.** `oracle-factory kb` genera `kb/` desde el registro (una nota por cambio y por requisito) y lo rehace en cada decisión; las notas de personas vencen solas cuando cambian sus fuentes; `por-que ARCHIVO:LÍNEA` va de una línea a su cambio. `oracle-factory preguntar` responde con los pasajes vigentes y su cita: búsqueda léxica, por embeddings (Ollama local con `qwen3-embedding:0.6b` por defecto, configurable) y por el grafo del vault, con su calidad medida por preguntas de oro.
- **Dos personas con sus agentes, sin pisarse.** Un banco de concurrencia de 13 escenarios (a la vez y de a turnos, en el orden de una semilla y en procesos simultáneos) audita que ninguna decisión se pierda ni quede a nombre de otro. Lo que encontró ya no pasa: un clon recién hecho puede trabajar, dos clones no generan el mismo ID, escribir a la vez no obliga a repetir, el registro de un cambio editado en dos ramas se une solo (lo que las dos decidieron distinto lo elige una persona con `decidir-union`), `resumen.md` y `kb/` se rehacen después de integrar, y la hora de cada evento lleva microsegundos con un orden determinista entre ramas.
- **Para agentes.** `oracle-factory --proyecto RUTA mcp` sirve el proyecto por MCP, de sólo lectura (`preguntar`, `estado`, `buscar`, `por_que`, `resumen`, `log`, `listar`). `oracle-factory agentes` escribe en `AGENTS.md` la guía para agentes desde la CLI (quién decide qué según el modo, los comandos de una persona y de un agente) y `--verificar` la mantiene al día. Una decisión de persona nunca la toma un agente, aunque corra en una terminal.
- **Más.** El checkout de un revisor es un clon aparte que no toca el repositorio; `aprobar-spec` se niega ante una spec de otra capacidad, `importar` no deja requisitos huérfanos y `estado` avisa un requisito que quedó sin medir. La extensión de VS Code pasa a 0.5.0 («Factory: Preguntar al proyecto»; se arma con `python3 editores/vscode/empaquetar.py`).
- Factory sigue con Oracle 0.39.0, Oracle Task 0.2.0 y Oracle Clue 0.1.0a2. La revisión independiente de cada cambio la hicieron Codex (GPT) y Agy (Gemini), lanzados a la vez con `pedir-revision`. Python >=3.11. Verificado en Linux.

```bash
uv publish dist/oracle_factory-0.1.0a13-py3-none-any.whl dist/oracle_factory-0.1.0a13.tar.gz
```

# Oracle Factory 0.1.0a12

- **Hechos de varios sensores.** `juzgar` acepta `--con` repetido, un archivo por sensor, y Oracle 0.39.0 los juzga juntos: un candidato integrado ya no necesita combinar los hechos de cada frente a mano. El registro guarda cada archivo con su huella (con uno solo, el registro de siempre); si cualquiera cambia, falta o no es una ruta, el juicio deja de valer, `estado` lo nombra y el próximo paso repite el juicio con todos los `--con`. Si dos sensores emiten la misma relación, Oracle lo rechaza nombrando la relación y los dos archivos, y Factory no registra veredicto.
- **Una portada viva.** La web pasó a pixel art: cada sección tiene una escena que se anima al llegar, el elenco (vos, el agente, codex, agy, Oracle y Clue) dice qué hace cada uno, y un minijuego deja decidir como persona con las reglas de la CLI —no se aprueba con un hallazgo medio abierto, un riesgo aceptado lleva su motivo, sin medidas acordadas no hay juicio—. Con teclado, con movimiento reducido no se anima nada, y no desborda de 320 a 1440 px. Esconde tres secretos.
- Factory fija **Oracle 0.39.0** (antes 0.38.2); Oracle Task sigue en 0.2.0 y Oracle Clue en 0.1.0a2. La revisión independiente de cada cambio la hicieron Codex (GPT) y Agy (Gemini), lanzados a la vez con `pedir-revision`. Python >=3.11. Verificado en Linux.

# Oracle Factory 0.1.0a11

- **Extensión de VS Code.** `editores/vscode/` agrega una vista «Factory» al explorador: los cambios abiertos, sus requisitos (medidas, decisión y veredicto), su revisión, sus artefactos (un clic abre cada archivo; una carpeta del candidato se muestra en el explorador; lo que falta o no es válido aparece marcado) y el próximo paso. El botón de terminal escribe el comando sin ejecutarlo: la decisión sigue en el menú de la CLI. Usa `.venv/bin/oracle-factory` del proyecto o el del `PATH`, sólo corre en espacios de trabajo de confianza y se arma sin `npm` con `python3 editores/vscode/empaquetar.py`. Está en el repositorio, no en el paquete de PyPI.
- **Un intento de revisión que no se registró queda a la vista.** Si `revisar` corta después de mostrar la revisión sin registrarla (un Aprobar no disponible, Cancelar, la entrada que se cierra), el registro guarda `revision_cancelada` con la causa y el candidato, y `estado` (también `--json`, en `avisos`) lo dice hasta que se registre una revisión.
- **Dos procesos no se pisan el registro.** `guardar` compara con lo último que el proceso leyó o escribió de `factory.json`, y comparar y reemplazar pasan bajo un bloqueo: una escritura concurrente se rechaza en vez de perderse.
- **Un valor del registro que no es una ruta se informa.** Un informe, unas decisiones o unos hechos que no son texto (un número, una lista, `""`) ya no hacen caer `estado` ni `resumen`: aparecen como pendiente «… no válido en el registro» y el próximo paso rehace la revisión o el juicio.

# Oracle Factory 0.1.0a10

- **El proyecto Oracle puede estar en una carpeta.** Un repositorio que ya tiene su proyecto Oracle en, por ejemplo, `medidas/` lo adopta con `oracle-factory init --oracle medidas`, que guarda `"oracle": "medidas"` en `.factory/config.json` sin crear nada de Oracle en la raíz. Factory importa, mide, juzga, abandona, lista (`donde`) y busca los requisitos ahí. Una carpeta absoluta, que sale del proyecto o sin `oracle.json` se rechaza con la causa. Con `"confiar_escalares": true`, Factory corre Oracle con `--confiar-escalares` y carga el catálogo con los escalares y las macros del proyecto, como `oracle cobertura`.
- **Vueltas de revisión proporcionales.** `pedir-revision` cuenta los hallazgos por severidad y sólo un medio o más sin aceptar pide otra vuelta; `estado` ofrece también `revisar` para aceptarlos o descartarlos con motivo. Los riesgos aceptados persisten entre vueltas y van en el pedido al revisor; `revisar` reconoce uno ya aceptado. Un informe sin severidad no se guarda ni se usa.
- **Revisores a la vez y paquete sin registros.** Varios `pedir-revision` del mismo candidato se turnan sólo en lo corto (checkout, número del paquete, evento) y el revisor corre sin esperar. El paquete de Clue deja fuera `.factory/`, `tareas/` y todo lo que no es producto (Oracle Clue 0.1.0a2, `preparar --excluir`).
- **Trazabilidad.** `oracle-factory trazabilidad ID` cruza cada requisito con los casos que lo prueban y con las líneas que cambió el candidato, y nombra las que no tienen respaldo.
- **JSON.** `estado`, `donde` y `resumen` con `--json` y esquema versionado (`oracle-factory.estado/1`, `.donde/1`, `.resumen/1`); `estado --json` trae también las `alternativas` del próximo paso.
- **Una medida confirmada cuyo catálogo cambia vuelve a pedir decisión.** La decisión y la propuesta guardan la huella del archivo de cada medida; si cambia, falta o no se puede leer, `estado` lo nombra y `juzgar` no la usa.
- **`abandonar`**, decidido por una persona con motivo, y un **`buscar`** que no recorre la evidencia ni los paquetes de Clue.
- **CLI:** la plantilla de `nuevo` trae `## ADDED Requirements` y `Tipo: funcional`; `medir` dice qué medidas reemplaza y cuáles quedan sin requisito; `medir --listar` separa las del proyecto de las del catálogo base de Oracle.
- **Docs y web:** los modos de trabajo y quién decide qué, en `docs/modos.md` y `site/modos.html`, con la tabla comprobada contra el código.
- La revisión independiente de cada cambio la hicieron Codex (GPT) y Agy (Gemini), lanzados a la vez con `pedir-revision`. Oracle sube a 0.38.2; Oracle Task sigue en 0.2.0 y Oracle Clue en 0.1.0a2. Python >=3.11. Verificado en Linux.

```bash
uv publish dist/oracle_factory-0.1.0a10-py3-none-any.whl dist/oracle_factory-0.1.0a10.tar.gz
```

La evidencia de cada cambio está en su tarea y en `.factory/cambios/`.

# Oracle Factory 0.1.0a9

- **Oracle Clue viene con Factory.** `oracle-clue==0.1.0a1` es dependencia fija, como `oracle-metalenguaje` y `oracle-task`. Factory lo usa desde su propio entorno, no del `PATH`. Si le falta esa distribución, da un error que dice cómo reinstalar. La instalación documentada expone también el comando `oracle-clue` (`--with-executables-from oracle-metalenguaje,oracle-task,oracle-clue`), para que quien revisa pueda correr `oracle-clue validar` a mano.
- **Todo informe de revisor se valida.** Ya no hay informes «sin validar». Un informe ilegible, que no es un objeto JSON, de otro candidato o que no se puede validar (porque le falta el paquete o el checkout) se avisa y no se usa.
- **El informe más nuevo de cada revisor reemplaza a los anteriores.** Con `codex-1.json` y `codex-2.json` en un mismo candidato cuenta el 2, aunque no se pueda usar; los anteriores quedan como vueltas registradas.
- **El menú de la decisión en `revisar` mantiene sus números.** «Aprobar» es siempre la 1. Cuando no se puede aprobar, dice por qué, y elegirla no registra nada. Antes, la opción 1 pasaba a ser «Pedir cambios».
- **`importar` deja afuera lo que la spec retira.** Los requisitos de `## REMOVED Requirements` no se importan ni necesitan tipo; se retiran de la spec consolidada al cerrar.
- La revisión independiente la hicieron Codex (GPT) y Agy (Gemini) en 7 vueltas lanzadas con `pedir-revision`. Oracle sigue en 0.38.1 y Oracle Task en 0.2.0. Python >=3.11. Verificado en Linux.

```bash
uv publish dist/oracle_factory-0.1.0a9-py3-none-any.whl dist/oracle_factory-0.1.0a9.tar.gz
```

La evidencia está en la tarea del cambio `20261012-131420-clue-dependencia`.

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
