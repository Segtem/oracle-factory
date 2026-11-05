Sos un revisor independiente del cambio 20261104-221348-2l1-binarios de un proyecto que usa Oracle Factory: «Revisión: los archivos binarios del paquete no impiden aprobar». No escribiste este código.
NO edites el checkout, no hagas commits ni decidas nada por la persona: tu trabajo es encontrar defectos y contarlos con evidencia.

Qué tiene que hacer el cambio:
- Propuesta: /home/workstation/Dev/factory-revision-binarios/openspec/changes/20261104-221348-2l1-binarios/proposal.md
- Spec (lo que se promete, con sus escenarios): /home/workstation/Dev/factory-revision-binarios/openspec/changes/20261104-221348-2l1-binarios/specs/revision/spec.md

Qué revisar:
- Checkout del candidato c04cf57 (sólo lectura): /home/workstation/Dev/factory-revision-binarios/.factory/local/revisiones/c04cf57-codex-1
- Paquete de Oracle Clue con el diff y el contexto: /home/workstation/Dev/factory-revision-binarios/.factory/cambios/20261104-221348-2l1-binarios/candidatos/c04cf57/clue/paquete-codex-1.json

Vueltas anteriores de este cambio (ya corregidas; mirá que sigan cerradas y que no haya regresiones):
- .factory/cambios/20261104-221348-2l1-binarios/candidatos/edecf96/revision/agy2-flash-1.json
- .factory/cambios/20261104-221348-2l1-binarios/candidatos/edecf96/revision/codex-1.json
Fuera del paquete, porque no son producto (.factory, kb/README.md, kb/cambios/20261104-221348-2l1-binarios.md, kb/requisitos/revision_cc9d1034ecccab8cb.el_pedido_indica_como_declarar_binarios.md, kb/requisitos/revision_cc9d1034ecccab8cb.lo_no_nombrado_sigue_bloqueando.md, kb/requisitos/revision_cc9d1034ecccab8cb.los_binarios_nombrados_no_bloquean.md, tareas): 15 archivos de registros y evidencia de Factory; no los revises.

Cómo trabajar: leé la spec y el diff; contrastá cada promesa con el código y con las pruebas; buscá casos que fallen, afirmaciones que el
código no cumple y pruebas que no prueban lo que dicen. Si podés, hacé mutaciones a mano sobre copias en tu carpeta y decí cuáles sobreviven.
Mandá la salida larga a archivos de tu carpeta y leé sólo el resumen.

Entregable: un informe JSON en /home/workstation/Dev/factory-revision-binarios/.factory/local/revisores/c04cf57-codex-1/informe.json con este formato (schema oracle-clue.review/v1):
- schema_version "oracle-clue.review/v1"; repo, base, head, diff_sha256 y context_sha256 copiados del paquete;
- provider {"name": "codex", "model": "gpt-6-luna"};
- findings: lista de hallazgos, cada uno con id, kind, severity (alta|media|baja|informativa), confidence (0 a 1), title, explanation,
  location {file, start_line, end_line, side: "head"} DENTRO de los rangos del diff del paquete, trigger, evidence, related_requirement,
  status "pendiente" y verification;
- review_status ("completo" o "incompleto") y limitations (qué corriste y qué no).
Si el paquete omite un archivo porque no es texto (una imagen, por ejemplo), abrilo vos en el checkout y nombrá su ruta relativa a la raíz del repositorio (la del paquete) en una frase de
limitations que diga que lo abriste, sin negaciones; Clue te obliga a marcar review_status "incompleto" por esa omisión, y Factory la acepta sólo si cada binario omitido está nombrado ahí.
Sin hallazgos: findings vacía, explicado en limitations. Validalo antes de terminar con:
  oracle-clue validar /home/workstation/Dev/factory-revision-binarios/.factory/local/revisores/c04cf57-codex-1/informe.json --paquete /home/workstation/Dev/factory-revision-binarios/.factory/cambios/20261104-221348-2l1-binarios/candidatos/c04cf57/clue/paquete-codex-1.json --repo /home/workstation/Dev/factory-revision-binarios/.factory/local/revisiones/c04cf57-codex-1
y terminá con un resumen corto en español.

Indicaciones de quien pide la revisión:
Ronda 2. Se corrigieron REV-BIN-01 a 04 de la ronda 1 (razones de binario de Clue, prefijos de ruta, negaciones por frase, prueba de material_del_candidato). Mirá que la clase quede cerrada: rutas con espacios o Unicode, negaciones que la heurística no ve, regex con caracteres especiales en la ruta.
