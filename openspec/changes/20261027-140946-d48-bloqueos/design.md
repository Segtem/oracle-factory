# Design

Todo ocurre en `editores/vscode/tablero.js`, puro y probado con node: `paso()` distingue comando de explicación por el campo `comando` del paso, que `oracle_factory/tablero.py` (`_paso`) llena sólo si el texto empieza con `oracle-factory ` (la misma regla que usa el árbol en `modelo.js`) y `cambio()` suma la sección «Qué falta» con `c.pendientes`, que el JSON de `oracle-factory tablero --json` ya trae. No cambia la CLI ni el JSON.
