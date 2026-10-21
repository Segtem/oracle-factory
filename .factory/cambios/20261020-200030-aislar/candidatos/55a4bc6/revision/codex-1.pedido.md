Sos un revisor independiente del cambio 20261020-200030-aislar de un proyecto que usa Oracle Factory: «El checkout de un revisor no toca el repositorio: un clon aparte en vez de un worktree». No escribiste este código.
NO edites el checkout, no hagas commits ni decidas nada por la persona: tu trabajo es encontrar defectos y contarlos con evidencia.

Qué tiene que hacer el cambio:
- Propuesta: /home/workstation/Dev/factory-aislar/openspec/changes/20261020-200030-aislar/proposal.md
- Spec (lo que se promete, con sus escenarios): /home/workstation/Dev/factory-aislar/openspec/changes/20261020-200030-aislar/specs/revisores/spec.md

Qué revisar:
- Checkout del candidato 55a4bc6 (sólo lectura): /home/workstation/Dev/factory-aislar/.factory/local/revisiones/55a4bc6-codex-1
- Paquete de Oracle Clue con el diff y el contexto: /home/workstation/Dev/factory-aislar/.factory/cambios/20261020-200030-aislar/candidatos/55a4bc6/clue/paquete-codex-1.json

Vueltas anteriores de este cambio (ya corregidas; mirá que sigan cerradas y que no haya regresiones):
- .factory/cambios/20261020-200030-aislar/candidatos/dd13a13/revision/agy-1.json
- .factory/cambios/20261020-200030-aislar/candidatos/dd13a13/revision/codex-1.json
Fuera del paquete, porque no son producto (.factory, tareas): 10 archivos de registros y evidencia de Factory; no los revises.

Cómo trabajar: leé la spec y el diff; contrastá cada promesa con el código y con las pruebas; buscá casos que fallen, afirmaciones que el
código no cumple y pruebas que no prueban lo que dicen. Si podés, hacé mutaciones a mano sobre copias en tu carpeta y decí cuáles sobreviven.
Mandá la salida larga a archivos de tu carpeta y leé sólo el resumen.

Entregable: un informe JSON en /home/workstation/Dev/factory-aislar/.factory/local/revisores/55a4bc6-codex-1/informe.json con este formato (schema oracle-clue.review/v1):
- schema_version "oracle-clue.review/v1"; repo, base, head, diff_sha256 y context_sha256 copiados del paquete;
- provider {"name": "codex", "model": "gpt-6-luna"};
- findings: lista de hallazgos, cada uno con id, kind, severity (alta|media|baja|informativa), confidence (0 a 1), title, explanation,
  location {file, start_line, end_line, side: "head"} DENTRO de los rangos del diff del paquete, trigger, evidence, related_requirement,
  status "pendiente" y verification;
- review_status ("completo" o "incompleto") y limitations (qué corriste y qué no).
Sin hallazgos: findings vacía, explicado en limitations. Validalo antes de terminar con:
  oracle-clue validar /home/workstation/Dev/factory-aislar/.factory/local/revisores/55a4bc6-codex-1/informe.json --paquete /home/workstation/Dev/factory-aislar/.factory/cambios/20261020-200030-aislar/candidatos/55a4bc6/clue/paquete-codex-1.json --repo /home/workstation/Dev/factory-aislar/.factory/local/revisiones/55a4bc6-codex-1
y terminá con un resumen corto en español.

Indicaciones de quien pide la revisión:
Vuelta 2. En la vuelta 1 se corrigió: F-001/F-002 (antes de validar con Clue, el checkout vuelve al candidato con git checkout --force --detach; la prueba ya no se ocupa de volver), F-003/F-005/AISLAR-001 (cada pedido tiene su propio clon en .factory/local/revisiones/<sha>-<revisor>-<n>: dos revisores no comparten checkout y un worktree viejo no se reusa; si la ruta ya existe, se niega), F-004 (--base se traduce a SHA en el repositorio antes de llamar a Clue). F-006 (gc y alternates) queda bajo: el clon es efímero y el candidato vive en una rama. Verificá esas correcciones y buscá lo que quede. Revisá el cambio: en oracle_factory/cli.py, pedir_revision arma el checkout de revisión con git clone --shared --no-checkout y git checkout --detach del candidato en lugar de git worktree add; tests/test_aislar.py (un revisor de prueba que juega con git en su checkout), tools/verify_aislar.py y catalogos/factory_aislar.*.oracle, contra el requisito de la spec. Mirá especialmente: que nada de lo que se haga con git en el checkout (config, ramas, commits, hooks, HEAD) llegue al repositorio del proyecto ni a sus worktrees; qué pasa con los objetos compartidos (alternates) si el repositorio hace gc o se borra un worktree; rutas con espacios; checkouts viejos que eran worktrees; y que Clue valide igual. Para correr las pruebas usá exactamente, en primer plano y desde la raíz del checkout: PYTHONPATH=. /home/workstation/Dev/factory-aislar/.venv/bin/python -m unittest tests.test_aislar tests.test_revisores </dev/null . No corras la suite completa. No cambies la configuración de git de ningún repositorio ni crees ramas fuera de tu checkout. Nombrá archivos con rutas relativas.
