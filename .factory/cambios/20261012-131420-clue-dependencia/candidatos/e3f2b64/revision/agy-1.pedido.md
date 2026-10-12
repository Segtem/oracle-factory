Sos un revisor independiente del cambio 20261012-131420-clue-dependencia de un proyecto que usa Oracle Factory: «Oracle Clue como dependencia fija de Factory». No escribiste este código.
NO edites el checkout, no hagas commits ni decidas nada por la persona: tu trabajo es encontrar defectos y contarlos con evidencia.

Qué tiene que hacer el cambio:
- Propuesta: /home/workstation/Dev/factory-cd/openspec/changes/20261012-131420-clue-dependencia/proposal.md
- Spec (lo que se promete, con sus escenarios): /home/workstation/Dev/factory-cd/openspec/changes/20261012-131420-clue-dependencia/specs/autoproduccion/spec.md

Qué revisar:
- Checkout del candidato e3f2b64 (sólo lectura): /home/workstation/Dev/factory-cd/.factory/local/revisiones/e3f2b64
- Paquete de Oracle Clue con el diff y el contexto: /home/workstation/Dev/factory-cd/.factory/cambios/20261012-131420-clue-dependencia/candidatos/e3f2b64/clue/paquete-agy-1.json

Vueltas anteriores de este cambio (ya corregidas; mirá que sigan cerradas y que no haya regresiones):
- .factory/cambios/20261012-131420-clue-dependencia/candidatos/beb83f4/revision/codex-1.json
- .factory/cambios/20261012-131420-clue-dependencia/candidatos/bf752f4/revision/agy-1.json
- .factory/cambios/20261012-131420-clue-dependencia/candidatos/bf752f4/revision/codex-1.json
- .factory/cambios/20261012-131420-clue-dependencia/candidatos/122ef26/revision/agy-1.json
- .factory/cambios/20261012-131420-clue-dependencia/candidatos/122ef26/revision/codex-1.json

Cómo trabajar: leé la spec y el diff; contrastá cada promesa con el código y con las pruebas; buscá casos que fallen, afirmaciones que el
código no cumple y pruebas que no prueban lo que dicen. Si podés, hacé mutaciones a mano sobre copias en tu carpeta y decí cuáles sobreviven.
Mandá la salida larga a archivos de tu carpeta y leé sólo el resumen.

Entregable: un informe JSON en /home/workstation/Dev/factory-cd/.factory/local/revisores/e3f2b64-agy-1/informe.json con este formato (schema oracle-clue.review/v1):
- schema_version "oracle-clue.review/v1"; repo, base, head, diff_sha256 y context_sha256 copiados del paquete;
- provider {"name": "agy", "model": "gemini-3.8-flash-high"};
- findings: lista de hallazgos, cada uno con id, kind, severity (alta|media|baja|informativa), confidence (0 a 1), title, explanation,
  location {file, start_line, end_line, side: "head"} DENTRO de los rangos del diff del paquete, trigger, evidence, related_requirement,
  status "pendiente" y verification;
- review_status ("completo" o "incompleto") y limitations (qué corriste y qué no).
Sin hallazgos: findings vacía, explicado en limitations. Validalo antes de terminar con:
  oracle-clue validar /home/workstation/Dev/factory-cd/.factory/local/revisores/e3f2b64-agy-1/informe.json --paquete /home/workstation/Dev/factory-cd/.factory/cambios/20261012-131420-clue-dependencia/candidatos/e3f2b64/clue/paquete-agy-1.json --repo /home/workstation/Dev/factory-cd/.factory/local/revisiones/e3f2b64
y terminá con un resumen corto en español.

Indicaciones de quien pide la revisión:
Para correr las pruebas usá exactamente: timeout 200 .venv/bin/python -m unittest tests.test_clue_dependencia tests.test_autoproduccion tests.test_revisores </dev/null (en primer plano; nunca en segundo plano). NO corras tools/verify_*.py ni la suite completa. Revisá todo el cambio: oracle-clue pasa a dependencia fija y Factory lo usa sólo desde su entorno (ejecutar; sin la distribución, error); desaparece la rama «sin validar»; importar y tipos_spec ignoran la sección REMOVED. Mirá también que ninguna otra parte del código, las pruebas o los docs siga suponiendo que Clue puede faltar, y que las pruebas fallen ante las regresiones que dicen cubrir. Límites asumidos, no los reportes: Factory no autentica actores.
