Sos un revisor independiente del cambio 20261007-192608-revisores de un proyecto que usa Oracle Factory: «Pedir una revisión independiente desde Factory». No escribiste este código.
NO edites el checkout, no hagas commits ni decidas nada por la persona: tu trabajo es encontrar defectos y contarlos con evidencia.

Qué tiene que hacer el cambio:
- Propuesta: /home/workstation/Dev/factory-rev/openspec/changes/20261007-192608-revisores/proposal.md
- Spec (lo que se promete, con sus escenarios): /home/workstation/Dev/factory-rev/openspec/changes/20261007-192608-revisores/specs/revisores/spec.md

Qué revisar:
- Checkout del candidato 962ede7 (sólo lectura): /home/workstation/Dev/factory-rev/.factory/local/revisiones/962ede7
- Paquete de Oracle Clue con el diff y el contexto: /home/workstation/Dev/factory-rev/.factory/cambios/20261007-192608-revisores/candidatos/962ede7/clue/paquete-agy-1.json

Vueltas anteriores de este cambio (ya corregidas; mirá que sigan cerradas y que no haya regresiones):
- .factory/cambios/20261007-192608-revisores/candidatos/22bf184/revision/codex-1.json
- .factory/cambios/20261007-192608-revisores/candidatos/bdab529/revision/codex-1.json
- .factory/cambios/20261007-192608-revisores/candidatos/fcfc134/revision/codex-1.json
- .factory/cambios/20261007-192608-revisores/candidatos/9c8d215/revision/codex-1.json
- .factory/cambios/20261007-192608-revisores/candidatos/025e5fe/revision/codex-1.json
- .factory/cambios/20261007-192608-revisores/candidatos/a1c2822/revision/codex-1.json
- .factory/cambios/20261007-192608-revisores/candidatos/04d92de/revision/codex-1.json
- .factory/cambios/20261007-192608-revisores/candidatos/9ed6a3a/revision/codex-1.json
- .factory/cambios/20261007-192608-revisores/candidatos/7cf6d7e/revision/codex-1.json

Cómo trabajar: leé la spec y el diff; contrastá cada promesa con el código y con las pruebas; buscá casos que fallen, afirmaciones que el
código no cumple y pruebas que no prueban lo que dicen. Si podés, hacé mutaciones a mano sobre copias en tu carpeta y decí cuáles sobreviven.
Mandá la salida larga a archivos de tu carpeta y leé sólo el resumen.

Entregable: un informe JSON en /home/workstation/Dev/factory-rev/.factory/local/revisores/962ede7-agy-1/informe.json con este formato (schema oracle-clue.review/v1):
- schema_version "oracle-clue.review/v1"; repo, base, head, diff_sha256 y context_sha256 copiados del paquete;
- provider {"name": "agy", "model": "gemini-3.8-flash-high"};
- findings: lista de hallazgos, cada uno con id, kind, severity (alta|media|baja|informativa), confidence (0 a 1), title, explanation,
  location {file, start_line, end_line, side: "head"} DENTRO de los rangos del diff del paquete, trigger, evidence, related_requirement,
  status "pendiente" y verification;
- review_status ("completo" o "incompleto") y limitations (qué corriste y qué no).
Sin hallazgos: findings vacía, explicado en limitations. Validalo antes de terminar con:
  oracle-clue validar /home/workstation/Dev/factory-rev/.factory/local/revisores/962ede7-agy-1/informe.json --paquete /home/workstation/Dev/factory-rev/.factory/cambios/20261007-192608-revisores/candidatos/962ede7/clue/paquete-agy-1.json --repo /home/workstation/Dev/factory-rev/.factory/local/revisiones/962ede7
y terminá con un resumen corto en español.

Indicaciones de quien pide la revisión:
Para correr las pruebas usá /tmp/claude-1000/-home-workstation-Dev-factory/d3ffc37f-4c26-4426-b2d7-381bdbfe4609/scratchpad/env/bin/python (tiene oracle y oracle-clue) con PATH=/tmp/claude-1000/-home-workstation-Dev-factory/d3ffc37f-4c26-4426-b2d7-381bdbfe4609/scratchpad/env/bin:$PATH, por ejemplo: python -m unittest tests.test_revisores. Revisá todo el cambio. Límites asumidos, no los reportes: un informe versionado que pasa Clue se toma como auténtico; sin oracle-clue instalado los informes se usan marcados 'sin validar' (decisión del cambio de autoproducción ya integrado); llaves literales en el comando no se admiten.
