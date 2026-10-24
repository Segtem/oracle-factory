# Oracle Factory — 0.1.0a13 (alpha)

Oracle Factory coordina a personas y agentes para producir software con dirección humana: desde una necesidad aceptada
hasta código, pruebas, revisión y entrega. Cada cambio tiene su acuerdo (propuesta y spec en formato **OpenSpec**), su
tarea (**Oracle Task**), requisitos medidos con evidencia (**Oracle**) y revisiones independientes validadas con
**Oracle Clue**. La persona decide el alcance, resuelve los hallazgos y acepta la entrega; los agentes trabajan, proponen
y quedan registrados como agentes.

Es una CLI local con un flujo visible en Git, una extensión de VS Code con un tablero de comando, y un servidor MCP de
sólo lectura para que un agente consulte el proyecto. No hace push ni publica ramas por su cuenta. El código y las
pruebas del producto los escribe quien trabaja (una persona o un agente); Factory registra qué se acordó, quién decidió
qué y qué evidencia lo respalda.

Las guías:

- [Modos de trabajo](docs/modos.md): quién decide qué en `confirmacion`, `funcional` y `autonomo`.
- [El tablero y el trabajo de a dos](docs/tablero.md): la extensión de VS Code, quién trabaja en qué, Live Share e integrar sin chocar.
- [El conocimiento del proyecto](docs/conocimiento.md): el vault `kb/`, `por-que` y `preguntar`.
- [Trabajar con agentes](docs/agentes.md): `--agente`, la guía de `AGENTS.md`, el MCP y los revisores.
- [Revisión guiada](docs/revision-guiada.md): pedir revisiones, preparar el informe y decidir los hallazgos.
- [Colaboración](docs/colaboracion.md): dos personas con sus agentes, del reparto a la integración, con el banco que lo prueba.
- [Dónde está cada cosa](docs/estructura.md) y [trazabilidad](docs/trazabilidad.md).


## Instalación

Está publicado en PyPI como `oracle-factory==0.1.0a13`, y su wheel, con los hashes, en el
[release de GitHub v0.1.0a13](https://github.com/Segtem/oracle-factory/releases/tag/v0.1.0a13). Con `uv`:

```bash
uv tool install --python 3.13 --with-executables-from oracle-metalenguaje,oracle-task,oracle-clue oracle-factory==0.1.0a13
uv tool update-shell
oracle-factory --version
oracle-factory --proyecto ./mi-proyecto init
oracle-factory --proyecto ./mi-proyecto nuevo --con-ejemplo notas "Comprobar el título de una nota"
```

Si uv advierte un conflicto porque `oracle`, `tasks` u `oracle-clue` ya están instalados, se instala sin
`--with-executables-from`:

```bash
uv tool install --python 3.13 oracle-factory==0.1.0a13
```

Factory usa sus dependencias (`oracle-metalenguaje 0.39.0`, `oracle-task 0.2.0` y `oracle-clue 0.1.0a2`) desde su entorno
aislado. Python 3.11 o posterior y Git. `--proyecto` va antes del subcomando; sin esa opción se usa la carpeta actual.

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
`oracle-factory --proyecto RUTA mcp` sirve el proyecto por MCP, de sólo lectura. Una decisión de persona nunca la toma un
agente. Ver [trabajar con agentes](docs/agentes.md).

**Revisión, trazabilidad y lo vigente.** `revision-preparar` arma el informe desde los de los revisores y `revision`
registra una revisión libre o guiada; `trazabilidad <id>` cruza cada requisito con las líneas que lo prueban;
`archivar` fusiona en `openspec/specs/` las specs de los cambios cerrados; `resumen` da el estado vigente en una lectura;
`donde`, `ruta` y `buscar` dicen dónde está cada cosa ([estructura](docs/estructura.md)).


## Alcance y límites

**En desarrollo en esta rama:** `preguntar` incorpora consultas al registro para cantidades/listados y respuestas
elaboradas con un modelo generativo explícitamente configurado, con fuentes y herramientas de sólo lectura. El JSON
pasa a `oracle-factory.preguntar/2`. Sin modelo conserva las consultas directas y la recuperación, indicando sus límites.
Ver [preguntar al proyecto](docs/conocimiento.md#preguntar). Esta ampliación aún no está en el paquete publicado.

- Usa Oracle, Oracle Task y Oracle Clue instalados con Factory; no copia sus reglas.
- Factory no ejecuta el sensor ni las pruebas del producto, ni certifica que un JSON de hechos provenga de la versión
  actual: guarda su huella, y la evidencia de otro candidato no vale. La cobertura completa de una spec requiere criterio
  humano y medidas defendibles.
- Lanza los revisores que declara cada proyecto (`pedir-revision`), pero el revisor no decide: los hallazgos los resuelve
  una persona.
- No autentica a nadie: una persona es un comando que corre en una terminal sin `--agente`. Los modos son un protocolo
  entre quienes trabajan juntos, no un control de acceso.
- No hace push ni publica ramas. Verificado en Linux; los comandos para Windows y macOS se revisaron pero no tienen
  ejecución automatizada.


## Vigencia de la evidencia

Antes de registrar la revisión, se terminan los cambios y se commitea el producto. Factory guarda HEAD y una huella de
los archivos del producto (versionados y nuevos no ignorados; sin `.factory/`, `tareas/` ni lo que genera). Si cambia el
código, la spec, las medidas o la evidencia, hay que repetir la revisión y el juicio. Un commit que sólo toca registros no
invalida: `estado` avisa cuando el HEAD es otro con el mismo producto. Los submódulos no están soportados.

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
Oracle Factory con un mismo ejemplo, en pixel art y con un minijuego para decidir como persona. Es una demostración: no
ejecuta agentes ni registra aprobaciones. GitHub Actions publica `site/` en GitHub Pages desde `main`; localmente,
`python3 -m http.server 8765 --directory site`. Para comprobarla en Chromium: `npm install --no-save
--package-lock=false playwright@1.62.1` y `node tests/test_site.cjs` (la portada viva: `node tests/test_web_viva.cjs`;
el minijuego, sin navegador: `node tests/test_juego.cjs`).


## Versiones

Lo que trajo cada versión está en [NOTAS-DE-RELEASE.md](NOTAS-DE-RELEASE.md).
