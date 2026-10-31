# Lista previa a la revisión

Antes de pedir una revisión, quien escribe el cambio mira esta lista. No bloquea nada y no cambia el pedido que recibe el revisor: es un recordatorio, y `oracle-factory pedir-revision` la muestra antes de lanzar al revisor.

## Por qué existe

Medimos los cambios cerrados de Factory (`python tools/medir_rondas.py`, que se puede volver a correr). El lazo de rondas de revisión es el cuello de botella principal: la mediana es de 2 rondas por cambio y el máximo de 6, y cada ronda tiene un costo fijo (corregir, reconfirmar medidas, regenerar la evidencia, esperar a un revisor) aunque cada vez traiga menos. Los hallazgos convergen: la primera ronda trae casi dos tercios de los hallazgos altos y medios (85 de 133) y la tercera y siguientes sólo 18; en total, 130, 46, 24, 10 y 2 hallazgos en las rondas 1 a 5. Lo que trae la primera ronda se repite por clases, y son las que esta lista pregunta antes: documentos y mensajes que no dicen lo que hace el código (20 en la ronda 1), rutas con `..` y enlaces simbólicos (18), falsos avisos o silencios (13), valores raros que hacen caer el comando (11), lectura distinta de la de la herramienta que ya lee el formato (9) y pruebas que no detectan una mutación (9). Muchas veces el ayudante correcto ya existía. Si el autor atrapa esas clases antes de pedir la revisión, la primera ronda trae menos y las siguientes se acortan o se evitan.

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

- **Reusar antes de escribir.** Si el código ya tiene un ayudante para lo que necesitás, usalo: es más barato que parchear un caso nuevo en cada ronda.
- **Arreglar la clase, no el caso.** Cuando un revisor señala un problema de una clase, buscá todos los lugares de esa clase y arreglalos juntos. Esta regla tiene menos respaldo que las demás: en los datos, cada clase baja ronda a ronda, así que es una buena práctica pero no un hallazgo de la medición.

## De dónde salen las clases

Del recuento de los hallazgos altos y medios de los cambios cerrados desde el 24 de octubre de 2026, agrupados por palabras clave de su título y su explicación (`tools/medir_rondas.py` imprime la tabla y el criterio está en el código). Es una medición aproximada: una palabra clave puede poner un hallazgo en más de una clase o en ninguna, y algunas preguntas (como la del verificador) vienen sobre todo de hallazgos que se repitieron aunque algunos fueran bajos. La lista se revisa cuando haya datos nuevos: si una clase deja de aparecer, sale; si aparece una nueva que se repite, entra. La fuente de las preguntas es `oracle_factory/lista_previa.py`, y una prueba comprueba que la lista numerada de este documento es exactamente esa, en el mismo orden.

## Qué no es

No es un gate ni reemplaza a la revisión independiente, a las mutaciones ni a Oracle. Tampoco mide si se cumplió: si reduce las rondas se mide después, sobre los cambios que vengan, con el mismo método.
