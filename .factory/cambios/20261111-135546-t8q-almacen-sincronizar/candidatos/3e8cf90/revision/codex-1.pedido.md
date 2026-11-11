Sos un revisor independiente del cambio 20261111-135546-t8q-almacen-sincronizar de un proyecto que usa Oracle Factory: «Registros fuera del repo del producto, etapa 4b2: conectar desde una URL y sincronizar el almacén entre personas». No escribiste este código.
NO edites el checkout, no hagas commits ni decidas nada por la persona: tu trabajo es encontrar defectos y contarlos con evidencia.

Qué tiene que hacer el cambio:
- Propuesta: /home/workstation/Dev/factory-almacen-sincronizar/openspec/changes/20261111-135546-t8q-almacen-sincronizar/proposal.md
- Spec (lo que se promete, con sus escenarios): /home/workstation/Dev/factory-almacen-sincronizar/openspec/changes/20261111-135546-t8q-almacen-sincronizar/specs/flujo/spec.md

Qué revisar:
- Checkout del candidato 3e8cf90 (sólo lectura): /home/workstation/Dev/factory-almacen-sincronizar/.factory/local/revisiones/3e8cf90-codex-1
- Paquete de Oracle Clue con el diff y el contexto: /home/workstation/Dev/factory-almacen-sincronizar/.factory/cambios/20261111-135546-t8q-almacen-sincronizar/candidatos/3e8cf90/clue/paquete-codex-1.json

Tests existentes que este candidato modificó o borró (la guarda del proyecto: un test que ya existía no se edita para que pase sin dejarlo dicho). Mirá si cada edición está justificada por el cambio y mencionalo en tu informe, aunque la encuentres legítima:
- tests/datos/ayuda-cli.json, modificado: 2 línea(s) quitada(s)
Fuera del paquete, porque no son producto (.factory, kb/README.md, kb/cambios/20261111-135546-t8q-almacen-sincronizar.md, kb/requisitos/flujo_c5b6a893e70e9eba0.conectar_una_url_clona_el_almacen_en_una_carpeta_del_usuario.md, kb/requisitos/flujo_c5b6a893e70e9eba0.sincronizar_sube_solo_si_es_una_persona_y_no_deja_nada_a_medias.md, kb/requisitos/flujo_c5b6a893e70e9eba0.sincronizar_une_los_registros_de_todos_sin_escribir_configuracion.md, tareas): 11 archivos de registros y evidencia de Factory; no los revises.

Cómo trabajar: leé la spec y el diff; contrastá cada promesa con el código y con las pruebas; buscá casos que fallen, afirmaciones que el
código no cumple y pruebas que no prueban lo que dicen. Si podés, hacé mutaciones a mano sobre copias en tu carpeta y decí cuáles sobreviven.
Mandá la salida larga a archivos de tu carpeta y leé sólo el resumen.

Entregable: un informe JSON en /home/workstation/Dev/factory-almacen-sincronizar/.factory/local/revisores/3e8cf90-codex-1/informe.json con este formato (schema oracle-clue.review/v1):
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
  oracle-clue validar /home/workstation/Dev/factory-almacen-sincronizar/.factory/local/revisores/3e8cf90-codex-1/informe.json --paquete /home/workstation/Dev/factory-almacen-sincronizar/.factory/cambios/20261111-135546-t8q-almacen-sincronizar/candidatos/3e8cf90/clue/paquete-codex-1.json --repo /home/workstation/Dev/factory-almacen-sincronizar/.factory/local/revisiones/3e8cf90-codex-1
y terminá con un resumen corto en español.

Indicaciones de quien pide la revisión:
Revisá almacen-sincronizar: etapa 4b2 de «registros fuera del repo del producto», la que permite a un equipo compartir el almacén. Lo construyó un agente lanzado por el conductor (claude -p, entorno filtrado, Python acotado); las pruebas las empezó él y las completé yo (cuota), y las mutaciones, la ayuda del CLI, la doc y la evidencia las hice yo. oracle_factory/almacenes.py: es_url, carpeta_de_clones, clonar (clona en un temporal junto al destino y renombra; reusa un clon de la misma URL; se niega con otra cosa), sincronizar (bajo el bloqueo del almacén de la 4b1: verifica limpio, escribe y commitea .gitattributes si falta, fetch, merge con los drivers de unión pasados con git -c, rehace lo generado; si algo falla, merge --abort y reset --hard al punto de partida; con --agente no sube; si es una persona, push). cli.drivers_de_union y escribir_atributos salieron de instalar_union sin cambiar hooks. Spec: openspec/changes/20261111-135546-t8q-almacen-sincronizar/specs/flujo/spec.md. Buscá: pérdida de trabajo local (el reset --hard es seguro sólo si el almacén está limpio: ¿hay forma de que no lo esté al llegar ahí, por ejemplo ignorados o lo local?), escrituras de configuración de Git (en el clon, el remoto o el usuario), un clon a medias, una URL mal reconocida, el push sin bloqueo o sin unión, el agente que sube, el conductor y huecos de prueba en tests/test_almacen_sincronizar.py. tests/datos/ayuda-cli.json se regeneró por el subcomando nuevo y la ayuda de conectar. Camino completo; sos el único revisor (agy sin cuota).
