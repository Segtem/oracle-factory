Sos un revisor independiente del cambio 20261019-182313-commits de un proyecto que usa Oracle Factory: «Los commits unidos a su cambio: trailer Cambio, oracle-factory log, estado y tablero». No escribiste este código.
NO edites el checkout, no hagas commits ni decidas nada por la persona: tu trabajo es encontrar defectos y contarlos con evidencia.

Qué tiene que hacer el cambio:
- Propuesta: /home/workstation/Dev/factory-commits/openspec/changes/20261019-182313-commits/proposal.md
- Spec (lo que se promete, con sus escenarios): /home/workstation/Dev/factory-commits/openspec/changes/20261019-182313-commits/specs/trazabilidad/spec.md

Qué revisar:
- Checkout del candidato 84e599f (sólo lectura): /home/workstation/Dev/factory-commits/.factory/local/revisiones/84e599f
- Paquete de Oracle Clue con el diff y el contexto: /home/workstation/Dev/factory-commits/.factory/cambios/20261019-182313-commits/candidatos/84e599f/clue/paquete-agy-2.json

Vueltas anteriores de este cambio (ya corregidas; mirá que sigan cerradas y que no haya regresiones):
- .factory/cambios/20261019-182313-commits/candidatos/5630ad5/revision/agy-1.json
- .factory/cambios/20261019-182313-commits/candidatos/5630ad5/revision/codex-1.json
- .factory/cambios/20261019-182313-commits/candidatos/069b7dc/revision/agy-1.json
- .factory/cambios/20261019-182313-commits/candidatos/069b7dc/revision/codex-1.json
- .factory/cambios/20261019-182313-commits/candidatos/9b40877/revision/agy-1.json
- .factory/cambios/20261019-182313-commits/candidatos/9b40877/revision/codex-1.json
- .factory/cambios/20261019-182313-commits/candidatos/a2ccce4/revision/agy-1.json
- .factory/cambios/20261019-182313-commits/candidatos/a2ccce4/revision/codex-1.json
- .factory/cambios/20261019-182313-commits/candidatos/32e0ca5/revision/agy-1.json
- .factory/cambios/20261019-182313-commits/candidatos/32e0ca5/revision/codex-1.json
Fuera del paquete, porque no son producto (.factory, tareas): 95 archivos de registros y evidencia de Factory; no los revises.

Cómo trabajar: leé la spec y el diff; contrastá cada promesa con el código y con las pruebas; buscá casos que fallen, afirmaciones que el
código no cumple y pruebas que no prueban lo que dicen. Si podés, hacé mutaciones a mano sobre copias en tu carpeta y decí cuáles sobreviven.
Mandá la salida larga a archivos de tu carpeta y leé sólo el resumen.

Entregable: un informe JSON en /home/workstation/Dev/factory-commits/.factory/local/revisores/84e599f-agy-2/informe.json con este formato (schema oracle-clue.review/v1):
- schema_version "oracle-clue.review/v1"; repo, base, head, diff_sha256 y context_sha256 copiados del paquete;
- provider {"name": "agy", "model": "gemini-3.8-flash-high"};
- findings: lista de hallazgos, cada uno con id, kind, severity (alta|media|baja|informativa), confidence (0 a 1), title, explanation,
  location {file, start_line, end_line, side: "head"} DENTRO de los rangos del diff del paquete, trigger, evidence, related_requirement,
  status "pendiente" y verification;
- review_status ("completo" o "incompleto") y limitations (qué corriste y qué no).
Sin hallazgos: findings vacía, explicado en limitations. Validalo antes de terminar con:
  oracle-clue validar /home/workstation/Dev/factory-commits/.factory/local/revisores/84e599f-agy-2/informe.json --paquete /home/workstation/Dev/factory-commits/.factory/cambios/20261019-182313-commits/candidatos/84e599f/clue/paquete-agy-2.json --repo /home/workstation/Dev/factory-commits/.factory/local/revisiones/84e599f
y terminá con un resumen corto en español.

Indicaciones de quien pide la revisión:
Vuelta 6 (agy otra vez: el pedido anterior pasó el tope). Desde la vuelta 5 (sin hallazgos de ninguno) sólo cambió requisitos/trazabilidad_c03c40840efaaab69.cada_commit_nuevo_dice_de_que_cambio_es.requisito: se le quitó la línea sin_medir. Verificá que el requisito quede bien medido y que nada más cambió. Es una revisión corta: no corras pruebas largas; si querés, PYTHONPATH=. /home/workstation/Dev/factory-commits/.venv/bin/python -m unittest tests.test_commits </dev/null . Nombrá archivos con rutas relativas.
