Sos un revisor independiente del cambio 20261017-121631-web-guias de un proyecto que usa Oracle Factory: «Las guías con la fábrica viva». No escribiste este código.
NO edites el checkout, no hagas commits ni decidas nada por la persona: tu trabajo es encontrar defectos y contarlos con evidencia.

Qué tiene que hacer el cambio:
- Propuesta: /home/workstation/Dev/factory-web-guias/openspec/changes/20261017-121631-web-guias/proposal.md
- Spec (lo que se promete, con sus escenarios): /home/workstation/Dev/factory-web-guias/openspec/changes/20261017-121631-web-guias/specs/web/spec.md

Qué revisar:
- Checkout del candidato 5e186b8 (sólo lectura): /home/workstation/Dev/factory-web-guias/.factory/local/revisiones/5e186b8
- Paquete de Oracle Clue con el diff y el contexto: /home/workstation/Dev/factory-web-guias/.factory/cambios/20261017-121631-web-guias/candidatos/5e186b8/clue/paquete-agy-1.json

Vueltas anteriores de este cambio (ya corregidas; mirá que sigan cerradas y que no haya regresiones):
- .factory/cambios/20261017-121631-web-guias/candidatos/41b3ee9/revision/agy-1.json
- .factory/cambios/20261017-121631-web-guias/candidatos/41b3ee9/revision/codex-1.json
- .factory/cambios/20261017-121631-web-guias/candidatos/9e97206/revision/agy-1.json
- .factory/cambios/20261017-121631-web-guias/candidatos/9e97206/revision/codex-1.json
Fuera del paquete, porque no son producto (.factory, tareas): 18 archivos de registros y evidencia de Factory; no los revises.

Cómo trabajar: leé la spec y el diff; contrastá cada promesa con el código y con las pruebas; buscá casos que fallen, afirmaciones que el
código no cumple y pruebas que no prueban lo que dicen. Si podés, hacé mutaciones a mano sobre copias en tu carpeta y decí cuáles sobreviven.
Mandá la salida larga a archivos de tu carpeta y leé sólo el resumen.

Entregable: un informe JSON en /home/workstation/Dev/factory-web-guias/.factory/local/revisores/5e186b8-agy-1/informe.json con este formato (schema oracle-clue.review/v1):
- schema_version "oracle-clue.review/v1"; repo, base, head, diff_sha256 y context_sha256 copiados del paquete;
- provider {"name": "agy", "model": "gemini-3.8-flash-high"};
- findings: lista de hallazgos, cada uno con id, kind, severity (alta|media|baja|informativa), confidence (0 a 1), title, explanation,
  location {file, start_line, end_line, side: "head"} DENTRO de los rangos del diff del paquete, trigger, evidence, related_requirement,
  status "pendiente" y verification;
- review_status ("completo" o "incompleto") y limitations (qué corriste y qué no).
Sin hallazgos: findings vacía, explicado en limitations. Validalo antes de terminar con:
  oracle-clue validar /home/workstation/Dev/factory-web-guias/.factory/local/revisores/5e186b8-agy-1/informe.json --paquete /home/workstation/Dev/factory-web-guias/.factory/cambios/20261017-121631-web-guias/candidatos/5e186b8/clue/paquete-agy-1.json --repo /home/workstation/Dev/factory-web-guias/.factory/local/revisiones/5e186b8
y terminá con un resumen corto en español.

Indicaciones de quien pide la revisión:
Vuelta 3. En la 2 codex (CG-001) y agy (AGY-001) marcaron que la normalización de espacios aplanaba los saltos de línea de los comandos, y agy (AGY-002) que no se comprobaba cuál escena tiene cada guía. Corregido: en pre y code el texto se compara tal cual; recorrer_cada_guia exige guia, modos y equipo; el texto congelado se regeneró desde main. Verificá que las correcciones sean de verdad y buscá lo que siga. Revisá el cambio en las guías: site/desde-cero.html, site/modos.html y site/colaboracion.html (escena al principio y personajes con globitos marcados data-viva), site/viva.js (escenas guia, modos y equipo; los secretos sólo en la portada), el CSS agregado al final de site/style.css, tests/texto_guias.cjs, tests/datos/guias-texto.json (el texto congelado de antes), tests/test_web_guias.cjs, tests/test_web_guias.py, tools/verify_web_guias.py y catalogos/factory_guias.*.oracle, contra los 2 requisitos de la spec. Mirá especialmente: que el texto y los comandos de las guías no hayan cambiado (también lo que la extracción de texto podría no ver), que lo que dicen los globitos sea correcto sobre Factory (modos, revisión, Oracle, Clue), accesibilidad (role=img, textos alternativos, movimiento reducido), animaciones que pisen la posición de un sprite, desbordes en pantallas chicas, y que la portada siga igual. Para correr las pruebas usá exactamente, en primer plano y desde la raíz del checkout: NODE_PATH=/home/workstation/Dev/factory-web-guias/node_modules node tests/test_web_guias.cjs <escenario> con cada uno de: recorrer_cada_guia movimiento_reducido_y_pantalla_chica comparar_con_la_version_anterior (Chromium está en /usr/bin/chromium). Si Chromium no arranca en tu sandbox, eso no es parte de la revisión: revisá estáticamente, anotá el límite y marcá la revisión completa. No corras la suite completa de Python. Nombrá archivos con rutas relativas.
