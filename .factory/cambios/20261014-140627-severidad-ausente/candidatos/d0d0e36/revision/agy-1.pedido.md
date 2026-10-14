Sos un revisor independiente del cambio 20261014-140627-severidad-ausente de un proyecto que usa Oracle Factory: «Spec de revisores: un informe sin severidad no se guarda». No escribiste este código.
NO edites el checkout, no hagas commits ni decidas nada por la persona: tu trabajo es encontrar defectos y contarlos con evidencia.

Qué tiene que hacer el cambio:
- Propuesta: /home/workstation/Dev/factory-severidad-ausente/openspec/changes/20261014-140627-severidad-ausente/proposal.md
- Spec (lo que se promete, con sus escenarios): /home/workstation/Dev/factory-severidad-ausente/openspec/changes/20261014-140627-severidad-ausente/specs/revisores/spec.md

Qué revisar:
- Checkout del candidato d0d0e36 (sólo lectura): /home/workstation/Dev/factory-severidad-ausente/.factory/local/revisiones/d0d0e36
- Paquete de Oracle Clue con el diff y el contexto: /home/workstation/Dev/factory-severidad-ausente/.factory/cambios/20261014-140627-severidad-ausente/candidatos/d0d0e36/clue/paquete-agy-1.json

Vueltas anteriores de este cambio (ya corregidas; mirá que sigan cerradas y que no haya regresiones):
- .factory/cambios/20261014-140627-severidad-ausente/candidatos/4f96d64/revision/agy-1.json
- .factory/cambios/20261014-140627-severidad-ausente/candidatos/4f96d64/revision/codex-1.json
Fuera del paquete, porque no son producto (.factory, tareas): 10 archivos de registros y evidencia de Factory; no los revises.

Cómo trabajar: leé la spec y el diff; contrastá cada promesa con el código y con las pruebas; buscá casos que fallen, afirmaciones que el
código no cumple y pruebas que no prueban lo que dicen. Si podés, hacé mutaciones a mano sobre copias en tu carpeta y decí cuáles sobreviven.
Mandá la salida larga a archivos de tu carpeta y leé sólo el resumen.

Entregable: un informe JSON en /home/workstation/Dev/factory-severidad-ausente/.factory/local/revisores/d0d0e36-agy-1/informe.json con este formato (schema oracle-clue.review/v1):
- schema_version "oracle-clue.review/v1"; repo, base, head, diff_sha256 y context_sha256 copiados del paquete;
- provider {"name": "agy", "model": "gemini-3.8-flash-high"};
- findings: lista de hallazgos, cada uno con id, kind, severity (alta|media|baja|informativa), confidence (0 a 1), title, explanation,
  location {file, start_line, end_line, side: "head"} DENTRO de los rangos del diff del paquete, trigger, evidence, related_requirement,
  status "pendiente" y verification;
- review_status ("completo" o "incompleto") y limitations (qué corriste y qué no).
Sin hallazgos: findings vacía, explicado en limitations. Validalo antes de terminar con:
  oracle-clue validar /home/workstation/Dev/factory-severidad-ausente/.factory/local/revisores/d0d0e36-agy-1/informe.json --paquete /home/workstation/Dev/factory-severidad-ausente/.factory/cambios/20261014-140627-severidad-ausente/candidatos/d0d0e36/clue/paquete-agy-1.json --repo /home/workstation/Dev/factory-severidad-ausente/.factory/local/revisiones/d0d0e36
y terminá con un resumen corto en español.

Indicaciones de quien pide la revisión:
Vuelta 2. En la 1, agy F-02 (la pérdida de severidad con un solo revisor) y el bajo repetido de agy F-04 y codex F-01 (vs1 sin pasar por la CLI de estado) quedaron corregidos. agy F-01 no se cambió: el filtro 'name in expected' no anula las omisiones, porque observed se compara con Counter(expected) y un caso que falta o se repite da incompleto; una prueba fuera del contrato no cuenta a propósito. agy F-03 (alta sin escenario propio) queda para la persona. Este cambio reescribe (MODIFIED) el requisito «el corte de vueltas sigue la severidad» de openspec/specs/revisores/spec.md con lo que pasa de verdad, sin cambiar el código: revisá la spec del cambio contra el código (oracle_factory/cli.py: pedir_revision y material_del_candidato; oracle_factory/preparacion.py: corte), y si tests/test_severidad_ausente.py y los casos vs1 de tests/test_vueltas.py prueban de verdad cada escenario. Mirá especialmente: si alguna promesa del requisito nuevo sigue sin cumplirse o sin probarse, y si tools/verify_severidad_ausente.py cuenta bien casos de dos módulos. Para correr las pruebas usá exactamente, en primer plano: cd /home/workstation/Dev/factory-severidad-ausente && /home/workstation/Dev/factory-severidad-ausente/.venv/bin/python -m unittest tests.test_severidad_ausente tests.test_vueltas </dev/null . No corras tools/verify_*.py ni la suite completa. Nombrá archivos con rutas relativas.
