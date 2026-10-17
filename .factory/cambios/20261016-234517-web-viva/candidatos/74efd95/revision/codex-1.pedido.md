Sos un revisor independiente del cambio 20261016-234517-web-viva de un proyecto que usa Oracle Factory: «Una portada viva: pixel art, personajes, escenas animadas y un minijuego de decisiones». No escribiste este código.
NO edites el checkout, no hagas commits ni decidas nada por la persona: tu trabajo es encontrar defectos y contarlos con evidencia.

Qué tiene que hacer el cambio:
- Propuesta: /home/workstation/Dev/factory-web-viva/openspec/changes/20261016-234517-web-viva/proposal.md
- Spec (lo que se promete, con sus escenarios): /home/workstation/Dev/factory-web-viva/openspec/changes/20261016-234517-web-viva/specs/web/spec.md

Qué revisar:
- Checkout del candidato 74efd95 (sólo lectura): /home/workstation/Dev/factory-web-viva/.factory/local/revisiones/74efd95
- Paquete de Oracle Clue con el diff y el contexto: /home/workstation/Dev/factory-web-viva/.factory/cambios/20261016-234517-web-viva/candidatos/74efd95/clue/paquete-codex-1.json

Vueltas anteriores de este cambio (ya corregidas; mirá que sigan cerradas y que no haya regresiones):
- .factory/cambios/20261016-234517-web-viva/candidatos/6877eb8/revision/agy-1.json
- .factory/cambios/20261016-234517-web-viva/candidatos/6877eb8/revision/codex-1.json
Fuera del paquete, porque no son producto (.factory, tareas): 10 archivos de registros y evidencia de Factory; no los revises.

Cómo trabajar: leé la spec y el diff; contrastá cada promesa con el código y con las pruebas; buscá casos que fallen, afirmaciones que el
código no cumple y pruebas que no prueban lo que dicen. Si podés, hacé mutaciones a mano sobre copias en tu carpeta y decí cuáles sobreviven.
Mandá la salida larga a archivos de tu carpeta y leé sólo el resumen.

Entregable: un informe JSON en /home/workstation/Dev/factory-web-viva/.factory/local/revisores/74efd95-codex-1/informe.json con este formato (schema oracle-clue.review/v1):
- schema_version "oracle-clue.review/v1"; repo, base, head, diff_sha256 y context_sha256 copiados del paquete;
- provider {"name": "codex", "model": "gpt-6-luna"};
- findings: lista de hallazgos, cada uno con id, kind, severity (alta|media|baja|informativa), confidence (0 a 1), title, explanation,
  location {file, start_line, end_line, side: "head"} DENTRO de los rangos del diff del paquete, trigger, evidence, related_requirement,
  status "pendiente" y verification;
- review_status ("completo" o "incompleto") y limitations (qué corriste y qué no).
Sin hallazgos: findings vacía, explicado en limitations. Validalo antes de terminar con:
  oracle-clue validar /home/workstation/Dev/factory-web-viva/.factory/local/revisores/74efd95-codex-1/informe.json --paquete /home/workstation/Dev/factory-web-viva/.factory/cambios/20261016-234517-web-viva/candidatos/74efd95/clue/paquete-codex-1.json --repo /home/workstation/Dev/factory-web-viva/.factory/local/revisiones/74efd95
y terminá con un resumen corto en español.

Indicaciones de quien pide la revisión:
Vuelta 2. En la 1 codex marcó WV-01 (los secretos dentro de una imagen accesible; además el SVG estaba aria-hidden) y agy agy-web-viva-1 (opciones no disponibles sin porqué: title undefined y foco que salta), agy-web-viva-3 (el clic del gato se llevaba el foco), y bajas (la persona de trabajar quieta, el globo sin anuncio, el desborde sólo probado sin animar, design.md). Corregido: botones de HTML sobre la escena (dentro de .escena-marco, en porcentajes del viewBox) con mousedown que no toma el foco; porque en riesgo/descartar ya resueltos; quien trabaja; role=status en el globo; desborde con escenas vivas; design.md. Verificá que las correcciones sean de verdad y buscá lo que siga. Revisá la portada nueva: site/index.html, site/pixel.js (sprites), site/viva.js (escenas, personajes, minijuego, easter eggs), site/juego.js (la máquina de estados del minijuego), el CSS agregado al final de site/style.css, el ajuste de las guías (link Jugá), tests/test_juego.cjs, tests/test_web_viva.cjs, tests/test_web_viva.py, el ajuste de tests/test_site.cjs, tools/verify_web_viva.py y catalogos/factory_viva.*.oracle, contra los 3 requisitos de la spec. Mirá especialmente: que las reglas del minijuego sean las de la CLI de Factory (oracle_factory/cli.py: corte por severidad, riesgo con motivo, medidas sin acordar, cierre), accesibilidad (teclado, foco, aria-live, aria-disabled, movimiento reducido, textos alternativos), que los easter eggs no tapen texto ni muevan el foco, animaciones que pisen la posición de un sprite, desbordes en pantallas chicas, y si las pruebas prueban de verdad cada escenario. Para correr las pruebas usá exactamente, en primer plano y desde la raíz del checkout: NODE_PATH=/home/workstation/Dev/factory-web-viva/node_modules node tests/test_juego.cjs y NODE_PATH=/home/workstation/Dev/factory-web-viva/node_modules node tests/test_web_viva.cjs <escenario> con cada uno de: recorrer_la_portada movimiento_reducido_y_pantalla_chica una_partida_que_cierra_en_verde aprobar_con_un_hallazgo_abierto_y_medidas_sin_acordar jugar_solo_con_teclado encontrar_los_tres (Chromium está en /usr/bin/chromium). Si Chromium no arranca en tu sandbox (por ejemplo, setsockopt: Operation not permitted), eso no es parte de la revisión: corré test_juego.cjs, revisá el resto estáticamente, anotá el límite y marcá la revisión completa. No corras la suite completa de Python. Nombrá archivos con rutas relativas.
