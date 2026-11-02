# Diseño

- Los casos salen de las clases `unittest.TestCase` del módulo de pruebas, leído con `ast` (no con expresiones regulares sobre el texto: un nombre dentro de una cadena no es un caso). Un caso es un método `test_<letras><n>_…` con 2 o 3 letras minúsculas; el id del caso es `Clase.método`, como en los verificadores actuales.
- Los requisitos salen de los encabezados «### Requirement: …» de la spec del cambio, en orden; el id Oracle completo sale del registro del cambio (`requisitos`), igual que hoy.
- Los hechos se llaman `<x>_caso` y `<x>_corrida`, con `<x>` el nombre del módulo sin `test_`, para que los catálogos nuevos tengan la misma forma que los de hoy.
- Las fuentes quietas, la trazabilidad y los archivos se reusan de `tools/verify_review_guided.py` (`Resultado`, `escribir`, `sha`) y de `oracle_factory.trazabilidad`, como los verificadores actuales; no se vuelve a escribir esa lógica.
- Los catálogos se escriben desde una plantilla única; escribirlos de nuevo con los mismos casos no cambia nada.
