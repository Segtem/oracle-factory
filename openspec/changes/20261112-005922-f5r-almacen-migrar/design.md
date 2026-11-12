# Diseño

- `migrar --almacen` vive en `almacenes.py` (`migrar(cli, almacen, verificar)`), junto a `comando` y `clonar`; `proyecto.comando_migrar` lo llama cuando viene `--almacen`.
- Las rutas de registros: `.factory` más las de `proyecto.oracle_raiz` y `openspec`, `tareas`, `kb`. Lo versionado sale de `git ls-files -z`; lo no versionado, de `git ls-files -z --others` (ignorado o no; si hay algo sin versionar que no está ignorado, se niega).
- Orden: comprobar todo → (URL: clonar) → copiar al almacén lo versionado y lo no versionado (si una copia falla, se borra la copia a medias y no cambió nada) → commit en el almacén → conectar → `git rm -r -q --cached` (si falla, se para sin borrar nada del producto y dice cómo terminar) → borrar del árbol del producto, que es cuando lo no versionado deja de estar en él. Si se corta, lo hecho está en el almacén antes de borrar nada del producto (hallazgos MIG-001 y MIG-002 de codex).
- El ensayo clona con `git clone --local --no-hardlinks` a un temporal, corre la CLI con `XDG_CONFIG_HOME`/`XDG_DATA_HOME` temporales y compara `listar --json` (o su equivalente) antes y después.
