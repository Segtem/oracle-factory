# Una lista previa a la revisión con las clases de problema que más rondas cuestan

## Por qué

Medimos los cambios cerrados desde el 24/10 (`python tools/medir_rondas.py`): el lazo de rondas de revisión es el cuello de botella principal. La mediana es de 2 rondas por cambio y el máximo de 6, y cada ronda tiene un costo fijo: corregir, reconfirmar medidas, regenerar la evidencia y esperar una revisión de unos 17 minutos, aunque cada ronda traiga menos hallazgos. Los hallazgos convergen: la primera ronda trae casi dos tercios de los hallazgos altos y medios (85 de 133) y de la tercera en adelante sólo 18. Lo que trae la primera ronda se repite por clases: documentos y mensajes que no dicen lo que hace el código, rutas con «..» y enlaces simbólicos, falsos avisos o silencios, valores raros que hacen caer el comando, lectura distinta de la de la herramienta que ya lee el formato y pruebas que no detectan una mutación. Muchas veces el ayudante correcto ya existía y un revisor lo señaló después. Si quien escribe atrapa esas clases antes de pedir la revisión, la primera ronda trae menos y las siguientes se acortan o se evitan.

## Qué cambia

- Hay una lista corta de verificación del autor, con una pregunta por cada clase de problema que más se repite y la regla de arreglar la clase y no sólo el caso, y de reusar el ayudante que ya existe antes de escribir otro.
- `pedir-revision` muestra esa lista antes de lanzar al revisor. Es un recordatorio: no bloquea ni cambia nada del pedido.
- La lista vive en un documento, `docs/lista-previa.md`, y el documento y el mensaje salen de la misma fuente, de modo que no pueden decir cosas distintas: una comprobación exige que la lista numerada del documento sea exactamente la del código, en el mismo orden.
- La medición que justifica las clases es reproducible: `tools/medir_rondas.py` cuenta los hallazgos por ronda, ordenando las rondas por los eventos de revisión y no por el nombre ni la fecha de los archivos.
- La guía para agentes que genera `oracle-factory agentes` nombra la lista y dice cuándo mirarla.

## Fuera de alcance

- Revisar la spec antes de implementar: es un cambio siguiente.
- Bloquear la revisión si la lista no se cumplió, o comprobar automáticamente que se cumplió.
- Cambiar los revisores, sus modelos o sus cuotas.
- Medir si la lista reduce las rondas: se mide después con el mismo método, sobre los cambios que vengan.

## Decisiones humanas

- Que sea un recordatorio y no un gate.
- Que las clases salgan de la medición propia y se revisen cada tanto con nuevos datos.
