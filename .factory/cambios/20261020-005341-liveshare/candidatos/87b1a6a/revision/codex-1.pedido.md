Sos un revisor independiente del cambio 20261020-005341-liveshare de un proyecto que usa Oracle Factory: «El tablero en pair programming: presencia, tablero compartido y chat con Live Share». No escribiste este código.
NO edites el checkout, no hagas commits ni decidas nada por la persona: tu trabajo es encontrar defectos y contarlos con evidencia.

Qué tiene que hacer el cambio:
- Propuesta: /home/workstation/Dev/factory-liveshare/openspec/changes/20261020-005341-liveshare/proposal.md
- Spec (lo que se promete, con sus escenarios): /home/workstation/Dev/factory-liveshare/openspec/changes/20261020-005341-liveshare/specs/ide/spec.md

Qué revisar:
- Checkout del candidato 87b1a6a (sólo lectura): /home/workstation/Dev/factory-liveshare/.factory/local/revisiones/87b1a6a
- Paquete de Oracle Clue con el diff y el contexto: /home/workstation/Dev/factory-liveshare/.factory/cambios/20261020-005341-liveshare/candidatos/87b1a6a/clue/paquete-codex-1.json

Vueltas anteriores de este cambio (ya corregidas; mirá que sigan cerradas y que no haya regresiones):
- .factory/cambios/20261020-005341-liveshare/candidatos/6592bb8/revision/agy-1.json
- .factory/cambios/20261020-005341-liveshare/candidatos/6592bb8/revision/codex-1.json
- .factory/cambios/20261020-005341-liveshare/candidatos/1f80205/revision/agy-1.json
- .factory/cambios/20261020-005341-liveshare/candidatos/1f80205/revision/codex-1.json
Fuera del paquete, porque no son producto (.factory, tareas): 18 archivos de registros y evidencia de Factory; no los revises.

Cómo trabajar: leé la spec y el diff; contrastá cada promesa con el código y con las pruebas; buscá casos que fallen, afirmaciones que el
código no cumple y pruebas que no prueban lo que dicen. Si podés, hacé mutaciones a mano sobre copias en tu carpeta y decí cuáles sobreviven.
Mandá la salida larga a archivos de tu carpeta y leé sólo el resumen.

Entregable: un informe JSON en /home/workstation/Dev/factory-liveshare/.factory/local/revisores/87b1a6a-codex-1/informe.json con este formato (schema oracle-clue.review/v1):
- schema_version "oracle-clue.review/v1"; repo, base, head, diff_sha256 y context_sha256 copiados del paquete;
- provider {"name": "codex", "model": "gpt-6-luna"};
- findings: lista de hallazgos, cada uno con id, kind, severity (alta|media|baja|informativa), confidence (0 a 1), title, explanation,
  location {file, start_line, end_line, side: "head"} DENTRO de los rangos del diff del paquete, trigger, evidence, related_requirement,
  status "pendiente" y verification;
- review_status ("completo" o "incompleto") y limitations (qué corriste y qué no).
Sin hallazgos: findings vacía, explicado en limitations. Validalo antes de terminar con:
  oracle-clue validar /home/workstation/Dev/factory-liveshare/.factory/local/revisores/87b1a6a-codex-1/informe.json --paquete /home/workstation/Dev/factory-liveshare/.factory/cambios/20261020-005341-liveshare/candidatos/87b1a6a/clue/paquete-codex-1.json --repo /home/workstation/Dev/factory-liveshare/.factory/local/revisiones/87b1a6a
y terminá con un resumen corto en español.

Indicaciones de quien pide la revisión:
Vuelta 3. En la vuelta 2 agy no dejó hallazgos y codex uno bajo (LS-SEC-07), corregido: el comando que pide un invitado sólo puede tener letras, números, espacios y . _ / : = - (sin operadores de shell); el del propio panel sigue como antes. Verificá esa corrección y buscá lo que quede. Revisá el cambio: editores/vscode/liveshare.js (la API de Live Share pedida a su extensión, el servicio oracle-factory del anfitrión con sus pedidos tablero, terminal, mensaje y diff, el proxy del invitado, la presencia), editores/vscode/extension.js (datosLocales, pintarTablero con la sesión, diffLocal, escribirComando, guardarMensaje, mensajeDelTablero para anfitrión e invitado, activate y el aviso a los invitados), editores/vscode/tablero.js (En la sesión, el chat por cambio y el formulario), package.json 0.3.0 (virtualWorkspaces) y empaquetar.py; en oracle_factory/cli.py el comando mensaje (con --de) y en oracle_factory/tablero.py texto y via en la línea de tiempo; README; tests/test_liveshare.py, tests/liveshare_en_node.cjs, tools/verify_liveshare.py y catalogos/factory_liveshare.*.oracle, contra los 3 requisitos de la spec. Mirá especialmente lo que llega de otra máquina: un invitado que pide abrir archivos fuera del espacio compartido, comandos que no son oracle-factory o tienen varias líneas, mensajes con HTML o enormes, nombres falsos, y que el tablero no decida nada; también que sin Live Share todo siga igual. Para correr las pruebas usá exactamente, en primer plano y desde la raíz del checkout: PYTHONPATH=. /home/workstation/Dev/factory-liveshare/.venv/bin/python -m unittest tests.test_liveshare tests.test_tablero </dev/null . Necesita node; si node no arranca, marcá esas pruebas como no ejecutadas y revisá el código. No corras la suite completa. Nombrá archivos con rutas relativas.
