Sos un revisor independiente del cambio 20261101-012816-1qf-testseditados de un proyecto que usa Oracle Factory: «Avisar de los tests que ya existían y el cambio modificó o borró». No escribiste este código.
NO edites el checkout, no hagas commits ni decidas nada por la persona: tu trabajo es encontrar defectos y contarlos con evidencia.

Qué tiene que hacer el cambio:
- Propuesta: /home/workstation/Dev/factory-tests-editados/openspec/changes/20261101-012816-1qf-testseditados/proposal.md
- Spec (lo que se promete, con sus escenarios): /home/workstation/Dev/factory-tests-editados/openspec/changes/20261101-012816-1qf-testseditados/specs/practicas/spec.md

Qué revisar:
- Checkout del candidato 1fd6363 (sólo lectura): /home/workstation/Dev/factory-tests-editados/.factory/local/revisiones/1fd6363-codex-1
- Paquete de Oracle Clue con el diff y el contexto: /home/workstation/Dev/factory-tests-editados/.factory/cambios/20261101-012816-1qf-testseditados/candidatos/1fd6363/clue/paquete-codex-1.json

Fuera del paquete, porque no son producto (.factory, kb/README.md, kb/cambios/20261101-012816-1qf-testseditados.md, kb/requisitos/practicas_c30250c98e6023842.el_estado_avisa_de_los_tests_existentes_que_el_cambio_modifico_o_borro.md, kb/requisitos/practicas_c30250c98e6023842.el_pedido_al_revisor_lleva_los_tests_editados.md, kb/requisitos/practicas_c30250c98e6023842.solo_cuentan_los_archivos_de_pruebas.md, tareas): 7 archivos de registros y evidencia de Factory; no los revises.

Cómo trabajar: leé la spec y el diff; contrastá cada promesa con el código y con las pruebas; buscá casos que fallen, afirmaciones que el
código no cumple y pruebas que no prueban lo que dicen. Si podés, hacé mutaciones a mano sobre copias en tu carpeta y decí cuáles sobreviven.
Mandá la salida larga a archivos de tu carpeta y leé sólo el resumen.

Entregable: un informe JSON en /home/workstation/Dev/factory-tests-editados/.factory/local/revisores/1fd6363-codex-1/informe.json con este formato (schema oracle-clue.review/v1):
- schema_version "oracle-clue.review/v1"; repo, base, head, diff_sha256 y context_sha256 copiados del paquete;
- provider {"name": "codex", "model": "gpt-6-luna"};
- findings: lista de hallazgos, cada uno con id, kind, severity (alta|media|baja|informativa), confidence (0 a 1), title, explanation,
  location {file, start_line, end_line, side: "head"} DENTRO de los rangos del diff del paquete, trigger, evidence, related_requirement,
  status "pendiente" y verification;
- review_status ("completo" o "incompleto") y limitations (qué corriste y qué no).
Sin hallazgos: findings vacía, explicado en limitations. Validalo antes de terminar con:
  oracle-clue validar /home/workstation/Dev/factory-tests-editados/.factory/local/revisores/1fd6363-codex-1/informe.json --paquete /home/workstation/Dev/factory-tests-editados/.factory/cambios/20261101-012816-1qf-testseditados/candidatos/1fd6363/clue/paquete-codex-1.json --repo /home/workstation/Dev/factory-tests-editados/.factory/local/revisiones/1fd6363-codex-1
y terminá con un resumen corto en español.

Indicaciones de quien pide la revisión:
No cambies la configuración de git de ningún repositorio. Revisá el cambio tests-editados: oracle_factory/alarmas.py (detección de los tests existentes que el candidato borró, renombró o a los que les quitó líneas, usando git diff contra la base del candidato), su uso en cli.mostrar, lecturas.datos_estado (clave tests_editados) y flujo_revision.pedir_revision (sección del pedido al revisor), docs/tests.md, tools/verify_tests_editados.py y tests/test_tests_editados.py. Es un aviso que no bloquea. Buscá errores reales: falsos avisos y falsos silencios (qué cuenta como archivo de pruebas, renombres, archivos binarios, rutas con espacios o comillas, diffs enormes, mayúsculas), rutas y argumentos de git peligrosos, que el aviso o la lista cambie el pedido cuando no debe, divergencias entre documento y código, pruebas que pasan por construcción; clasificá por severidad.
