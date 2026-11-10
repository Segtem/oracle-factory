# Autopilot: el agente lanzado recibe un entorno filtrado y una guía de permisos sin Python abierto

## Por qué

Al estudiar un repo de referencia (dsh-superagent) vimos que ellos quitan del entorno las variables con KEY, PASSWORD, SECRET o TOKEN antes de lanzar procesos. En Factory, `autopilot --ejecutar --lanzar` le pasa al agente lanzado TODO el entorno de la persona (`{**os.environ, …}`): por ejemplo claves de API y tokens. Además, la guía de permisos que usamos para `claude -p` incluye `Bash(.venv/bin/python:*)`, que deja correr cualquier Python, con red, lectura del entorno y hasta `git push`. Se dijo varias veces que el agente trabajaba «sin red» y con «permisos acotados»; eso era más fuerte de lo cierto.

## Qué cambia

- El agente lanzado recibe sólo un entorno mínimo: lo que necesita para correr herramientas de línea de comandos (rutas, usuario, idioma, terminal, carpetas XDG, los plazos de Bash de Claude Code) y `FACTORY_AGENTE`. Ninguna otra variable pasa, aunque su nombre no parezca un secreto.
- `--entorno NOMBRE` (repetible, sólo con `--ejecutar --lanzar`) agrega una variable por nombre, por esa corrida: la persona decide qué entrega, como ya decide qué comando lanza. No se guarda.
- Los comandos mecánicos de Factory no cambian (son código de Factory, no un agente).
- `docs/modos.md` muestra la guía de permisos recomendada: Python acotado a `-m unittest` y a `tools/verificar_cambio.py`, no abierto, con el motivo.

## Fuera de alcance

- Hacer cumplir los permisos del agente (los define el comando de `--lanzar`, que es de la persona) y aislar el proceso (contenedor, red).
- Los revisores externos (codex, agy), que se lanzan por otra vía.

## Decisiones humanas

Ninguna nueva; se confirma al aprobar la spec que el filtro es una lista de permitidos (no una lista de prohibidos por nombre) y que `--entorno` es explícito por corrida.
