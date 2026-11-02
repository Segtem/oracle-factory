Sos un revisor independiente del cambio 20261102-000745-j7r-verificadorgenerico de un proyecto que usa Oracle Factory: «Un verificador reutilizable para la evidencia de cada cambio». No escribiste este código.
NO edites el checkout, no hagas commits ni decidas nada por la persona: tu trabajo es encontrar defectos y contarlos con evidencia.

Qué tiene que hacer el cambio:
- Propuesta: /home/workstation/Dev/factory-verificador-generico/openspec/changes/20261102-000745-j7r-verificadorgenerico/proposal.md
- Spec (lo que se promete, con sus escenarios): /home/workstation/Dev/factory-verificador-generico/openspec/changes/20261102-000745-j7r-verificadorgenerico/specs/practicas/spec.md

Qué revisar:
- Checkout del candidato c41e9ce (sólo lectura): /home/workstation/Dev/factory-verificador-generico/.factory/local/revisiones/c41e9ce-agy2-flash-1
- Paquete de Oracle Clue con el diff y el contexto: /home/workstation/Dev/factory-verificador-generico/.factory/cambios/20261102-000745-j7r-verificadorgenerico/candidatos/c41e9ce/clue/paquete-agy2-flash-1.json

Vueltas anteriores de este cambio (ya corregidas; mirá que sigan cerradas y que no haya regresiones):
- .factory/cambios/20261102-000745-j7r-verificadorgenerico/candidatos/1b54f3f/revision/agy2-flash-1.json
- .factory/cambios/20261102-000745-j7r-verificadorgenerico/candidatos/1b54f3f/revision/codex-1.json
- .factory/cambios/20261102-000745-j7r-verificadorgenerico/candidatos/eca559f/revision/agy2-flash-1.json
- .factory/cambios/20261102-000745-j7r-verificadorgenerico/candidatos/eca559f/revision/codex-1.json
- .factory/cambios/20261102-000745-j7r-verificadorgenerico/candidatos/bd88492/revision/agy2-flash-1.json
- .factory/cambios/20261102-000745-j7r-verificadorgenerico/candidatos/bd88492/revision/codex-1.json
- .factory/cambios/20261102-000745-j7r-verificadorgenerico/candidatos/a35cbce/revision/agy2-flash-1.json
- .factory/cambios/20261102-000745-j7r-verificadorgenerico/candidatos/a35cbce/revision/codex-1.json
- .factory/cambios/20261102-000745-j7r-verificadorgenerico/candidatos/749822a/revision/agy2-flash-1.json
- .factory/cambios/20261102-000745-j7r-verificadorgenerico/candidatos/749822a/revision/codex-1.json
- .factory/cambios/20261102-000745-j7r-verificadorgenerico/candidatos/55ef385/revision/agy2-flash-1.json
- .factory/cambios/20261102-000745-j7r-verificadorgenerico/candidatos/55ef385/revision/codex-1.json
Fuera del paquete, porque no son producto (.factory, kb/README.md, kb/cambios/20261102-000745-j7r-verificadorgenerico.md, kb/requisitos/practicas_ca947e8cba4f605c1.el_verificador_atribuye_cada_caso_al_requisito_que_su_nombre_indica.md, kb/requisitos/practicas_ca947e8cba4f605c1.el_verificador_escribe_los_catalogos_del_cambio.md, kb/requisitos/practicas_ca947e8cba4f605c1.el_verificador_produce_la_evidencia_completa_del_cambio.md, tareas): 56 archivos de registros y evidencia de Factory; no los revises.

Cómo trabajar: leé la spec y el diff; contrastá cada promesa con el código y con las pruebas; buscá casos que fallen, afirmaciones que el
código no cumple y pruebas que no prueban lo que dicen. Si podés, hacé mutaciones a mano sobre copias en tu carpeta y decí cuáles sobreviven.
Mandá la salida larga a archivos de tu carpeta y leé sólo el resumen.

Entregable: un informe JSON en /home/workstation/Dev/factory-verificador-generico/.factory/local/revisores/c41e9ce-agy2-flash-1/informe.json con este formato (schema oracle-clue.review/v1):
- schema_version "oracle-clue.review/v1"; repo, base, head, diff_sha256 y context_sha256 copiados del paquete;
- provider {"name": "agy", "model": "gemini-3.8-flash-high"};
- findings: lista de hallazgos, cada uno con id, kind, severity (alta|media|baja|informativa), confidence (0 a 1), title, explanation,
  location {file, start_line, end_line, side: "head"} DENTRO de los rangos del diff del paquete, trigger, evidence, related_requirement,
  status "pendiente" y verification;
- review_status ("completo" o "incompleto") y limitations (qué corriste y qué no).
Sin hallazgos: findings vacía, explicado en limitations. Validalo antes de terminar con:
  oracle-clue validar /home/workstation/Dev/factory-verificador-generico/.factory/local/revisores/c41e9ce-agy2-flash-1/informe.json --paquete /home/workstation/Dev/factory-verificador-generico/.factory/cambios/20261102-000745-j7r-verificadorgenerico/candidatos/c41e9ce/clue/paquete-agy2-flash-1.json --repo /home/workstation/Dev/factory-verificador-generico/.factory/local/revisiones/c41e9ce-agy2-flash-1
y terminá con un resumen corto en español.

Indicaciones de quien pide la revisión:
No cambies la configuración de git de ningún repositorio. Es la séptima ronda de verificador-generico. La sexta trajo 1 hallazgo bajo de cada revisor (el mismo): --catalogos seguía enlaces simbólicos al escribir. Ahora escribir_catalogos rechaza, antes de escribir nada, que catalogos/ o cualquiera de los catálogos del cambio sea un enlace simbólico (ContratoInvalido, código 2). Límite declarado en docs/tests.md: un requisito con «Pruebas: no aplica — motivo» sigue necesitando un caso con esta herramienta. Verificá que el arreglo cubre la CLASE y buscá errores reales nuevos y de impacto práctico en tools/verificar_cambio.py, tests/test_verificador_generico.py, docs/tests.md y los catálogos; marcá cuáles hallazgos son exóticos y por qué. Si no hay nada de impacto práctico, decilo con claridad. Clasificá por severidad.
