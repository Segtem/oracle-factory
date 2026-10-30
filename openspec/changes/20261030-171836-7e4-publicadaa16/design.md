# Diseño

Es un cambio de textos y de pruebas: la regla de `tools/docs_al_dia.py` que detecta lo que sigue llamando candidata a una versión publicada ya existe desde la 0.1.0a15. El estado de la versión sigue teniendo una sola fuente: el encabezado de sus notas. `tests/test_entrega_a16.py` y el texto de la guía que fija `tests/datos/guias-texto.json` pasan al estado publicado, y las pruebas `tests/test_publicada_a16.py` conservan la cobertura de la regla inversa que tenía `test_publicada_a15.py`.
