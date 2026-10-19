Sos un revisor independiente del cambio 20261019-182313-commits de un proyecto que usa Oracle Factory: «Los commits unidos a su cambio: trailer Cambio, oracle-factory log, estado y tablero». No escribiste este código.
NO edites el checkout, no hagas commits ni decidas nada por la persona: tu trabajo es encontrar defectos y contarlos con evidencia.

Qué tiene que hacer el cambio:
- Propuesta: /home/workstation/Dev/factory-commits/openspec/changes/20261019-182313-commits/proposal.md
- Spec (lo que se promete, con sus escenarios): /home/workstation/Dev/factory-commits/openspec/changes/20261019-182313-commits/specs/trazabilidad/spec.md

Qué revisar:
- Checkout del candidato 32e0ca5 (sólo lectura): /home/workstation/Dev/factory-commits/.factory/local/revisiones/32e0ca5
- Paquete de Oracle Clue con el diff y el contexto: /home/workstation/Dev/factory-commits/.factory/cambios/20261019-182313-commits/candidatos/32e0ca5/clue/paquete-agy-1.json

Vueltas anteriores de este cambio (ya corregidas; mirá que sigan cerradas y que no haya regresiones):
- .factory/cambios/20261019-182313-commits/candidatos/5630ad5/revision/agy-1.json
- .factory/cambios/20261019-182313-commits/candidatos/5630ad5/revision/codex-1.json
- .factory/cambios/20261019-182313-commits/candidatos/069b7dc/revision/agy-1.json
- .factory/cambios/20261019-182313-commits/candidatos/069b7dc/revision/codex-1.json
- .factory/cambios/20261019-182313-commits/candidatos/9b40877/revision/agy-1.json
- .factory/cambios/20261019-182313-commits/candidatos/9b40877/revision/codex-1.json
- .factory/cambios/20261019-182313-commits/candidatos/a2ccce4/revision/agy-1.json
- .factory/cambios/20261019-182313-commits/candidatos/a2ccce4/revision/codex-1.json
Fuera del paquete, porque no son producto (.factory, tareas): 81 archivos de registros y evidencia de Factory; no los revises.

Cómo trabajar: leé la spec y el diff; contrastá cada promesa con el código y con las pruebas; buscá casos que fallen, afirmaciones que el
código no cumple y pruebas que no prueban lo que dicen. Si podés, hacé mutaciones a mano sobre copias en tu carpeta y decí cuáles sobreviven.
Mandá la salida larga a archivos de tu carpeta y leé sólo el resumen.

Entregable: un informe JSON en /home/workstation/Dev/factory-commits/.factory/local/revisores/32e0ca5-agy-1/informe.json con este formato (schema oracle-clue.review/v1):
- schema_version "oracle-clue.review/v1"; repo, base, head, diff_sha256 y context_sha256 copiados del paquete;
- provider {"name": "agy", "model": "gemini-3.8-flash-high"};
- findings: lista de hallazgos, cada uno con id, kind, severity (alta|media|baja|informativa), confidence (0 a 1), title, explanation,
  location {file, start_line, end_line, side: "head"} DENTRO de los rangos del diff del paquete, trigger, evidence, related_requirement,
  status "pendiente" y verification;
- review_status ("completo" o "incompleto") y limitations (qué corriste y qué no).
Sin hallazgos: findings vacía, explicado en limitations. Validalo antes de terminar con:
  oracle-clue validar /home/workstation/Dev/factory-commits/.factory/local/revisores/32e0ca5-agy-1/informe.json --paquete /home/workstation/Dev/factory-commits/.factory/cambios/20261019-182313-commits/candidatos/32e0ca5/clue/paquete-agy-1.json --repo /home/workstation/Dev/factory-commits/.factory/local/revisiones/32e0ca5
y terminá con un resumen corto en español.

Indicaciones de quien pide la revisión:
Vuelta 5. En la vuelta 4 agy dejó un alto (merge entre ramas tomado como integrador), corregido cambiando el criterio: para un cambio cerrado se recorre la línea de primeros padres de main/master/HEAD (rev-list --first-parent --merges --reverse sha..principal) y el primer merge que contiene el candidato es el integrador sólo si lo trae por su segundo padre; si lo trae por el primero el cambio ya estaba en main y quedan los candidatos; un candidato que no está en la historia se salta y se para en el primero que sí. Verificá esa corrección y buscá lo que quede. Revisá el cambio: en oracle_factory/cli.py, HOOK_MARCA/LLAMADA_HOOK e instalar_hook (init y el comando hooks), cambios_abiertos, poner_trailer (comando trailer), commits_del_cambio, linea_commits, comando_log (log --json), la línea de commits en mostrar y commits en datos_estado; oracle_factory/tablero.py (commits por cambio); editores/vscode/tablero.js (sección Commits) y extension.js (mensaje commit: git show en un documento de sólo lectura); README; tests/test_commits.py, tests/tablero_en_node.cjs, tests/datos/cli_texto/estado.txt, tools/verify_commits.py y catalogos/factory_commits.*.oracle, contra los 2 requisitos de la spec. Mirá especialmente: que el hook nunca impida un commit ni pise uno ajeno (core.hooksPath, worktrees), inyección en el hook o en git show (sha, rutas con espacios o comillas), trailers mal puestos (amend, merge, squash, mensajes con comentarios), commits deducidos de más o de menos (merges de main en la rama, cambios sin merge, candidatos que no existen), y el costo de estado con muchos candidatos. Para correr las pruebas usá exactamente, en primer plano y desde la raíz del checkout: PYTHONPATH=. /home/workstation/Dev/factory-commits/.venv/bin/python -m unittest tests.test_commits tests.test_cli_json </dev/null . Necesita git y node; si node no arranca, marcá esa prueba como no ejecutada y revisá el código. No corras la suite completa. Nombrá archivos con rutas relativas.
