# Diseño

Se sigue la receta de las entregas anteriores: las herramientas `probar_entrega_a16.py`, `verify_entrega_a16.py` y `mutar_entrega_a16.py` y las pruebas `test_entrega_a16.py` y `test_entrega_integridad_a16.py` salen de las de la 0.1.0a15, con nombres de hechos propios (`entrega_a16_*`) para no chocar con los de la entrega anterior. Lo nuevo de esta versión se comprueba con el wheel instalado en un entorno aislado, un proyecto temporal con `uv.lock` y un servidor OSV local; ninguna comprobación toca la red.
