Sos un revisor independiente del cambio 20261025-122552-ho0-entrega-a14 de un proyecto que usa Oracle Factory: «Preparar la distribución 0.1.0a14 con documentación y RAG actualizados». No escribiste este código.
NO edites el checkout, no hagas commits ni decidas nada por la persona: tu trabajo es encontrar defectos y contarlos con evidencia.

Qué tiene que hacer el cambio:
- Propuesta: /home/workstation/Dev/factory-entrega-a14/openspec/changes/20261025-122552-ho0-entrega-a14/proposal.md
- Spec (lo que se promete, con sus escenarios): /home/workstation/Dev/factory-entrega-a14/openspec/changes/20261025-122552-ho0-entrega-a14/specs/distribucion/spec.md

Qué revisar:
- Checkout del candidato 364a015 (sólo lectura): /home/workstation/Dev/factory-entrega-a14/.factory/local/revisiones/364a015-agy2-1
- Paquete de Oracle Clue con el diff y el contexto: /home/workstation/Dev/factory-entrega-a14/.factory/cambios/20261025-122552-ho0-entrega-a14/candidatos/364a015/clue/paquete-agy2-1.json

Fuera del paquete, porque no son producto (.factory, kb/README.md, kb/cambios/20261025-122552-ho0-entrega-a14.md, kb/requisitos/distribucion_c477fe3fb3e543879.la_distribucion_instalada_ofrece_las_consultas_del_proyecto.md, kb/requisitos/distribucion_c477fe3fb3e543879.la_entrega_registra_sus_pruebas_y_sus_limites.md, kb/requisitos/distribucion_c477fe3fb3e543879.la_version_de_entrega_es_coherente_y_declara_su_estado.md, tareas): 7 archivos de registros y evidencia de Factory; no los revises.

Cómo trabajar: leé la spec y el diff; contrastá cada promesa con el código y con las pruebas; buscá casos que fallen, afirmaciones que el
código no cumple y pruebas que no prueban lo que dicen. Si podés, hacé mutaciones a mano sobre copias en tu carpeta y decí cuáles sobreviven.
Mandá la salida larga a archivos de tu carpeta y leé sólo el resumen.

Entregable: un informe JSON en /home/workstation/Dev/factory-entrega-a14/.factory/local/revisores/364a015-agy2-1/informe.json con este formato (schema oracle-clue.review/v1):
- schema_version "oracle-clue.review/v1"; repo, base, head, diff_sha256 y context_sha256 copiados del paquete;
- provider {"name": "agy", "model": "gemini-3.8-flash-high"};
- findings: lista de hallazgos, cada uno con id, kind, severity (alta|media|baja|informativa), confidence (0 a 1), title, explanation,
  location {file, start_line, end_line, side: "head"} DENTRO de los rangos del diff del paquete, trigger, evidence, related_requirement,
  status "pendiente" y verification;
- review_status ("completo" o "incompleto") y limitations (qué corriste y qué no).
Sin hallazgos: findings vacía, explicado en limitations. Validalo antes de terminar con:
  oracle-clue validar /home/workstation/Dev/factory-entrega-a14/.factory/local/revisores/364a015-agy2-1/informe.json --paquete /home/workstation/Dev/factory-entrega-a14/.factory/cambios/20261025-122552-ho0-entrega-a14/candidatos/364a015/clue/paquete-agy2-1.json --repo /home/workstation/Dev/factory-entrega-a14/.factory/local/revisiones/364a015-agy2-1
y terminá con un resumen corto en español.

Indicaciones de quien pide la revisión:
Vuelta 1. Revisá el cambio contra los tres requisitos aprobados de openspec/changes/20261025-122552-ho0-entrega-a14/specs/distribucion/spec.md. Es preparación 0.1.0a14, todavía sin publicación. Inspeccioná tools/probar_entrega_a14.py, tools/verify_entrega_a14.py, tools/mutar_entrega_a14.py, tests/test_entrega_a14.py, tests/test_entrega_integridad.py, los cuatro catalogos/factory_entrega_a14.*.oracle, metadata, README/notas/guías/web. Mirá especialmente: ausencia de falsos verdes; suite completa real sin omisiones/duplicados/fallas; mutantes de implementación con identidad y fuentes actuales; artefactos nuevos con hashes y origen instalado fuera del checkout; respuesta mixta con citas documentales y conteo calculado, rechazo de escritura y registro intacto; evidencia suficiente y límites de simulación/publicación honestos. La evidencia formal commiteada está en .factory/cambios/20261025-122552-ho0-entrega-a14/candidatos/364a015/evidencia (480/480 pruebas y 14 mutantes). Para correr pruebas usá exactamente, en primer plano y desde la raíz del checkout: PYTHONPATH=. /home/workstation/Dev/factory-entrega-a14/.venv/bin/python -m unittest tests.test_entrega_a14 tests.test_entrega_integridad tests.test_docs </dev/null . No corras la suite completa ni mutaciones, no edites archivos, no cambies configuración de git de ningún repositorio ni ejecutes decisiones de persona. Nombrá archivos con rutas relativas y reportá hallazgos concretos con severidad, disparador y explicación.
