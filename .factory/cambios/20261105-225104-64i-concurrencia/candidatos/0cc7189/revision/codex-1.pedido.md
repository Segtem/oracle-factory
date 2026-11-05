Sos un revisor independiente del cambio 20261105-225104-64i-concurrencia de un proyecto que usa Oracle Factory: «Web: simulación pixel art de personas y agentes trabajando a la vez». No escribiste este código.
NO edites el checkout, no hagas commits ni decidas nada por la persona: tu trabajo es encontrar defectos y contarlos con evidencia.

Qué tiene que hacer el cambio:
- Propuesta: /home/workstation/Dev/factory-web-concurrencia/openspec/changes/20261105-225104-64i-concurrencia/proposal.md
- Spec (lo que se promete, con sus escenarios): /home/workstation/Dev/factory-web-concurrencia/openspec/changes/20261105-225104-64i-concurrencia/specs/web/spec.md

Qué revisar:
- Checkout del candidato 0cc7189 (sólo lectura): /home/workstation/Dev/factory-web-concurrencia/.factory/local/revisiones/0cc7189-codex-1
- Paquete de Oracle Clue con el diff y el contexto: /home/workstation/Dev/factory-web-concurrencia/.factory/cambios/20261105-225104-64i-concurrencia/candidatos/0cc7189/clue/paquete-codex-1.json

Vueltas anteriores de este cambio (ya corregidas; mirá que sigan cerradas y que no haya regresiones):
- .factory/cambios/20261105-225104-64i-concurrencia/candidatos/c329d53/revision/codex-1.json
Tests existentes que este candidato modificó o borró (la guarda del proyecto: un test que ya existía no se edita para que pase sin dejarlo dicho). Mirá si cada edición está justificada por el cambio y mencionalo en tu informe, aunque la encuentres legítima:
- tests/datos/guias-texto.json, modificado: 1 línea(s) quitada(s)
Fuera del paquete, porque no son producto (.factory, kb/README.md, kb/cambios/20261105-225104-64i-concurrencia.md, kb/requisitos/web_cc8d4b754936380f4.la_escena_se_controla_y_es_accesible.md, kb/requisitos/web_cc8d4b754936380f4.la_simulacion_dice_que_es_una_simulacion.md, kb/requisitos/web_cc8d4b754936380f4.la_simulacion_sigue_las_reglas.md, kb/requisitos/web_cc8d4b754936380f4.los_escenarios_cuentan_la_concurrencia.md, tareas): 14 archivos de registros y evidencia de Factory; no los revises.

Cómo trabajar: leé la spec y el diff; contrastá cada promesa con el código y con las pruebas; buscá casos que fallen, afirmaciones que el
código no cumple y pruebas que no prueban lo que dicen. Si podés, hacé mutaciones a mano sobre copias en tu carpeta y decí cuáles sobreviven.
Mandá la salida larga a archivos de tu carpeta y leé sólo el resumen.

Entregable: un informe JSON en /home/workstation/Dev/factory-web-concurrencia/.factory/local/revisores/0cc7189-codex-1/informe.json con este formato (schema oracle-clue.review/v1):
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
  oracle-clue validar /home/workstation/Dev/factory-web-concurrencia/.factory/local/revisores/0cc7189-codex-1/informe.json --paquete /home/workstation/Dev/factory-web-concurrencia/.factory/cambios/20261105-225104-64i-concurrencia/candidatos/0cc7189/clue/paquete-codex-1.json --repo /home/workstation/Dev/factory-web-concurrencia/.factory/local/revisiones/0cc7189-codex-1
y terminá con un resumen corto en español.

Indicaciones de quien pide la revisión:
Ronda 2. Se corrigieron CC-1 (cerrar exige una revisión vigente; los guiones de mismo-archivo y revision-vieja suman las revisiones que faltaban) y CC-2 (ids de evento por rama y secuencia). Es una simulación de reglas. Mirá que la clase quede cerrada: otras decisiones o acciones que el motor acepta sin cumplir una regla que cita (por ejemplo integrar o tomar por un agente, cerrar tras una unión pendiente, revisión hecha por quien escribió el cambio), estados imposibles, y que ningún escenario cierre con una revisión vieja. Declarado: tests/datos/guias-texto.json se regeneró por una frase nueva con enlace en colaboracion.html; ninguna prueba existente se editó.
