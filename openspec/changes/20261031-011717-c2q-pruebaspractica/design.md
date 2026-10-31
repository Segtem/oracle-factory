# Diseño

- La plantilla vive en `oracle_factory/plantillas.py` (`tareas`, en español y en inglés); el paso nuevo va antes de «implementar».
- El aviso se calcula leyendo `trazabilidad.json` del candidato vigente con `estructura.ruta_canonica(..., "evidencia", sha)` y su clave `requisitos`, que ya trae los casos de cada requisito; no corre Git ni el sensor.
- La excepción se lee de la spec del cambio como `Tipo:`: una línea `Pruebas: no aplica — motivo` dentro del requisito, con la misma forma de leerla (`modos.py` y `resumen.py` ya leen `Tipo:`). Como la spec se aprueba por una persona, aprobarla es aprobar el motivo.
- Todo es un aviso: no entra en `pendientes_actuales` ni cambia el próximo paso.
