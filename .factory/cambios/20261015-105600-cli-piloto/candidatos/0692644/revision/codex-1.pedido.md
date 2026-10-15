Sos un revisor independiente del cambio 20261015-105600-cli-piloto de un proyecto que usa Oracle Factory: «CLI: plantilla de cambio, medir que avisa qué reemplaza y --listar separado». No escribiste este código.
NO edites el checkout, no hagas commits ni decidas nada por la persona: tu trabajo es encontrar defectos y contarlos con evidencia.

Qué tiene que hacer el cambio:
- Propuesta: /home/workstation/Dev/factory-cli-piloto/openspec/changes/20261015-105600-cli-piloto/proposal.md
- Spec (lo que se promete, con sus escenarios): /home/workstation/Dev/factory-cli-piloto/openspec/changes/20261015-105600-cli-piloto/specs/cli/spec.md

Qué revisar:
- Checkout del candidato 0692644 (sólo lectura): /home/workstation/Dev/factory-cli-piloto/.factory/local/revisiones/0692644
- Paquete de Oracle Clue con el diff y el contexto: /home/workstation/Dev/factory-cli-piloto/.factory/cambios/20261015-105600-cli-piloto/candidatos/0692644/clue/paquete-codex-1.json

Vueltas anteriores de este cambio (ya corregidas; mirá que sigan cerradas y que no haya regresiones):
- .factory/cambios/20261015-105600-cli-piloto/candidatos/51a67b8/revision/agy-1.json
- .factory/cambios/20261015-105600-cli-piloto/candidatos/51a67b8/revision/codex-1.json
Fuera del paquete, porque no son producto (.factory, tareas): 10 archivos de registros y evidencia de Factory; no los revises.

Cómo trabajar: leé la spec y el diff; contrastá cada promesa con el código y con las pruebas; buscá casos que fallen, afirmaciones que el
código no cumple y pruebas que no prueban lo que dicen. Si podés, hacé mutaciones a mano sobre copias en tu carpeta y decí cuáles sobreviven.
Mandá la salida larga a archivos de tu carpeta y leé sólo el resumen.

Entregable: un informe JSON en /home/workstation/Dev/factory-cli-piloto/.factory/local/revisores/0692644-codex-1/informe.json con este formato (schema oracle-clue.review/v1):
- schema_version "oracle-clue.review/v1"; repo, base, head, diff_sha256 y context_sha256 copiados del paquete;
- provider {"name": "codex", "model": "gpt-6-luna"};
- findings: lista de hallazgos, cada uno con id, kind, severity (alta|media|baja|informativa), confidence (0 a 1), title, explanation,
  location {file, start_line, end_line, side: "head"} DENTRO de los rangos del diff del paquete, trigger, evidence, related_requirement,
  status "pendiente" y verification;
- review_status ("completo" o "incompleto") y limitations (qué corriste y qué no).
Sin hallazgos: findings vacía, explicado en limitations. Validalo antes de terminar con:
  oracle-clue validar /home/workstation/Dev/factory-cli-piloto/.factory/local/revisores/0692644-codex-1/informe.json --paquete /home/workstation/Dev/factory-cli-piloto/.factory/cambios/20261015-105600-cli-piloto/candidatos/0692644/clue/paquete-codex-1.json --repo /home/workstation/Dev/factory-cli-piloto/.factory/local/revisiones/0692644
y terminá con un resumen corto en español.

Indicaciones de quien pide la revisión:
Vuelta 2. En la 1: codex CLUE-001 y agy (requisitos ilegibles hacían afirmar que una medida quedó suelta) corregido: si hay ilegibles, medir los nombra y no afirma; el inventario se calcula una vez; las pruebas ahora exigen tipos en el registro, que la spec se rechace por sus propios TODO, y archivo, umbral, ámbito y alcance en --listar. El segundo requisito armado a mano en cp2 sigue declarado en los límites del sensor. Revisá la implementación (oracle_factory/cli.py: la plantilla en nuevo, medir con medidas_en_uso y el aviso de reemplazo, y medir --listar) contra los 3 requisitos de la spec, y si tests/test_cli_piloto.py prueba de verdad cada escenario; revisá también tools/verify_cli_piloto.py, los catálogos factory_piloto y el README. Mirá especialmente: medidas que se señalan sin requisito cuando otro las usa (o al revés), requisitos que no se pueden leer, el origen que distingue el catálogo base, y que la plantilla siga rechazándose con TODO e importándose completada. Para correr las pruebas usá exactamente, en primer plano: cd /home/workstation/Dev/factory-cli-piloto && /home/workstation/Dev/factory-cli-piloto/.venv/bin/python -m unittest tests.test_cli_piloto tests.test_cli_humana </dev/null . No corras tools/verify_*.py ni la suite completa. Nombrá archivos con rutas relativas.
