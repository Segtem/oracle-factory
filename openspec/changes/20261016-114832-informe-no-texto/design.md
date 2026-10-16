# Design

- `ruta_del_registro(valor) -> Path | None` en `cli.py`: `ROOT / valor` si `estructura._texto(valor)` lo acepta (el criterio de `donde`), si no `None`.
- Lo usan los cinco lugares que hoy hacen `ROOT / valor`: `juicio_vigente`, `problemas_de_revision`, el bucle de Oracle de `pendientes_actuales`, `archivos_faltantes` y los hechos juzgados de `_pasos`.
- En `problemas_de_revision` y `pendientes_actuales`, un valor presente y no válido agrega «<etiqueta> no válido en el registro (no es una ruta de texto)»; `archivos_faltantes` no lo lista como archivo que falta (no hay archivo que recuperar desde Git), así el próximo paso sigue al de la revisión o el juicio.
