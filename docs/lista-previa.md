# Lista previa a la revisión

Antes de pedir una revisión, quien escribe el cambio mira esta lista. No bloquea nada y no cambia el pedido que recibe el revisor: es un recordatorio, y `oracle-factory pedir-revision` la muestra antes de lanzar al revisor.

## Por qué existe

Medimos los cambios cerrados de Factory: el lazo de rondas de revisión es el cuello de botella principal. La mediana es de 2 a 3 rondas por cambio y el máximo de 6, y las rondas 2 y 3 traen más hallazgos que la primera, porque cada corrección abre superficie nueva. Los hallazgos altos y medios se repiten por clases (las rutas con `..` y enlaces simbólicos pasaron de 3 en la primera ronda a 17 en la tercera o más), y muchas veces el ayudante correcto ya existía. Cada ronda cuesta corregir, reconfirmar medidas, regenerar la evidencia y esperar a un revisor. La lista pregunta por esas clases antes, cuando arreglarlas es más barato.

## Las preguntas

1. ¿Buscaste en el código el ayudante que ya existe (por ejemplo para rutas, nombres o lectura de la spec) antes de escribir otro?
2. ¿Rechazás «..», las rutas absolutas y los enlaces simbólicos de todo el camino antes de leer o escribir un archivo?
3. ¿Qué hace el código con None, un número, una lista, un byte nulo o un archivo que falta, y puede terminar en un traceback?
4. ¿Leés el formato igual que la herramienta que ya lo lee (Oracle, exigir_spec, modos): mismos espacios, mayúsculas y encabezados?
5. ¿Puede haber un falso aviso o un falso silencio: qué muestra sin candidato, sin requisitos, o con la spec cambiada?
6. ¿Cada prueba falla si rompés la línea que vigila? Corré las mutaciones: ¿sobrevive alguna?
7. ¿Lo que dicen los documentos, los mensajes y los docstrings es lo que el código hace hoy?
8. ¿El verificador mide la estabilidad después de su última corrida, cuenta cualquier caso nuevo y no cuenta su propia carpeta?
9. Si un hallazgo anterior fue de una clase de problema, ¿arreglaste la clase entera o sólo el caso que te señalaron?

## Dos reglas detrás de la lista

- **Reusar antes de escribir.** Si el código ya tiene un ayudante para lo que necesitás, usalo; arreglar un caso con un parche nuevo en cada ronda es lo que más rondas costó.
- **Arreglar la clase, no el caso.** Cuando un revisor señala un problema de una clase, buscá todos los lugares de esa clase y arreglalos juntos; si no, la próxima ronda trae la variante siguiente.

## De dónde salen las clases

Del recuento de los hallazgos altos y medios de los cambios cerrados desde el 24 de octubre de 2026, agrupados por tipo. La lista se revisa cuando haya datos nuevos: si una clase deja de aparecer, sale; si aparece una nueva que se repite, entra. La fuente de las preguntas es `oracle_factory/lista_previa.py`, y una prueba comprueba que este documento las trae todas con el mismo texto.

## Qué no es

No es un gate ni reemplaza a la revisión independiente, a las mutaciones ni a Oracle. Tampoco mide si se cumplió: si reduce las rondas se mide después, sobre los cambios que vengan, con el mismo método.
