# Diseño

- Las claves que la extensión lee se registran en node, envolviendo cada JSON en un `Proxy` que anota la ruta de cada lectura (los índices de un arreglo se anotan como `[]`) y llamando a las funciones puras de la extensión: `modelo.raiz`, `modelo.hijosCambio` y `tablero.html`. La extensión misma no se toca.
- Los proyectos de las pruebas son los de `tests/test_vscode.py` y `tests/test_tablero*.py` (un cambio abierto, uno medido, uno juzgado, uno abandonado, con revisión, con responsable), para que cada rama de la extensión tenga una oportunidad de leer sus claves.
- Una clave opcional es la que falta o es `null` en algunos estados; el contrato la marca con `"opcional": true`, y la prueba de la CLI la exige sólo si su objeto padre existe en algún estado.
- El contrato se compara por rutas (`cambios[].proximo_paso.comando`), no por el JSON entero: lo que la extensión no lee puede cambiar libremente.
