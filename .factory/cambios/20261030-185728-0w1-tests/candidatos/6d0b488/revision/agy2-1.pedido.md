Sos un revisor independiente del cambio 20261030-185728-0w1-tests de un proyecto que usa Oracle Factory: «Tests unitarios como práctica del desarrollo: el paso de escribirlos primero». No escribiste este código.
NO edites el checkout, no hagas commits ni decidas nada por la persona: tu trabajo es encontrar defectos y contarlos con evidencia.

Qué tiene que hacer el cambio:
- Propuesta: /home/workstation/Dev/factory-tests-unitarios/openspec/changes/20261030-185728-0w1-tests/proposal.md
- Spec (lo que se promete, con sus escenarios): /home/workstation/Dev/factory-tests-unitarios/openspec/changes/20261030-185728-0w1-tests/specs/desarrollo/spec.md

Qué revisar:
- Checkout del candidato 6d0b488 (sólo lectura): /home/workstation/Dev/factory-tests-unitarios/.factory/local/revisiones/6d0b488-agy2-1
- Paquete de Oracle Clue con el diff y el contexto: /home/workstation/Dev/factory-tests-unitarios/.factory/cambios/20261030-185728-0w1-tests/candidatos/6d0b488/clue/paquete-agy2-1.json

Fuera del paquete, porque no son producto (.factory, kb/README.md, kb/cambios/20261030-185728-0w1-tests.md, kb/requisitos/desarrollo_cb4e5e98f60cb24f1.documento_de_la_practica.md, kb/requisitos/desarrollo_cb4e5e98f60cb24f1.guia_de_tests_para_agentes.md, kb/requisitos/desarrollo_cb4e5e98f60cb24f1.paso_de_tests_primero.md, tareas): 8 archivos de registros y evidencia de Factory; no los revises.

Cómo trabajar: leé la spec y el diff; contrastá cada promesa con el código y con las pruebas; buscá casos que fallen, afirmaciones que el
código no cumple y pruebas que no prueban lo que dicen. Si podés, hacé mutaciones a mano sobre copias en tu carpeta y decí cuáles sobreviven.
Mandá la salida larga a archivos de tu carpeta y leé sólo el resumen.

Entregable: un informe JSON en /home/workstation/Dev/factory-tests-unitarios/.factory/local/revisores/6d0b488-agy2-1/informe.json con este formato (schema oracle-clue.review/v1):
- schema_version "oracle-clue.review/v1"; repo, base, head, diff_sha256 y context_sha256 copiados del paquete;
- provider {"name": "agy", "model": "gemini-4-argon-high"};
- findings: lista de hallazgos, cada uno con id, kind, severity (alta|media|baja|informativa), confidence (0 a 1), title, explanation,
  location {file, start_line, end_line, side: "head"} DENTRO de los rangos del diff del paquete, trigger, evidence, related_requirement,
  status "pendiente" y verification;
- review_status ("completo" o "incompleto") y limitations (qué corriste y qué no).
Sin hallazgos: findings vacía, explicado en limitations. Validalo antes de terminar con:
  oracle-clue validar /home/workstation/Dev/factory-tests-unitarios/.factory/local/revisores/6d0b488-agy2-1/informe.json --paquete /home/workstation/Dev/factory-tests-unitarios/.factory/cambios/20261030-185728-0w1-tests/candidatos/6d0b488/clue/paquete-agy2-1.json --repo /home/workstation/Dev/factory-tests-unitarios/.factory/local/revisiones/6d0b488-agy2-1
y terminá con un resumen corto en español.

Indicaciones de quien pide la revisión:
No cambies la configuración de git de ningún repositorio. Revisá el cambio tests-unitarios: el paso de escribir primero los tests en la plantilla de tareas (oracle_factory/plantillas.py, español e inglés), la línea de la guía para agentes (oracle_factory/agentes.py y AGENTS.md generado), docs/tests.md y tests/test_tests_unitarios.py. Este cambio se integró con main, que trae un cambio hermano (pruebas-practica: avisos en estado y la excepción «Pruebas: no aplica»); la redacción del paso es la de este cambio y se adaptaron dos pruebas del hermano. Buscá errores reales (contradicciones entre docs/tests.md, la plantilla y la guía; afirmaciones falsas sobre lo que Factory hace o no hace; fuentes citadas mal; pruebas que pasan por construcción); clasificá por severidad.
