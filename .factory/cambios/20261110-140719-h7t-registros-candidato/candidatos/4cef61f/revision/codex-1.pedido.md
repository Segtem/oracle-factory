Sos un revisor independiente del cambio 20261110-140719-h7t-registros-candidato de un proyecto que usa Oracle Factory: «Registros fuera del repo del producto, etapa 3: el candidato y la huella con dos fuentes». No escribiste este código.
NO edites el checkout, no hagas commits ni decidas nada por la persona: tu trabajo es encontrar defectos y contarlos con evidencia.

Qué tiene que hacer el cambio:
- Propuesta: /home/workstation/Dev/factory-registros-candidato/openspec/changes/20261110-140719-h7t-registros-candidato/proposal.md
- Spec (lo que se promete, con sus escenarios): /home/workstation/Dev/factory-registros-candidato/openspec/changes/20261110-140719-h7t-registros-candidato/specs/flujo/spec.md

Qué revisar:
- Checkout del candidato 4cef61f (sólo lectura): /home/workstation/Dev/factory-registros-candidato/.factory/local/revisiones/4cef61f-codex-1
- Paquete de Oracle Clue con el diff y el contexto: /home/workstation/Dev/factory-registros-candidato/.factory/cambios/20261110-140719-h7t-registros-candidato/candidatos/4cef61f/clue/paquete-codex-1.json

Tests existentes que este candidato modificó o borró (la guarda del proyecto: un test que ya existía no se edita para que pase sin dejarlo dicho). Mirá si cada edición está justificada por el cambio y mencionalo en tu informe, aunque la encuentres legítima:
- tests/test_registros_raiz.py, modificado: 5 línea(s) quitada(s); tests quitados: test_rr3_un_comando_de_candidato_falla_con_el_mensaje_de_la_etapa_3; 4 aserción(es) quitada(s)
Fuera del paquete, porque no son producto (.factory, kb/README.md, kb/cambios/20261110-140719-h7t-registros-candidato.md, kb/requisitos/flujo_c47a7d33c8e5ed925.con_almacen_aparte_el_candidato_es_el_ancestro_con_evidencia.md, kb/requisitos/flujo_c47a7d33c8e5ed925.con_almacen_aparte_el_ciclo_completo_funciona_sin_tocar_el_producto.md, kb/requisitos/flujo_c47a7d33c8e5ed925.con_almacen_aparte_la_huella_es_el_producto_y_este_cambio.md, kb/requisitos/flujo_c47a7d33c8e5ed925.con_almacen_aparte_no_hay_hook_en_el_producto.md, tareas): 12 archivos de registros y evidencia de Factory; no los revises.

Cómo trabajar: leé la spec y el diff; contrastá cada promesa con el código y con las pruebas; buscá casos que fallen, afirmaciones que el
código no cumple y pruebas que no prueban lo que dicen. Si podés, hacé mutaciones a mano sobre copias en tu carpeta y decí cuáles sobreviven.
Mandá la salida larga a archivos de tu carpeta y leé sólo el resumen.

Entregable: un informe JSON en /home/workstation/Dev/factory-registros-candidato/.factory/local/revisores/4cef61f-codex-1/informe.json con este formato (schema oracle-clue.review/v1):
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
  oracle-clue validar /home/workstation/Dev/factory-registros-candidato/.factory/local/revisores/4cef61f-codex-1/informe.json --paquete /home/workstation/Dev/factory-registros-candidato/.factory/cambios/20261110-140719-h7t-registros-candidato/candidatos/4cef61f/clue/paquete-codex-1.json --repo /home/workstation/Dev/factory-registros-candidato/.factory/local/revisiones/4cef61f-codex-1
y terminá con un resumen corto en español.

Indicaciones de quien pide la revisión:
Revisá registros-candidato: etapa 3 de 6 de «registros fuera del repo del producto». Lo construyó un agente lanzado por el conductor (claude -p, entorno filtrado, Python acotado) desde una spec aprobada; revisalo como cualquier otro. Con almacén aparte (cli.PRODUCTO no es None): cli.git_producto corre git en el repo del producto con GIT_OPTIONAL_LOCKS=0; el candidato vigente es el ancestro más cercano de HEAD con carpeta de evidencia en el almacén y sin cambios de producto desde entonces; la huella (contexto_del_cambio + almacenes.con_el_cambio) es el producto más la propuesta, la spec, los requisitos y los catálogos de las medidas elegidas de ESTE cambio; pedir-revision, revision-preparar, revision, revisar, juzgar y cerrar dejan de negarse; la base vacía se crea en el clon del revisor; hooks se niega. Sin almacén aparte nada debe cambiar. Spec: openspec/changes/20261110-140719-h7t-registros-candidato/specs/flujo/spec.md. Buscá: escrituras en el producto o su .git (árbol, índice, refs, hooks, config, objetos), llamadas a git que sigan corriendo sobre el almacén cuando miran el producto (hay ~36 funciones con git; revisá las que no cambiaron), huella que no incluya algo de este cambio o incluya algo de otro, candidato equivocado (ramas, merges, commits vacíos, evidencia de otro cambio), regresiones sin almacén aparte, y huecos de prueba en tests/test_registros_candidato.py. Editado a propósito: tests/test_registros_raiz.py (rr3 probaba el rechazo «etapa 3» que esta etapa quita). Límites declarados: procedencia sobre un producto con uv.lock y la cabeza del paquete sin candidato no tienen prueba. Camino completo; sos el único revisor (agy sin cuota).
