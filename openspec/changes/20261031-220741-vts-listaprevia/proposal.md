# Una lista previa a la revisión con las clases de problema que más rondas cuestan

## Por qué

Medimos los 19 cambios cerrados desde el 24/10: el lazo de rondas de revisión es el cuello de botella principal. La mediana es de 2 a 3 rondas por cambio y el máximo de 6; las rondas 2 y 3 traen más hallazgos que la primera (68 y 58 contra 39), porque cada corrección abre superficie nueva. Los hallazgos altos y medios se repiten por clases: las rutas con «..» y enlaces simbólicos pasan de 3 en la primera ronda a 17 en la tercera o más, y aparecen valores raros que hacen caer el comando, lectores que no leen el formato igual que la herramienta que ya lo lee, avisos falsos o silenciados, pruebas que no detectan una mutación y textos que no dicen lo que el código hace. Muchas veces el ayudante correcto ya existía y un revisor lo señaló después de varios parches. Cada ronda cuesta corregir, reconfirmar medidas, regenerar la evidencia y esperar una revisión de unos 17 minutos.

## Qué cambia

- Hay una lista corta de verificación del autor, con una pregunta por cada clase de problema que más se repite y la regla de arreglar la clase y no sólo el caso, y de reusar el ayudante que ya existe antes de escribir otro.
- `pedir-revision` muestra esa lista antes de lanzar al revisor. Es un recordatorio: no bloquea ni cambia nada del pedido.
- La lista vive en un documento, `docs/lista-previa.md`, y el documento y el mensaje salen de la misma fuente, de modo que no pueden decir cosas distintas.
- La guía para agentes que genera `oracle-factory agentes` nombra la lista y dice cuándo mirarla.

## Fuera de alcance

- Revisar la spec antes de implementar: es un cambio siguiente.
- Bloquear la revisión si la lista no se cumplió, o comprobar automáticamente que se cumplió.
- Cambiar los revisores, sus modelos o sus cuotas.
- Medir si la lista reduce las rondas: se mide después con el mismo método, sobre los cambios que vengan.

## Decisiones humanas

- Que sea un recordatorio y no un gate.
- Que las clases salgan de la medición propia y se revisen cada tanto con nuevos datos.
