# Design

Notas para implementar después de la aceptación. No son parte del contrato.

- **Fase 1 (este cambio):** `.factory/` con `cambios/<ID>/candidatos/<sha7>/` y `local/`; descubrimiento; exclusión de la huella; los cuatro comandos. El estado de cada cambio y `factory.json` del proyecto siguen donde están.
- **Fase 2 (cambio propio):** mover a `.factory/` el estado de cada cambio (`factory.json`, `review.md`, `oracle-veredicto.txt`) y la configuración del proyecto, leyendo el lugar viejo como histórico.
- **Descubrimiento:** una función `raiz_del_proyecto()` que sube con `Path.parents`; reemplaza `ROOT = Path.cwd()` al cargar y se omite con `--proyecto`. Cuidado con las pruebas, que fijan `ROOT` a mano.
- **Huella:** `contexto_producto()` ya excluye `tareas/` y los tres registros de `openspec/changes/<ID>/`; pasa a excluir también `.factory/`. Conviene hacerlo sobre el cambio de vigencia por contenido, que toca la misma función.
- **SHA de 7 caracteres:** `git rev-parse --short=7`. Si dos candidatos del mismo cambio colisionaran, `ruta` falla en vez de elegir.
- **Checkouts de revisión:** un worktree dentro de `.factory/local/` no hace ruido si está ignorado; sin ignorar, la huella lo rechazaría como directorio Git. Por eso `init` agrega el ignore.
