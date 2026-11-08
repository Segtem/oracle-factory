Sos un revisor independiente del cambio 20261108-220606-51z-autopilot de un proyecto que usa Oracle Factory: «Conductor autopilot: decide el siguiente paso por reglas (sin actuar)». No escribiste este código.
NO edites el checkout, no hagas commits ni decidas nada por la persona: tu trabajo es encontrar defectos y contarlos con evidencia.

Qué tiene que hacer el cambio:
- Propuesta: /home/workstation/Dev/factory-autopilot/openspec/changes/20261108-220606-51z-autopilot/proposal.md
- Spec (lo que se promete, con sus escenarios): /home/workstation/Dev/factory-autopilot/openspec/changes/20261108-220606-51z-autopilot/specs/flujo/spec.md

Qué revisar:
- Checkout del candidato bbd6b80 (sólo lectura): /home/workstation/Dev/factory-autopilot/.factory/local/revisiones/bbd6b80-codex-1
- Paquete de Oracle Clue con el diff y el contexto: /home/workstation/Dev/factory-autopilot/.factory/cambios/20261108-220606-51z-autopilot/candidatos/bbd6b80/clue/paquete-codex-1.json

Vueltas anteriores de este cambio (ya corregidas; mirá que sigan cerradas y que no haya regresiones):
- .factory/cambios/20261108-220606-51z-autopilot/candidatos/92fc31a/revision/codex-1.json
Tests existentes que este candidato modificó o borró (la guarda del proyecto: un test que ya existía no se edita para que pase sin dejarlo dicho). Mirá si cada edición está justificada por el cambio y mencionalo en tu informe, aunque la encuentres legítima:
- tests/datos/ayuda-cli.json, modificado: 1 línea(s) quitada(s)
Fuera del paquete, porque no son producto (.factory, kb/README.md, kb/cambios/20261108-220606-51z-autopilot.md, kb/requisitos/flujo_cc3cbaf2da9e917bd.autopilot_solo_lee_y_lo_muestra.md, kb/requisitos/flujo_cc3cbaf2da9e917bd.el_conductor_decide_el_siguiente_paso_por_reglas.md, kb/requisitos/flujo_cc3cbaf2da9e917bd.el_conductor_frena_ante_un_freno_o_un_paso_que_no_conoce.md, tareas): 17 archivos de registros y evidencia de Factory; no los revises.

Cómo trabajar: leé la spec y el diff; contrastá cada promesa con el código y con las pruebas; buscá casos que fallen, afirmaciones que el
código no cumple y pruebas que no prueban lo que dicen. Si podés, hacé mutaciones a mano sobre copias en tu carpeta y decí cuáles sobreviven.
Mandá la salida larga a archivos de tu carpeta y leé sólo el resumen.

Entregable: un informe JSON en /home/workstation/Dev/factory-autopilot/.factory/local/revisores/bbd6b80-codex-1/informe.json con este formato (schema oracle-clue.review/v1):
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
  oracle-clue validar /home/workstation/Dev/factory-autopilot/.factory/local/revisores/bbd6b80-codex-1/informe.json --paquete /home/workstation/Dev/factory-autopilot/.factory/cambios/20261108-220606-51z-autopilot/candidatos/bbd6b80/clue/paquete-codex-1.json --repo /home/workstation/Dev/factory-autopilot/.factory/local/revisiones/bbd6b80-codex-1
y terminá con un resumen corto en español.

Indicaciones de quien pide la revisión:
Ronda 2 del cambio autopilot, candidato bbd6b80. Spec: openspec/changes/20261108-220606-51z-autopilot/specs/flujo/spec.md. En la ronda 1 (candidato 92fc31a) hubo un hallazgo medio AP-1: decidir() leía tokens[1] como subcomando y no reconocía el prefijo global --agente (ni --proyecto, ni la forma con «=», ni abreviaturas). Lo corregí en la clase entera: ahora decidir() clasifica con el parser real de Factory (autopilot._analizar usa construir_parser().parse_args) y un comando que el parser rechaza frena. Mirá especialmente: (1) efectos secundarios de usar argparse dentro de decidir (SystemExit, salida a stdout/stderr, variables de entorno como FACTORY_AGENTE, que --version o -h no cuelguen ni impriman); (2) que ninguna decisión de persona pueda salir como actuar o delegar por ninguna forma de escribir el comando (con prefijos, abreviaturas de subcomando, mayúsculas, --agente=..., opciones repetidas, un valor de --agente que se parezca a un subcomando); (3) que frenar nunca traiga comando ni instrucción; (4) que los frenos y los datos ilegibles frenen. Tests: tests/test_autopilot.py (ap1–ap3, sin métodos nuevos desde la ronda 1). Evidencia: 1310 pruebas OK; 28 mutaciones propias detectadas salvo la equivalente declarada (len(tokens) < 3 → < 2).
