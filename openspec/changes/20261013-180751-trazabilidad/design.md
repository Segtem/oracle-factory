# Design

- `oracle_factory/trazabilidad.py`, puro salvo la traza: `trazar(raiz, contratos)` recibe `{requisito: [id de prueba de unittest]}`, carga cada caso con `unittest`, lo corre bajo `sys.settrace` (y `threading.settrace`) juntando `(archivo, línea)` de archivos dentro de la raíz y fuera de `.venv`, y devuelve el objeto de `trazabilidad.json`. Un caso que falla se registra con su resultado.
- `lineas_ejecutables(texto)` compila el archivo y recorre los objetos de código (`co_lines`): ésas son las líneas que una traza puede ver. Una línea cambiada que no está ahí (comentario, blanco, parte de una expresión de varias líneas sin evento propio) no cuenta como sin respaldo.
- `cruzar(trazas, cambios, ejecutables)` es puro: recibe la traza, las líneas cambiadas por archivo (de `git diff -U0 base candidato`) y las ejecutables de cada archivo Python cambiado, y devuelve por requisito, sin respaldo y no rastreables.
- La CLI toma el candidato vigente y la base como `pedir-revision` (merge-base con main), lee `trazabilidad.json` de la evidencia y lee los archivos en el candidato con `git show`, no del árbol de trabajo.
- El sensor de este cambio usa el ayudante y deja la trazabilidad junto a `hechos.json`.
