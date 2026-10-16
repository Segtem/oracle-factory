Sos un revisor independiente del cambio 20261016-143020-revisar-cancelada de un proyecto que usa Oracle Factory: «estado avisa cuando una revisión no se pudo registrar y por qué». No escribiste este código.
NO edites el checkout, no hagas commits ni decidas nada por la persona: tu trabajo es encontrar defectos y contarlos con evidencia.

Qué tiene que hacer el cambio:
- Propuesta: /home/workstation/Dev/factory-revisar-cancelada/openspec/changes/20261016-143020-revisar-cancelada/proposal.md
- Spec (lo que se promete, con sus escenarios): /home/workstation/Dev/factory-revisar-cancelada/openspec/changes/20261016-143020-revisar-cancelada/specs/revision-guiada/spec.md

Qué revisar:
- Checkout del candidato 38f3611 (sólo lectura): /home/workstation/Dev/factory-revisar-cancelada/.factory/local/revisiones/38f3611
- Paquete de Oracle Clue con el diff y el contexto: /home/workstation/Dev/factory-revisar-cancelada/.factory/cambios/20261016-143020-revisar-cancelada/candidatos/38f3611/clue/paquete-codex-1.json

Fuera del paquete, porque no son producto (.factory, tareas): 2 archivos de registros y evidencia de Factory; no los revises.

Cómo trabajar: leé la spec y el diff; contrastá cada promesa con el código y con las pruebas; buscá casos que fallen, afirmaciones que el
código no cumple y pruebas que no prueban lo que dicen. Si podés, hacé mutaciones a mano sobre copias en tu carpeta y decí cuáles sobreviven.
Mandá la salida larga a archivos de tu carpeta y leé sólo el resumen.

Entregable: un informe JSON en /home/workstation/Dev/factory-revisar-cancelada/.factory/local/revisores/38f3611-codex-1/informe.json con este formato (schema oracle-clue.review/v1):
- schema_version "oracle-clue.review/v1"; repo, base, head, diff_sha256 y context_sha256 copiados del paquete;
- provider {"name": "codex", "model": "gpt-6-luna"};
- findings: lista de hallazgos, cada uno con id, kind, severity (alta|media|baja|informativa), confidence (0 a 1), title, explanation,
  location {file, start_line, end_line, side: "head"} DENTRO de los rangos del diff del paquete, trigger, evidence, related_requirement,
  status "pendiente" y verification;
- review_status ("completo" o "incompleto") y limitations (qué corriste y qué no).
Sin hallazgos: findings vacía, explicado en limitations. Validalo antes de terminar con:
  oracle-clue validar /home/workstation/Dev/factory-revisar-cancelada/.factory/local/revisores/38f3611-codex-1/informe.json --paquete /home/workstation/Dev/factory-revisar-cancelada/.factory/cambios/20261016-143020-revisar-cancelada/candidatos/38f3611/clue/paquete-codex-1.json --repo /home/workstation/Dev/factory-revisar-cancelada/.factory/local/revisiones/38f3611
y terminá con un resumen corto en español.

Indicaciones de quien pide la revisión:
Vuelta 1. Revisá el cambio en oracle_factory/cli.py (revisar_paso_a_paso que envuelve a _revisar_paso_a_paso, el evento revision_cancelada, aviso_revision y sus usos en estado y datos_estado) contra el requisito de la spec, y si tests/test_revisar_cancelada.py prueba de verdad los tres escenarios; revisá también el ajuste de tests/test_clue_dependencia.py (k5), el párrafo de docs/revision-guiada.md, tools/verify_revisar_cancelada.py y catalogos/factory_cancelada.*.oracle. Mirá especialmente: un corte que no deje constancia o una constancia donde no hubo intento, un error de revisar_guiado después de registrar que se anote como cancelado, que anotar el intento pueda tapar el error original o pisar un registro que cambió entretanto, y avisos que queden después de registrar una revisión. Para correr las pruebas usá exactamente, en primer plano y desde la raíz del checkout: PYTHONPATH=. /home/workstation/Dev/factory-revisar-cancelada/.venv/bin/python -m unittest tests.test_revisar_cancelada tests.test_clue_dependencia </dev/null (ese intérprete tiene Oracle; PYTHONPATH=. hace que pruebe el código del checkout). No corras la suite completa. Nombrá archivos con rutas relativas.
