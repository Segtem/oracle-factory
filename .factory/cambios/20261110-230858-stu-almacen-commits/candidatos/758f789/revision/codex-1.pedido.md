Sos un revisor independiente del cambio 20261110-230858-stu-almacen-commits de un proyecto que usa Oracle Factory: «Registros fuera del repo del producto, etapa 4a: Factory commitea en el almacén tras cada comando que escribe registros». No escribiste este código.
NO edites el checkout, no hagas commits ni decidas nada por la persona: tu trabajo es encontrar defectos y contarlos con evidencia.

Qué tiene que hacer el cambio:
- Propuesta: /home/workstation/Dev/factory-almacen-commits/openspec/changes/20261110-230858-stu-almacen-commits/proposal.md
- Spec (lo que se promete, con sus escenarios): /home/workstation/Dev/factory-almacen-commits/openspec/changes/20261110-230858-stu-almacen-commits/specs/flujo/spec.md

Qué revisar:
- Checkout del candidato 758f789 (sólo lectura): /home/workstation/Dev/factory-almacen-commits/.factory/local/revisiones/758f789-codex-1
- Paquete de Oracle Clue con el diff y el contexto: /home/workstation/Dev/factory-almacen-commits/.factory/cambios/20261110-230858-stu-almacen-commits/candidatos/758f789/clue/paquete-codex-1.json

Vueltas anteriores de este cambio (ya corregidas; mirá que sigan cerradas y que no haya regresiones):
- .factory/cambios/20261110-230858-stu-almacen-commits/candidatos/4010151/revision/codex-1.json
- .factory/cambios/20261110-230858-stu-almacen-commits/candidatos/618b9de/revision/codex-1.json
- .factory/cambios/20261110-230858-stu-almacen-commits/candidatos/7dd111d/revision/codex-1.json
- .factory/cambios/20261110-230858-stu-almacen-commits/candidatos/57017da/revision/codex-1.json
Fuera del paquete, porque no son producto (.factory, kb/README.md, kb/cambios/20261110-230858-stu-almacen-commits.md, kb/requisitos/flujo_c3d4de75771af14ec.con_almacen_cada_comando_que_escribe_deja_su_commit.md, kb/requisitos/flujo_c3d4de75771af14ec.el_commit_del_almacen_no_escribe_configuracion_ni_hace_fallar.md, tareas): 34 archivos de registros y evidencia de Factory; no los revises.

Cómo trabajar: leé la spec y el diff; contrastá cada promesa con el código y con las pruebas; buscá casos que fallen, afirmaciones que el
código no cumple y pruebas que no prueban lo que dicen. Si podés, hacé mutaciones a mano sobre copias en tu carpeta y decí cuáles sobreviven.
Mandá la salida larga a archivos de tu carpeta y leé sólo el resumen.

Entregable: un informe JSON en /home/workstation/Dev/factory-almacen-commits/.factory/local/revisores/758f789-codex-1/informe.json con este formato (schema oracle-clue.review/v1):
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
  oracle-clue validar /home/workstation/Dev/factory-almacen-commits/.factory/local/revisores/758f789-codex-1/informe.json --paquete /home/workstation/Dev/factory-almacen-commits/.factory/cambios/20261110-230858-stu-almacen-commits/candidatos/758f789/clue/paquete-codex-1.json --repo /home/workstation/Dev/factory-almacen-commits/.factory/local/revisiones/758f789-codex-1
y terminá con un resumen corto en español.

Indicaciones de quien pide la revisión:
Revisá almacen-commits (ronda 5). Ronda 4: F1 (el bit de ejecución no contaba en la foto) y F2 (una falla de git status al sacar la foto previa desactivaba el commit sin aviso) corregidos: _huella incluye el modo; foto devuelve {FALLA: motivo} si es un repo y git falla, y commitear avisa sin intentar el commit. Antes de reportar un hallazgo nuevo, considerá si es un caso que un comando de Factory pueda producir de verdad o sólo en teoría, y decilo en el hallazgo. Verificá las correcciones y buscá lo que quede, con un caso que reproduzca.
