Sos un revisor independiente del cambio 20261007-223645-decisiones-guiadas de un proyecto que usa Oracle Factory: «Decisiones guiadas: menú y opciones en vez de frases». No escribiste este código.
NO edites el checkout, no hagas commits ni decidas nada por la persona: tu trabajo es encontrar defectos y contarlos con evidencia.

Qué tiene que hacer el cambio:
- Propuesta: /home/workstation/Dev/factory-dg/openspec/changes/20261007-223645-decisiones-guiadas/proposal.md
- Spec (lo que se promete, con sus escenarios): /home/workstation/Dev/factory-dg/openspec/changes/20261007-223645-decisiones-guiadas/specs/decisiones/spec.md

Qué revisar:
- Checkout del candidato 349adaa (sólo lectura): /home/workstation/Dev/factory-dg/.factory/local/revisiones/349adaa
- Paquete de Oracle Clue con el diff y el contexto: /home/workstation/Dev/factory-dg/.factory/cambios/20261007-223645-decisiones-guiadas/candidatos/349adaa/clue/paquete-codex-1.json

Vueltas anteriores de este cambio (ya corregidas; mirá que sigan cerradas y que no haya regresiones):
- .factory/cambios/20261007-223645-decisiones-guiadas/candidatos/158b050/revision/codex-1.json
- .factory/cambios/20261007-223645-decisiones-guiadas/candidatos/7b7bc16/revision/codex-1.json
- .factory/cambios/20261007-223645-decisiones-guiadas/candidatos/76e6b07/revision/codex-1.json
- .factory/cambios/20261007-223645-decisiones-guiadas/candidatos/449b8eb/revision/agy-1.json
- .factory/cambios/20261007-223645-decisiones-guiadas/candidatos/449b8eb/revision/codex-1.json
- .factory/cambios/20261007-223645-decisiones-guiadas/candidatos/792efe2/revision/codex-1.json

Cómo trabajar: leé la spec y el diff; contrastá cada promesa con el código y con las pruebas; buscá casos que fallen, afirmaciones que el
código no cumple y pruebas que no prueban lo que dicen. Si podés, hacé mutaciones a mano sobre copias en tu carpeta y decí cuáles sobreviven.
Mandá la salida larga a archivos de tu carpeta y leé sólo el resumen.

Entregable: un informe JSON en /home/workstation/Dev/factory-dg/.factory/local/revisores/349adaa-codex-1/informe.json con este formato (schema oracle-clue.review/v1):
- schema_version "oracle-clue.review/v1"; repo, base, head, diff_sha256 y context_sha256 copiados del paquete;
- provider {"name": "codex", "model": "gpt-6-luna"};
- findings: lista de hallazgos, cada uno con id, kind, severity (alta|media|baja|informativa), confidence (0 a 1), title, explanation,
  location {file, start_line, end_line, side: "head"} DENTRO de los rangos del diff del paquete, trigger, evidence, related_requirement,
  status "pendiente" y verification;
- review_status ("completo" o "incompleto") y limitations (qué corriste y qué no).
Sin hallazgos: findings vacía, explicado en limitations. Validalo antes de terminar con:
  oracle-clue validar /home/workstation/Dev/factory-dg/.factory/local/revisores/349adaa-codex-1/informe.json --paquete /home/workstation/Dev/factory-dg/.factory/cambios/20261007-223645-decisiones-guiadas/candidatos/349adaa/clue/paquete-codex-1.json --repo /home/workstation/Dev/factory-dg/.factory/local/revisiones/349adaa
y terminá con un resumen corto en español.

Indicaciones de quien pide la revisión:
La base de este paquete no es main: es main más la migración mecánica de 17 archivos de pruebas y arneses (las frases de confirmación tipeadas reemplazadas por la opción '1'); el paquete completo supera el límite de Clue. Esa parte la cubre la suite. Para correr las pruebas usá .venv/bin/python con PATH=/tmp/claude-1000/-home-workstation-Dev-factory/d3ffc37f-4c26-4426-b2d7-381bdbfe4609/scratchpad/env/bin:$PATH, por ejemplo: .venv/bin/python -m unittest tests.test_decisiones. Revisá todo lo que está en el paquete, incluidos choques de lo nuevo con contratos existentes del registro y de los documentos de revisión. Límites asumidos, no los reportes: Factory no autentica actores (distingue terminal de --agente); el menú usa input() con números, sin curses.
