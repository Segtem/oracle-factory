Sos un revisor independiente del cambio 20261020-173143-avisos de un proyecto que usa Oracle Factory: «Tres defectos de Factory a la vista: una spec de otra capacidad, requisitos huérfanos al reimportar y un requisito que quedó sin medir». No escribiste este código.
NO edites el checkout, no hagas commits ni decidas nada por la persona: tu trabajo es encontrar defectos y contarlos con evidencia.

Qué tiene que hacer el cambio:
- Propuesta: /home/workstation/Dev/factory-avisos/openspec/changes/20261020-173143-avisos/proposal.md
- Spec (lo que se promete, con sus escenarios): /home/workstation/Dev/factory-avisos/openspec/changes/20261020-173143-avisos/specs/flujo/spec.md

Qué revisar:
- Checkout del candidato 16b7eb9 (sólo lectura): /home/workstation/Dev/factory-avisos/.factory/local/revisiones/16b7eb9-codex-1
- Paquete de Oracle Clue con el diff y el contexto: /home/workstation/Dev/factory-avisos/.factory/cambios/20261020-173143-avisos/candidatos/16b7eb9/clue/paquete-codex-1.json

Fuera del paquete, porque no son producto (.factory, kb/README.md, kb/cambios/20261020-173143-avisos.md, kb/requisitos/flujo_c36d8b0a54786f254.reimportar_no_deja_requisitos_huerfanos.md, kb/requisitos/flujo_c36d8b0a54786f254.un_requisito_que_quedo_sin_medir_se_avisa_a_tiempo.md, kb/requisitos/flujo_c36d8b0a54786f254.una_spec_de_otra_capacidad_no_se_pierde_en_silencio.md, tareas): 8 archivos de registros y evidencia de Factory; no los revises.

Cómo trabajar: leé la spec y el diff; contrastá cada promesa con el código y con las pruebas; buscá casos que fallen, afirmaciones que el
código no cumple y pruebas que no prueban lo que dicen. Si podés, hacé mutaciones a mano sobre copias en tu carpeta y decí cuáles sobreviven.
Mandá la salida larga a archivos de tu carpeta y leé sólo el resumen.

Entregable: un informe JSON en /home/workstation/Dev/factory-avisos/.factory/local/revisores/16b7eb9-codex-1/informe.json con este formato (schema oracle-clue.review/v1):
- schema_version "oracle-clue.review/v1"; repo, base, head, diff_sha256 y context_sha256 copiados del paquete;
- provider {"name": "codex", "model": "gpt-6-luna"};
- findings: lista de hallazgos, cada uno con id, kind, severity (alta|media|baja|informativa), confidence (0 a 1), title, explanation,
  location {file, start_line, end_line, side: "head"} DENTRO de los rangos del diff del paquete, trigger, evidence, related_requirement,
  status "pendiente" y verification;
- review_status ("completo" o "incompleto") y limitations (qué corriste y qué no).
Sin hallazgos: findings vacía, explicado en limitations. Validalo antes de terminar con:
  oracle-clue validar /home/workstation/Dev/factory-avisos/.factory/local/revisores/16b7eb9-codex-1/informe.json --paquete /home/workstation/Dev/factory-avisos/.factory/cambios/20261020-173143-avisos/candidatos/16b7eb9/clue/paquete-codex-1.json --repo /home/workstation/Dev/factory-avisos/.factory/local/revisiones/16b7eb9-codex-1
y terminá con un resumen corto en español.

Indicaciones de quien pide la revisión:
Vuelta 1. Revisá el cambio: en oracle_factory/cli.py, specs_de_otra_capacidad y su uso en aprobar-spec, la limpieza de los requisitos de una importación anterior en importar, sin_medir_con_medidas, aviso_sin_medir (en estado y estado --json) y el mensaje de cobertura de juzgar; tests/test_avisos.py, tools/verify_avisos.py y catalogos/factory_avisos.*.oracle, contra los 3 requisitos de la spec. Mirá especialmente: que importar nunca quite requisitos de otro cambio ni los que la spec nueva trae, que aprobar-spec no registre nada al negarse, rutas raras en specs/, y avisos falsos de sin medir. Para correr las pruebas usá exactamente, en primer plano y desde la raíz del checkout: PYTHONPATH=. /home/workstation/Dev/factory-avisos/.venv/bin/python -m unittest tests.test_avisos </dev/null . No corras la suite completa. No cambies la configuración de git de ningún repositorio. Nombrá archivos con rutas relativas.
