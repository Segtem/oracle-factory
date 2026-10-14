Sos un revisor independiente del cambio 20261014-204205-donde-no-valido de un proyecto que usa Oracle Factory: «donde --json etiqueta no_valido una entrada inválida del registro». No escribiste este código.
NO edites el checkout, no hagas commits ni decidas nada por la persona: tu trabajo es encontrar defectos y contarlos con evidencia.

Qué tiene que hacer el cambio:
- Propuesta: /home/workstation/Dev/factory-donde-no-valido/openspec/changes/20261014-204205-donde-no-valido/proposal.md
- Spec (lo que se promete, con sus escenarios): /home/workstation/Dev/factory-donde-no-valido/openspec/changes/20261014-204205-donde-no-valido/specs/cli/spec.md

Qué revisar:
- Checkout del candidato 97e0a37 (sólo lectura): /home/workstation/Dev/factory-donde-no-valido/.factory/local/revisiones/97e0a37
- Paquete de Oracle Clue con el diff y el contexto: /home/workstation/Dev/factory-donde-no-valido/.factory/cambios/20261014-204205-donde-no-valido/candidatos/97e0a37/clue/paquete-codex-1.json

Vueltas anteriores de este cambio (ya corregidas; mirá que sigan cerradas y que no haya regresiones):
- .factory/cambios/20261014-204205-donde-no-valido/candidatos/77ed726/revision/agy-1.json
- .factory/cambios/20261014-204205-donde-no-valido/candidatos/77ed726/revision/codex-1.json
Fuera del paquete, porque no son producto (.factory, tareas): 10 archivos de registros y evidencia de Factory; no los revises.

Cómo trabajar: leé la spec y el diff; contrastá cada promesa con el código y con las pruebas; buscá casos que fallen, afirmaciones que el
código no cumple y pruebas que no prueban lo que dicen. Si podés, hacé mutaciones a mano sobre copias en tu carpeta y decí cuáles sobreviven.
Mandá la salida larga a archivos de tu carpeta y leé sólo el resumen.

Entregable: un informe JSON en /home/workstation/Dev/factory-donde-no-valido/.factory/local/revisores/97e0a37-codex-1/informe.json con este formato (schema oracle-clue.review/v1):
- schema_version "oracle-clue.review/v1"; repo, base, head, diff_sha256 y context_sha256 copiados del paquete;
- provider {"name": "codex", "model": "gpt-6-luna"};
- findings: lista de hallazgos, cada uno con id, kind, severity (alta|media|baja|informativa), confidence (0 a 1), title, explanation,
  location {file, start_line, end_line, side: "head"} DENTRO de los rangos del diff del paquete, trigger, evidence, related_requirement,
  status "pendiente" y verification;
- review_status ("completo" o "incompleto") y limitations (qué corriste y qué no).
Sin hallazgos: findings vacía, explicado en limitations. Validalo antes de terminar con:
  oracle-clue validar /home/workstation/Dev/factory-donde-no-valido/.factory/local/revisores/97e0a37-codex-1/informe.json --paquete /home/workstation/Dev/factory-donde-no-valido/.factory/cambios/20261014-204205-donde-no-valido/candidatos/97e0a37/clue/paquete-codex-1.json --repo /home/workstation/Dev/factory-donde-no-valido/.factory/local/revisiones/97e0a37
y terminá con un resumen corto en español.

Indicaciones de quien pide la revisión:
Vuelta 2. En la 1, codex y agy marcaron el mismo medio (DONDE-NOVALIDO-TEST-001: con una entrada inválida, la prueba no exigía que se sigan listando todos los demás artefactos); corregido comparando con el listado de antes de romper el registro. Este cambio reescribe (MODIFIED) el requisito «donde y resumen se leen como JSON» de openspec/specs/cli/spec.md: define historico y no_valido y suma el escenario «donde con una entrada inválida», sin cambiar el producto. Revisá la spec del cambio contra el código (oracle_factory/cli.py: datos_donde; oracle_factory/estructura.py: donde), si los tres casos cj2 de tests/test_cli_json.py prueban de verdad cada escenario, y tools/verify_donde_no_valido.py con los catálogos factory_no_valido. También cambió cómo cuentan sus casos tools/verify_cli_json.py y tools/verify_donde_ausente.py (sólo los suyos, para que un caso nuevo de otro cambio no los deje incompletos): mirá que sigan detectando un caso que falta o se repite. Para correr las pruebas usá exactamente, en primer plano: cd /home/workstation/Dev/factory-donde-no-valido && /home/workstation/Dev/factory-donde-no-valido/.venv/bin/python -m unittest tests.test_cli_json tests.test_estructura </dev/null . No corras tools/verify_*.py ni la suite completa. Nombrá archivos con rutas relativas.
