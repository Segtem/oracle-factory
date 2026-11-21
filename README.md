# Oracle Factory — 0.1.0a20 (alpha)

Oracle Factory coordina a personas y agentes para producir software con dirección humana: desde una necesidad aceptada
hasta código, pruebas, revisión y entrega. Cada cambio tiene su acuerdo (propuesta y spec en formato **OpenSpec**), su
tarea (**Oracle Task**), requisitos medidos con evidencia (**Oracle**) y revisiones independientes validadas con
**Oracle Clue**. La persona decide el alcance, resuelve los hallazgos y acepta la entrega; los agentes trabajan, proponen
y quedan registrados como agentes. Los hechos que juzga Oracle los produce el sensor del proyecto: con `oracle-factory evidencia`,
Factory lo corre sobre un checkout limpio del commit y registra lo que dio, así `juzgar` dice si los hechos salieron de ahí o los
declaró alguien a mano. El sensor sigue siendo código del proyecto, escrito por quien trabaja: no es una medida independiente.

La 0.1.0a20 incorpora firmas SSH para decisiones de persona, verifica también los abandonos y conserva con una base
explícita las decisiones anteriores a la activación de firmas. Está publicada en PyPI y en
[GitHub](https://github.com/Segtem/oracle-factory/releases/tag/v0.1.0a20).

Es una CLI local con un flujo visible en Git, una extensión de VS Code con un tablero de comando, y un servidor MCP para que un agente consulte el
proyecto sin cambiar nada versionado (`preguntar` escribe su caché local). No empuja el producto ni publica ramas: sólo `sincronizar`, corrido por una persona, sube el almacén de registros. El código y las
pruebas del producto los escribe quien trabaja (una persona o un agente); Factory registra qué se acordó, quién decidió
qué y qué evidencia lo respalda.

Las guías:

- [Instalar el kit y la extensión de VS Code](docs/instalacion.md): CLI sola o kit completo, versión, conflictos y VSIX descargable.
- [Construir Buscaminas desde cero](docs/tutorial-buscaminas.md): un juego de terminal con pruebas, sensor, revisión y cierre, paso a paso.
- [Tres ejemplos cortos](docs/ejemplos-cortos.md): precio, CSV y ayuda para ver qué aporta Factory a cambios distintos.
- [Modos de trabajo](docs/modos.md): quién decide qué en `confirmacion`, `funcional` y `autonomo`.
- [El tablero y el trabajo de a dos](docs/tablero.md): la extensión de VS Code, quién trabaja en qué, Live Share e integrar sin chocar.
- [El conocimiento del proyecto](docs/conocimiento.md): el vault `kb/`, `por-que` y `preguntar`.
- [Trabajar con agentes](docs/agentes.md): `--agente`, la guía de `AGENTS.md`, el MCP y los revisores.
- [Revisión guiada](docs/revision-guiada.md): pedir revisiones, preparar el informe y decidir los hallazgos.
- [Colaboración](docs/colaboracion.md): dos personas con sus agentes, del reparto a la integración, con el banco que lo prueba.
- [La procedencia de las dependencias](docs/procedencia.md): el inventario CycloneDX que `procedencia ID` guarda en el candidato, quién usó una dependencia y la auditoría contra avisos OSV.
- [Dónde está cada cosa](docs/estructura.md) y [trazabilidad](docs/trazabilidad.md).


## Instalación

Versión publicada en PyPI: `oracle-factory==0.1.0a20`. Con `uv`:

```bash
uv python install 3.13
uv tool install --python 3.13 oracle-factory==0.1.0a20
uv tool update-shell
oracle-factory --version
oracle-factory --proyecto ./mi-proyecto init
oracle-factory --proyecto ./mi-proyecto nuevo --con-ejemplo notas "Comprobar el título de una nota"
```

Si querés exponer también los comandos de Oracle, Oracle Task y Oracle Clue desde el entorno de Factory:

```bash
uv tool install --python 3.13 --with-executables-from oracle-metalenguaje,oracle-task,oracle-clue oracle-factory==0.1.0a20
```

Factory usa sus dependencias (`oracle-metalenguaje 0.39.0`, `oracle-task 0.2.0` y `oracle-clue 0.1.0a2`) desde su entorno
aislado. Python 3.11 o posterior y Git. `--proyecto` va antes del subcomando; sin esa opción se usa la carpeta actual.
La [guía de instalación](docs/instalacion.md) explica cómo comprobar las cuatro versiones, resolver conflictos de ejecutables, actualizar una versión fijada e instalar el tablero de VS Code sin clonar Factory.

`init` crea la estructura de Oracle, Oracle Task y OpenSpec, la carpeta `.factory/`, los hooks de Git y la guía para
agentes de `AGENTS.md`; agrega al `.gitignore` lo local (`.factory/local/`, `__pycache__/`, `*.py[cod]`) sin sobrescribir
la configuración existente, y no crea commits ni aprobaciones. Un proyecto creado con una versión anterior sigue
funcionando; `oracle-factory migrar` pasa su estado a `.factory/`.

La [guía desde cero](https://segtem.github.io/oracle-factory/desde-cero.html) recorre el ejemplo de notas en un proyecto
vacío sin clonar Factory.


## El flujo de un cambio

```bash
oracle-factory init
oracle-factory nuevo --con-ejemplo notas "Comprobar el título de una nota"
oracle-factory listar                      # el ID completo y la fase de cada cambio
oracle-factory aprobar-spec <id>
oracle-factory importar <id>
oracle-factory medir <id> --listar
oracle-factory medir <id> --requisito <id-requisito> --medida notas.casos_ejecutados --medida notas.resultados --quitar-sin-medir
```

1. `nuevo` crea la tarea y el paquete OpenSpec del cambio (`--con-ejemplo notas` trae el ejemplo entero; `--capacidad
   <slug> --sufijo <s>` una plantilla en blanco). Una persona revisa la propuesta y la spec y la aprueba con
   `aprobar-spec`, eligiendo en un menú; un agente puede proponerla con `--agente`.
2. `importar` pasa los requisitos a Oracle: nacen **sin medir**. `medir --listar` muestra las medidas disponibles y
   `medir --requisito … --medida …` las asocia (un agente las propone; una persona las confirma con `medir <id>
   --confirmar`).
3. Se implementa y se prueba por fuera de Factory. El sensor del proyecto deja la evidencia en la carpeta del candidato
   (`oracle-factory ruta <id> evidencia`).
4. `pedir-revision <id> --a REVISOR` lanza un revisor configurado y valida su informe con Clue; `revisar <id>` registra la
   revisión paso a paso, decidiendo cada hallazgo ([revisión guiada](docs/revision-guiada.md)).
5. `juzgar <id>` exige cobertura de todos los requisitos y corre Oracle sobre la evidencia (`--con` repetido, un archivo
   por sensor). Un «sin juicio» no habilita el cierre.
6. `cerrar <id>` exige spec, importación, revisión sin hallazgos abiertos y juicio verde, todos vigentes; la persona
   confirma en el menú. La spec del cambio se fusiona en `openspec/specs/`.

Un cambio que no se va a terminar se abandona con `oracle-factory abandonar <id>` (lo decide una persona y elige el
motivo; un agente lo propone con `--agente … abandonar <id> --motivo "…"`): sus requisitos salen de `requisitos/` y nada se
fusiona. `oracle-factory modo <id> MODO` cambia el modo de trabajo de un cambio (bajar la intervención es de una persona).

En todo momento, `oracle-factory estado <id>` dice qué falta y calcula el próximo paso; en una terminal ofrece ejecutarlo.
`estado`, `donde` y `resumen` tienen `--json` con esquema versionado para un IDE, un panel o un agente
([estructura](docs/estructura.md#salidas-en-json)).

Para copiar sólo el programa de ejemplo a una carpeta nueva, usá `oracle-factory ejemplo notas --destino ./ejemplo-notas`.


## Las herramientas

**El tablero de comando.** La extensión de VS Code (`editores/vscode/`, 0.5.0) muestra los cambios abiertos y abre un
tablero con lo que te necesita, la línea de tiempo de cada cambio con quién decidió qué, los hallazgos, los commits y las
métricas; lo arma `oracle-factory tablero --json`. Con Live Share, el tablero se comparte y cada cambio tiene su chat
(`oracle-factory mensaje`). Ver [el tablero y el trabajo de a dos](docs/tablero.md).

**Quién trabaja en qué y cada commit con su cambio.** `oracle-factory tomar <id> --con claude-code` te registra como
responsable con tu agente (`--relevo` si lo tenía otra persona; `soltar` lo libera). Los hooks que instala `init` (o
`oracle-factory hooks`) agregan `Cambio: <ID>` a cada commit, y `oracle-factory log <id>` lista los commits de un cambio.
Ver [quién trabaja en qué y los commits](docs/tablero.md#quién-trabaja-en-qué).

**Integrar sin chocar.** El registro de un cambio editado en dos ramas se une solo al integrar; lo que las dos
decidieron distinto lo elige una persona con `oracle-factory decidir-union`, y `resumen.md` y `kb/` se rehacen después
del merge. Un banco de 13 escenarios con dos personas y sus agentes lo prueba ([colaboración](docs/colaboracion.md)).

**El conocimiento del proyecto.** `oracle-factory kb` genera `kb/` desde el registro (una nota por cambio y por
requisito) y lo rehace con cada decisión; las notas de personas vencen cuando cambian sus fuentes (`kb revisada`);
`por-que ARCHIVO:LÍNEA` va de una línea a su cambio; y `oracle-factory preguntar "¿por qué los IDs llevan letras al
azar?"` responde con los pasajes vigentes y su cita, por palabras, embeddings (Ollama local por defecto) y el grafo del vault. Ver [el conocimiento del proyecto](docs/conocimiento.md).

**Para agentes.** `oracle-factory agentes` escribe en `AGENTS.md` la guía para agentes, armada desde la CLI y verificada;
`oracle-factory --proyecto RUTA mcp` sirve el proyecto por MCP: no cambia nada versionado, pero `preguntar` escribe su caché local
y puede llamar al modelo configurado. Con `--agente`, un agente nunca queda registrado como persona; sin él, Factory no puede
saberlo. Ver [trabajar con agentes](docs/agentes.md).

**Revisión, trazabilidad y lo vigente.** `revision-preparar` arma el informe desde los de los revisores y `revision`
registra una revisión libre o guiada; `trazabilidad <id>` cruza cada requisito con las líneas que lo prueban;
`archivar` fusiona en `openspec/specs/` las specs de los cambios cerrados; `resumen` da el estado vigente en una lectura;
`donde`, `ruta` y `buscar` dicen dónde está cada cosa ([estructura](docs/estructura.md)).


## Alcance y límites

`preguntar` hace consultas al registro para cantidades y listados, y respuestas elaboradas con un modelo generativo configurado
explícitamente, con fuentes y herramientas de sólo lectura (JSON `oracle-factory.preguntar/2`). Sin modelo conserva las consultas
directas y la recuperación, indicando sus límites. Ver [preguntar al proyecto](docs/conocimiento.md#preguntar).

- Usa Oracle, Oracle Task y Oracle Clue instalados con Factory; no copia sus reglas.
- Factory corre el sensor del proyecto sólo con `oracle-factory evidencia` (sobre un checkout limpio del commit) y entonces
  registra la huella de lo que produjo; con hechos dejados a mano, `juzgar` y `estado` lo dicen («declarados»), y el proyecto puede
  exigir hechos de Factory para cerrar (`"sensor": {"hechos": "exigir"}` en `.factory/config.json`). Que el sensor mida lo que debe
  no lo comprueba nadie más que quien lo revisa: es código del proyecto. La evidencia de otro candidato no vale. La cobertura completa de una spec requiere criterio
  humano y medidas defendibles.
- Lanza los revisores que declara cada proyecto (`pedir-revision`), pero el revisor no decide: los hallazgos los resuelve
  una persona.
- Sin firmas, no autentica a nadie: una persona es un comando que corre en una terminal sin `--agente`, y los modos son un
  protocolo entre quienes trabajan juntos, no un control de acceso. Con `"firmas": "exigir"` en `.factory/config.json`, cada
  decisión de una persona se firma con su llave (una sólo para Factory, con frase) y `verificar`, `juzgar` y `cerrar` no cuentan
  una sin firma válida de `.factory-firmantes`. No cubre a otro proceso del mismo usuario que lea la memoria de `ssh-keygen` ni un
  registrador de teclas. Ver [firmas](docs/firmas.md).
- No empuja el producto ni publica ramas; `sincronizar`, corrido por una persona, sube el almacén de registros. Verificado en Linux; los comandos para Windows y macOS se revisaron pero no tienen
  ejecución automatizada.


## Vigencia de la evidencia

Antes de registrar la revisión, se terminan los cambios y se commitea el producto. Factory guarda HEAD y una huella de
los archivos del producto (versionados y nuevos no ignorados; sin `.factory/`, `tareas/` ni lo que genera). Si cambia el
código, la spec o las medidas, hay que repetir la revisión y el juicio; si cambia sólo la evidencia, vence el juicio y la
revisión sigue vigente. Un commit que sólo toca registros no invalida: `estado` avisa cuando el HEAD es otro con el mismo producto. Lo que Git ignora queda fuera de la huella: `estado` avisa
de cada archivo de código o configuración ignorado dentro del producto, porque puede cambiar el comportamiento sin vencer nada.
Los submódulos no están soportados.

### Factory produce los hechos

El proyecto declara su sensor en `.factory/config.json` y `oracle-factory evidencia ID` lo corre sobre un checkout limpio del
commit (sin remoto, en una carpeta temporal del sistema, fuera del producto y del almacén, que se borra al terminar), con su tope y deteniendo a todo su grupo de procesos si
vence. Se niega si el producto tiene cambios sin commitear. Los hechos quedan en la carpeta de evidencia del candidato y la corrida,
en el registro del cambio (`evidencia_producida`: comando, commit, código, huella de los hechos, quién).

```json
"sensor": {"comando": ["{python}", "tools/sensor.py", "--salida", "{salida}"], "tope_minutos": 60, "hechos": "avisar"}
```

Los marcadores del comando: `{python}` (el Python de Factory), `{cambio}`, `{salida}` (la carpeta de evidencia, que el sensor crea y
donde deja `hechos.json`), `{registros}` (dónde están los registros) y `{producto}` (la carpeta del producto, para lo que no se
versiona, como `node_modules`). `evidencia` no acepta argumentos para el sensor: corre exactamente el comando aprobado, y con un entorno mínimo (un `PATH` fijo con
las carpetas del sistema, la del Python de Factory y `~/.local/bin`; el `HOME` del usuario; el idioma y la carpeta temporal): nada del
entorno de quien lo corre, como `PYTHONPATH` o `LD_PRELOAD`, llega al sensor. En el checkout,
`almacenes.registros_de` devuelve los registros del proyecto aunque el checkout no esté conectado al almacén. Con `"hechos": "exigir"`,
`cerrar` se niega si los hechos del veredicto no los produjo Factory para el candidato vigente, en una corrida que terminó bien (una
que falló o se pasó del tope queda registrada, pero no respalda sus hechos); con `"avisar"` (el valor por defecto), sólo se avisa.

**El sensor lo aprueba una persona.** `oracle-factory aprobar-sensor` (sólo una persona desde su terminal; con `--agente` se niega)
muestra la declaración vigente y la última aprobada, y registra en `.factory/sensor-aprobado.json` su huella, quién la aprobó y
cuándo. `oracle-factory evidencia` se niega a correr un sensor que no esté entre los aprobados (nunca se aprobó, o alguien cambió su
comando), y sólo los hechos de un sensor aprobado cuentan como «producidos por Factory». Cada producción registra la huella del sensor
con que se hizo. **Límite:** con `"firmas": "exigir"`, la aprobación del sensor lleva una firma verificable, pero cada
ejecución del sensor no tiene firma propia; sin esa opción, quien edita el registro puede fingir una aprobación. Cambiar el sensor
ya no alcanza con editar la configuración. Por la misma razón, un proceso del mismo usuario que
esté corriendo a la vez puede modificar el checkout temporal antes de que corra el sensor: Factory se protege de lo que llega por la
configuración o el entorno, no de otro programa con los mismos permisos.

La preparación de la revisión no da por buena una evidencia que se contradice: si `resultado.json` dice `exitoso` y a la vez cero
pruebas, fuentes que cambiaron, otro commit o artefactos con otro hash, la comprobación queda «falla» y nombra la contradicción.
Si sólo trae `exitoso`, el informe dice que el éxito lo declara el sensor y Factory no pudo comprobarlo.

Renovar la aprobación de la spec invalida la importación, la revisión y el veredicto anteriores; otra asociación de
medidas invalida la revisión y el juicio, y una decisión de medidas deja de valer si cambia el archivo de alguna de sus
medidas.


## Pruebas

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests </dev/null
```

La suite incluye regresiones con Git real y la integración completa (tarea, importación, evidencia insuficiente, juicio y
cierre); sus aprobaciones son fixtures. `python3 tools/docs_al_dia.py` comprueba que esta documentación nombre cada
comando de la CLI, sólo comandos que existen y la versión de `pyproject.toml`.


## Web

**[Abrir la web](https://segtem.github.io/oracle-factory/) · [Guía desde cero](https://segtem.github.io/oracle-factory/desde-cero.html)**

La [portada](site/index.html) compara vibe coding, el ciclo de desarrollo, el trabajo guiado por especificaciones y
Oracle Factory con un mismo ejemplo, en pixel art y con un minijuego para decidir como persona. Es una demostración en el navegador: la página no corre nada ni registra aprobaciones. GitHub Actions publica `site/` en GitHub Pages desde `main`; localmente,
`python3 -m http.server 8765 --directory site`. Para comprobarla en Chromium: `npm install --no-save
--package-lock=false playwright@1.62.1` y `node tests/test_site.cjs` (la portada viva: `node tests/test_web_viva.cjs`;
el minijuego, sin navegador: `node tests/test_juego.cjs`).


## Historial de versiones

La versión publicada anterior es [0.1.0a19](https://github.com/Segtem/oracle-factory/releases/tag/v0.1.0a19) (en PyPI como `oracle-factory==0.1.0a19`); la 0.1.0a18 trajo `verificar` para CI y los despliegues con prueba, la 0.1.0a17 trajo la puerta antes de publicar y el camino ligero, la 0.1.0a16 trajo la procedencia de las dependencias y los avisos de OSV, la 0.1.0a15 trajo el tablero que dice qué hacer y los bloqueos que nombran su causa, la 0.1.0a14 trajo la distribución verificable y las consultas del proyecto, la 0.1.0a13 trajo el tablero de comando y el conocimiento del proyecto, la 0.1.0a12 agregó la portada viva y la 0.1.0a9 incorporó Oracle Clue. Lo que trajo cada versión está en [NOTAS-DE-RELEASE.md](NOTAS-DE-RELEASE.md).
