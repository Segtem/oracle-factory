# Oracle Factory — 0.1.0a12 (alpha)

La visión de Oracle Factory es coordinar agentes y herramientas para producir software completo: desde una necesidad aceptada hasta código, pruebas, revisión y entrega. La persona decide el alcance, resuelve hallazgos y acepta la entrega.

Hoy existe una POC de CLI: genera documentos con formato **OpenSpec**, usa **oracle-task** para tareas e importa requisitos y evalúa evidencia con **Oracle**. La implementación del producto y las pruebas se ejecutan por fuera de la CLI. Recibe informes manuales de revisión; **Oracle Clue** prepara contexto y valida informes externos en su primer alpha; el análisis con IA sigue pendiente y CodeRabbit es una alternativa externa.

Es una CLI local y un flujo visible en Git. No hace commits ni publica ramas por cuenta propia. La aprobación de alcance, la resolución de hallazgos y el cierre son acciones humanas.

Para saber quién decide qué en cada modo de trabajo (`confirmacion`, `funcional`, `autonomo`) y cómo leerlo en `estado`, consultá [los modos de trabajo](docs/modos.md).

Para saber dónde está cada cosa y cómo encontrarla (`donde`, `ruta`, `buscar`), consultá la [estructura de carpetas](docs/estructura.md).

Para trabajar entre dos personas con sus agentes, consultá la [guía de colaboración](docs/colaboracion.md): reparto, checkouts separados, relevos, revisión con Clue e integración con evidencia vigente. Incluye plantillas y una demostración local; las asignaciones son acuerdos humanos y el piloto con personas se registra por separado.

La [revisión guiada](docs/revision-guiada.md) prepara informes pendientes, separa decisiones y calcula hallazgos abiertos. El formato libre sigue disponible y exige `--hallazgos-abiertos` explícito al registrarlo.


## Instalación del corte alpha

El corte alpha 0.1.0a12 trae una portada nueva en pixel art —escenas que se animan al llegar, el elenco de la fábrica y un minijuego para decidir como persona con las reglas de la CLI— y `juzgar --con` repetido, un archivo de hechos por sensor, con Oracle 0.39.0: dos sensores que emiten la misma relación no dejan veredicto. La 0.1.0a11 trajo la extensión de VS Code (`editores/vscode/`, en el repositorio: una vista con los cambios abiertos, sus requisitos, revisión, veredicto y artefactos, y el próximo paso escrito en la terminal sin ejecutarlo); hace que `revisar` deje constancia de un intento cortado sin registrar, que `estado` avisa con su causa; que dos procesos que escriben el mismo registro no se pisen; y que un valor del registro que no es una ruta se informe como pendiente en vez de hacer caer `estado` y `resumen`. La 0.1.0a10 abrió Factory a proyectos que ya tienen su proyecto Oracle en una carpeta (`"oracle": "medidas"` en `.factory/config.json`, `init --oracle`, y `confiar_escalares` para sus escalares) y fijó Oracle 0.38.2. Trajo vueltas de revisión proporcionales a la severidad, con riesgos aceptados que persisten y revisores que se pueden lanzar a la vez sobre un paquete sin los registros de Factory; la trazabilidad de cada requisito a sus casos y a las líneas que cambió el candidato (`trazabilidad`); `estado`, `donde` y `resumen` en JSON; `abandonar`; que una medida confirmada vuelva a pedir decisión si cambia su catálogo; y los modos de trabajo explicados en `docs/modos.md` y en el sitio. La 0.1.0a9 trajo Oracle Clue como dependencia fija: se instala con Factory, que lo usa desde su propio entorno, y todo informe de revisor se valida (ya no hay informes «sin validar»). Además, el informe más nuevo de cada revisor reemplaza a los anteriores, el menú de la decisión en `revisar` mantiene sus números y dice por qué no se puede aprobar, e `importar` deja afuera los requisitos que la spec retira. La 0.1.0a8 hizo la CLI cómoda para la persona: `oracle-factory estado ID` calcula el próximo paso según lo que está vigente (spec, medidas, revisión, juicio, cierre, o qué archivo recuperar) y en una terminal ofrece ejecutarlo; los errores nombran su causa y cómo seguir; `resumen --ver` muestra el resumen con formato; y en un clon, `python fabrica.py` usa solo el `.venv`. La 0.1.0a7 trajo las decisiones guiadas: cada decisión de una persona se toma en un menú de opciones en vez de tipear una frase; `oracle-factory revisar` registra la revisión paso a paso, con un motivo que se elige (el del agente, uno armado con los datos del cambio o uno propio); y `medir --confirmar` confirma de una vez las medidas propuestas. Suma también `pedir-revision`, que lanza un revisor configurado, valida su informe con Oracle Clue y lo guarda en el candidato. La 0.1.0a6 trajo el resumen del estado actual (`oracle-factory resumen`) y `nuevo --sufijo`; la 0.1.0a5 trajo la spec consolidada por capacidad (`openspec/specs/`, `archivar`) y la 0.1.0a4 los modos de trabajo, la revisión guiada, la vigencia por contenido, la portabilidad y la carpeta `.factory/` con `donde`, `ruta`, `buscar` y `migrar` (ver [NOTAS-DE-RELEASE.md](NOTAS-DE-RELEASE.md)).

