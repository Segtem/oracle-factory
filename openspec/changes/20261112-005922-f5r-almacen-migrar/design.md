# Diseño

- `migrar --almacen` vive en `almacenes.py` (`migrar(cli, almacen, verificar)`), junto a `comando` y `clonar`; `proyecto.comando_migrar` lo llama cuando viene `--almacen`.
- Las rutas de registros: `.factory` más las de `proyecto.oracle_raiz` y `openspec`, `tareas`, `kb`. Lo versionado sale de `git ls-files -z`; lo no versionado, de `git ls-files -z --others` (ignorado o no; si hay algo sin versionar que no está ignorado, se niega).
- Orden: comprobar todo → (URL: clonar) → copiar lo versionado al almacén → commit en el almacén → mover lo no versionado (rename; si cruza de disco, copia y borra) → conectar → `git rm -r -q --cached` + borrar del árbol del producto. Si se corta, lo hecho está en el almacén antes de borrar nada del producto.
- El ensayo clona con `git clone --local --no-hardlinks` a un temporal, corre la CLI con `XDG_CONFIG_HOME`/`XDG_DATA_HOME` temporales y compara `listar --json` (o su equivalente) antes y después.
