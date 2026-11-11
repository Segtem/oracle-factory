Sos un revisor independiente del cambio 20261111-135546-t8q-almacen-sincronizar de un proyecto que usa Oracle Factory: «Registros fuera del repo del producto, etapa 4b2: conectar desde una URL y sincronizar el almacén entre personas». No escribiste este código.
NO edites el checkout, no hagas commits ni decidas nada por la persona: tu trabajo es encontrar defectos y contarlos con evidencia.

Qué tiene que hacer el cambio:
- Propuesta: /home/workstation/Dev/factory-almacen-sincronizar/openspec/changes/20261111-135546-t8q-almacen-sincronizar/proposal.md
- Spec (lo que se promete, con sus escenarios): /home/workstation/Dev/factory-almacen-sincronizar/openspec/changes/20261111-135546-t8q-almacen-sincronizar/specs/flujo/spec.md

Qué revisar:
- Checkout del candidato 1a1c920 (sólo lectura): /home/workstation/Dev/factory-almacen-sincronizar/.factory/local/revisiones/1a1c920-codex-1
- Paquete de Oracle Clue con el diff y el contexto: /home/workstation/Dev/factory-almacen-sincronizar/.factory/cambios/20261111-135546-t8q-almacen-sincronizar/candidatos/1a1c920/clue/paquete-codex-1.json

Vueltas anteriores de este cambio (ya corregidas; mirá que sigan cerradas y que no haya regresiones):
- .factory/cambios/20261111-135546-t8q-almacen-sincronizar/candidatos/3e8cf90/revision/codex-1.json
Tests existentes que este candidato modificó o borró (la guarda del proyecto: un test que ya existía no se edita para que pase sin dejarlo dicho). Mirá si cada edición está justificada por el cambio y mencionalo en tu informe, aunque la encuentres legítima:
- tests/datos/ayuda-cli.json, modificado: 2 línea(s) quitada(s)
Fuera del paquete, porque no son producto (.factory, kb/README.md, kb/cambios/20261111-135546-t8q-almacen-sincronizar.md, kb/requisitos/flujo_c5b6a893e70e9eba0.conectar_una_url_clona_el_almacen_en_una_carpeta_del_usuario.md, kb/requisitos/flujo_c5b6a893e70e9eba0.sincronizar_sube_solo_si_es_una_persona_y_no_deja_nada_a_medias.md, kb/requisitos/flujo_c5b6a893e70e9eba0.sincronizar_une_los_registros_de_todos_sin_escribir_configuracion.md, tareas): 17 archivos de registros y evidencia de Factory; no los revises.

Cómo trabajar: leé la spec y el diff; contrastá cada promesa con el código y con las pruebas; buscá casos que fallen, afirmaciones que el
código no cumple y pruebas que no prueban lo que dicen. Si podés, hacé mutaciones a mano sobre copias en tu carpeta y decí cuáles sobreviven.
Mandá la salida larga a archivos de tu carpeta y leé sólo el resumen.

Entregable: un informe JSON en /home/workstation/Dev/factory-almacen-sincronizar/.factory/local/revisores/1a1c920-codex-1/informe.json con este formato (schema oracle-clue.review/v1):
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
  oracle-clue validar /home/workstation/Dev/factory-almacen-sincronizar/.factory/local/revisores/1a1c920-codex-1/informe.json --paquete /home/workstation/Dev/factory-almacen-sincronizar/.factory/cambios/20261111-135546-t8q-almacen-sincronizar/candidatos/1a1c920/clue/paquete-codex-1.json --repo /home/workstation/Dev/factory-almacen-sincronizar/.factory/local/revisiones/1a1c920-codex-1
y terminá con un resumen corto en español.

Indicaciones de quien pide la revisión:
Revisá almacen-sincronizar (ronda 2). Ronda 1: codex-01 (alto: un archivo local ignorado o sin versionar que el remoto agrega versionado se perdía) corregido en _unir: después del fetch se miran los archivos que agrega el remoto (git diff --diff-filter=A HEAD...REMOTO/RAMA) y si alguno existe en el disco sin estar versionado, no se une, se dice cuáles y el almacén queda como estaba; un archivo que agregaron igual las dos partes sigue uniéndose. codex-02 (la subida fuera del bloqueo) es un falso positivo: el push está indentado dentro del with bloqueo(...); queda fijado con una prueba que intenta tomar el bloqueo justo cuando corre el push y no puede. Verificá y buscá lo que quede, con un caso que reproduzca (por ejemplo: archivos que el remoto modifica o renombra sobre algo local ignorado, o lo local de Factory).
