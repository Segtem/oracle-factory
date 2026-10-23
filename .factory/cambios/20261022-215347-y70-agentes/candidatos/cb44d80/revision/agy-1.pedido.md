Sos un revisor independiente del cambio 20261022-215347-y70-agentes de un proyecto que usa Oracle Factory: «La guía para agentes en AGENTS.md: generada desde la CLI, verificada y siempre al día». No escribiste este código.
NO edites el checkout, no hagas commits ni decidas nada por la persona: tu trabajo es encontrar defectos y contarlos con evidencia.

Qué tiene que hacer el cambio:
- Propuesta: /home/workstation/Dev/factory-agentes/openspec/changes/20261022-215347-y70-agentes/proposal.md
- Spec (lo que se promete, con sus escenarios): /home/workstation/Dev/factory-agentes/openspec/changes/20261022-215347-y70-agentes/specs/flujo/spec.md

Qué revisar:
- Checkout del candidato cb44d80 (sólo lectura): /home/workstation/Dev/factory-agentes/.factory/local/revisiones/cb44d80-agy-1
- Paquete de Oracle Clue con el diff y el contexto: /home/workstation/Dev/factory-agentes/.factory/cambios/20261022-215347-y70-agentes/candidatos/cb44d80/clue/paquete-agy-1.json

Fuera del paquete, porque no son producto (.factory, kb/README.md, kb/cambios/20261022-215347-y70-agentes.md, kb/requisitos/flujo_cbbf375bdcabddbc9.la_guia_dice_lo_que_hace_la_cli.md, kb/requisitos/flujo_cbbf375bdcabddbc9.la_guia_para_agentes_se_genera_y_no_se_desactualiza.md, tareas): 6 archivos de registros y evidencia de Factory; no los revises.

Cómo trabajar: leé la spec y el diff; contrastá cada promesa con el código y con las pruebas; buscá casos que fallen, afirmaciones que el
código no cumple y pruebas que no prueban lo que dicen. Si podés, hacé mutaciones a mano sobre copias en tu carpeta y decí cuáles sobreviven.
Mandá la salida larga a archivos de tu carpeta y leé sólo el resumen.

Entregable: un informe JSON en /home/workstation/Dev/factory-agentes/.factory/local/revisores/cb44d80-agy-1/informe.json con este formato (schema oracle-clue.review/v1):
- schema_version "oracle-clue.review/v1"; repo, base, head, diff_sha256 y context_sha256 copiados del paquete;
- provider {"name": "agy", "model": "gemini-3.8-flash-high"};
- findings: lista de hallazgos, cada uno con id, kind, severity (alta|media|baja|informativa), confidence (0 a 1), title, explanation,
  location {file, start_line, end_line, side: "head"} DENTRO de los rangos del diff del paquete, trigger, evidence, related_requirement,
  status "pendiente" y verification;
- review_status ("completo" o "incompleto") y limitations (qué corriste y qué no).
Sin hallazgos: findings vacía, explicado en limitations. Validalo antes de terminar con:
  oracle-clue validar /home/workstation/Dev/factory-agentes/.factory/local/revisores/cb44d80-agy-1/informe.json --paquete /home/workstation/Dev/factory-agentes/.factory/cambios/20261022-215347-y70-agentes/candidatos/cb44d80/clue/paquete-agy-1.json --repo /home/workstation/Dev/factory-agentes/.factory/local/revisiones/cb44d80-agy-1
y terminá con un resumen corto en español.

Indicaciones de quien pide la revisión:
Vuelta 1. Revisá el cambio, contra los 2 requisitos de su spec: oracle_factory/agentes.py (el bloque de la guía, las listas PERSONA, AGENTE y LECTURA, con_bloque, con_claude), comando_agentes, el cambio en exigir_terminal (una decisión de persona nunca la toma un agente) y la llamada desde init en oracle_factory/cli.py, AGENTS.md y CLAUDE.md del repositorio, tests/test_agentes.py, tools/verify_agentes.py, catalogos/factory_agentes.*.oracle y el README. Mirá especialmente: comandos que la guía da como de una persona y que un agente todavía pueda decidir (en cualquier modo), comandos de agente que la guía omita o que no acepten --agente, que la guía diga algo que la CLI no hace, que agentes pise lo que el proyecto escribió en AGENTS.md o CLAUDE.md (marcas repetidas, sin cerrar, enlaces simbólicos), y que exigir_terminal rompa un camino legítimo de agente. Para correr las pruebas usá exactamente, en primer plano y desde la raíz del checkout: PYTHONPATH=. /home/workstation/Dev/factory-agentes/.venv/bin/python -m unittest tests.test_agentes </dev/null . No corras la suite completa. No cambies la configuración de git de ningún repositorio. Nombrá archivos con rutas relativas.
