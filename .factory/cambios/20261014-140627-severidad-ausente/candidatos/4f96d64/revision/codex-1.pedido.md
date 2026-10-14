Sos un revisor independiente del cambio 20261014-140627-severidad-ausente de un proyecto que usa Oracle Factory: «Spec de revisores: un informe sin severidad no se guarda». No escribiste este código.
NO edites el checkout, no hagas commits ni decidas nada por la persona: tu trabajo es encontrar defectos y contarlos con evidencia.

Qué tiene que hacer el cambio:
- Propuesta: /home/workstation/Dev/factory-severidad-ausente/openspec/changes/20261014-140627-severidad-ausente/proposal.md
- Spec (lo que se promete, con sus escenarios): /home/workstation/Dev/factory-severidad-ausente/openspec/changes/20261014-140627-severidad-ausente/specs/revisores/spec.md

Qué revisar:
- Checkout del candidato 4f96d64 (sólo lectura): /home/workstation/Dev/factory-severidad-ausente/.factory/local/revisiones/4f96d64
- Paquete de Oracle Clue con el diff y el contexto: /home/workstation/Dev/factory-severidad-ausente/.factory/cambios/20261014-140627-severidad-ausente/candidatos/4f96d64/clue/paquete-codex-1.json

Fuera del paquete, porque no son producto (.factory, tareas): 2 archivos de registros y evidencia de Factory; no los revises.

Cómo trabajar: leé la spec y el diff; contrastá cada promesa con el código y con las pruebas; buscá casos que fallen, afirmaciones que el
código no cumple y pruebas que no prueban lo que dicen. Si podés, hacé mutaciones a mano sobre copias en tu carpeta y decí cuáles sobreviven.
Mandá la salida larga a archivos de tu carpeta y leé sólo el resumen.

Entregable: un informe JSON en /home/workstation/Dev/factory-severidad-ausente/.factory/local/revisores/4f96d64-codex-1/informe.json con este formato (schema oracle-clue.review/v1):
- schema_version "oracle-clue.review/v1"; repo, base, head, diff_sha256 y context_sha256 copiados del paquete;
- provider {"name": "codex", "model": "gpt-6-luna"};
- findings: lista de hallazgos, cada uno con id, kind, severity (alta|media|baja|informativa), confidence (0 a 1), title, explanation,
  location {file, start_line, end_line, side: "head"} DENTRO de los rangos del diff del paquete, trigger, evidence, related_requirement,
  status "pendiente" y verification;
- review_status ("completo" o "incompleto") y limitations (qué corriste y qué no).
Sin hallazgos: findings vacía, explicado en limitations. Validalo antes de terminar con:
  oracle-clue validar /home/workstation/Dev/factory-severidad-ausente/.factory/local/revisores/4f96d64-codex-1/informe.json --paquete /home/workstation/Dev/factory-severidad-ausente/.factory/cambios/20261014-140627-severidad-ausente/candidatos/4f96d64/clue/paquete-codex-1.json --repo /home/workstation/Dev/factory-severidad-ausente/.factory/local/revisiones/4f96d64
y terminá con un resumen corto en español.

Indicaciones de quien pide la revisión:
Vuelta 1. Este cambio reescribe (MODIFIED) el requisito «el corte de vueltas sigue la severidad» de openspec/specs/revisores/spec.md con lo que pasa de verdad, sin cambiar el código: revisá la spec del cambio contra el código (oracle_factory/cli.py: pedir_revision y material_del_candidato; oracle_factory/preparacion.py: corte), y si tests/test_severidad_ausente.py y los casos vs1 de tests/test_vueltas.py prueban de verdad cada escenario. Mirá especialmente: si alguna promesa del requisito nuevo sigue sin cumplirse o sin probarse, y si tools/verify_severidad_ausente.py cuenta bien casos de dos módulos. Para correr las pruebas usá exactamente, en primer plano: cd /home/workstation/Dev/factory-severidad-ausente && /home/workstation/Dev/factory-severidad-ausente/.venv/bin/python -m unittest tests.test_severidad_ausente tests.test_vueltas </dev/null . No corras tools/verify_*.py ni la suite completa. Nombrá archivos con rutas relativas.
