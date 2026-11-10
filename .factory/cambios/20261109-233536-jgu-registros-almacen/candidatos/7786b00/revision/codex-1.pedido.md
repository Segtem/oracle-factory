Sos un revisor independiente del cambio 20261109-233536-jgu-registros-almacen de un proyecto que usa Oracle Factory: «Registros fuera del repo del producto, etapa 2: el almacén y conectar». No escribiste este código.
NO edites el checkout, no hagas commits ni decidas nada por la persona: tu trabajo es encontrar defectos y contarlos con evidencia.

Qué tiene que hacer el cambio:
- Propuesta: /home/workstation/Dev/factory-registros-almacen/openspec/changes/20261109-233536-jgu-registros-almacen/proposal.md
- Spec (lo que se promete, con sus escenarios): /home/workstation/Dev/factory-registros-almacen/openspec/changes/20261109-233536-jgu-registros-almacen/specs/flujo/spec.md

Qué revisar:
- Checkout del candidato 7786b00 (sólo lectura): /home/workstation/Dev/factory-registros-almacen/.factory/local/revisiones/7786b00-codex-1
- Paquete de Oracle Clue con el diff y el contexto: /home/workstation/Dev/factory-registros-almacen/.factory/cambios/20261109-233536-jgu-registros-almacen/candidatos/7786b00/clue/paquete-codex-1.json

Vueltas anteriores de este cambio (ya corregidas; mirá que sigan cerradas y que no haya regresiones):
- .factory/cambios/20261109-233536-jgu-registros-almacen/candidatos/fb6769c/revision/codex-1.json
Tests existentes que este candidato modificó o borró (la guarda del proyecto: un test que ya existía no se edita para que pase sin dejarlo dicho). Mirá si cada edición está justificada por el cambio y mencionalo en tu informe, aunque la encuentres legítima:
- tests/datos/ayuda-cli.json, modificado: 1 línea(s) quitada(s)
Fuera del paquete, porque no son producto (.factory, kb/README.md, kb/cambios/20261109-233536-jgu-registros-almacen.md, kb/requisitos/flujo_c92ca9731e38f72e0.con_el_producto_conectado_los_comandos_usan_el_almacen.md, kb/requisitos/flujo_c92ca9731e38f72e0.conectar_guarda_el_almacen_por_usuario_sin_tocar_el_producto.md, kb/requisitos/flujo_c92ca9731e38f72e0.conectar_sin_argumentos_y_desconectar.md, kb/requisitos/flujo_c92ca9731e38f72e0.un_producto_con_su_propio_factory_conectado_se_niega.md, tareas): 18 archivos de registros y evidencia de Factory; no los revises.

Cómo trabajar: leé la spec y el diff; contrastá cada promesa con el código y con las pruebas; buscá casos que fallen, afirmaciones que el
código no cumple y pruebas que no prueban lo que dicen. Si podés, hacé mutaciones a mano sobre copias en tu carpeta y decí cuáles sobreviven.
Mandá la salida larga a archivos de tu carpeta y leé sólo el resumen.

Entregable: un informe JSON en /home/workstation/Dev/factory-registros-almacen/.factory/local/revisores/7786b00-codex-1/informe.json con este formato (schema oracle-clue.review/v1):
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
  oracle-clue validar /home/workstation/Dev/factory-registros-almacen/.factory/local/revisores/7786b00-codex-1/informe.json --paquete /home/workstation/Dev/factory-registros-almacen/.factory/cambios/20261109-233536-jgu-registros-almacen/candidatos/7786b00/clue/paquete-codex-1.json --repo /home/workstation/Dev/factory-registros-almacen/.factory/local/revisiones/7786b00-codex-1
y terminá con un resumen corto en español.

Indicaciones de quien pide la revisión:
Revisá registros-almacen (ronda 2). Ronda 1: un hallazgo medio (dos conectar a la vez podían perder una conexión: leer-modificar-guardar sin bloqueo y temporal de nombre fijo) corregido: oracle_factory/almacenes.py tiene ahora actualizando() (flock exclusivo sobre almacenes.json.lock, relee bajo el bloqueo, guarda con un temporal propio creado con mkstemp junto al archivo y borrado si falla); conectar y desconectar lo usan; la prueba lanza 6 procesos a la vez. Sin fcntl (Windows) no hay bloqueo: está dicho en un comentario. Verificá la corrección y buscá lo que quede: bloqueo que se pierda (fd cerrado antes de guardar, excepciones), deadlock, el archivo .lock como residuo, conectar que deje el almacén a medias si falla algo después de inicializarlo, producto equivocado (worktrees, repos anidados, enlaces), escrituras en el producto o el HOME real, mensajes engañosos y huecos de prueba. Spec: openspec/changes/20261109-233536-jgu-registros-almacen/specs/flujo/spec.md.
