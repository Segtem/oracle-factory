# Trabajar con agentes

Factory no es un agente ni lo reemplaza: Claude Code, Codex o cualquier otro hacen el trabajo, y Factory lleva el
registro de qué se acordó, quién decidió y qué evidencia lo respalda. Lo que un agente necesita es saber el flujo, poder
consultar el proyecto y que quede claro qué es suyo y qué es de una persona.

## `--agente`: quién hizo qué

Un agente corre cada comando de Factory con `--agente NOMBRE` (`claude-code`, `codex`…), y queda registrado como agente.
Según el modo de trabajo del cambio ([modos](modos.md)), en cada una de las cuatro decisiones (spec, medidas, revisión,
cierre) un agente decide, propone (cuenta cuando una persona la confirma) o no puede. Hay cosas que son de una persona en
cualquier modo: confirmar medidas, revisar paso a paso, abandonar, bajar la intervención, soltar un cambio, elegir en
`decidir-union` y marcar revisada una nota. Con `--agente` se niegan aunque el agente corra en una terminal.

Factory no autentica: una persona es un comando que corre en una terminal sin `--agente`. Es un protocolo entre quienes
trabajan juntos, no un control de acceso.

## La guía de `AGENTS.md`

```bash
oracle-factory agentes
```

escribe (o actualiza) en el `AGENTS.md` del proyecto un bloque marcado con la guía para agentes, armada desde la propia
CLI: quién decide qué en cada modo, con el modo del proyecto marcado, los comandos de una persona y los de un agente, y
cómo consultar el proyecto. No toca lo que el proyecto escribió fuera del bloque, y agrega `@AGENTS.md` al `CLAUDE.md`
para que Claude Code la lea (Codex lee `AGENTS.md`). `init` la escribe al empezar. `oracle-factory agentes --verificar`
falla si quedó vieja (por ejemplo, después de cambiar el modo por defecto) o si las marcas del bloque están rotas; en ese
caso no escribe nada.

Una prueba de Factory comprueba que la guía dice lo que hace la CLI: corre cada decisión en cada modo como agente y cada
comando de persona, y compara con la tabla.

## Consultar el proyecto por MCP

```bash
claude mcp add factory -- oracle-factory --proyecto /ruta/al/proyecto mcp
codex mcp add factory -- oracle-factory --proyecto /ruta/al/proyecto mcp
```

`oracle-factory mcp` sirve el proyecto por MCP (stdio), de sólo lectura. Sus herramientas son las consultas de la CLI y
devuelven lo mismo: `preguntar` (respuestas y fuentes, con sus límites), `estado`, `buscar`, `por_que`, `resumen`, `log` y
`listar`. Ninguna cambia el proyecto; un argumento mal formado o un error vuelve como error de la herramienta y el
servidor sigue atendiendo.

## Revisores independientes

Una revisión la puede hacer otra persona u otro agente, de otra familia de modelo que el que escribió el código. Cada
proyecto declara sus revisores en `.factory/config.json` (el comando, el proveedor, el modelo y un tope de minutos) y
`oracle-factory pedir-revision ID --a codex` prepara un clon aparte del candidato y su paquete de Oracle Clue, arma el
pedido, lanza al revisor, valida su informe con Clue y lo guarda en el candidato. Se pueden lanzar varios a la vez. El
revisor no decide: lo que trae se decide en `revisar`. Ver [revisión guiada](revision-guiada.md).

## Con un modelo local

Factory no necesita un agente comercial: cualquier agente que corra comandos puede trabajar con Factory siguiendo la guía
de `AGENTS.md`. Los embeddings de `preguntar` ya corren en la máquina con Ollama ([conocimiento](conocimiento.md)).

## El camino ligero

No todo cambio necesita el mismo recorrido de revisión. `oracle-factory estado ID` dice, en la línea «Camino de revisión» y en la clave `camino` de su JSON, si el candidato califica para el **camino ligero**: agrega 150 líneas de producto o menos (sin contar las pruebas) y no toca las reglas de decisión (`cli.py`, `modos.py`, `flujo_revision.py`, `flujo_medidas.py`, `revision.py`, `preparacion.py`, `puerta.py`, `unir.py` y `alarmas.py`, dentro de `oracle_factory/`; este último porque ahí vive el propio clasificador). Si no califica, dice por qué. Con el camino ligero alcanza **un revisor y una ronda**: si no trae hallazgos medios ni altos, se pasa a preparar la revisión; si trae, el cambio sigue el camino completo.

Es una orientación, no un gate: no cambia los pasos pendientes, el próximo paso ni quién decide. La aprobación de la spec, la confirmación de las medidas, la revisión humana y el cierre siguen siendo los de siempre, y un candidato que no califica puede cerrarse igual. Si Git no puede decirlo, o no hay candidato, `camino` queda en `null` y no se afirma nada. Los umbrales salen de 20 cambios cerrados y son una referencia, no una ley.

**Límites conocidos.** Las líneas son las agregadas en archivos de producto: un archivo binario no suma líneas, lo que se borra no se resta, y un renombre puro (por ejemplo de un archivo de pruebas a un módulo de producto) o una copia sin modificar su origen aportan pocas o ninguna línea. Un cambio de ese tipo puede salir «ligero» aunque convenga una revisión más completa: la orientación no reemplaza el criterio de quien revisa, y ante la duda se pide la ronda completa.

