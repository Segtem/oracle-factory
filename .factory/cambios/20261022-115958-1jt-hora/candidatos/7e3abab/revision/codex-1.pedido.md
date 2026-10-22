Sos un revisor independiente del cambio 20261022-115958-1jt-hora de un proyecto que usa Oracle Factory: «La hora de cada evento con microsegundos: lo de dos ramas en el mismo segundo queda en orden». No escribiste este código.
NO edites el checkout, no hagas commits ni decidas nada por la persona: tu trabajo es encontrar defectos y contarlos con evidencia.

Qué tiene que hacer el cambio:
- Propuesta: /home/workstation/Dev/factory-hora/openspec/changes/20261022-115958-1jt-hora/proposal.md
- Spec (lo que se promete, con sus escenarios): /home/workstation/Dev/factory-hora/openspec/changes/20261022-115958-1jt-hora/specs/colaboracion/spec.md

Qué revisar:
- Checkout del candidato 7e3abab (sólo lectura): /home/workstation/Dev/factory-hora/.factory/local/revisiones/7e3abab-codex-1
- Paquete de Oracle Clue con el diff y el contexto: /home/workstation/Dev/factory-hora/.factory/cambios/20261022-115958-1jt-hora/candidatos/7e3abab/clue/paquete-codex-1.json

Vueltas anteriores de este cambio (ya corregidas; mirá que sigan cerradas y que no haya regresiones):
- .factory/cambios/20261022-115958-1jt-hora/candidatos/6489a62/revision/agy-1.json
- .factory/cambios/20261022-115958-1jt-hora/candidatos/6489a62/revision/codex-1.json
Fuera del paquete, porque no son producto (.factory, kb/README.md, kb/cambios/20261022-115958-1jt-hora.md, kb/requisitos/colaboracion_cac5d9b2dbb283ed3.al_unir_dos_ramas_lo_del_mismo_segundo_queda_en_el_orden_en_que_se_escribio.md, kb/requisitos/colaboracion_cac5d9b2dbb283ed3.la_hora_de_un_evento_distingue_lo_escrito_en_el_mismo_segundo.md, tareas): 14 archivos de registros y evidencia de Factory; no los revises.

Cómo trabajar: leé la spec y el diff; contrastá cada promesa con el código y con las pruebas; buscá casos que fallen, afirmaciones que el
código no cumple y pruebas que no prueban lo que dicen. Si podés, hacé mutaciones a mano sobre copias en tu carpeta y decí cuáles sobreviven.
Mandá la salida larga a archivos de tu carpeta y leé sólo el resumen.

Entregable: un informe JSON en /home/workstation/Dev/factory-hora/.factory/local/revisores/7e3abab-codex-1/informe.json con este formato (schema oracle-clue.review/v1):
- schema_version "oracle-clue.review/v1"; repo, base, head, diff_sha256 y context_sha256 copiados del paquete;
- provider {"name": "codex", "model": "gpt-6-luna"};
- findings: lista de hallazgos, cada uno con id, kind, severity (alta|media|baja|informativa), confidence (0 a 1), title, explanation,
  location {file, start_line, end_line, side: "head"} DENTRO de los rangos del diff del paquete, trigger, evidence, related_requirement,
  status "pendiente" y verification;
- review_status ("completo" o "incompleto") y limitations (qué corriste y qué no).
Sin hallazgos: findings vacía, explicado en limitations. Validalo antes de terminar con:
  oracle-clue validar /home/workstation/Dev/factory-hora/.factory/local/revisores/7e3abab-codex-1/informe.json --paquete /home/workstation/Dev/factory-hora/.factory/cambios/20261022-115958-1jt-hora/candidatos/7e3abab/clue/paquete-codex-1.json --repo /home/workstation/Dev/factory-hora/.factory/local/revisiones/7e3abab-codex-1
y terminá con un resumen corto en español.

Indicaciones de quien pide la revisión:
Vuelta 2: se corrigieron los de la vuelta 1: unir.hora ordena por la hora parseada (segundos o microsegundos, Z o +00:00; lo viejo cuenta desde el principio de su segundo) en vez de por el texto (HORA-004); ho2 mezcla una rama vieja y una nueva en el mismo segundo (HORA-001 de agy); a4 exige el orden exacto en que se escribieron en modo ordenado e informa los pares de las dos ramas del mismo segundo, y ho2 repite hasta tener uno (HORA-002, HORA-001 de codex); ho1 espera a que los dos mensajes caigan en el mismo segundo y muestra estado en texto con un registro viejo (HORA-003). Revisá el cambio, contra los 2 requisitos de su spec: ahora() en oracle_factory/cli.py (la hora con microsegundos), cómo se comparan y ordenan las horas en el resto del código (unir.py, kb.py, resumen.py, tablero.py, la extensión de VS Code), tools/banco.py (a4 sin esperar entre días), tests/test_hora.py, tools/verify_hora.py, catalogos/factory_hora.*.oracle y docs/colaboracion.md. Mirá especialmente: comparaciones de horas como texto que fallen al mezclar horas en segundos y con microsegundos, horas que se muestren o se corten mal, eventos iguales que antes se deduplicaban y ahora no, y si las pruebas prueban lo que prometen los requisitos. Para correr las pruebas usá exactamente, en primer plano y desde la raíz del checkout: PYTHONPATH=. /home/workstation/Dev/factory-hora/.venv/bin/python -m unittest tests.test_hora </dev/null . No corras la suite completa. No cambies la configuración de git de ningún repositorio. Nombrá archivos con rutas relativas.
