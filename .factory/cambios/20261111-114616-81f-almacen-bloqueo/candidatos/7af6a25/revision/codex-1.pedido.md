Sos un revisor independiente del cambio 20261111-114616-81f-almacen-bloqueo de un proyecto que usa Oracle Factory: «Registros fuera del repo del producto, etapa 4b1: cada comando commitea sólo lo de su cambio, con un bloqueo corto». No escribiste este código.
NO edites el checkout, no hagas commits ni decidas nada por la persona: tu trabajo es encontrar defectos y contarlos con evidencia.

Qué tiene que hacer el cambio:
- Propuesta: /home/workstation/Dev/factory-almacen-bloqueo/openspec/changes/20261111-114616-81f-almacen-bloqueo/proposal.md
- Spec (lo que se promete, con sus escenarios): /home/workstation/Dev/factory-almacen-bloqueo/openspec/changes/20261111-114616-81f-almacen-bloqueo/specs/flujo/spec.md

Qué revisar:
- Checkout del candidato 7af6a25 (sólo lectura): /home/workstation/Dev/factory-almacen-bloqueo/.factory/local/revisiones/7af6a25-codex-1
- Paquete de Oracle Clue con el diff y el contexto: /home/workstation/Dev/factory-almacen-bloqueo/.factory/cambios/20261111-114616-81f-almacen-bloqueo/candidatos/7af6a25/clue/paquete-codex-1.json

Fuera del paquete, porque no son producto (.factory, kb/README.md, kb/cambios/20261111-114616-81f-almacen-bloqueo.md, kb/requisitos/flujo_cd33948e0810e1545.con_almacen_cada_comando_commitea_solo_lo_de_su_cambio.md, kb/requisitos/flujo_cd33948e0810e1545.el_commit_del_almacen_se_hace_con_un_bloqueo_corto.md, tareas): 10 archivos de registros y evidencia de Factory; no los revises.

Cómo trabajar: leé la spec y el diff; contrastá cada promesa con el código y con las pruebas; buscá casos que fallen, afirmaciones que el
código no cumple y pruebas que no prueban lo que dicen. Si podés, hacé mutaciones a mano sobre copias en tu carpeta y decí cuáles sobreviven.
Mandá la salida larga a archivos de tu carpeta y leé sólo el resumen.

Entregable: un informe JSON en /home/workstation/Dev/factory-almacen-bloqueo/.factory/local/revisores/7af6a25-codex-1/informe.json con este formato (schema oracle-clue.review/v1):
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
  oracle-clue validar /home/workstation/Dev/factory-almacen-bloqueo/.factory/local/revisores/7af6a25-codex-1/informe.json --paquete /home/workstation/Dev/factory-almacen-bloqueo/.factory/cambios/20261111-114616-81f-almacen-bloqueo/candidatos/7af6a25/clue/paquete-codex-1.json --repo /home/workstation/Dev/factory-almacen-bloqueo/.factory/local/revisiones/7af6a25-codex-1
y terminá con un resumen corto en español.

Indicaciones de quien pide la revisión:
Revisá almacen-bloqueo: etapa 4b1 de «registros fuera del repo del producto». Lo construyó un agente lanzado por el conductor (claude -p, entorno filtrado, Python acotado); la evidencia, las mutaciones y la revisión las hice yo, y corregí una ayuda de la prueba que leía mal git status. En oracle_factory/almacenes.py: _cambio_de clasifica cada ruta del almacén por cambio (su carpeta en .factory/cambios/, tareas/ u openspec/changes/, o kb/cambios/ID.md; si no tiene forma de ID, es común); con un cambio, el commit lleva lo que cambió de ese cambio y de lo común, y además lo pendiente del propio cambio aunque ya estuviera cambiado antes (para que lo que otro comando dejó lo commitee el comando de ese cambio); lo de otro cambio queda sin commitear; un comando sin cambio commitea todo; la foto final, el add y el commit van bajo bloqueo() (flock exclusivo sobre un archivo de la carpeta de Git del almacén, sólo durante el commit, con plazo de 30 s; si no se consigue, avisa y deja los registros). Spec: openspec/changes/20261111-114616-81f-almacen-bloqueo/specs/flujo/spec.md. Buscá: archivos de otro cambio que entren igual, archivos propios o comunes que no entren, carreras que todavía choquen con index.lock, un bloqueo tomado de más (durante el comando) o que no se suelte, plazos, el modo sin almacén alterado, y huecos de prueba en tests/test_almacen_bloqueo.py. Límite declarado: dos comandos sobre el MISMO cambio a la vez pueden compartir archivos. Una consecuencia a mirar: lo pendiente del propio cambio entra aunque estuviera editado a mano antes del comando (afloja una regla de la 4a). Sos el único revisor (agy sin cuota).
