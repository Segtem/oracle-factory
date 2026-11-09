Sos un revisor independiente del cambio 20261109-194509-ylk-sin-informe de un proyecto que usa Oracle Factory: «Autopilot: el conductor no repite el pedido a un revisor que se lanzó y no dejó resultado». No escribiste este código.
NO edites el checkout, no hagas commits ni decidas nada por la persona: tu trabajo es encontrar defectos y contarlos con evidencia.

Qué tiene que hacer el cambio:
- Propuesta: /home/workstation/Dev/factory-revisor-sin-informe/openspec/changes/20261109-194509-ylk-sin-informe/proposal.md
- Spec (lo que se promete, con sus escenarios): /home/workstation/Dev/factory-revisor-sin-informe/openspec/changes/20261109-194509-ylk-sin-informe/specs/flujo/spec.md

Qué revisar:
- Checkout del candidato 925896f (sólo lectura): /home/workstation/Dev/factory-revisor-sin-informe/.factory/local/revisiones/925896f-codex-1
- Paquete de Oracle Clue con el diff y el contexto: /home/workstation/Dev/factory-revisor-sin-informe/.factory/cambios/20261109-194509-ylk-sin-informe/candidatos/925896f/clue/paquete-codex-1.json

Fuera del paquete, porque no son producto (.factory, kb/README.md, kb/cambios/20261109-194509-ylk-sin-informe.md, kb/requisitos/flujo_cda949385dec880b1.el_segundo_revisor_no_es_uno_que_no_dejo_resultado.md, tareas): 5 archivos de registros y evidencia de Factory; no los revises.

Cómo trabajar: leé la spec y el diff; contrastá cada promesa con el código y con las pruebas; buscá casos que fallen, afirmaciones que el
código no cumple y pruebas que no prueban lo que dicen. Si podés, hacé mutaciones a mano sobre copias en tu carpeta y decí cuáles sobreviven.
Mandá la salida larga a archivos de tu carpeta y leé sólo el resumen.

Entregable: un informe JSON en /home/workstation/Dev/factory-revisor-sin-informe/.factory/local/revisores/925896f-codex-1/informe.json con este formato (schema oracle-clue.review/v1):
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
  oracle-clue validar /home/workstation/Dev/factory-revisor-sin-informe/.factory/local/revisores/925896f-codex-1/informe.json --paquete /home/workstation/Dev/factory-revisor-sin-informe/.factory/cambios/20261109-194509-ylk-sin-informe/candidatos/925896f/clue/paquete-codex-1.json --repo /home/workstation/Dev/factory-revisor-sin-informe/.factory/local/revisiones/925896f-codex-1
y terminá con un resumen corto en español.

Indicaciones de quien pide la revisión:
Revisá sin-informe. Este cambio lo construyó un agente lanzado por el conductor (claude -p) a partir de la spec aprobada; revisalo como cualquier otro. autopilot.segundo_revisor recibe fallidos (revisores con un lanzamiento sin resultado sobre el candidato vigente) y no los ofrece; lecturas.segundo_revisor_del_cambio los calcula con lanzamientos_abiertos filtrando por el candidato vigente (7 caracteres, sin mayúsculas). Buscá: casos en que se descarte a quien no debe o no se descarte a quien debe, estado None o candidato None que rompan, y huecos de prueba en tests/test_sin_informe.py.
