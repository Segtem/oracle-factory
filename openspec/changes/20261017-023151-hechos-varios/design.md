# Design

- `juzgar(identificador, hechos: list[Path])`; la CLI declara `--con` con `action="append"`. Cada ruta pasa por las mismas comprobaciones de hoy (que exista, relativa al proyecto o aviso, ignorada por Git o aviso) y por la de «el producto o los hechos cambiaron durante el juicio».
- El registro: `hechos` y `hechos_sha256` son el primer archivo, como hoy; `hechos_mas` es `[{"ruta", "sha256"}]` con los demás, sólo si hay más de uno. Un registro viejo no cambia de significado.
- `hechos_registrados(oracle) -> list[(ruta, sha256)]` es el único lugar que arma la lista; la usan `juicio_vigente`, `pendientes_actuales`, `archivos_faltantes`, `_pasos` (repetir con los mismos `--con`), `estructura.donde` y `datos_estado`.
