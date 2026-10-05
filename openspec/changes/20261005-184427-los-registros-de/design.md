# Design

Se completa después de la aceptación.

- `juzgar` guarda `str(hechos.relative_to(ROOT))` si está dentro de `ROOT`, y la ruta absoluta con una advertencia si no.
- `pendientes_actuales` resuelve `ROOT / ruta`: ya sirve con una ruta relativa; sólo cambia el mensaje de «ausente».
- `importar` reescribe la `fuente` de cada `.requisito` recién escrito, sustituyendo el prefijo `ROOT/` antes de la primera medida; la reescritura queda antes de `medir`, que guarda el hash del archivo.
- `git check-ignore -q <ruta>` decide si los hechos están ignorados.
- `tools/verify_maquinas.py` arma la imagen con el wheel del checkout, levanta un remoto y dos estaciones y siempre las elimina al terminar.
