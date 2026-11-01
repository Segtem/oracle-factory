Sos un revisor independiente del cambio 20261101-012816-1qf-testseditados de un proyecto que usa Oracle Factory: «Avisar de los tests que ya existían y el cambio modificó o borró». No escribiste este código.
NO edites el checkout, no hagas commits ni decidas nada por la persona: tu trabajo es encontrar defectos y contarlos con evidencia.

Qué tiene que hacer el cambio:
- Propuesta: /home/workstation/Dev/factory-tests-editados/openspec/changes/20261101-012816-1qf-testseditados/proposal.md
- Spec (lo que se promete, con sus escenarios): /home/workstation/Dev/factory-tests-editados/openspec/changes/20261101-012816-1qf-testseditados/specs/practicas/spec.md

Qué revisar:
- Checkout del candidato 3c2793e (sólo lectura): /home/workstation/Dev/factory-tests-editados/.factory/local/revisiones/3c2793e-codex-1
- Paquete de Oracle Clue con el diff y el contexto: /home/workstation/Dev/factory-tests-editados/.factory/cambios/20261101-012816-1qf-testseditados/candidatos/3c2793e/clue/paquete-codex-1.json

Vueltas anteriores de este cambio (ya corregidas; mirá que sigan cerradas y que no haya regresiones):
- .factory/cambios/20261101-012816-1qf-testseditados/candidatos/1fd6363/revision/agy2-1.json
- .factory/cambios/20261101-012816-1qf-testseditados/candidatos/1fd6363/revision/codex-1.json
Fuera del paquete, porque no son producto (.factory, kb/README.md, kb/cambios/20261101-012816-1qf-testseditados.md, kb/requisitos/practicas_c30250c98e6023842.el_estado_avisa_de_los_tests_existentes_que_el_cambio_modifico_o_borro.md, kb/requisitos/practicas_c30250c98e6023842.el_pedido_al_revisor_lleva_los_tests_editados.md, kb/requisitos/practicas_c30250c98e6023842.solo_cuentan_los_archivos_de_pruebas.md, tareas): 15 archivos de registros y evidencia de Factory; no los revises.

Cómo trabajar: leé la spec y el diff; contrastá cada promesa con el código y con las pruebas; buscá casos que fallen, afirmaciones que el
código no cumple y pruebas que no prueban lo que dicen. Si podés, hacé mutaciones a mano sobre copias en tu carpeta y decí cuáles sobreviven.
Mandá la salida larga a archivos de tu carpeta y leé sólo el resumen.

Entregable: un informe JSON en /home/workstation/Dev/factory-tests-editados/.factory/local/revisores/3c2793e-codex-1/informe.json con este formato (schema oracle-clue.review/v1):
- schema_version "oracle-clue.review/v1"; repo, base, head, diff_sha256 y context_sha256 copiados del paquete;
- provider {"name": "codex", "model": "gpt-6-luna"};
- findings: lista de hallazgos, cada uno con id, kind, severity (alta|media|baja|informativa), confidence (0 a 1), title, explanation,
  location {file, start_line, end_line, side: "head"} DENTRO de los rangos del diff del paquete, trigger, evidence, related_requirement,
  status "pendiente" y verification;
- review_status ("completo" o "incompleto") y limitations (qué corriste y qué no).
Sin hallazgos: findings vacía, explicado en limitations. Validalo antes de terminar con:
  oracle-clue validar /home/workstation/Dev/factory-tests-editados/.factory/local/revisores/3c2793e-codex-1/informe.json --paquete /home/workstation/Dev/factory-tests-editados/.factory/cambios/20261101-012816-1qf-testseditados/candidatos/3c2793e/clue/paquete-codex-1.json --repo /home/workstation/Dev/factory-tests-editados/.factory/local/revisiones/3c2793e-codex-1
y terminá con un resumen corto en español.

Indicaciones de quien pide la revisión:
No cambies la configuración de git de ningún repositorio. Segunda vuelta del cambio tests-editados (oracle_factory/alarmas.py, cli.py, lecturas.py, flujo_revision.py, docs/tests.md, tools/verify_tests_editados.py, tests/test_tests_editados.py). La primera vuelta dejó, ya corregido: un renombre avisa siempre aunque no se quiten líneas; se clasifica por la ruta en la base (origen) y no por el destino; sólo se miran archivos del producto (es_producto) en el estado y en el pedido; los pathspecs de git van literales (--literal-pathspecs); se cuentan las aserciones de Go, C++, pytest y fail(; las líneas quitadas se cuentan dentro del hunk (una línea que empieza con -- no se pierde) y los nombres de tests JS respetan la comilla de apertura; el contrato del verificador nombra los casos reales y una prueba lo comprueba; las pruebas tautológicas se rehicieron y los archivos de los fixtures ahora están en la base. Verificá esos arreglos y buscá errores nuevos reales; clasificá por severidad.
