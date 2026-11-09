Sos un revisor independiente del cambio 20261109-162444-701-segundo-revisor de un proyecto que usa Oracle Factory: «Autopilot: en el camino completo el conductor pide un segundo revisor de otro proveedor». No escribiste este código.
NO edites el checkout, no hagas commits ni decidas nada por la persona: tu trabajo es encontrar defectos y contarlos con evidencia.

Qué tiene que hacer el cambio:
- Propuesta: /home/workstation/Dev/factory-segundo-revisor/openspec/changes/20261109-162444-701-segundo-revisor/proposal.md
- Spec (lo que se promete, con sus escenarios): /home/workstation/Dev/factory-segundo-revisor/openspec/changes/20261109-162444-701-segundo-revisor/specs/flujo/spec.md

Qué revisar:
- Checkout del candidato 5e2f1c8 (sólo lectura): /home/workstation/Dev/factory-segundo-revisor/.factory/local/revisiones/5e2f1c8-codex-1
- Paquete de Oracle Clue con el diff y el contexto: /home/workstation/Dev/factory-segundo-revisor/.factory/cambios/20261109-162444-701-segundo-revisor/candidatos/5e2f1c8/clue/paquete-codex-1.json

Vueltas anteriores de este cambio (ya corregidas; mirá que sigan cerradas y que no haya regresiones):
- .factory/cambios/20261109-162444-701-segundo-revisor/candidatos/bdf566d/revision/codex-1.json
Fuera del paquete, porque no son producto (.factory, kb/README.md, kb/cambios/20261109-162444-701-segundo-revisor.md, kb/requisitos/flujo_c350dc50b9b6cde6a.el_conductor_pide_el_segundo_revisor_antes_de_la_revision.md, kb/requisitos/flujo_c350dc50b9b6cde6a.estado_dice_que_segundo_revisor_falta_en_el_camino_completo.md, tareas): 12 archivos de registros y evidencia de Factory; no los revises.

Cómo trabajar: leé la spec y el diff; contrastá cada promesa con el código y con las pruebas; buscá casos que fallen, afirmaciones que el
código no cumple y pruebas que no prueban lo que dicen. Si podés, hacé mutaciones a mano sobre copias en tu carpeta y decí cuáles sobreviven.
Mandá la salida larga a archivos de tu carpeta y leé sólo el resumen.

Entregable: un informe JSON en /home/workstation/Dev/factory-segundo-revisor/.factory/local/revisores/5e2f1c8-codex-1/informe.json con este formato (schema oracle-clue.review/v1):
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
  oracle-clue validar /home/workstation/Dev/factory-segundo-revisor/.factory/local/revisores/5e2f1c8-codex-1/informe.json --paquete /home/workstation/Dev/factory-segundo-revisor/.factory/cambios/20261109-162444-701-segundo-revisor/candidatos/5e2f1c8/clue/paquete-codex-1.json --repo /home/workstation/Dev/factory-segundo-revisor/.factory/local/revisiones/5e2f1c8-codex-1
y terminá con un resumen corto en español.

Indicaciones de quien pide la revisión:
Revisá segundo-revisor (ronda 2). autopilot.segundo_revisor calcula para un cambio de camino completo el revisor configurado de otro proveedor que falta; lecturas.segundo_revisor_del_cambio lo expone en estado --json y devuelve null si la configuración o algún informe de revision/*.json no se puede leer (hallazgo SR-1 de la ronda 1, corregido); autopilot.decidir, ante el paso revisar, decide actuar con pedir-revision --a ESE antes de delegar la propuesta. El nombre debe empezar con letra o dígito (más estricto que la spec). Buscá casos de comando no debido, bucles, proveedor mal contado y huecos de prueba en tests/test_segundo_revisor.py.
