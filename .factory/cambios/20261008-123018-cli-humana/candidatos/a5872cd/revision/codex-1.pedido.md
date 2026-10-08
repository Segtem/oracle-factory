Sos un revisor independiente del cambio 20261008-123018-cli-humana de un proyecto que usa Oracle Factory: «La CLI cómoda para la persona: errores claros, comando propio, salidas legibles y próximo paso». No escribiste este código.
NO edites el checkout, no hagas commits ni decidas nada por la persona: tu trabajo es encontrar defectos y contarlos con evidencia.

Qué tiene que hacer el cambio:
- Propuesta: /home/workstation/Dev/factory-ch/openspec/changes/20261008-123018-cli-humana/proposal.md
- Spec (lo que se promete, con sus escenarios): /home/workstation/Dev/factory-ch/openspec/changes/20261008-123018-cli-humana/specs/cli/spec.md

Qué revisar:
- Checkout del candidato a5872cd (sólo lectura): /home/workstation/Dev/factory-ch/.factory/local/revisiones/a5872cd
- Paquete de Oracle Clue con el diff y el contexto: /home/workstation/Dev/factory-ch/.factory/cambios/20261008-123018-cli-humana/candidatos/a5872cd/clue/paquete-codex-1.json

Vueltas anteriores de este cambio (ya corregidas; mirá que sigan cerradas y que no haya regresiones):
- .factory/cambios/20261008-123018-cli-humana/candidatos/2515b20/revision/codex-1.json
- .factory/cambios/20261008-123018-cli-humana/candidatos/ddf034c/revision/codex-1.json
- .factory/cambios/20261008-123018-cli-humana/candidatos/2efe4e6/revision/codex-1.json
- .factory/cambios/20261008-123018-cli-humana/candidatos/6699c9f/revision/agy-1.json
- .factory/cambios/20261008-123018-cli-humana/candidatos/6699c9f/revision/codex-1.json
- .factory/cambios/20261008-123018-cli-humana/candidatos/9902c08/revision/agy-1.json
- .factory/cambios/20261008-123018-cli-humana/candidatos/9902c08/revision/codex-1.json
- .factory/cambios/20261008-123018-cli-humana/candidatos/313d391/revision/codex-1.json
- .factory/cambios/20261008-123018-cli-humana/candidatos/4db955b/revision/agy-1.json
- .factory/cambios/20261008-123018-cli-humana/candidatos/4db955b/revision/codex-1.json
- .factory/cambios/20261008-123018-cli-humana/candidatos/a9b3d62/revision/codex-1.json
- .factory/cambios/20261008-123018-cli-humana/candidatos/3a01816/revision/agy-1.json
- .factory/cambios/20261008-123018-cli-humana/candidatos/3a01816/revision/codex-1.json
- .factory/cambios/20261008-123018-cli-humana/candidatos/56b005b/revision/agy-1.json
- .factory/cambios/20261008-123018-cli-humana/candidatos/56b005b/revision/codex-1.json
- .factory/cambios/20261008-123018-cli-humana/candidatos/2391733/revision/agy-1.json
- .factory/cambios/20261008-123018-cli-humana/candidatos/2391733/revision/codex-1.json
- .factory/cambios/20261008-123018-cli-humana/candidatos/27cd98c/revision/agy-1.json
- .factory/cambios/20261008-123018-cli-humana/candidatos/27cd98c/revision/codex-1.json

Cómo trabajar: leé la spec y el diff; contrastá cada promesa con el código y con las pruebas; buscá casos que fallen, afirmaciones que el
código no cumple y pruebas que no prueban lo que dicen. Si podés, hacé mutaciones a mano sobre copias en tu carpeta y decí cuáles sobreviven.
Mandá la salida larga a archivos de tu carpeta y leé sólo el resumen.

Entregable: un informe JSON en /home/workstation/Dev/factory-ch/.factory/local/revisores/a5872cd-codex-1/informe.json con este formato (schema oracle-clue.review/v1):
- schema_version "oracle-clue.review/v1"; repo, base, head, diff_sha256 y context_sha256 copiados del paquete;
- provider {"name": "codex", "model": "gpt-6-luna"};
- findings: lista de hallazgos, cada uno con id, kind, severity (alta|media|baja|informativa), confidence (0 a 1), title, explanation,
  location {file, start_line, end_line, side: "head"} DENTRO de los rangos del diff del paquete, trigger, evidence, related_requirement,
  status "pendiente" y verification;
- review_status ("completo" o "incompleto") y limitations (qué corriste y qué no).
Sin hallazgos: findings vacía, explicado en limitations. Validalo antes de terminar con:
  oracle-clue validar /home/workstation/Dev/factory-ch/.factory/local/revisores/a5872cd-codex-1/informe.json --paquete /home/workstation/Dev/factory-ch/.factory/cambios/20261008-123018-cli-humana/candidatos/a5872cd/clue/paquete-codex-1.json --repo /home/workstation/Dev/factory-ch/.factory/local/revisiones/a5872cd
y terminá con un resumen corto en español.

Indicaciones de quien pide la revisión:
Para correr las pruebas usá exactamente: timeout 120 env PATH=/tmp/claude-1000/-home-workstation-Dev-factory/d3ffc37f-4c26-4426-b2d7-381bdbfe4609/scratchpad/env/bin:$PATH .venv/bin/python -m unittest tests.test_cli_humana </dev/null (tarda unos segundos; corrélo en primer plano, nunca en segundo plano). NO corras tools/verify_*.py ni la suite completa. Revisá todo el cambio. proximo_paso es una secuencia según lo vigente (spec aprobada → requisitos → medidas (propuestas_confirmables, compartida con medir --confirmar) → revisión válida para el producto actual (problemas_de_revision) → juicio vigente → cierre). Buscá estados del flujo donde el paso calculado no sea el que corresponde, donde el menú ofrezca algo que no avanza, o donde estado falle por archivos ausentes. Límites asumidos, no los reportes: Factory no autentica actores; el menú usa input() con números.
