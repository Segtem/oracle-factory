# Una puerta local de salida: escaneo de secretos y verificaciones antes de cada push

## Por qué

Antes de empujar a un remoto público hoy se hacen a mano tres cosas: un `grep` de patrones de secretos sobre el diff, y las verificaciones `agentes`, `kb` y `resumen` con `--verificar`. Depende de que alguien se acuerde y de que lo haga bien: el `grep` ya dio falsos positivos (la palabra «secreto» en un informe de revisión) y sólo mira el diff contra el remoto, no los commits intermedios, de modo que un secreto agregado en un commit y quitado en el siguiente igual viaja en la historia que se publica. El informe de Shift Left que estudiamos pide exactamente lo contrario: que los controles de seguridad sean un componente permanente del repositorio y no un script ad hoc, y que corran antes de que el defecto salga. Cuestan segundos (las verificaciones tardan unos 2 segundos), así que no hay motivo para dejarlas a la memoria.

Hay tres tareas abiertas que tocan el tema: `shift-left` (correr lo determinista en el pre-push), `analizadores` (adaptar ruff, bandit y similares) y `ci-remoto` (un `verificar` para CI). Esta es la parte que no depende de ninguna de ellas, y queda hecha como una lista de comprobaciones a la que se pueden sumar después.

## Qué cambia

- Un comando nuevo, `oracle-factory puerta`, corre las comprobaciones y sale con código distinto de cero si alguna falla:
  - **secretos:** busca claves privadas, claves de AWS, tokens de GitHub, de PyPI y de Slack, claves de Google y claves tipo `sk-…`, y asignaciones sospechosas (`token = "…"` con un valor largo), en las líneas agregadas por **todos** los commits del rango que se va a publicar, no sólo en el resultado final. Muestra archivo, línea, commit y tipo, con el valor tapado: nunca imprime el secreto entero.
  - **verificaciones:** `agentes --verificar`, `kb --verificar` y `resumen --verificar`. Una guía para agentes vieja bloquea: confunde a los agentes y no se arregla sola. Un conocimiento o un resumen vencidos avisan sin bloquear, porque Factory los rehace al integrar. Lo que el proyecto todavía no generó se omite, para no frenar el primer push de un proyecto nuevo.
- La puerta es de **sólo lectura**: no escribe nada en el proyecto. Para eso se corrige un defecto que apareció al probarla: `oracle-factory agentes` (con o sin `--verificar`) regeneraba `kb/` al terminar, porque no figuraba entre los comandos de sólo lectura; una verificación que escribe dejaría el árbol de trabajo distinto después de un push.
- `oracle-factory hooks` instala además un hook `pre-push` que llama a la puerta con los commits que se van a empujar. Bloquea el push si falla, y se puede saltear con `git push --no-verify`, como cualquier hook de Git. Si el intérprete de Factory no está (un `.venv` borrado), el hook avisa y deja pasar: una herramienta rota no impide trabajar.
- Una línea con la marca `factory:secreto-ok` queda exenta, para los casos conocidos (un valor de ejemplo, una prueba).

## Fuera de alcance

- Correr la suite de pruebas completa (tarda minutos): sigue siendo parte de la integración.
- Analizadores estáticos (ruff, bandit, SARIF): es la tarea `analizadores`.
- El comando `verificar` y el workflow de CI de `ci-remoto`.
- Cambiar la configuración de Git (`core.hooksPath`) o instalar hooks sin que la persona corra `oracle-factory hooks`.
- Reescribir historia publicada.

## Decisiones humanas

- Que la puerta bloquee el push (con salida por `--no-verify`) y no sólo avise.
- Que la lista de patrones empiece corta y de valores con forma de credencial, no de palabras.
