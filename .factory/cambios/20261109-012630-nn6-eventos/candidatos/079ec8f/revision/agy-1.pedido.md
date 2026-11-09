Sos un revisor independiente del cambio 20261109-012630-nn6-eventos de un proyecto que usa Oracle Factory: «El registro tolera eventos que no son objetos». No escribiste este código.
NO edites el checkout, no hagas commits ni decidas nada por la persona: tu trabajo es encontrar defectos y contarlos con evidencia.

Qué tiene que hacer el cambio:
- Propuesta: /home/workstation/Dev/factory-eventos-raros/openspec/changes/20261109-012630-nn6-eventos/proposal.md
- Spec (lo que se promete, con sus escenarios): /home/workstation/Dev/factory-eventos-raros/openspec/changes/20261109-012630-nn6-eventos/specs/flujo/spec.md

Qué revisar:
- Checkout del candidato 079ec8f (sólo lectura): /home/workstation/Dev/factory-eventos-raros/.factory/local/revisiones/079ec8f-agy-1
- Paquete de Oracle Clue con el diff y el contexto: /home/workstation/Dev/factory-eventos-raros/.factory/cambios/20261109-012630-nn6-eventos/candidatos/079ec8f/clue/paquete-agy-1.json

Fuera del paquete, porque no son producto (.factory, kb/README.md, kb/cambios/20261109-012630-nn6-eventos.md, kb/requisitos/flujo_cf9d3b25ba991cfbd.leer_ignora_los_eventos_que_no_son_objetos.md, kb/requisitos/flujo_cf9d3b25ba991cfbd.los_comandos_de_lectura_siguen_funcionando_con_eventos_raros.md, tareas): 6 archivos de registros y evidencia de Factory; no los revises.

Cómo trabajar: leé la spec y el diff; contrastá cada promesa con el código y con las pruebas; buscá casos que fallen, afirmaciones que el
código no cumple y pruebas que no prueban lo que dicen. Si podés, hacé mutaciones a mano sobre copias en tu carpeta y decí cuáles sobreviven.
Mandá la salida larga a archivos de tu carpeta y leé sólo el resumen.

Entregable: un informe JSON en /home/workstation/Dev/factory-eventos-raros/.factory/local/revisores/079ec8f-agy-1/informe.json con este formato (schema oracle-clue.review/v1):
- schema_version "oracle-clue.review/v1"; repo, base, head, diff_sha256 y context_sha256 copiados del paquete;
- provider {"name": "agy", "model": "gemini-3.8-flash-high"};
- findings: lista de hallazgos, cada uno con id, kind, severity (alta|media|baja|informativa), confidence (0 a 1), title, explanation,
  location {file, start_line, end_line, side: "head"} DENTRO de los rangos del diff del paquete, trigger, evidence, related_requirement,
  status "pendiente" y verification;
- review_status ("completo" o "incompleto") y limitations (qué corriste y qué no).
Si el paquete omite un archivo porque no es texto (una imagen, por ejemplo), abrilo vos en el checkout y declaralo con una línea de
limitations por archivo, exactamente `abierto: RUTA` (la ruta tal como figura en el paquete). Clue te obliga a marcar review_status
"incompleto" por esa omisión; Factory la acepta sólo si cada binario omitido está declarado así. No declares uno que no abriste.
Sin hallazgos: findings vacía, explicado en limitations. Validalo antes de terminar con:
  oracle-clue validar /home/workstation/Dev/factory-eventos-raros/.factory/local/revisores/079ec8f-agy-1/informe.json --paquete /home/workstation/Dev/factory-eventos-raros/.factory/cambios/20261109-012630-nn6-eventos/candidatos/079ec8f/clue/paquete-agy-1.json --repo /home/workstation/Dev/factory-eventos-raros/.factory/local/revisiones/079ec8f-agy-1
y terminá con un resumen corto en español.
