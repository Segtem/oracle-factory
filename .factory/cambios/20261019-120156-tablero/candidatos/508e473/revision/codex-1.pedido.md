Sos un revisor independiente del cambio 20261019-120156-tablero de un proyecto que usa Oracle Factory: «El tablero de comando en VS Code: qué te necesita, la línea de tiempo, los hallazgos y las métricas». No escribiste este código.
NO edites el checkout, no hagas commits ni decidas nada por la persona: tu trabajo es encontrar defectos y contarlos con evidencia.

Qué tiene que hacer el cambio:
- Propuesta: /home/workstation/Dev/factory-tablero/openspec/changes/20261019-120156-tablero/proposal.md
- Spec (lo que se promete, con sus escenarios): /home/workstation/Dev/factory-tablero/openspec/changes/20261019-120156-tablero/specs/ide/spec.md

Qué revisar:
- Checkout del candidato 508e473 (sólo lectura): /home/workstation/Dev/factory-tablero/.factory/local/revisiones/508e473
- Paquete de Oracle Clue con el diff y el contexto: /home/workstation/Dev/factory-tablero/.factory/cambios/20261019-120156-tablero/candidatos/508e473/clue/paquete-codex-1.json

Vueltas anteriores de este cambio (ya corregidas; mirá que sigan cerradas y que no haya regresiones):
- .factory/cambios/20261019-120156-tablero/candidatos/b08b14c/revision/agy-1.json
- .factory/cambios/20261019-120156-tablero/candidatos/b08b14c/revision/codex-1.json
Fuera del paquete, porque no son producto (.factory, tareas): 10 archivos de registros y evidencia de Factory; no los revises.

Cómo trabajar: leé la spec y el diff; contrastá cada promesa con el código y con las pruebas; buscá casos que fallen, afirmaciones que el
código no cumple y pruebas que no prueban lo que dicen. Si podés, hacé mutaciones a mano sobre copias en tu carpeta y decí cuáles sobreviven.
Mandá la salida larga a archivos de tu carpeta y leé sólo el resumen.

Entregable: un informe JSON en /home/workstation/Dev/factory-tablero/.factory/local/revisores/508e473-codex-1/informe.json con este formato (schema oracle-clue.review/v1):
- schema_version "oracle-clue.review/v1"; repo, base, head, diff_sha256 y context_sha256 copiados del paquete;
- provider {"name": "codex", "model": "gpt-6-luna"};
- findings: lista de hallazgos, cada uno con id, kind, severity (alta|media|baja|informativa), confidence (0 a 1), title, explanation,
  location {file, start_line, end_line, side: "head"} DENTRO de los rangos del diff del paquete, trigger, evidence, related_requirement,
  status "pendiente" y verification;
- review_status ("completo" o "incompleto") y limitations (qué corriste y qué no).
Sin hallazgos: findings vacía, explicado en limitations. Validalo antes de terminar con:
  oracle-clue validar /home/workstation/Dev/factory-tablero/.factory/local/revisores/508e473-codex-1/informe.json --paquete /home/workstation/Dev/factory-tablero/.factory/cambios/20261019-120156-tablero/candidatos/508e473/clue/paquete-codex-1.json --repo /home/workstation/Dev/factory-tablero/.factory/local/revisiones/508e473
y terminá con un resumen corto en español.

Indicaciones de quien pide la revisión:
Vuelta 2. En la vuelta 1 se corrigió: AGY-1/TABLERO-001 (mensajeDelTablero resuelve enlaces con realpath y sólo abre archivos regulares dentro del proyecto), AGY-2 (informes(): el informe más nuevo de un revisor en un candidato reemplaza a los anteriores, como en revision-preparar), AGY-3 (una revisión registrada a mano sin revisores pedidos cuenta como una vuelta), AGY-4 (_horas no se cae con fechas con y sin zona; esa fase no cuenta) y AGY-5 (modelo.comandoDe rechaza comandos con saltos de línea). Verificá esas correcciones y buscá lo que quede. Revisá el cambio: oracle_factory/tablero.py (hitos, informes, metricas_del_cambio, _paso, _cumplidos, armar) y el subcomando tablero --json en oracle_factory/cli.py; la extensión de VS Code en editores/vscode/ (tablero.js: el HTML del panel con CSP y escape; extension.js: pintarTablero, mensajeDelTablero —que sólo abre archivos dentro del proyecto y escribe comandos sin Enter—, abrirTablero, el vigía que lo rehace; package.json 0.2.0 y empaquetar.py); README; tests/test_tablero.py, tests/tablero_en_node.cjs, tools/verify_tablero.py y catalogos/factory_tablero.*.oracle, contra los 2 requisitos de la spec. Mirá especialmente: inyección de HTML o scripts en el panel por títulos, rutas o hallazgos de un informe; abrir archivos fuera del proyecto (rutas con .., absolutas, symlinks); métricas mal contadas (fases, vueltas, hallazgos de candidatos viejos, riesgos aceptados, actores); qué se marca como decisión de la persona; y que el tablero no falle con registros viejos o informes rotos. Para correr las pruebas usá exactamente, en primer plano y desde la raíz del checkout: PYTHONPATH=. /home/workstation/Dev/factory-tablero/.venv/bin/python -m unittest tests.test_tablero </dev/null . Necesita node; si node no arranca en tu entorno, marcá esas pruebas como no ejecutadas y revisá el código. No corras la suite completa. Nombrá archivos con rutas relativas.
