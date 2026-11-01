# Diseño

- Las rondas salen de los eventos del cambio: se cuentan los candidatos distintos con un evento `revision_pedida` o `revision_lanzada` (la misma definición que usa `tools/medir_rondas.py`). No se ordena nada por fecha de archivo.
- El tamaño sale de `git diff --numstat` entre la base del candidato (merge-base con main) y el candidato, sumando las líneas agregadas de los archivos que `es_producto` acepta y que no son de pruebas (`alarmas.es_de_pruebas`). Sin candidato vigente no hay aviso.
- Los dos cálculos van en `oracle_factory/alarmas.py` junto al de tests editados, y se muestran donde ya se muestran aquel (`estado`, `lecturas`). Un fallo de Git o un registro ilegible devuelve «no se pudo calcular» y no avisa.
