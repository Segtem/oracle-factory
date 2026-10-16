Sos un revisor independiente del cambio 20261016-175720-bloqueo-registro de un proyecto que usa Oracle Factory: «Dos procesos que escriben el mismo registro no se pisan». No escribiste este código.
NO edites el checkout, no hagas commits ni decidas nada por la persona: tu trabajo es encontrar defectos y contarlos con evidencia.

Qué tiene que hacer el cambio:
- Propuesta: /home/workstation/Dev/factory-bloqueo-registro/openspec/changes/20261016-175720-bloqueo-registro/proposal.md
- Spec (lo que se promete, con sus escenarios): /home/workstation/Dev/factory-bloqueo-registro/openspec/changes/20261016-175720-bloqueo-registro/specs/flujo/spec.md

Qué revisar:
- Checkout del candidato f72807d (sólo lectura): /home/workstation/Dev/factory-bloqueo-registro/.factory/local/revisiones/f72807d
- Paquete de Oracle Clue con el diff y el contexto: /home/workstation/Dev/factory-bloqueo-registro/.factory/cambios/20261016-175720-bloqueo-registro/candidatos/f72807d/clue/paquete-codex-1.json

Vueltas anteriores de este cambio (ya corregidas; mirá que sigan cerradas y que no haya regresiones):
- .factory/cambios/20261016-175720-bloqueo-registro/candidatos/8b84fcc/revision/agy-1.json
- .factory/cambios/20261016-175720-bloqueo-registro/candidatos/8b84fcc/revision/codex-1.json
- .factory/cambios/20261016-175720-bloqueo-registro/candidatos/d1b1f6e/revision/agy-1.json
- .factory/cambios/20261016-175720-bloqueo-registro/candidatos/d1b1f6e/revision/codex-1.json
Fuera del paquete, porque no son producto (.factory, tareas): 18 archivos de registros y evidencia de Factory; no los revises.

Cómo trabajar: leé la spec y el diff; contrastá cada promesa con el código y con las pruebas; buscá casos que fallen, afirmaciones que el
código no cumple y pruebas que no prueban lo que dicen. Si podés, hacé mutaciones a mano sobre copias en tu carpeta y decí cuáles sobreviven.
Mandá la salida larga a archivos de tu carpeta y leé sólo el resumen.

Entregable: un informe JSON en /home/workstation/Dev/factory-bloqueo-registro/.factory/local/revisores/f72807d-codex-1/informe.json con este formato (schema oracle-clue.review/v1):
- schema_version "oracle-clue.review/v1"; repo, base, head, diff_sha256 y context_sha256 copiados del paquete;
- provider {"name": "codex", "model": "gpt-6-luna"};
- findings: lista de hallazgos, cada uno con id, kind, severity (alta|media|baja|informativa), confidence (0 a 1), title, explanation,
  location {file, start_line, end_line, side: "head"} DENTRO de los rangos del diff del paquete, trigger, evidence, related_requirement,
  status "pendiente" y verification;
- review_status ("completo" o "incompleto") y limitations (qué corriste y qué no).
Sin hallazgos: findings vacía, explicado en limitations. Validalo antes de terminar con:
  oracle-clue validar /home/workstation/Dev/factory-bloqueo-registro/.factory/local/revisores/f72807d-codex-1/informe.json --paquete /home/workstation/Dev/factory-bloqueo-registro/.factory/cambios/20261016-175720-bloqueo-registro/candidatos/f72807d/clue/paquete-codex-1.json --repo /home/workstation/Dev/factory-bloqueo-registro/.factory/local/revisiones/f72807d
y terminá con un resumen corto en español.

Indicaciones de quien pide la revisión:
Vuelta 3. En la 2 agy marcó agy-1 (media): bl1 no aislaba la lectura, porque nuevo ya había dejado el registro en LEIDOS y quitar LEIDOS en leer sobrevivía. Corregido: bl1 y bl2 vacían LEIDOS después de nuevo, como un proceso nuevo; esa mutación ahora muere. Las bajas de la vuelta 2 (alcance del catálogo sobre bl3, el sensor que corre la suite entera, el flock sobre carpetas compartidas) las decide la persona. Verificá la corrección y buscá lo que siga. Revisá el cambio en oracle_factory/cli.py (LEIDOS, leer, guardar con esperado por defecto, y el flock sobre la carpeta en escribir_atomico) contra el requisito de la spec, y si tests/test_bloqueo_registro.py prueba de verdad los tres escenarios con un segundo proceso; revisá también el párrafo de docs/colaboracion.md, tools/verify_bloqueo_registro.py y catalogos/factory_bloqueo.*.oracle. Mirá especialmente: escrituras del registro que no pasen por guardar ni escribir_atomico (también en otros módulos de oracle_factory/), un mismo proceso que ahora falle sin razón (leer de un lugar y guardar en otro, una ruta distinta para el mismo archivo, un registro que se lee sin leer()), interbloqueos o esperas sin fin, el bloqueo sobre carpetas que no son de un cambio, y qué pasa cuando el archivo no existía. Para correr las pruebas usá exactamente, en primer plano y desde la raíz del checkout: PYTHONPATH=. /home/workstation/Dev/factory-bloqueo-registro/.venv/bin/python -m unittest tests.test_bloqueo_registro </dev/null (ese intérprete tiene Oracle; PYTHONPATH=. hace que pruebe el código del checkout). No corras la suite completa. Nombrá archivos con rutas relativas.
