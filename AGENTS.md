# Oracle Factory

Este repositorio es Factory mismo, y se desarrolla con Factory: cada cambio va en su worktree
(`git worktree add -b tarea/<x> ../factory-<x> main`) con su propio `.venv` (`uv venv .venv; uv pip install -p .venv -e .`).

- Las pruebas: `.venv/bin/python -m unittest discover -s tests </dev/null` (con `</dev/null`: algunas leen la terminal).
- La evidencia de cada cambio la produce su `tools/verify_<x>.py --salida $(oracle-factory ruta ID evidencia)`, con las
  fuentes quietas: no se edita el worktree mientras corre.
- Una revisión independiente se pide con `oracle-factory --agente NOMBRE pedir-revision ID --a codex` (y `--a agy`).
- No reescribas la historia publicada de Git ni la configuración de Git de ningún repositorio.
- Si cambiás la versión o las dependencias de `pyproject.toml`, regenerá y commiteá el `uv.lock` (`uv lock`): una prueba exige que coincidan.

<!-- oracle-factory agentes: inicio (generado por `oracle-factory agentes`; no se edita a mano) -->

## Trabajar con Oracle Factory (para agentes)

Este proyecto usa Oracle Factory: cada cambio tiene su propuesta, su spec, requisitos medidos por Oracle, una revisión y un cierre. Las decisiones son de una persona; un agente trabaja, propone y deja todo registrado.

- Corré cada comando de Factory como agente: `oracle-factory --agente NOMBRE …` (tu nombre: `claude-code`, `codex`…). Sin `--agente` la acción se registra como de una persona, y no lo sos.
- El próximo paso de un cambio lo dice `oracle-factory estado ID` (o `--json`): seguilo en vez de adivinar.
- Antes de implementar, la spec tiene que estar aprobada por una persona. No edites a mano `.factory/`, `tareas/` ni `kb/` generado.
- Los tests unitarios son parte del desarrollo y no suplantan a Oracle: escribilos primero, cuando sea posible, y no bloquean nada. Un test que ya existía no se edita para que pase sin dejarlo dicho a quien revisa (ver `docs/tests.md`).

### Las decisiones, según el modo de trabajo

Cada decisión tiene su comando. Con `--agente`, según el modo del cambio, el agente la decide, la propone (cuenta cuando una persona la confirma repitiendo el comando sin `--agente`) o no puede; una persona, desde su terminal, siempre decide:

- Spec: `oracle-factory aprobar-spec ID` (aprobar la propuesta y la spec)
- Medidas: `oracle-factory medir ID --requisito R --medida M --quitar-sin-medir` (elegir las medidas de un requisito)
- Revisión: `oracle-factory revision ID --informe INFORME --revisor R --decision aprobar|cambios --hallazgos-abiertos N` (registrar la decisión de una revisión)
- Cierre: `oracle-factory cerrar ID` (cerrar el cambio)

| Modo | Spec | Medidas | Revisión | Cierre |
| --- | --- | --- | --- | --- |
| autonomo | decide | decide | decide | decide |
| funcional | no puede (funcional) / decide (no funcional) | no puede (funcional) / decide (no funcional) | no puede (funcional) / decide (no funcional) | no puede |
| **confirmacion** (el de este proyecto) | propone | propone | propone | no puede |

### Sólo de una persona, en cualquier modo

Con `--agente` se niegan o dejan sólo una propuesta. Pedíselos a la persona, con el comando listo para copiar:

- `oracle-factory medir ID --confirmar`: confirmar las medidas que propuso un agente
- `oracle-factory revisar ID`: revisar paso a paso y registrar la decisión (un agente la propone con --agente --decision --motivo)
- `oracle-factory abandonar ID`: abandonar el cambio (un agente propone el motivo con --agente --motivo)
- `oracle-factory modo ID MODO`: bajar la intervención humana de un cambio
- `oracle-factory soltar ID`: dejar de ser responsable de un cambio
- `oracle-factory decidir-union ID CAMPO nuestro|suyo`: elegir qué vale cuando dos ramas decidieron distinto
- `oracle-factory kb revisada NOTA`: marcar revisada una nota de personas del vault

### Comandos de un agente (con `--agente NOMBRE`)

- `oracle-factory --agente NOMBRE nuevo --capacidad C --sufijo S "TÍTULO"`: crear un cambio con su propuesta y su spec para completar
- `oracle-factory --agente NOMBRE importar ID`: importar los requisitos de la spec aprobada
- `oracle-factory --agente NOMBRE pedir-revision ID --a REVISOR`: pedir una revisión independiente del candidato
- `oracle-factory --agente NOMBRE revision-preparar ID`: preparar el informe para que una persona revise
- `oracle-factory --agente NOMBRE revisar ID --decision aprobar|cambios --motivo M`: proponer la decisión de la revisión
- `oracle-factory --agente NOMBRE juzgar ID`: correr Oracle sobre la evidencia del candidato
- `oracle-factory --agente NOMBRE mensaje ID "TEXTO"`: dejar un mensaje en el registro del cambio
- `oracle-factory --agente NOMBRE tomar ID`: sumarse como agente al cambio
- `oracle-factory --agente NOMBRE abandonar ID --motivo M`: proponer el motivo de un abandono

### Consultar el proyecto (sólo lectura)

- `oracle-factory estado ID`, `oracle-factory preguntar "PREGUNTA"`, `oracle-factory por-que ARCHIVO:LÍNEA`, `oracle-factory buscar TEXTO`, `oracle-factory log ID`, `oracle-factory resumen`, `oracle-factory listar`.
- `preguntar` devuelve pasajes vigentes del conocimiento del proyecto con su cita: úsalo antes de suponer por qué algo es como es.
- Por MCP, las mismas consultas como herramientas: `claude mcp add factory -- oracle-factory --proyecto RUTA mcp` (o `codex mcp add …`).

<!-- oracle-factory agentes: fin -->
