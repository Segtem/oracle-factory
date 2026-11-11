Sos un revisor independiente del cambio 20261111-161316-dd7-almacen-guia de un proyecto que usa Oracle Factory: «Registros fuera del repo del producto, etapa 5a: la guía de agentes y la skill van al producto sin versionar». No escribiste este código.
NO edites el checkout, no hagas commits ni decidas nada por la persona: tu trabajo es encontrar defectos y contarlos con evidencia.

Qué tiene que hacer el cambio:
- Propuesta: /home/workstation/Dev/factory-almacen-guia/openspec/changes/20261111-161316-dd7-almacen-guia/proposal.md
- Spec (lo que se promete, con sus escenarios): /home/workstation/Dev/factory-almacen-guia/openspec/changes/20261111-161316-dd7-almacen-guia/specs/flujo/spec.md

Qué revisar:
- Checkout del candidato 9e4c901 (sólo lectura): /home/workstation/Dev/factory-almacen-guia/.factory/local/revisiones/9e4c901-codex-1
- Paquete de Oracle Clue con el diff y el contexto: /home/workstation/Dev/factory-almacen-guia/.factory/cambios/20261111-161316-dd7-almacen-guia/candidatos/9e4c901/clue/paquete-codex-1.json

Vueltas anteriores de este cambio (ya corregidas; mirá que sigan cerradas y que no haya regresiones):
- .factory/cambios/20261111-161316-dd7-almacen-guia/candidatos/70bb078/revision/codex-1.json
Fuera del paquete, porque no son producto (.factory, kb/README.md, kb/cambios/20261111-161316-dd7-almacen-guia.md, kb/requisitos/flujo_cb87b2b390ceaef68.con_almacen_la_guia_no_pisa_lo_que_el_producto_versiona_y_dice_del_almacen.md, kb/requisitos/flujo_cb87b2b390ceaef68.con_almacen_la_guia_y_la_skill_van_al_producto_sin_versionar.md, tareas): 12 archivos de registros y evidencia de Factory; no los revises.

Cómo trabajar: leé la spec y el diff; contrastá cada promesa con el código y con las pruebas; buscá casos que fallen, afirmaciones que el
código no cumple y pruebas que no prueban lo que dicen. Si podés, hacé mutaciones a mano sobre copias en tu carpeta y decí cuáles sobreviven.
Mandá la salida larga a archivos de tu carpeta y leé sólo el resumen.

Entregable: un informe JSON en /home/workstation/Dev/factory-almacen-guia/.factory/local/revisores/9e4c901-codex-1/informe.json con este formato (schema oracle-clue.review/v1):
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
  oracle-clue validar /home/workstation/Dev/factory-almacen-guia/.factory/local/revisores/9e4c901-codex-1/informe.json --paquete /home/workstation/Dev/factory-almacen-guia/.factory/cambios/20261111-161316-dd7-almacen-guia/candidatos/9e4c901/clue/paquete-codex-1.json --repo /home/workstation/Dev/factory-almacen-guia/.factory/local/revisiones/9e4c901-codex-1
y terminá con un resumen corto en español.

Indicaciones de quien pide la revisión:
Revisá almacen-guia (ronda 2). Ronda 1: R1 (las rutas con metacaracteres de Git no quedarían excluidas literalmente) NO se reproduce: las rutas que excluye _excluir son tres constantes (AGENTS.md, CLAUDE.md, .claude/skills/oracle-factory/SKILL.md) sin metacaracteres, y el patrón es relativo a la raíz del repo del producto, así que el nombre de su carpeta no entra; lo comprobé con un producto en la carpeta 'prod a[b]*?' (git status limpio) y quedó fijado en tests/test_almacen_guia.py. Propongo descartarlo con ese motivo. Si te sigue pareciendo un problema, dame un caso que reproduzca con las rutas que Factory escribe. Buscá además lo que quede.
