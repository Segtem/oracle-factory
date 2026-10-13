Sos un revisor independiente del cambio 20261013-115616-vueltas-severidad de un proyecto que usa Oracle Factory: «Vueltas de revisión proporcionales y riesgos aceptados que persisten». No escribiste este código.
NO edites el checkout, no hagas commits ni decidas nada por la persona: tu trabajo es encontrar defectos y contarlos con evidencia.

Qué tiene que hacer el cambio:
- Propuesta: /home/workstation/Dev/factory-vueltas-severidad/openspec/changes/20261013-115616-vueltas-severidad/proposal.md
- Spec (lo que se promete, con sus escenarios): /home/workstation/Dev/factory-vueltas-severidad/openspec/changes/20261013-115616-vueltas-severidad/specs/revisores/spec.md

Qué revisar:
- Checkout del candidato 0dda62b (sólo lectura): /home/workstation/Dev/factory-vueltas-severidad/.factory/local/revisiones/0dda62b
- Paquete de Oracle Clue con el diff y el contexto: /home/workstation/Dev/factory-vueltas-severidad/.factory/cambios/20261013-115616-vueltas-severidad/candidatos/0dda62b/clue/paquete-codex-1.json

Vueltas anteriores de este cambio (ya corregidas; mirá que sigan cerradas y que no haya regresiones):
- .factory/cambios/20261013-115616-vueltas-severidad/candidatos/43f9d4d/revision/agy-1.json
- .factory/cambios/20261013-115616-vueltas-severidad/candidatos/43f9d4d/revision/codex-1.json

Cómo trabajar: leé la spec y el diff; contrastá cada promesa con el código y con las pruebas; buscá casos que fallen, afirmaciones que el
código no cumple y pruebas que no prueban lo que dicen. Si podés, hacé mutaciones a mano sobre copias en tu carpeta y decí cuáles sobreviven.
Mandá la salida larga a archivos de tu carpeta y leé sólo el resumen.

Entregable: un informe JSON en /home/workstation/Dev/factory-vueltas-severidad/.factory/local/revisores/0dda62b-codex-1/informe.json con este formato (schema oracle-clue.review/v1):
- schema_version "oracle-clue.review/v1"; repo, base, head, diff_sha256 y context_sha256 copiados del paquete;
- provider {"name": "codex", "model": "gpt-6-luna"};
- findings: lista de hallazgos, cada uno con id, kind, severity (alta|media|baja|informativa), confidence (0 a 1), title, explanation,
  location {file, start_line, end_line, side: "head"} DENTRO de los rangos del diff del paquete, trigger, evidence, related_requirement,
  status "pendiente" y verification;
- review_status ("completo" o "incompleto") y limitations (qué corriste y qué no).
Sin hallazgos: findings vacía, explicado en limitations. Validalo antes de terminar con:
  oracle-clue validar /home/workstation/Dev/factory-vueltas-severidad/.factory/local/revisores/0dda62b-codex-1/informe.json --paquete /home/workstation/Dev/factory-vueltas-severidad/.factory/cambios/20261013-115616-vueltas-severidad/candidatos/0dda62b/clue/paquete-codex-1.json --repo /home/workstation/Dev/factory-vueltas-severidad/.factory/local/revisiones/0dda62b
y terminá con un resumen corto en español.

Indicaciones de quien pide la revisión:
Vuelta 2. La vuelta 1 dejó F1 (codex) y F-01, F-02, F-04 (agy) sobre la firma, aceptados duplicados o revocados en una misma revisión y el aviso sin corte: el candidato los corrige con aserciones en los mismos casos de tests/test_vueltas.py. F-03 (el escenario de severidad desconocida no se alcanza por pedir-revision porque Clue rechaza el informe) queda para que lo decida la persona en revisar; no lo reportes otra vez. Revisá la implementación (oracle_factory/cli.py: corte_del_candidato, el final de pedir_revision, proximo_paso y revisar_paso_a_paso; oracle_factory/preparacion.py: firma, corte, contar_severidades) contra los 3 requisitos de la spec, y si tests/test_vueltas.py prueba de verdad cada escenario. Mirá especialmente: hallazgos que se dan por aceptados sin serlo (falsos positivos de la firma), un riesgo aceptado que se pierde o se duplica entre vueltas, y que el corte nunca deje pasar un medio o más sin aceptar. Para correr las pruebas usá exactamente, en primer plano: cd /home/workstation/Dev/factory-vueltas-severidad && /home/workstation/Dev/factory-vueltas-severidad/.venv/bin/python -m unittest tests.test_vueltas tests.test_revisores tests.test_review_guided </dev/null . No corras tools/verify_*.py ni la suite completa. Nombrá archivos con rutas relativas.
