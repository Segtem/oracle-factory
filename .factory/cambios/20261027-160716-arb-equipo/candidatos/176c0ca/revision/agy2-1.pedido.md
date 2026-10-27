Sos un revisor independiente del cambio 20261027-160716-arb-equipo de un proyecto que usa Oracle Factory: «El tablero dice a quién necesita cada cambio y qué pasó hace poco». No escribiste este código.
NO edites el checkout, no hagas commits ni decidas nada por la persona: tu trabajo es encontrar defectos y contarlos con evidencia.

Qué tiene que hacer el cambio:
- Propuesta: /home/workstation/Dev/factory-tablero-equipo/openspec/changes/20261027-160716-arb-equipo/proposal.md
- Spec (lo que se promete, con sus escenarios): /home/workstation/Dev/factory-tablero-equipo/openspec/changes/20261027-160716-arb-equipo/specs/tablero/spec.md

Qué revisar:
- Checkout del candidato 176c0ca (sólo lectura): /home/workstation/Dev/factory-tablero-equipo/.factory/local/revisiones/176c0ca-agy2-1
- Paquete de Oracle Clue con el diff y el contexto: /home/workstation/Dev/factory-tablero-equipo/.factory/cambios/20261027-160716-arb-equipo/candidatos/176c0ca/clue/paquete-agy2-1.json

Vueltas anteriores de este cambio (ya corregidas; mirá que sigan cerradas y que no haya regresiones):
- .factory/cambios/20261027-160716-arb-equipo/candidatos/4997662/revision/agy-1.json
- .factory/cambios/20261027-160716-arb-equipo/candidatos/4997662/revision/agy2-1.json
Fuera del paquete, porque no son producto (.factory, kb/README.md, kb/cambios/20261027-160716-arb-equipo.md, kb/requisitos/tablero_ca9f1ed71bc00602b.actividad_reciente_del_proyecto.md, kb/requisitos/tablero_ca9f1ed71bc00602b.el_tablero_dice_a_quien_necesita.md, tareas): 15 archivos de registros y evidencia de Factory; no los revises.

Cómo trabajar: leé la spec y el diff; contrastá cada promesa con el código y con las pruebas; buscá casos que fallen, afirmaciones que el
código no cumple y pruebas que no prueban lo que dicen. Si podés, hacé mutaciones a mano sobre copias en tu carpeta y decí cuáles sobreviven.
Mandá la salida larga a archivos de tu carpeta y leé sólo el resumen.

Entregable: un informe JSON en /home/workstation/Dev/factory-tablero-equipo/.factory/local/revisores/176c0ca-agy2-1/informe.json con este formato (schema oracle-clue.review/v1):
- schema_version "oracle-clue.review/v1"; repo, base, head, diff_sha256 y context_sha256 copiados del paquete;
- provider {"name": "agy", "model": "gemini-3.8-flash-high"};
- findings: lista de hallazgos, cada uno con id, kind, severity (alta|media|baja|informativa), confidence (0 a 1), title, explanation,
  location {file, start_line, end_line, side: "head"} DENTRO de los rangos del diff del paquete, trigger, evidence, related_requirement,
  status "pendiente" y verification;
- review_status ("completo" o "incompleto") y limitations (qué corriste y qué no).
Sin hallazgos: findings vacía, explicado en limitations. Validalo antes de terminar con:
  oracle-clue validar /home/workstation/Dev/factory-tablero-equipo/.factory/local/revisores/176c0ca-agy2-1/informe.json --paquete /home/workstation/Dev/factory-tablero-equipo/.factory/cambios/20261027-160716-arb-equipo/candidatos/176c0ca/clue/paquete-agy2-1.json --repo /home/workstation/Dev/factory-tablero-equipo/.factory/local/revisiones/176c0ca-agy2-1
y terminá con un resumen corto en español.

Indicaciones de quien pide la revisión:
Vuelta 2: se corrigieron los hallazgos de la vuelta 1 (orden por instante con husos distintos, escapado de acciones desconocidas, intercalación entre cambios, alternativas con LA DECIDE). Revisá el cambio contra los requisitos de su spec (openspec/changes/20261027-160716-arb-equipo/specs/tablero/spec.md): oracle_factory/tablero.py (yo y actividad en armar), editores/vscode/tablero.js (paso, cambio, actividad y proyecto), tests/test_tablero_equipo.py, tools/verify_tablero_equipo.py, catalogos/factory_tablero_equipo.*.oracle y el párrafo nuevo de docs/tablero.md. Mirá especialmente: que 'yo' se lea de Git sin escribir nada, que el rótulo «LA DECIDE» y la actividad escapen todo texto del registro, que un cambio sin responsable o tuyo siga como «TE NECESITA», que la actividad sólo traiga cambios abiertos, ordene bien y corte en diez, que el esquema del JSON siga siendo compatible (la extensión, el MCP y otras pruebas), que el invitado de Live Share no rompa y que las pruebas fallen de verdad si se rompe el comportamiento. Para correr las pruebas usá exactamente, en primer plano y desde la raíz del checkout: PYTHONPATH=. $PWD/.venv/bin/python -m unittest tests.test_tablero_equipo tests.test_tablero </dev/null . No corras la suite completa. No cambies la configuración de git de ningún repositorio. Nombrá archivos con rutas relativas.
