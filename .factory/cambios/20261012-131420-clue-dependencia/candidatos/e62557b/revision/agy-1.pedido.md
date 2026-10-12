Sos un revisor independiente del cambio 20261012-131420-clue-dependencia de un proyecto que usa Oracle Factory: «Oracle Clue como dependencia fija de Factory». No escribiste este código.
NO edites el checkout, no hagas commits ni decidas nada por la persona: tu trabajo es encontrar defectos y contarlos con evidencia.

Qué tiene que hacer el cambio:
- Propuesta: /home/workstation/Dev/factory-cd/openspec/changes/20261012-131420-clue-dependencia/proposal.md
- Spec (lo que se promete, con sus escenarios): /home/workstation/Dev/factory-cd/openspec/changes/20261012-131420-clue-dependencia/specs/autoproduccion/spec.md

Qué revisar:
- Checkout del candidato e62557b (sólo lectura): /home/workstation/Dev/factory-cd/.factory/local/revisiones/e62557b
- Paquete de Oracle Clue con el diff y el contexto: /home/workstation/Dev/factory-cd/.factory/cambios/20261012-131420-clue-dependencia/candidatos/e62557b/clue/paquete-agy-1.json

Vueltas anteriores de este cambio (ya corregidas; mirá que sigan cerradas y que no haya regresiones):
- .factory/cambios/20261012-131420-clue-dependencia/candidatos/beb83f4/revision/codex-1.json
- .factory/cambios/20261012-131420-clue-dependencia/candidatos/bf752f4/revision/agy-1.json
- .factory/cambios/20261012-131420-clue-dependencia/candidatos/bf752f4/revision/codex-1.json
- .factory/cambios/20261012-131420-clue-dependencia/candidatos/122ef26/revision/agy-1.json
- .factory/cambios/20261012-131420-clue-dependencia/candidatos/122ef26/revision/codex-1.json
- .factory/cambios/20261012-131420-clue-dependencia/candidatos/e3f2b64/revision/agy-1.json
- .factory/cambios/20261012-131420-clue-dependencia/candidatos/e3f2b64/revision/codex-1.json

Cómo trabajar: leé la spec y el diff; contrastá cada promesa con el código y con las pruebas; buscá casos que fallen, afirmaciones que el
código no cumple y pruebas que no prueban lo que dicen. Si podés, hacé mutaciones a mano sobre copias en tu carpeta y decí cuáles sobreviven.
Mandá la salida larga a archivos de tu carpeta y leé sólo el resumen.

Entregable: un informe JSON en /home/workstation/Dev/factory-cd/.factory/local/revisores/e62557b-agy-1/informe.json con este formato (schema oracle-clue.review/v1):
- schema_version "oracle-clue.review/v1"; repo, base, head, diff_sha256 y context_sha256 copiados del paquete;
- provider {"name": "agy", "model": "gemini-3.8-flash-high"};
- findings: lista de hallazgos, cada uno con id, kind, severity (alta|media|baja|informativa), confidence (0 a 1), title, explanation,
  location {file, start_line, end_line, side: "head"} DENTRO de los rangos del diff del paquete, trigger, evidence, related_requirement,
  status "pendiente" y verification;
- review_status ("completo" o "incompleto") y limitations (qué corriste y qué no).
Sin hallazgos: findings vacía, explicado en limitations. Validalo antes de terminar con:
  oracle-clue validar /home/workstation/Dev/factory-cd/.factory/local/revisores/e62557b-agy-1/informe.json --paquete /home/workstation/Dev/factory-cd/.factory/cambios/20261012-131420-clue-dependencia/candidatos/e62557b/clue/paquete-agy-1.json --repo /home/workstation/Dev/factory-cd/.factory/local/revisiones/e62557b
y terminá con un resumen corto en español.

Indicaciones de quien pide la revisión:
Revisión incremental: la base del paquete es e3f2b64, que codex y agy revisaron completo sin hallazgos (sólo no pudieron correr las pruebas porque el pedido indicaba un .venv que el checkout no tiene). Para correr las pruebas, desde el checkout del candidato usá exactamente este intérprete: timeout 200 /home/workstation/Dev/factory-cd/.venv/bin/python -m unittest tests.test_clue_dependencia tests.test_autoproduccion tests.test_revisores tests.test_decisiones </dev/null (en primer plano; nunca en segundo plano). Con eso tu revisión puede ser completa. NO corras tools/verify_*.py ni la suite completa. Desde e3f2b64: el informe más nuevo de cada revisor reemplaza a los anteriores (material_del_candidato y preparar_revision); el menú de la decisión en revisar mantiene sus números y dice por qué no se puede aprobar. Mirá que las pruebas fallen ante las regresiones que dicen cubrir. Límites asumidos, no los reportes: Factory no autentica actores.