Está publicado en PyPI como `oracle-factory==0.1.0a12` y su wheel, con los hashes, en el [release de GitHub v0.1.0a12](https://github.com/Segtem/oracle-factory/releases/tag/v0.1.0a12). Un proyecto creado con una versión anterior sigue funcionando; `oracle-factory migrar` pasa su estado a `.factory/`.

Para instalarlo con `uv`:

```bash
uv tool install --python 3.13 --with-executables-from oracle-metalenguaje,oracle-task,oracle-clue oracle-factory==0.1.0a12
uv tool update-shell
oracle-factory --version
oracle-factory --proyecto ./mi-proyecto init
oracle-factory --proyecto ./mi-proyecto nuevo --con-ejemplo notas "Comprobar el título de una nota"
```

Si uv advierte sobre conflicto porque los ejecutables `oracle`, `tasks` u `oracle-clue` ya están instalados en tu sistema, podés instalarlo sin `--with-executables-from`:

```bash
uv tool install --python 3.13 oracle-factory==0.1.0a12
```

Factory utiliza sus dependencias internas (`oracle-metalenguaje 0.39.0`, `oracle-task 0.2.0` y `oracle-clue 0.1.0a2`) desde su entorno aislado y no requiere exponer sus binarios en el PATH global para operar.

`--proyecto` se coloca antes del subcomando; sin esa opción se usa la carpeta actual. `init` crea la estructura de Oracle, Oracle Task y OpenSpec, añade ignores para `.factory/local/` (lo local de Factory), `__pycache__/` y `*.py[cod]` sin sobrescribir configuración existente y no crea commits ni aprobaciones. Git debe estar instalado. Python 3.11 o posterior.

Los archivos indicados con `--informe` y `--con` se interpretan desde el proyecto seleccionado; también aceptan rutas absolutas.

La [guía desde cero](https://segtem.github.io/oracle-factory/desde-cero.html) recorre el ejemplo de notas en un proyecto vacío sin clonar Factory. Para desarrollo desde el checkout, `python3 fabrica.py` conserva la misma interfaz y selección de proyecto.

El [release de GitHub](https://github.com/Segtem/oracle-factory/releases/tag/v0.1.0a12) conserva los artefactos y sus hashes. El paquete sigue siendo experimental: no coordina agentes automáticamente ni integra todavía Clue.


## Flujo de la POC

1. `oracle-factory init`: inicializa Oracle, tareas y acuerdos; añade entradas necesarias a `.gitignore` sin sobrescribir la configuración del usuario. Los mensajes siguientes provienen de Factory.
2. `oracle-factory nuevo --con-ejemplo notas "<pedido>"`: crea la tarea y el paquete OpenSpec copiando el ejemplo entero a `examples/notas`, la propuesta y spec al cambio y las reglas a `catalogos/`. Verifica destinos antes de crear la tarea y rechaza destinos existentes sin sobrescribir archivos. (También está disponible `oracle-factory nuevo --capacidad <slug> "<pedido>"` para plantillas en blanco sin ejemplo).
3. `oracle-factory listar`: recupera únicamente los cambios de Factory del proyecto con su ID completo y fase actual.
4. `oracle-factory aprobar-spec <id>`: muestra la propuesta y la spec y pregunta con un menú; la persona elige la opción que aprueba escribiendo su número. El agente espera; no puede aceptar por la persona.
5. `oracle-factory importar <id>`: invoca al importador de Oracle. Los requisitos nuevos nacen **sin medir** y aislados por dominio para evitar herencias indebidas.
6. `oracle-factory medir <id> --listar`: muestra los requisitos importados del cambio y las medidas disponibles: primero las del proyecto, con sus límites y fuentes, y al final las del catálogo base de Oracle, una por línea. Al elegir, `medir` dice qué medidas reemplaza y cuáles quedan sin requisito.
   `oracle-factory medir <id> --requisito <id-requisito> --medida notas.casos_ejecutados --medida notas.resultados --quitar-sin-medir`: asocia medidas explícitamente sin edición manual de indentación. Conserva `sin_medir` por defecto; para retirarlo exige `--quitar-sin-medir` explícito (o `--sin-medir "alcance pendiente"` para cobertura parcial). Una asociación inválida no modifica archivos; modificar la asociación invalida la revisión y el juicio previos. Enlazar medidas no prueba pertinencia ni cumplimiento por sí mismo.
7. Implementar y probar: los tests y el sensor se ejecutan por fuera de Factory.
8. `oracle-factory revision <id> --informe <ruta> --revisor "<nombre>" --decision aprobar --hallazgos-abiertos 0`: registra la revisión humana y su decisión, vinculadas al commit de Git y a la huella de archivos del producto.
9. `oracle-factory juzgar <id> --con <hechos.json>`: exige cobertura completa de los requisitos importados y corre Oracle sobre la evidencia aportada por el sensor. Un exit code 0 con «sin juicio» o fallas en sombra no habilita el cierre.
10. `oracle-factory cerrar <id>`: exige que todos los gates (spec, importación, revisión sin hallazgos abiertos y juicio verde) estén completos y vigentes. La persona confirma eligiendo la opción de cerrar en el menú.

Un cambio que no se va a terminar se abandona con `oracle-factory abandonar <id>`. Lo decide una persona desde un menú, en cualquier modo, y elige el motivo (un agente puede proponerlo con `--agente … abandonar <id> --motivo "…"`). Pasa a la fase `abandonada`: sus `.requisito` salen de `requisitos/` (quedan en Git), su tarea se cierra con el motivo, nada se fusiona en `openspec/specs/`, y el resumen lo muestra aparte. También vale para una carpeta de `openspec/changes/` sin registro.

En todo momento se puede consultar el estado con `oracle-factory estado <id>`: dice qué falta y calcula el próximo paso (por ejemplo `medir <id> --confirmar`, `revisar <id>` o `cerrar <id>`); en una terminal ofrece ejecutarlo desde un menú. Sin terminal o con `--agente` sólo lo imprime. Para un IDE, un panel o un agente, `estado <id> --json`, `donde <id> --json` y `resumen --json` dan lo mismo como JSON con esquema versionado (`oracle-factory.estado/1`, `.donde/1`, `.resumen/1`), sin preguntar ni escribir nada; ver [docs/estructura.md](docs/estructura.md#salidas-en-json). Para revisar por promesa, `trazabilidad <id>` muestra qué líneas cambiadas del candidato ejecutan los casos de cada requisito y cuáles no respalda ninguno ([docs/trazabilidad.md](docs/trazabilidad.md)).

En un clon de Factory, `python fabrica.py estado <id>` usa el entorno del clon (`.venv`) aunque se lo llame con otro intérprete; con el entorno activado (`source .venv/bin/activate` en bash o zsh, `source .venv/bin/activate.fish` en fish) se usa directamente `oracle-factory estado <id>`.


## Ejemplo mínimo

En tu proyecto inicializado, creá un cambio con el ejemplo y aprobá la spec tras revisarla:

```bash
oracle-factory init
oracle-factory nuevo --con-ejemplo notas "Comprobar el título de una nota"
# Recuperar el ID impreso o con: oracle-factory listar
oracle-factory aprobar-spec <id>
oracle-factory importar <id>
oracle-factory medir <id> --listar
oracle-factory medir <id> --requisito <id-requisito> --medida notas.casos_ejecutados --medida notas.resultados --quitar-sin-medir
```

Si necesitás los comandos independientes `oracle`, `tasks` y `oracle-clue` (por ejemplo, para que un revisor valide su informe a mano con `oracle-clue validar`), usá la instalación con `--with-executables-from oracle-metalenguaje,oracle-task,oracle-clue`. Luego podés consultar `oracle cobertura --proyecto .`: hasta mapear todos los requisitos, Factory no acepta evidencia ni permite cerrar.


## Alcance y límites de esta POC

- Usa los comandos instalados de Oracle y oracle-task; no implementa copias de sus reglas.
- No instala ni invoca CodeRabbit. Recibe su informe exportado o pegado y hace explícita la decisión humana. El análisis con IA sigue pendiente y Clue en su primer alpha prepara contexto y valida informes externos.
- Oracle evalúa los hechos aportados; Factory no ejecuta el sensor ni certifica que ese JSON provenga de la versión actual. No lee el código para demostrar cualquier afirmación. La cobertura completa de una spec requiere criterio humano y medidas defendibles.
- No archiva automáticamente el cambio OpenSpec ni modifica código del producto. No realiza git push ni publicación de ramas.
- El flujo se verificó en Linux; los comandos para Windows y macOS fueron revisados pero no cuentan con ejecución automatizada completa en esos sistemas. Las guías no sustituyen la dirección de una persona competente.


## Preparación y vigencia de la evidencia

Usar Python 3, Git y las herramientas instaladas. La integración se probó con Oracle 0.39.0 y Oracle Task 0.2.0. No se requiere la CLI de OpenSpec para importar estas specs a Oracle; esta POC no valida el ciclo completo del CLI OpenSpec.

Antes de registrar la revisión, terminar los cambios y crear el commit del producto. La CLI guarda HEAD y una huella de archivos versionados y nuevos no ignorados. Si cambia el código, la spec, las medidas o la evidencia (la huella de archivos), repetir la revisión/juicio. Un commit que sólo toca registros de tareas no invalida: se guarda el commit revisado y `estado` avisa cuando el HEAD actual es otro con el producto idéntico. Los registros de tareas y los informes generados en el paquete no se incluyen en la huella del producto, pero los informes se verifican por hash propio. Los archivos ignorados y dependencias externas quedan fuera de esa huella; los submódulos no están soportados.

Renovar la aprobación de propuesta/spec invalida la importación, la revisión y el veredicto anteriores. Una asociación de medidas diferente invalida la revisión y el juicio. Una decisión de medidas también deja de valer si después cambia el archivo de alguna de sus medidas (umbral, filtro, alcance): `estado` la marca y se vuelve a decidir con `medir` y las mismas medidas. Las confirmaciones interactivas son un protocolo del operador: registran el usuario del sistema, sin autenticar de forma independiente a una persona.


## Pruebas

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v
```

La suite incluye regresiones con Git real y una integración temporal de creación de tarea, importación Oracle, rechazo de evidencia insuficiente, juicio y cierre. Las aprobaciones de esa prueba son fixtures; no aprueban ningún cambio real.


## Web y guía desde cero

**[Abrir la web](https://segtem.github.io/oracle-factory/) · [Guía desde cero](https://segtem.github.io/oracle-factory/desde-cero.html)**

La [portada interactiva](site/index.html) compara vibe coding, el ciclo de desarrollo, el trabajo guiado por especificaciones y Oracle Factory con un mismo ejemplo. El recorrido pixel art muestra las decisiones humanas y una vuelta de revisión, corrección y nuevas pruebas. Es una demostración visual; no ejecuta agentes ni registra aprobaciones reales.

La [guía desde cero](site/desde-cero.html) recorre el [ejemplo de notas](examples/notas) hasta el cierre local con inicio guiado y comando `medir`.

Para ver ambas páginas localmente:

```bash
python3 -m http.server 8765 --directory site
```

Abrir <http://localhost:8765>. También funcionan abriendo `site/index.html` sin conexión. El sitio no tiene dependencias externas en tiempo de ejecución. GitHub Actions publica `site/` en GitHub Pages desde `main`.

Para comprobar la web en Chromium, instalar la dependencia de desarrollo Playwright y ejecutar:

```bash
npm install --no-save --package-lock=false playwright@1.62.1
node tests/test_site.cjs
```

La portada viva (escenas, personajes, el minijuego y sus secretos) tiene su propia prueba por escenario: `node tests/test_web_viva.cjs recorrer_la_portada` (los nombres están en el archivo), y la máquina del minijuego se prueba sin navegador con `node tests/test_juego.cjs`. La prueba usa `/usr/bin/chromium` por defecto; se puede indicar otro ejecutable con la variable `CHROMIUM`. Comprueba los controles, las decisiones, el teclado, movimiento reducido, adaptación móvil, enlaces y funcionamiento sin red.


## Extensión de VS Code

[`editores/vscode/`](editores/vscode) agrega una vista «Factory» al explorador: los cambios abiertos, sus requisitos (medidas, decisión y veredicto), su revisión, sus artefactos (un clic los abre; el que falta aparece marcado) y el próximo paso. El botón de terminal **escribe** el comando en una terminal del proyecto sin ejecutarlo: la decisión se sigue tomando en el menú de la CLI. Usa `.venv/bin/oracle-factory` del proyecto si existe, si no `oracle-factory` del `PATH`, o la configuración de usuario `factory.comando`. Sólo corre en espacios de trabajo de confianza. El botón de tablero (o *Factory: Abrir el tablero*) abre el **tablero de comando**: por cada cambio abierto, lo que necesita tu decisión con su comando, los hallazgos de los revisores (un clic abre `archivo:línea`), los requisitos con sus medidas, sus commits (un clic abre el diff), los avisos, la línea de tiempo y las métricas del cambio y del proyecto; se rehace solo cuando cambia un registro. Lo arma `oracle-factory tablero --json`.

**Commits unidos a su cambio.** `init` (o `oracle-factory hooks`, en un proyecto que ya existía) instala los hooks de Git `prepare-commit-msg` y `commit-msg`, que agregan `Cambio: <ID>` a cada commit: el cambio que nombra el mensaje (un merge «Integrar <ID>»), si no el único abierto, y con varios abiertos el que tomaste (también si el mensaje se escribe en el editor; cerrarlo vacío sigue abortando el commit); si ya tenés uno propio no lo toca y te dice la línea para encadenarlo, y nunca impiden un commit. `oracle-factory log ID` (o `--json`) lista los commits del cambio: los que llevan su trailer y, para los de antes, los que se deducen de sus candidatos y del merge que los integró. `estado` dice cuántos tiene y el último.

**Quién trabaja en qué.** `oracle-factory tomar ID --con claude-code` te registra como responsable del cambio, con el agente con el que trabajás; si otra persona ya lo tiene, hace falta `--relevo` (queda constancia de quién lo tenía), y `soltar ID` lo libera. Un agente que corre `--agente NOMBRE tomar ID` se suma al cambio sin quedar como responsable. Es un acuerdo registrado, no un candado. `estado` y el tablero muestran, por cambio, la persona responsable, sus agentes (los declarados y los que actuaron en las últimas 24 horas, con su última acción) y los revisores en curso; el tablero muestra también quién está en qué en todo el proyecto.

**De a dos, con Live Share.** Con la extensión [Live Share](https://marketplace.visualstudio.com/items?itemName=MS-vsliveshare.vsliveshare) en una sesión, el tablero (extensión 0.3.0) muestra quién está conectado y con qué rol. Quien comparte publica su tablero: un invitado con la extensión lo ve aunque no tenga la CLI de Factory ni el proyecto, se rehace cuando cambia un registro, sus enlaces abren los archivos compartidos y el botón de un comando lo escribe, sin Enter, en la terminal «Factory» de quien comparte. Cada cambio tiene un chat; los mensajes quedan en su registro con el nombre que da Live Share y quién los guardó (no escribas secretos: se versionan). Factory no autentica a nadie: quien comparte sólo acepta el nombre de un invitado conectado, y con varios invitados uno podría usar el de otro. Desde la terminal, `oracle-factory mensaje ID "texto"` deja un mensaje como persona o, con `--agente`, como agente. Sin Live Share el tablero sigue igual. Los botones del tablero manejan la sesión aunque no veas la barra de estado: «Instalar Live Share», «Compartir sesión» (Live Share copia el enlace), «Unirse a una sesión» (pide el enlace), «Terminar sesión» y «Salir de la sesión».

Se arma sin `npm`:

```bash
python3 editores/vscode/empaquetar.py
code --install-extension editores/vscode/oracle-factory-0.3.1.vsix
```
