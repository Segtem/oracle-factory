# Una skill de agente con el flujo de Factory

## Por qué

La guía para agentes que Factory genera en `AGENTS.md` dice **quién decide qué** y **qué comandos hay**, pero no cuenta **cómo se trabaja un cambio de punta a punta**, y los errores que cometimos en las últimas semanas son todos de procedimiento, no de reglas: abrir un cambio duplicado sin mirar `git worktree list` y `listar`; correr `oracle-factory agentes` dentro de un worktree y regenerar la guía con el código de `main` (el comando global es la instalación editable de `main`, no el del worktree); proponer medidas antes de regenerar los catálogos; pedir revisión sin haber corrido antes la suite completa; leer como éxito una línea suelta de la salida en vez de la última; afirmar un conteo sin contarlo. Un agente nuevo (Claude Code, Codex, agy) los repite porque nadie se los dijo. Las skills de pair programming que estudiamos resuelven lo mismo con condiciones de parada explícitas.

## Qué cambia

- Una skill, `oracle_factory/data/skill/SKILL.md` (con el encabezado `name` y `description` que leen las herramientas de agentes), con el procedimiento: qué mirar antes de abrir un cambio, cómo armar el worktree, el orden de los pasos de un cambio, qué corre cada uno y con qué CLI, qué se hace en cada ronda de revisión, el camino ligero y las condiciones de parada (una decisión de diseño que la spec no cubre, querer agregar algo no pedido, tener que cambiar o saltear un test, dos intentos fallidos, un paso de más de 50 líneas o tres archivos).
- `oracle-factory skill` muestra el texto; `oracle-factory skill --instalar` lo escribe en `.claude/skills/oracle-factory/SKILL.md` **del proyecto**, sin pisar un archivo distinto salvo con `--forzar`, y nunca toca la carpeta personal del usuario ni la configuración de ninguna herramienta.
- La guía para agentes (`AGENTS.md`) nombra el comando.
- Una prueba comprueba que la skill no se desactualice: cada comando de Factory que nombra existe en la CLI, los umbrales que cita (4 rondas, 450 líneas, 150 líneas) son los del código y los documentos que enlaza existen.

## Fuera de alcance

- Instalar la skill en `~/.claude/`, en la configuración de Codex o de agy, o en el repositorio de ninguna herramienta: sólo el proyecto, y sólo si se pide.
- Cambiar quién decide cada paso, los modos de trabajo o los gates: la skill describe el procedimiento, no lo impone.
- Una skill por herramienta: el mismo texto sirve a las tres.
- Generar la skill desde el código como la guía: es texto escrito a mano, con una prueba que la contrasta.

## Decisiones humanas

- Las condiciones de parada y las reglas de procedimiento que la skill establece (están en el diseño; las propongo yo).
- Que se instale sólo en el proyecto y sólo con `--instalar`.
- Que el texto esté en español, como el resto de la documentación.
