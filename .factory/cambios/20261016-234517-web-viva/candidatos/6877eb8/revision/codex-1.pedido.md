Sos un revisor independiente del cambio 20261016-234517-web-viva de un proyecto que usa Oracle Factory: «Una portada viva: pixel art, personajes, escenas animadas y un minijuego de decisiones». No escribiste este código.
NO edites el checkout, no hagas commits ni decidas nada por la persona: tu trabajo es encontrar defectos y contarlos con evidencia.

Qué tiene que hacer el cambio:
- Propuesta: /home/workstation/Dev/factory-web-viva/openspec/changes/20261016-234517-web-viva/proposal.md
- Spec (lo que se promete, con sus escenarios): /home/workstation/Dev/factory-web-viva/openspec/changes/20261016-234517-web-viva/specs/web/spec.md

Qué revisar:
- Checkout del candidato 6877eb8 (sólo lectura): /home/workstation/Dev/factory-web-viva/.factory/local/revisiones/6877eb8
- Paquete de Oracle Clue con el diff y el contexto: /home/workstation/Dev/factory-web-viva/.factory/cambios/20261016-234517-web-viva/candidatos/6877eb8/clue/paquete-codex-1.json

Fuera del paquete, porque no son producto (.factory, tareas): 2 archivos de registros y evidencia de Factory; no los revises.

Cómo trabajar: leé la spec y el diff; contrastá cada promesa con el código y con las pruebas; buscá casos que fallen, afirmaciones que el
código no cumple y pruebas que no prueban lo que dicen. Si podés, hacé mutaciones a mano sobre copias en tu carpeta y decí cuáles sobreviven.
Mandá la salida larga a archivos de tu carpeta y leé sólo el resumen.

Entregable: un informe JSON en /home/workstation/Dev/factory-web-viva/.factory/local/revisores/6877eb8-codex-1/informe.json con este formato (schema oracle-clue.review/v1):
- schema_version "oracle-clue.review/v1"; repo, base, head, diff_sha256 y context_sha256 copiados del paquete;
- provider {"name": "codex", "model": "gpt-6-luna"};
- findings: lista de hallazgos, cada uno con id, kind, severity (alta|media|baja|informativa), confidence (0 a 1), title, explanation,
  location {file, start_line, end_line, side: "head"} DENTRO de los rangos del diff del paquete, trigger, evidence, related_requirement,
  status "pendiente" y verification;
- review_status ("completo" o "incompleto") y limitations (qué corriste y qué no).
Sin hallazgos: findings vacía, explicado en limitations. Validalo antes de terminar con:
  oracle-clue validar /home/workstation/Dev/factory-web-viva/.factory/local/revisores/6877eb8-codex-1/informe.json --paquete /home/workstation/Dev/factory-web-viva/.factory/cambios/20261016-234517-web-viva/candidatos/6877eb8/clue/paquete-codex-1.json --repo /home/workstation/Dev/factory-web-viva/.factory/local/revisiones/6877eb8
y terminá con un resumen corto en español.

Indicaciones de quien pide la revisión:
Vuelta 1. Revisá la portada nueva: site/index.html, site/pixel.js (sprites), site/viva.js (escenas, personajes, minijuego, easter eggs), site/juego.js (la máquina de estados del minijuego), el CSS agregado al final de site/style.css, el ajuste de las guías (link Jugá), tests/test_juego.cjs, tests/test_web_viva.cjs, tests/test_web_viva.py, el ajuste de tests/test_site.cjs, tools/verify_web_viva.py y catalogos/factory_viva.*.oracle, contra los 3 requisitos de la spec. Mirá especialmente: que las reglas del minijuego sean las de la CLI de Factory (oracle_factory/cli.py: corte por severidad, riesgo con motivo, medidas sin acordar, cierre), accesibilidad (teclado, foco, aria-live, aria-disabled, movimiento reducido, textos alternativos), que los easter eggs no tapen texto ni muevan el foco, animaciones que pisen la posición de un sprite, desbordes en pantallas chicas, y si las pruebas prueban de verdad cada escenario. Para correr las pruebas usá exactamente, en primer plano y desde la raíz del checkout: NODE_PATH=/home/workstation/Dev/factory-web-viva/node_modules node tests/test_juego.cjs y NODE_PATH=/home/workstation/Dev/factory-web-viva/node_modules node tests/test_web_viva.cjs <escenario> con cada uno de: recorrer_la_portada movimiento_reducido_y_pantalla_chica una_partida_que_cierra_en_verde aprobar_con_un_hallazgo_abierto_y_medidas_sin_acordar jugar_solo_con_teclado encontrar_los_tres (Chromium está en /usr/bin/chromium). No corras la suite completa de Python. Nombrá archivos con rutas relativas.
