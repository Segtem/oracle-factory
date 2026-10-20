Sos un revisor independiente del cambio 20261019-232444-quien de un proyecto que usa Oracle Factory: «Quién trabaja en qué: tomar un cambio, su persona y sus agentes en estado y en el tablero». No escribiste este código.
NO edites el checkout, no hagas commits ni decidas nada por la persona: tu trabajo es encontrar defectos y contarlos con evidencia.

Qué tiene que hacer el cambio:
- Propuesta: /home/workstation/Dev/factory-quien/openspec/changes/20261019-232444-quien/proposal.md
- Spec (lo que se promete, con sus escenarios): /home/workstation/Dev/factory-quien/openspec/changes/20261019-232444-quien/specs/colaboracion/spec.md

Qué revisar:
- Checkout del candidato b25339a (sólo lectura): /home/workstation/Dev/factory-quien/.factory/local/revisiones/b25339a
- Paquete de Oracle Clue con el diff y el contexto: /home/workstation/Dev/factory-quien/.factory/cambios/20261019-232444-quien/candidatos/b25339a/clue/paquete-codex-1.json

Vueltas anteriores de este cambio (ya corregidas; mirá que sigan cerradas y que no haya regresiones):
- .factory/cambios/20261019-232444-quien/candidatos/1e6459f/revision/agy-1.json
- .factory/cambios/20261019-232444-quien/candidatos/1e6459f/revision/codex-1.json
Fuera del paquete, porque no son producto (.factory, tareas): 10 archivos de registros y evidencia de Factory; no los revises.

Cómo trabajar: leé la spec y el diff; contrastá cada promesa con el código y con las pruebas; buscá casos que fallen, afirmaciones que el
código no cumple y pruebas que no prueban lo que dicen. Si podés, hacé mutaciones a mano sobre copias en tu carpeta y decí cuáles sobreviven.
Mandá la salida larga a archivos de tu carpeta y leé sólo el resumen.

Entregable: un informe JSON en /home/workstation/Dev/factory-quien/.factory/local/revisores/b25339a-codex-1/informe.json con este formato (schema oracle-clue.review/v1):
- schema_version "oracle-clue.review/v1"; repo, base, head, diff_sha256 y context_sha256 copiados del paquete;
- provider {"name": "codex", "model": "gpt-6-luna"};
- findings: lista de hallazgos, cada uno con id, kind, severity (alta|media|baja|informativa), confidence (0 a 1), title, explanation,
  location {file, start_line, end_line, side: "head"} DENTRO de los rangos del diff del paquete, trigger, evidence, related_requirement,
  status "pendiente" y verification;
- review_status ("completo" o "incompleto") y limitations (qué corriste y qué no).
Sin hallazgos: findings vacía, explicado en limitations. Validalo antes de terminar con:
  oracle-clue validar /home/workstation/Dev/factory-quien/.factory/local/revisores/b25339a-codex-1/informe.json --paquete /home/workstation/Dev/factory-quien/.factory/cambios/20261019-232444-quien/candidatos/b25339a/clue/paquete-codex-1.json --repo /home/workstation/Dev/factory-quien/.factory/local/revisiones/b25339a
y terminá con un resumen corto en español.

Indicaciones de quien pide la revisión:
Vuelta 2. En la vuelta 1 se corrigió: qn-01 (un agente no declarado con actividad reciente aparece; el test también pide tablero --json), qn-02/QN-002 (una fecha futura con más de cinco minutos no es reciente; una sin zona se lee en UTC), qn-03 (con dos cambios tomados por quien commitea, sin trailer), qn-04 (la clase Quien comprueba que git no sale del temporal) y qn-05 (hora vacía en el panel). QN-001 no se cambió: un revision_pedida con resultado interrumpido es un pedido que terminó (Ctrl-C), no un revisor en curso; es la regla del cambio higiene (hg1: tras Ctrl-C estado no avisa de un lanzamiento sin resultado), y lanzamientos_abiertos lo dice en su docstring. Verificá esas correcciones y buscá lo que quede. Revisá el cambio: en oracle_factory/cli.py, tomar, soltar, ACTIVIDAD_RECIENTE, quien_del_cambio, linea_quien, lanzamientos_abiertos (y aviso_lanzamientos, que ahora la usa), cambio_del_commit y poner_trailer, la línea de quién en mostrar y quien en datos_estado, y los subcomandos tomar y soltar; oracle_factory/tablero.py (quien por cambio, por_responsable y sin_responsable); editores/vscode/tablero.js (Responsable, agentes y revisores en cada cambio, «Quién está en qué»); README; tests/test_quien.py, tests/test_commits.py (GIT_CEILING_DIRECTORIES y la comprobación del toplevel), tests/datos/cli_texto/estado.txt, tools/verify_quien.py y catalogos/factory_quien.*.oracle, contra los 3 requisitos de la spec. Mirá especialmente: que nadie quede responsable sin ser una persona desde su terminal, que un relevo o soltar no pisen a otra persona, inyección de HTML en el panel por nombres de personas o agentes, la elección del cambio del trailer (IDs en el mensaje, varios abiertos, user.name vacío), fechas raras en la actividad, y que los tests con git no puedan tocar un repositorio que los contenga. Para correr las pruebas usá exactamente, en primer plano y desde la raíz del checkout: PYTHONPATH=. /home/workstation/Dev/factory-quien/.venv/bin/python -m unittest tests.test_quien tests.test_commits </dev/null . Necesita git y node; si node no arranca, marcá esa prueba como no ejecutada y revisá el código. No corras la suite completa. Nombrá archivos con rutas relativas.
