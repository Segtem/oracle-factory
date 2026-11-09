Sos un revisor independiente del cambio 20261109-201722-oja-construir-primero de un proyecto que usa Oracle Factory: «Autopilot: ante medir --listar sin medidas todavía el conductor delega construir primero». No escribiste este código.
NO edites el checkout, no hagas commits ni decidas nada por la persona: tu trabajo es encontrar defectos y contarlos con evidencia.

Qué tiene que hacer el cambio:
- Propuesta: /home/workstation/Dev/factory-construir-primero/openspec/changes/20261109-201722-oja-construir-primero/proposal.md
- Spec (lo que se promete, con sus escenarios): /home/workstation/Dev/factory-construir-primero/openspec/changes/20261109-201722-oja-construir-primero/specs/flujo/spec.md

Qué revisar:
- Checkout del candidato b1a8886 (sólo lectura): /home/workstation/Dev/factory-construir-primero/.factory/local/revisiones/b1a8886-codex-1
- Paquete de Oracle Clue con el diff y el contexto: /home/workstation/Dev/factory-construir-primero/.factory/cambios/20261109-201722-oja-construir-primero/candidatos/b1a8886/clue/paquete-codex-1.json

Vueltas anteriores de este cambio (ya corregidas; mirá que sigan cerradas y que no haya regresiones):
- .factory/cambios/20261109-201722-oja-construir-primero/candidatos/cbe6500/revision/codex-1.json
Fuera del paquete, porque no son producto (.factory, kb/README.md, kb/cambios/20261109-201722-oja-construir-primero.md, kb/requisitos/flujo_c0d820474143ed460.ante_medir_listar_el_conductor_manda_construir_antes_de_elegir_medidas.md, tareas): 11 archivos de registros y evidencia de Factory; no los revises.

Cómo trabajar: leé la spec y el diff; contrastá cada promesa con el código y con las pruebas; buscá casos que fallen, afirmaciones que el
código no cumple y pruebas que no prueban lo que dicen. Si podés, hacé mutaciones a mano sobre copias en tu carpeta y decí cuáles sobreviven.
Mandá la salida larga a archivos de tu carpeta y leé sólo el resumen.

Entregable: un informe JSON en /home/workstation/Dev/factory-construir-primero/.factory/local/revisores/b1a8886-codex-1/informe.json con este formato (schema oracle-clue.review/v1):
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
  oracle-clue validar /home/workstation/Dev/factory-construir-primero/.factory/local/revisores/b1a8886-codex-1/informe.json --paquete /home/workstation/Dev/factory-construir-primero/.factory/cambios/20261109-201722-oja-construir-primero/candidatos/b1a8886/clue/paquete-codex-1.json --repo /home/workstation/Dev/factory-construir-primero/.factory/local/revisiones/b1a8886-codex-1
y terminá con un resumen corto en español.

Indicaciones de quien pide la revisión:
Revisá construir-primero (ronda 2). Ronda 1: CP1-001 (la condición «pruebas ni catálogos» era ambigua) corregido; además corregí un error mío: la instrucción listaba la evidencia del candidato como parte de construir, y en el flujo real la evidencia va DESPUÉS de que una persona confirma las medidas; la spec cambió y Brian la aprobó de nuevo. La instrucción de oracle_factory/autopilot.py ante medir --listar dice ahora: construir lo que falte (pruebas de cada escenario antes que el código y catálogos de medidas) sin correr todavía la evidencia completa; después elegir y proponer las medidas; confirmarlas es de una persona y la evidencia se hace después. Buscá ambigüedad, bucles, algo que sea de una persona, y huecos de prueba en tests/test_construir_primero.py y docs/modos.md.
