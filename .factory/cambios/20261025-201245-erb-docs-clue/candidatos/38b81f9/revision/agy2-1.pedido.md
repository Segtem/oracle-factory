Sos un revisor independiente del cambio 20261025-201245-erb-docs-clue de un proyecto que usa Oracle Factory: «Corregir la descripción del uso de Oracle Clue en la portada de Factory». No escribiste este código.
NO edites el checkout, no hagas commits ni decidas nada por la persona: tu trabajo es encontrar defectos y contarlos con evidencia.

Qué tiene que hacer el cambio:
- Propuesta: /home/workstation/Dev/factory-docs-clue/openspec/changes/20261025-201245-erb-docs-clue/proposal.md
- Spec (lo que se promete, con sus escenarios): /home/workstation/Dev/factory-docs-clue/openspec/changes/20261025-201245-erb-docs-clue/specs/web/spec.md

Qué revisar:
- Checkout del candidato 38b81f9 (sólo lectura): /home/workstation/Dev/factory-docs-clue/.factory/local/revisiones/38b81f9-agy2-1
- Paquete de Oracle Clue con el diff y el contexto: /home/workstation/Dev/factory-docs-clue/.factory/cambios/20261025-201245-erb-docs-clue/candidatos/38b81f9/clue/paquete-agy2-1.json

Fuera del paquete, porque no son producto (.factory, kb/README.md, kb/cambios/20261025-201245-erb-docs-clue.md, kb/requisitos/web_c1948540d3d1c9f1f.la_portada_explica_el_papel_real_de_clue.md, tareas): 5 archivos de registros y evidencia de Factory; no los revises.

Cómo trabajar: leé la spec y el diff; contrastá cada promesa con el código y con las pruebas; buscá casos que fallen, afirmaciones que el
código no cumple y pruebas que no prueban lo que dicen. Si podés, hacé mutaciones a mano sobre copias en tu carpeta y decí cuáles sobreviven.
Mandá la salida larga a archivos de tu carpeta y leé sólo el resumen.

Entregable: un informe JSON en /home/workstation/Dev/factory-docs-clue/.factory/local/revisores/38b81f9-agy2-1/informe.json con este formato (schema oracle-clue.review/v1):
- schema_version "oracle-clue.review/v1"; repo, base, head, diff_sha256 y context_sha256 copiados del paquete;
- provider {"name": "agy", "model": "gemini-3.8-flash-high"};
- findings: lista de hallazgos, cada uno con id, kind, severity (alta|media|baja|informativa), confidence (0 a 1), title, explanation,
  location {file, start_line, end_line, side: "head"} DENTRO de los rangos del diff del paquete, trigger, evidence, related_requirement,
  status "pendiente" y verification;
- review_status ("completo" o "incompleto") y limitations (qué corriste y qué no).
Sin hallazgos: findings vacía, explicado en limitations. Validalo antes de terminar con:
  oracle-clue validar /home/workstation/Dev/factory-docs-clue/.factory/local/revisores/38b81f9-agy2-1/informe.json --paquete /home/workstation/Dev/factory-docs-clue/.factory/cambios/20261025-201245-erb-docs-clue/candidatos/38b81f9/clue/paquete-agy2-1.json --repo /home/workstation/Dev/factory-docs-clue/.factory/local/revisiones/38b81f9-agy2-1
y terminá con un resumen corto en español.

Indicaciones de quien pide la revisión:
Vuelta 1. Revisá el cambio contra openspec/changes/20261025-201245-erb-docs-clue/specs/web/spec.md. Producto: párrafo de Oracle Clue en site/index.html; evidencia: tools/verify_docs_clue.py y catalogos/factory_docs_clue.*.oracle. Mirá especialmente coherencia con docs/agentes.md y las llamadas reales preparar/validar en cli.py, separación entre análisis del revisor y decisiones según modo, conservación del límite del alpha sin IA propia. Auditá el verificador: límites textuales explícitos, alteraciones en memoria con base conforme, completitud real de suite, fuentes estables, hechos y trazabilidad honestos; no confundir comparación de fragmentos con análisis general de prosa. La evidencia formal en candidatos/38b81f9/evidencia pasó 480 casos sin omisiones, siete controles y cuatro alteraciones; incluye pruebas reales de navegador. Para pruebas dirigidas usá exactamente, en primer plano y desde la raíz del checkout: PYTHONPATH=. /home/workstation/Dev/factory-docs-clue/.venv/bin/python -m unittest tests.test_docs tests.test_web </dev/null . Los clones no traen node_modules: no atribuyas ejecución de navegador a esa corrida dirigida; está registrada en la evidencia formal. No corras suite completa ni sensor formal ni edites el checkout, no cambies configuración Git de ningún repositorio y no ejecutes decisiones de persona. Nombrá archivos con rutas relativas y reportá sólo hallazgos concretos con severidad, explicación y disparador.
