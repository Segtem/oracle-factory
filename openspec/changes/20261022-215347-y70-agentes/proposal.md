# La guía para agentes en AGENTS.md: generada desde la CLI, verificada y siempre al día

## Why

Un agente nuevo (Claude Code, Codex, agy) que entra a un proyecto con Factory no sabe el flujo: qué comandos corre con
`--agente`, qué decisiones son de una persona y sólo puede proponer, cómo consultar el estado o preguntar al proyecto.
Hoy eso lo sabe quien estuvo en la conversación. El `AGENTS.md` de Factory, escrito a mano, ya quedó viejo: habla de
`fabrica.py` y de CodeRabbit. Una guía escrita a mano se pudre como cualquier vault.

## What changes

- `oracle-factory agentes` escribe en el `AGENTS.md` del proyecto (lo crea si no está) un bloque marcado, sin tocar lo
  que el proyecto escribió afuera del bloque. Codex lee `AGENTS.md`; Claude Code lo lee con una línea `@AGENTS.md` en su
  `CLAUDE.md`, que el comando agrega si falta.
- El bloque se arma desde la propia CLI: quién decide qué en cada modo de trabajo (de `modos.via_agente`, con el modo
  por defecto del proyecto marcado), qué comandos son de una persona y cuáles corre un agente con `--agente NOMBRE`,
  cómo saber el próximo paso, y cómo consultar el proyecto (`estado`, `preguntar`, `por-que`, el MCP).
- `oracle-factory agentes --verificar` falla, sin escribir, si el bloque falta o quedó viejo; `init` lo escribe.
- La guía dice la verdad: una prueba recorre cada comando que la guía marca como de persona y comprueba que, con
  `--agente`, se niega o sólo deja una propuesta.
- El `AGENTS.md` de Factory pasa a ser ese bloque más lo propio del repositorio.

## Out of scope

- Los hooks de Claude Code que agregan `--agente` solos o avisan de un comando de persona (otro cambio, decidido por Brian).
- Una skill de Claude Code.

## Human decisions

- Decidido por Brian (2026-10-22): un bloque generado en AGENTS.md; los hooks en otro cambio.
