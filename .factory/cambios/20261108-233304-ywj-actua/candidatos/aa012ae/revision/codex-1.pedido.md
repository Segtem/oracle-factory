Sos un revisor independiente del cambio 20261108-233304-ywj-actua de un proyecto que usa Oracle Factory: «Autopilot que actúa: corre lo mecánico, delega lo creativo, con topes y rastro». No escribiste este código.
NO edites el checkout, no hagas commits ni decidas nada por la persona: tu trabajo es encontrar defectos y contarlos con evidencia.

Qué tiene que hacer el cambio:
- Propuesta: /home/workstation/Dev/factory-autopilot-actua/openspec/changes/20261108-233304-ywj-actua/proposal.md
- Spec (lo que se promete, con sus escenarios): /home/workstation/Dev/factory-autopilot-actua/openspec/changes/20261108-233304-ywj-actua/specs/flujo/spec.md

Qué revisar:
- Checkout del candidato aa012ae (sólo lectura): /home/workstation/Dev/factory-autopilot-actua/.factory/local/revisiones/aa012ae-codex-1
- Paquete de Oracle Clue con el diff y el contexto: /home/workstation/Dev/factory-autopilot-actua/.factory/cambios/20261108-233304-ywj-actua/candidatos/aa012ae/clue/paquete-codex-1.json

Vueltas anteriores de este cambio (ya corregidas; mirá que sigan cerradas y que no haya regresiones):
- .factory/cambios/20261108-233304-ywj-actua/candidatos/a690c89/revision/codex-1.json
- .factory/cambios/20261108-233304-ywj-actua/candidatos/d90883c/revision/codex-1.json
Tests existentes que este candidato modificó o borró (la guarda del proyecto: un test que ya existía no se edita para que pase sin dejarlo dicho). Mirá si cada edición está justificada por el cambio y mencionalo en tu informe, aunque la encuentres legítima:
- tests/datos/ayuda-cli.json, modificado: 1 línea(s) quitada(s)
Fuera del paquete, porque no son producto (.factory, kb/README.md, kb/cambios/20261108-233304-ywj-actua.md, kb/requisitos/flujo_cbe1c0ee48f2ba730.autopilot_ejecutar_solo_actua_como_agente_y_nunca_decide_por_una_persona.md, kb/requisitos/flujo_cbe1c0ee48f2ba730.cada_paso_deja_su_porque_en_el_registro.md, kb/requisitos/flujo_cbe1c0ee48f2ba730.el_bucle_observa_decide_actua_y_vuelve_a_observar.md, kb/requisitos/flujo_cbe1c0ee48f2ba730.el_bucle_tiene_topes_y_se_frena_solo.md, tareas): 20 archivos de registros y evidencia de Factory; no los revises.

Cómo trabajar: leé la spec y el diff; contrastá cada promesa con el código y con las pruebas; buscá casos que fallen, afirmaciones que el
código no cumple y pruebas que no prueban lo que dicen. Si podés, hacé mutaciones a mano sobre copias en tu carpeta y decí cuáles sobreviven.
Mandá la salida larga a archivos de tu carpeta y leé sólo el resumen.

Entregable: un informe JSON en /home/workstation/Dev/factory-autopilot-actua/.factory/local/revisores/aa012ae-codex-1/informe.json con este formato (schema oracle-clue.review/v1):
- schema_version "oracle-clue.review/v1"; repo, base, head, diff_sha256 y context_sha256 copiados del paquete;
- provider {"name": "codex", "model": "gpt-6-luna"};
- findings: lista de hallazgos, cada uno con id, kind, severity (alta|media|baja|informativa), confidence (0 a 1), title, explanation,
  location {file, start_line, end_line, side: "head"} DENTRO de los rangos del diff del paquete, trigger, evidence, related_requirement,
  status "pendiente" y verification;
- review_status ("completo" o "incompleto") y limitations (qué corriste y qué no).
Si el paquete omite un archivo porque no es texto (una imagen, por ejemplo), abrilo vos en el checkout y declaralo con una línea de
limitations por archivo, exactamente `abierto: RUTA` (la ruta tal como figura en el paquete). Clue te obliga a marcar review_status
"incompleto" por esa omisión; Factory la acepta sólo si cada binario omitido está declarado así. No declares uno que no abriste.
Sin hallazgos: findings vacía, explicado en limitations. Validalo antes de terminar con:
  oracle-clue validar /home/workstation/Dev/factory-autopilot-actua/.factory/local/revisores/aa012ae-codex-1/informe.json --paquete /home/workstation/Dev/factory-autopilot-actua/.factory/cambios/20261108-233304-ywj-actua/candidatos/aa012ae/clue/paquete-codex-1.json --repo /home/workstation/Dev/factory-autopilot-actua/.factory/local/revisiones/aa012ae-codex-1
y terminá con un resumen corto en español.

Indicaciones de quien pide la revisión:
Ronda 3 del cambio actua, candidato aa012ae. Spec: openspec/changes/20261108-233304-ywj-actua/specs/flujo/spec.md. Rondas anteriores: ACTUA-001 (el plazo de un paso se calculaba antes de dejar el porqué) y ACTUA-002 (_proceso estiraba cualquier plazo a 1 s y el mensaje final tenía 60 s fijos). Ahora: todo proceso toma su plazo del reloj justo antes de correr, _proceso usa el plazo exacto y no arranca con plazo <= 0, el porqué usa min(60, restante) y no se deja si no queda tiempo, y el mensaje final tiene un plazo propio explícito de 10 s (PLAZO_FINAL) FUERA del tope: es una decisión de diseño documentada en docs/modos.md, porque el rastro del motivo de la detención lo exige la spec aunque el tiempo se haya agotado, y dejarlo no es actuar. Si lo ves como un incumplimiento de la spec, decí por qué y qué alternativa cumpliría las dos cosas. Mirá lo que quede de la clase de tiempo/plazos y lo demás: que el bucle nunca corra una decisión de persona, el lanzamiento con --lanzar (un argumento, sin shell, entorno), el porqué antes de actuar, los topes y la falta de progreso, datos ilegibles o frenos, --json y el código de salida. Tests: tests/test_conductor.py (co1–co4, sin métodos nuevos desde la ronda 1). Evidencia: 1326 pruebas OK; 41 mutaciones propias, 39 detectadas y 2 equivalentes declaradas (len(nombre) < 3 y la verificación final del subcomando en argumentos_mecanicos, defensas redundantes con el parser).
