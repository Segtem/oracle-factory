Sos un revisor independiente del cambio 20261103-113909-oen-contratojson de un proyecto que usa Oracle Factory: «Pruebas de contrato entre la CLI y la extensión de VS Code». No escribiste este código.
NO edites el checkout, no hagas commits ni decidas nada por la persona: tu trabajo es encontrar defectos y contarlos con evidencia.

Qué tiene que hacer el cambio:
- Propuesta: /home/workstation/Dev/factory-contrato-json/openspec/changes/20261103-113909-oen-contratojson/proposal.md
- Spec (lo que se promete, con sus escenarios): /home/workstation/Dev/factory-contrato-json/openspec/changes/20261103-113909-oen-contratojson/specs/ide/spec.md

Qué revisar:
- Checkout del candidato 58363a1 (sólo lectura): /home/workstation/Dev/factory-contrato-json/.factory/local/revisiones/58363a1-agy2-flash-1
- Paquete de Oracle Clue con el diff y el contexto: /home/workstation/Dev/factory-contrato-json/.factory/cambios/20261103-113909-oen-contratojson/candidatos/58363a1/clue/paquete-agy2-flash-1.json

Vueltas anteriores de este cambio (ya corregidas; mirá que sigan cerradas y que no haya regresiones):
- .factory/cambios/20261103-113909-oen-contratojson/candidatos/eea6c47/revision/agy2-flash-1.json
- .factory/cambios/20261103-113909-oen-contratojson/candidatos/eea6c47/revision/codex-1.json
Fuera del paquete, porque no son producto (.factory, kb/README.md, kb/cambios/20261103-113909-oen-contratojson.md, kb/requisitos/ide_cc0ded3b7b46b23f7.el_documento_explica_como_actualizar_el_contrato.md, kb/requisitos/ide_cc0ded3b7b46b23f7.la_cli_entrega_cada_clave_declarada_con_un_tipo_permitido.md, kb/requisitos/ide_cc0ded3b7b46b23f7.la_extension_solo_lee_de_los_json_de_la_cli_lo_que_el_contrato_declara.md, tareas): 15 archivos de registros y evidencia de Factory; no los revises.

Cómo trabajar: leé la spec y el diff; contrastá cada promesa con el código y con las pruebas; buscá casos que fallen, afirmaciones que el
código no cumple y pruebas que no prueban lo que dicen. Si podés, hacé mutaciones a mano sobre copias en tu carpeta y decí cuáles sobreviven.
Mandá la salida larga a archivos de tu carpeta y leé sólo el resumen.

Entregable: un informe JSON en /home/workstation/Dev/factory-contrato-json/.factory/local/revisores/58363a1-agy2-flash-1/informe.json con este formato (schema oracle-clue.review/v1):
- schema_version "oracle-clue.review/v1"; repo, base, head, diff_sha256 y context_sha256 copiados del paquete;
- provider {"name": "agy", "model": "gemini-3.8-flash-high"};
- findings: lista de hallazgos, cada uno con id, kind, severity (alta|media|baja|informativa), confidence (0 a 1), title, explanation,
  location {file, start_line, end_line, side: "head"} DENTRO de los rangos del diff del paquete, trigger, evidence, related_requirement,
  status "pendiente" y verification;
- review_status ("completo" o "incompleto") y limitations (qué corriste y qué no).
Sin hallazgos: findings vacía, explicado en limitations. Validalo antes de terminar con:
  oracle-clue validar /home/workstation/Dev/factory-contrato-json/.factory/local/revisores/58363a1-agy2-flash-1/informe.json --paquete /home/workstation/Dev/factory-contrato-json/.factory/cambios/20261103-113909-oen-contratojson/candidatos/58363a1/clue/paquete-agy2-flash-1.json --repo /home/workstation/Dev/factory-contrato-json/.factory/local/revisiones/58363a1-agy2-flash-1
y terminá con un resumen corto en español.

Indicaciones de quien pide la revisión:
No cambies la configuración de git de ningún repositorio. Es la segunda ronda de contrato-json. La primera trajo 14 hallazgos, casi todos de cobertura del contrato: el primer contrato salió sólo de lo que los estados de prueba hacían leer, y faltaban ramas (propuestas de medidas, hallazgos de revisores, candidato vigente, proyecto con cerrados). Ahora hay dos instantáneas con muchos más estados (cerrado con revisión, abierto con candidato y hallazgos de codex y agy, con propuesta de un agente, sin avanzar, con responsable y mensajes, abandonado), el contrato tiene tipos tomados del código de la CLI con una «nota» donde son más anchos de lo observado, hay una revisión estática del texto de modelo.js y tablero.js (nombres con punto que no son del contrato ni de NOMBRES_PROPIOS), el registrador intercepta `in` y lee varias instantáneas, y `esperando` y `sesion` se tratan como cosas de la extensión. Verificá que los arreglos cubren la CLASE y que los tipos del contrato son correctos mirando oracle_factory/ (tablero.py, lecturas.py, cli.py); buscá errores reales y de impacto práctico en editores/vscode/contrato.json, tools/contrato_vscode.py, tests/contrato_en_node.cjs, tests/test_contrato_vscode.py y docs/tablero.md. Marcá los exóticos. Clasificá por severidad.
