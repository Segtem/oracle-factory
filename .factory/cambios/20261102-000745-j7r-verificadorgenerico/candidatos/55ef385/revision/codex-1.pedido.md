Sos un revisor independiente del cambio 20261102-000745-j7r-verificadorgenerico de un proyecto que usa Oracle Factory: «Un verificador reutilizable para la evidencia de cada cambio». No escribiste este código.
NO edites el checkout, no hagas commits ni decidas nada por la persona: tu trabajo es encontrar defectos y contarlos con evidencia.

Qué tiene que hacer el cambio:
- Propuesta: /home/workstation/Dev/factory-verificador-generico/openspec/changes/20261102-000745-j7r-verificadorgenerico/proposal.md
- Spec (lo que se promete, con sus escenarios): /home/workstation/Dev/factory-verificador-generico/openspec/changes/20261102-000745-j7r-verificadorgenerico/specs/practicas/spec.md

Qué revisar:
- Checkout del candidato 55ef385 (sólo lectura): /home/workstation/Dev/factory-verificador-generico/.factory/local/revisiones/55ef385-codex-1
- Paquete de Oracle Clue con el diff y el contexto: /home/workstation/Dev/factory-verificador-generico/.factory/cambios/20261102-000745-j7r-verificadorgenerico/candidatos/55ef385/clue/paquete-codex-1.json

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
Fuera del paquete, porque no son producto (.factory, kb/README.md, kb/cambios/20261102-000745-j7r-verificadorgenerico.md, kb/requisitos/practicas_ca947e8cba4f605c1.el_verificador_atribuye_cada_caso_al_requisito_que_su_nombre_indica.md, kb/requisitos/practicas_ca947e8cba4f605c1.el_verificador_escribe_los_catalogos_del_cambio.md, kb/requisitos/practicas_ca947e8cba4f605c1.el_verificador_produce_la_evidencia_completa_del_cambio.md, tareas): 48 archivos de registros y evidencia de Factory; no los revises.

Cómo trabajar: leé la spec y el diff; contrastá cada promesa con el código y con las pruebas; buscá casos que fallen, afirmaciones que el
código no cumple y pruebas que no prueban lo que dicen. Si podés, hacé mutaciones a mano sobre copias en tu carpeta y decí cuáles sobreviven.
Mandá la salida larga a archivos de tu carpeta y leé sólo el resumen.

Entregable: un informe JSON en /home/workstation/Dev/factory-verificador-generico/.factory/local/revisores/55ef385-codex-1/informe.json con este formato (schema oracle-clue.review/v1):
- schema_version "oracle-clue.review/v1"; repo, base, head, diff_sha256 y context_sha256 copiados del paquete;
- provider {"name": "codex", "model": "gpt-6-luna"};
- findings: lista de hallazgos, cada uno con id, kind, severity (alta|media|baja|informativa), confidence (0 a 1), title, explanation,
  location {file, start_line, end_line, side: "head"} DENTRO de los rangos del diff del paquete, trigger, evidence, related_requirement,
  status "pendiente" y verification;
- review_status ("completo" o "incompleto") y limitations (qué corriste y qué no).
Sin hallazgos: findings vacía, explicado en limitations. Validalo antes de terminar con:
  oracle-clue validar /home/workstation/Dev/factory-verificador-generico/.factory/local/revisores/55ef385-codex-1/informe.json --paquete /home/workstation/Dev/factory-verificador-generico/.factory/cambios/20261102-000745-j7r-verificadorgenerico/candidatos/55ef385/clue/paquete-codex-1.json --repo /home/workstation/Dev/factory-verificador-generico/.factory/local/revisiones/55ef385-codex-1
y terminá con un resumen corto en español.

Indicaciones de quien pide la revisión:
No cambies la configuración de git de ningún repositorio. Es la sexta ronda de verificador-generico. La quinta trajo 1 hallazgo de codex (flash dio 0): al regenerar con --catalogos, los catálogos del mismo módulo que la spec ya no pide quedaban como medidas activas; ahora se retiran y se nombran «(retirado)» en la salida, sin tocar otros módulos (el punto después de factory_<x> separa `demo` de `demo_extra`). Límite declarado en docs/tests.md: un requisito con «Pruebas: no aplica — motivo» sigue necesitando un caso con esta herramienta. Verificá que el arreglo cubre la CLASE (por ejemplo: carpeta de catálogos con enlaces simbólicos o subcarpetas, permisos, el orden de escritura frente al retiro, qué pasa si el retiro falla a mitad) y buscá errores reales nuevos y de impacto práctico en tools/verificar_cambio.py, tests/test_verificador_generico.py, docs/tests.md y los catálogos; decí cuáles hallazgos son exóticos y por qué. Clasificá por severidad.
