# Design

Es un cambio de textos y de una regla de `tools/docs_al_dia.py`. La regla nueva es la inversa de `publicacion_prematura`: si `NOTAS-DE-RELEASE.md` ya no marca la versión actual como «en preparación», se señala cualquier texto del README, de `docs/` o de la web que la llame candidata, en preparación o instalable cuando se publique. El estado de la versión sigue teniendo una sola fuente: el encabezado de sus notas. `tests/test_entrega_a15.py` y el texto de la guía que fija `tests/datos/guias-texto.json` cambian a lo mismo.
