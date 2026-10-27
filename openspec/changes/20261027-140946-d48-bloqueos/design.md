# Design

Todo ocurre en `editores/vscode/tablero.js`, puro y probado con node: `paso()` distingue comando de explicación por el prefijo `oracle-factory` (la misma regla que ya usa el árbol en `modelo.js`) y `cambio()` suma la sección «Qué falta» con `c.pendientes`, que el JSON de `oracle-factory tablero --json` ya trae. No cambia la CLI ni el JSON.
