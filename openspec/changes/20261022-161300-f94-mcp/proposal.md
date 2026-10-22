# Preguntar al proyecto desde el editor y desde un agente: el comando de VS Code y oracle-factory mcp, de sólo lectura

## Why

`oracle-factory preguntar` responde con pasajes vigentes y sus citas, pero sólo desde una terminal. Quien trabaja en VS
Code tiene que salir del editor para preguntar, y un agente (Claude Code, Codex) tiene que saber armar la línea de
comandos y leer su salida. Factory no tiene servidor MCP: un agente no puede consultar el estado de un cambio, su
historia o por qué existe una línea como una herramienta más.

## What changes

- `oracle-factory mcp` sirve, por la entrada y la salida estándar, un servidor MCP de sólo lectura sobre el proyecto,
  sin dependencias nuevas. Sus herramientas son las consultas que ya existen: preguntar, estado, buscar, por qué existe
  una línea, resumen, log de un cambio y la lista de cambios. Devuelven lo mismo que la CLI (en JSON cuando la CLI lo
  tiene). Ninguna cambia el proyecto: las decisiones siguen siendo de una persona en su terminal, y lo que propone un
  agente lo propone con la CLI, como hoy.
- Se registra con una línea en Claude Code (`claude mcp add factory -- oracle-factory mcp --proyecto RUTA`) y en Codex.
- La extensión de VS Code suma «Factory: Preguntar al proyecto» (en la paleta y como botón del tablero): pide la pregunta
  y muestra los pasajes con su cita, sin cambiar nada.

## Out of scope

- Herramientas MCP que decidan o propongan (decidido por Brian: sólo leer).
- Que el MCP o la extensión redacten la respuesta con un LLM: muestran los pasajes; responde quien los lee.
- Preguntar desde la sesión de un invitado de Live Share.

## Human decisions

- Decidido por Brian (2026-10-22): el MCP vive dentro de Factory, como un subcomando, y es de sólo lectura.
