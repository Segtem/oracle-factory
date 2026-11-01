# La puerta local de salida

Antes de publicar, Factory comprueba en segundos lo que es barato y determinista, en vez de dejarlo a la memoria de quien empuja. Hoy son dos comprobaciones; es una lista a la que se pueden sumar otras (analizadores estáticos, un `verificar` para CI).

```bash
oracle-factory puerta                 # lo que el remoto todavía no tiene
oracle-factory puerta HEAD~3..HEAD    # un rango de git log
oracle-factory hooks                  # instala el hook pre-push que la llama en cada git push
```

## Qué comprueba

**Secretos.** Busca credenciales en las líneas agregadas por *todos* los commits (un commit de merge cuenta con lo que agrega frente a todos sus padres, p. ej. un secreto escrito al resolver un conflicto) que se van a publicar, no sólo en el resultado final: un secreto agregado en un commit y quitado en el siguiente igual viaja en la historia. Busca valores con forma de credencial, no palabras: una clave privada, una clave de AWS (permanente `AKIA…` o temporal `ASIA…`), un token de GitHub, de PyPI o de Slack, una clave de Google, una clave tipo `sk-`, y una asignación sospechosa (un nombre como `token`, `secret`, `password` o `api_key` asignado a un valor entre comillas de 16 o más caracteres sin espacios y con letras y dígitos). Muestra el archivo, la línea, el commit y el tipo con el valor tapado: nunca imprime el secreto entero.

**Verificaciones.** Corre `agentes --verificar`, `kb --verificar` y `resumen --verificar` (todas, aunque una falle) y nombra cuál falló. Una guía para agentes vieja **bloquea**: confunde a los agentes y no se arregla sola. Un conocimiento (`kb/`) o un resumen vencidos **avisan sin bloquear**: Factory los rehace al integrar, así que vencidos son un estado cotidiano (por ejemplo, tras agregar un mensaje a un cambio). Si un proyecto todavía no generó su `kb/` o su resumen, esa verificación se omite y se dice: no hay nada vencido que corregir, y bloquear el primer push de un proyecto nuevo sería hostil.

**Sólo lectura.** La puerta no escribe nada en el proyecto: ni siquiera cuando el conocimiento está vencido. (Al probarla apareció un defecto anterior: `oracle-factory agentes`, con o sin `--verificar`, regeneraba `kb/` al terminar porque no figuraba entre los comandos de sólo lectura; ahora figura, y `agentes` sigue escribiendo `AGENTS.md` pero ya no `kb/`.)

## El hook pre-push

`oracle-factory hooks` (y `init`) instala un hook `pre-push` que llama a la puerta con lo que Git está por empujar: una rama nueva se mira desde lo que ningún remoto tiene, una existente desde el commit remoto, y borrar una rama remota no se mira. No pisa un hook `pre-push` ajeno: avisa y te da la línea para encadenarla en el tuyo. No toca `core.hooksPath` ni ninguna otra configuración de Git.

La puerta bloquea el push sólo cuando **encuentra algo** (sale con el código 3). Cualquier otra salida distinta de cero (el intérprete de Factory borrado, un proyecto mal configurado, un error interno) avisa y deja pasar: una herramienta rota no tiene que impedir trabajar.

## Saltearla y eximir

- `git push --no-verify` saltea el hook, como cualquier hook de Git. Revisá antes lo que publicás.
- Una línea con la marca `factory:secreto-ok` queda exenta: sirve para un valor de ejemplo conocido o una prueba.

## Límites

Es un recordatorio rápido con patrones, no un escáner completo: no busca entropía alta ni formatos que no listó, y una credencial con otra forma puede pasar. Una asignación con un valor sin dígitos (`password = "una-frase-larga"`) tampoco se marca. No corre la suite de pruebas (tarda minutos) ni analizadores estáticos: son tareas aparte (`analizadores`, `ci-remoto`). Una asignación cuyo valor está en otra línea (`api_key = (` y el valor abajo, o un YAML con el valor en la línea siguiente) no se marca: se mira línea por línea; los formatos con forma propia (clave de AWS, token de GitHub…) sí se marcan estén donde estén. Las líneas se miran enteras, sea cual sea su largo.
