Sos un revisor independiente del cambio 20261021-235127-fjn-rag de un proyecto que usa Oracle Factory: «RAG del conocimiento: preguntar al vault con búsqueda híbrida, sólo lo vigente, con citas y calidad medida». No escribiste este código.
NO edites el checkout, no hagas commits ni decidas nada por la persona: tu trabajo es encontrar defectos y contarlos con evidencia.

Qué tiene que hacer el cambio:
- Propuesta: /home/workstation/Dev/factory-rag/openspec/changes/20261021-235127-fjn-rag/proposal.md
- Spec (lo que se promete, con sus escenarios): /home/workstation/Dev/factory-rag/openspec/changes/20261021-235127-fjn-rag/specs/conocimiento/spec.md

Qué revisar:
- Checkout del candidato 19f79ec (sólo lectura): /home/workstation/Dev/factory-rag/.factory/local/revisiones/19f79ec-agy-1
- Paquete de Oracle Clue con el diff y el contexto: /home/workstation/Dev/factory-rag/.factory/cambios/20261021-235127-fjn-rag/candidatos/19f79ec/clue/paquete-agy-1.json

Fuera del paquete, porque no son producto (.factory, kb/README.md, kb/cambios/20261021-235127-fjn-rag.md, kb/requisitos/conocimiento_c48413c31f1bcbd66.el_indice_se_mantiene_solo.md, kb/requisitos/conocimiento_c48413c31f1bcbd66.la_busqueda_es_hibrida_y_dice_que_uso.md, kb/requisitos/conocimiento_c48413c31f1bcbd66.la_calidad_se_mide_con_preguntas_de_oro.md, kb/requisitos/conocimiento_c48413c31f1bcbd66.los_embeddings_son_configurables_y_locales_por_defecto.md, kb/requisitos/conocimiento_c48413c31f1bcbd66.preguntar_devuelve_pasajes_vigentes_con_su_cita.md, tareas): 9 archivos de registros y evidencia de Factory; no los revises.

Cómo trabajar: leé la spec y el diff; contrastá cada promesa con el código y con las pruebas; buscá casos que fallen, afirmaciones que el
código no cumple y pruebas que no prueban lo que dicen. Si podés, hacé mutaciones a mano sobre copias en tu carpeta y decí cuáles sobreviven.
Mandá la salida larga a archivos de tu carpeta y leé sólo el resumen.

Entregable: un informe JSON en /home/workstation/Dev/factory-rag/.factory/local/revisores/19f79ec-agy-1/informe.json con este formato (schema oracle-clue.review/v1):
- schema_version "oracle-clue.review/v1"; repo, base, head, diff_sha256 y context_sha256 copiados del paquete;
- provider {"name": "agy", "model": "gemini-3.8-flash-high"};
- findings: lista de hallazgos, cada uno con id, kind, severity (alta|media|baja|informativa), confidence (0 a 1), title, explanation,
  location {file, start_line, end_line, side: "head"} DENTRO de los rangos del diff del paquete, trigger, evidence, related_requirement,
  status "pendiente" y verification;
- review_status ("completo" o "incompleto") y limitations (qué corriste y qué no).
Sin hallazgos: findings vacía, explicado en limitations. Validalo antes de terminar con:
  oracle-clue validar /home/workstation/Dev/factory-rag/.factory/local/revisores/19f79ec-agy-1/informe.json --paquete /home/workstation/Dev/factory-rag/.factory/cambios/20261021-235127-fjn-rag/candidatos/19f79ec/clue/paquete-agy-1.json --repo /home/workstation/Dev/factory-rag/.factory/local/revisiones/19f79ec-agy-1
y terminá con un resumen corto en español.

Indicaciones de quien pide la revisión:
Vuelta 1. Revisá el cambio, contra los 5 requisitos de su spec: oracle_factory/rag.py (corpus y vigencia, BM25, embeddings por HTTP con Ollama u OpenAI, índice SQLite en .factory/local/rag/, fusión RRF y grafo, preguntas de oro), comando_preguntar y la clave rag de la configuración en oracle_factory/cli.py, tests/test_rag.py, tools/verify_rag.py, catalogos/factory_rag.*.oracle, kb/preguntas-de-oro.json y el README. Mirá especialmente: texto del proyecto que pueda salir a una URL no configurada, pasajes no vigentes que se cuelen (notas por revisar, cambios abandonados, requisitos no vigentes), un índice que quede viejo o pida embeddings de más, que preguntar escriba algo fuera de .factory/local/rag/, rutas o archivos raros en el corpus (enlaces simbólicos, archivos enormes, codificaciones), y si las medidas prueban lo que prometen. Para correr las pruebas usá exactamente, en primer plano y desde la raíz del checkout: PYTHONPATH=. /home/workstation/Dev/factory-rag/.venv/bin/python -m unittest tests.test_rag </dev/null . No corras la suite completa. No cambies la configuración de git de ningún repositorio. Nombrá archivos con rutas relativas.
