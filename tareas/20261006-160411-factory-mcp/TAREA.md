# factory-mcp: capa fina sobre la CLI para que un agente pregunte en vez de leer

- ESTADO: ABIERTA
- PRIORIDAD: 30
- ETIQUETAS: compresion


## Objetivo

Servidor MCP delgado sobre las mismas funciones de la CLI (`estado`, `donde`, `buscar`, `resumen`, un requisito con su medida y su veredicto), como `oracle-mcp` y `jam-mcp`. Depende de `archivar` y `resumen`. La CLI sigue siendo la fuente.

Parte del plan «comprimir lo que se lee, no lo que se guarda» (2026-10-06): el registro sigue append-only y atado a hashes; encima, vistas derivadas que la herramienta regenera de forma determinista.
