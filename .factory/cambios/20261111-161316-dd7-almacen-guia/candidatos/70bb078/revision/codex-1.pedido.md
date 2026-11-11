Sos un revisor independiente del cambio 20261111-161316-dd7-almacen-guia de un proyecto que usa Oracle Factory: «Registros fuera del repo del producto, etapa 5a: la guía de agentes y la skill van al producto sin versionar». No escribiste este código.
NO edites el checkout, no hagas commits ni decidas nada por la persona: tu trabajo es encontrar defectos y contarlos con evidencia.

Qué tiene que hacer el cambio:
- Propuesta: /home/workstation/Dev/factory-almacen-guia/openspec/changes/20261111-161316-dd7-almacen-guia/proposal.md
- Spec (lo que se promete, con sus escenarios): /home/workstation/Dev/factory-almacen-guia/openspec/changes/20261111-161316-dd7-almacen-guia/specs/flujo/spec.md

Qué revisar:
- Checkout del candidato 70bb078 (sólo lectura): /home/workstation/Dev/factory-almacen-guia/.factory/local/revisiones/70bb078-codex-1
- Paquete de Oracle Clue con el diff y el contexto: /home/workstation/Dev/factory-almacen-guia/.factory/cambios/20261111-161316-dd7-almacen-guia/candidatos/70bb078/clue/paquete-codex-1.json

Fuera del paquete, porque no son producto (.factory, kb/README.md, kb/cambios/20261111-161316-dd7-almacen-guia.md, kb/requisitos/flujo_cb87b2b390ceaef68.con_almacen_la_guia_no_pisa_lo_que_el_producto_versiona_y_dice_del_almacen.md, kb/requisitos/flujo_cb87b2b390ceaef68.con_almacen_la_guia_y_la_skill_van_al_producto_sin_versionar.md, tareas): 6 archivos de registros y evidencia de Factory; no los revises.

Cómo trabajar: leé la spec y el diff; contrastá cada promesa con el código y con las pruebas; buscá casos que fallen, afirmaciones que el
código no cumple y pruebas que no prueban lo que dicen. Si podés, hacé mutaciones a mano sobre copias en tu carpeta y decí cuáles sobreviven.
Mandá la salida larga a archivos de tu carpeta y leé sólo el resumen.

Entregable: un informe JSON en /home/workstation/Dev/factory-almacen-guia/.factory/local/revisores/70bb078-codex-1/informe.json con este formato (schema oracle-clue.review/v1):
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
  oracle-clue validar /home/workstation/Dev/factory-almacen-guia/.factory/local/revisores/70bb078-codex-1/informe.json --paquete /home/workstation/Dev/factory-almacen-guia/.factory/cambios/20261111-161316-dd7-almacen-guia/candidatos/70bb078/clue/paquete-codex-1.json --repo /home/workstation/Dev/factory-almacen-guia/.factory/local/revisiones/70bb078-codex-1
y terminá con un resumen corto en español.

Indicaciones de quien pide la revisión:
Revisá almacen-guia: etapa 5a de «registros fuera del repo del producto». Con almacén aparte (cli.PRODUCTO), comando_agentes y comando_skill (--instalar) delegan en almacenes.guia_en_producto / skill_en_producto: escriben AGENTS.md (bloque de agentes.bloque con con_almacen=True: una sección que dice que los registros viven en un almacén aparte y que se comparten con sincronizar), CLAUDE.md y .claude/skills/oracle-factory/SKILL.md en el PRODUCTO, y _excluir los agrega a info/exclude del directorio común de Git del producto (git rev-parse --git-common-dir), salvo lo que git check-ignore ya ignora, con un encabezado una sola vez; nunca .gitignore ni configuración de Git. Si el producto ya versiona alguno, se niega (también con --forzar). No sigue enlaces simbólicos. proyecto.inicializar ya no escribe la guía cuando prepara un almacén (conectar no toca el producto) y avisa que hay que correr agentes. Sin almacén nada cambia. Spec: openspec/changes/20261111-161316-dd7-almacen-guia/specs/flujo/spec.md. Buscá: escrituras en el producto o su .git fuera de esos archivos y de info/exclude, un worktree que excluya en el lugar equivocado, rutas con caracteres especiales en exclude (patrones de gitignore: *, ?, [, !, espacios finales), la verificación que mire el lugar equivocado, regresiones sin almacén (init, agentes, skill) y huecos de prueba en tests/test_almacen_guia.py. Camino completo; sos el único revisor (agy sin cuota).
