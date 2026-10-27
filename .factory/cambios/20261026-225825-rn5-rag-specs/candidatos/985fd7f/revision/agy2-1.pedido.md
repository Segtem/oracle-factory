Sos un revisor independiente del cambio 20261026-225825-rn5-rag-specs de un proyecto que usa Oracle Factory: «Preguntar cuántas specs hay y cuáles son». No escribiste este código.
NO edites el checkout, no hagas commits ni decidas nada por la persona: tu trabajo es encontrar defectos y contarlos con evidencia.

Qué tiene que hacer el cambio:
- Propuesta: /home/workstation/Dev/factory-rag-specs/openspec/changes/20261026-225825-rn5-rag-specs/proposal.md
- Spec (lo que se promete, con sus escenarios): /home/workstation/Dev/factory-rag-specs/openspec/changes/20261026-225825-rn5-rag-specs/specs/conocimiento/spec.md

Qué revisar:
- Checkout del candidato 985fd7f (sólo lectura): /home/workstation/Dev/factory-rag-specs/.factory/local/revisiones/985fd7f-agy2-1
- Paquete de Oracle Clue con el diff y el contexto: /home/workstation/Dev/factory-rag-specs/.factory/cambios/20261026-225825-rn5-rag-specs/candidatos/985fd7f/clue/paquete-agy2-1.json

Vueltas anteriores de este cambio (ya corregidas; mirá que sigan cerradas y que no haya regresiones):
- .factory/cambios/20261026-225825-rn5-rag-specs/candidatos/84f98b2/revision/agy-1.json
- .factory/cambios/20261026-225825-rn5-rag-specs/candidatos/84f98b2/revision/agy2-1.json
- .factory/cambios/20261026-225825-rn5-rag-specs/candidatos/c1d27f5/revision/agy-1.json
- .factory/cambios/20261026-225825-rn5-rag-specs/candidatos/c1d27f5/revision/agy2-1.json
- .factory/cambios/20261026-225825-rn5-rag-specs/candidatos/6fd3d3d/revision/agy-1.json
- .factory/cambios/20261026-225825-rn5-rag-specs/candidatos/6fd3d3d/revision/agy2-1.json
- .factory/cambios/20261026-225825-rn5-rag-specs/candidatos/b5c25be/revision/agy-1.json
- .factory/cambios/20261026-225825-rn5-rag-specs/candidatos/b5c25be/revision/agy2-1.json
Fuera del paquete, porque no son producto (.factory, kb/README.md, kb/cambios/20261026-225825-rn5-rag-specs.md, kb/requisitos/conocimiento_c6dd9c535b1df9607.contar_y_listar_specs.md, kb/requisitos/conocimiento_c6dd9c535b1df9607.filtro_de_specs_no_admitido.md, kb/requisitos/conocimiento_c6dd9c535b1df9607.las_demas_preguntas_no_cambian.md, tareas): 39 archivos de registros y evidencia de Factory; no los revises.

Cómo trabajar: leé la spec y el diff; contrastá cada promesa con el código y con las pruebas; buscá casos que fallen, afirmaciones que el
código no cumple y pruebas que no prueban lo que dicen. Si podés, hacé mutaciones a mano sobre copias en tu carpeta y decí cuáles sobreviven.
Mandá la salida larga a archivos de tu carpeta y leé sólo el resumen.

Entregable: un informe JSON en /home/workstation/Dev/factory-rag-specs/.factory/local/revisores/985fd7f-agy2-1/informe.json con este formato (schema oracle-clue.review/v1):
- schema_version "oracle-clue.review/v1"; repo, base, head, diff_sha256 y context_sha256 copiados del paquete;
- provider {"name": "agy", "model": "gemini-3.8-flash-high"};
- findings: lista de hallazgos, cada uno con id, kind, severity (alta|media|baja|informativa), confidence (0 a 1), title, explanation,
  location {file, start_line, end_line, side: "head"} DENTRO de los rangos del diff del paquete, trigger, evidence, related_requirement,
  status "pendiente" y verification;
- review_status ("completo" o "incompleto") y limitations (qué corriste y qué no).
Sin hallazgos: findings vacía, explicado en limitations. Validalo antes de terminar con:
  oracle-clue validar /home/workstation/Dev/factory-rag-specs/.factory/local/revisores/985fd7f-agy2-1/informe.json --paquete /home/workstation/Dev/factory-rag-specs/.factory/cambios/20261026-225825-rn5-rag-specs/candidatos/985fd7f/clue/paquete-agy2-1.json --repo /home/workstation/Dev/factory-rag-specs/.factory/local/revisiones/985fd7f-agy2-1
y terminá con un resumen corto en español.

Indicaciones de quien pide la revisión:
Vuelta 5: se corrigieron los hallazgos de la vuelta 4 (demostrativos plurales, preposición a, palabras funcionales). Revisá el cambio contra los requisitos de su spec (openspec/changes/20261026-225825-rn5-rag-specs/specs/conocimiento/spec.md): oracle_factory/consultas.py (interpretar_specs, specs, respuesta_specs y directa), cómo lo usa oracle_factory/rag.py (preguntar) y oracle_factory/generacion.py (elaborar), tests/test_rag_specs.py, tools/verify_rag_specs.py, catalogos/factory_rag_specs.*.oracle y el párrafo nuevo de docs/conocimiento.md. Mirá especialmente: que una pregunta de specs mal clasificada no tape una pregunta de documentos legítima (falsos positivos del vocabulario), que una pregunta con tareas o cambios siga yendo al camino de antes, que el JSON de la respuesta (valor, fuentes, criterio) no rompa a quien consume --json ni al MCP, que las rutas leídas queden dentro del proyecto (symlinks) y que las pruebas fallen de verdad si se rompe el comportamiento. Para correr las pruebas usá exactamente, en primer plano y desde la raíz del checkout: PYTHONPATH=. /home/workstation/Dev/factory-rag-specs/.venv/bin/python -m unittest tests.test_rag_specs tests.test_preguntar </dev/null . No corras la suite completa. No cambies la configuración de git de ningún repositorio. Nombrá archivos con rutas relativas.
