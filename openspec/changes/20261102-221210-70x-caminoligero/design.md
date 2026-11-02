# Diseño

- El cálculo vive en `oracle_factory/alarmas.py`, junto a las otras señales del flujo: reusa `lineas_de_producto` y `base_del_candidato`, y suma `archivos_cambiados` de la trazabilidad para saber qué archivos tocó el candidato (incluye un archivo renombrado desde o hacia una regla de decisión).
- La lista de reglas de decisión es una constante (`REGLAS_DE_DECISION`) que el documento y la guía nombran; una prueba compara la lista del código con el documento.
- Sin candidato vigente, o si Git no puede decirlo, el camino queda en «no se pudo calcular» (`null`), no en «completo»: no se afirma nada.
- El texto de la guía sale del código (umbral y lista), como el resto de `agentes.py`, para que `agentes --verificar` detecte si quedó vieja.
