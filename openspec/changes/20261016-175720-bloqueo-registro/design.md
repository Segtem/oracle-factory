# Design

- `LEIDOS: dict[Path, bytes]` en `cli.py`. `leer` guarda los bytes que leyó y `escribir_atomico` actualiza los de una ruta que ya estaba ahí. `guardar` pasa `esperado=LEIDOS.get(destino)` si no le dan uno.
- `escribir_atomico` toma `fcntl.flock(LOCK_EX)` sobre un descriptor de la carpeta destino, desde la comparación hasta `os.replace`. Una carpeta por cambio en `.factory/cambios/<ID>/`, así que dos cambios no se esperan entre sí.
