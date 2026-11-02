# Un verificador reutilizable para la evidencia de cada cambio

## Por qué

Cada cambio de Factory trae su propio `tools/verify_<x>.py` (100 líneas casi idénticas: la lista de casos por requisito, la corrida de la suite, los hechos, la trazabilidad y la prueba de que las fuentes quedaron quietas) y entre tres y cinco catálogos `catalogos/factory_<x>.*.oracle` que sólo cambian en el nombre del requisito y en el número de casos. Hoy los genero con un script de un solo uso en cada cambio. Hay más de 40 verificadores así. Esa repetición cuesta en cada cambio, ya produjo errores (una lista de casos con un nombre mal escrito deja la evidencia en rojo sin que el producto falle; una expresión regular que leía mal las clases de las pruebas) y es justo el exceso de ceremonia que critican los estudios que revisamos. No toca ninguna decisión humana ni ninguna revisión: es plomería.

## Qué cambia

- Una herramienta `tools/verificar_cambio.py` que, dado el id de un cambio y su módulo de pruebas, produce la evidencia del cambio sin un verificador escrito a mano. Los casos de cada requisito salen de los nombres de las pruebas: un caso `test_<letras><n>_…` prueba el requisito número `n` de la spec del cambio, en el orden en que la spec los lista.
- La herramienta falla, sin declarar éxito, si un requisito no tiene ningún caso, si un caso nombra un número que no corresponde a ningún requisito, o si el módulo no tiene casos.
- Produce los mismos archivos que hoy (`suite.txt`, `hechos.json`, `trazabilidad.json`, `resultado.json`) y exige lo mismo: todos los casos pasan, la corrida está completa, las fuentes no cambiaron mientras corría y la trazabilidad es ok.
- Con `--catalogos` escribe los catálogos Oracle del cambio (la corrida completa y uno por requisito, con el número de casos que cuenta) en vez de generarlos con un script aparte.
- `docs/tests.md` explica la convención de nombres y el uso.

## Fuera de alcance

- Migrar los más de 40 verificadores existentes: siguen como están; el nuevo es para los cambios que vengan.
- La revisión reducida para cambios chicos: es un cambio aparte, que decide Brian.
- Cambiar qué mide Oracle o cómo se confirman las medidas: las medidas las sigue proponiendo el agente y confirmando una persona.
- Convertirlo en un subcomando de `oracle-factory`.

## Decisiones humanas

- La convención: el número del nombre de la prueba es el orden del requisito en la spec.
- Que la herramienta viva en `tools/` y no en el comando `oracle-factory`.
