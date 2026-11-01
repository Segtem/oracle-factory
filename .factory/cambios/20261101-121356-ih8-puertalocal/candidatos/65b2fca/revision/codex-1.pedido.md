Sos un revisor independiente del cambio 20261101-121356-ih8-puertalocal de un proyecto que usa Oracle Factory: «Una puerta local de salida: escaneo de secretos y verificaciones antes de cada push». No escribiste este código.
NO edites el checkout, no hagas commits ni decidas nada por la persona: tu trabajo es encontrar defectos y contarlos con evidencia.

Qué tiene que hacer el cambio:
- Propuesta: /home/workstation/Dev/factory-puerta-local/openspec/changes/20261101-121356-ih8-puertalocal/proposal.md
- Spec (lo que se promete, con sus escenarios): /home/workstation/Dev/factory-puerta-local/openspec/changes/20261101-121356-ih8-puertalocal/specs/calidad/spec.md

Qué revisar:
- Checkout del candidato 65b2fca (sólo lectura): /home/workstation/Dev/factory-puerta-local/.factory/local/revisiones/65b2fca-codex-1
- Paquete de Oracle Clue con el diff y el contexto: /home/workstation/Dev/factory-puerta-local/.factory/cambios/20261101-121356-ih8-puertalocal/candidatos/65b2fca/clue/paquete-codex-1.json

Vueltas anteriores de este cambio (ya corregidas; mirá que sigan cerradas y que no haya regresiones):
- .factory/cambios/20261101-121356-ih8-puertalocal/candidatos/7658f1d/revision/agy2-flash-1.json
- .factory/cambios/20261101-121356-ih8-puertalocal/candidatos/7658f1d/revision/codex-1.json
Tests existentes que este candidato modificó o borró (la guarda del proyecto: un test que ya existía no se edita para que pase sin dejarlo dicho). Mirá si cada edición está justificada por el cambio y mencionalo en tu informe, aunque la encuentres legítima:
- tests/datos/ayuda-cli.json, modificado: 1 línea(s) quitada(s)
Fuera del paquete, porque no son producto (.factory, kb/README.md, kb/cambios/20261101-121356-ih8-puertalocal.md, kb/requisitos/calidad_cdbf33d35727ca9d7.el_hook_pre_push_llama_a_la_puerta_con_lo_que_se_empuja.md, kb/requisitos/calidad_cdbf33d35727ca9d7.la_puerta_corre_las_verificaciones_del_proyecto.md, kb/requisitos/calidad_cdbf33d35727ca9d7.la_puerta_detecta_secretos_en_todos_los_commits_que_se_publican.md, kb/requisitos/calidad_cdbf33d35727ca9d7.la_puerta_no_modifica_el_arbol_de_trabajo.md, tareas): 16 archivos de registros y evidencia de Factory; no los revises.

Cómo trabajar: leé la spec y el diff; contrastá cada promesa con el código y con las pruebas; buscá casos que fallen, afirmaciones que el
código no cumple y pruebas que no prueban lo que dicen. Si podés, hacé mutaciones a mano sobre copias en tu carpeta y decí cuáles sobreviven.
Mandá la salida larga a archivos de tu carpeta y leé sólo el resumen.

Entregable: un informe JSON en /home/workstation/Dev/factory-puerta-local/.factory/local/revisores/65b2fca-codex-1/informe.json con este formato (schema oracle-clue.review/v1):
- schema_version "oracle-clue.review/v1"; repo, base, head, diff_sha256 y context_sha256 copiados del paquete;
- provider {"name": "codex", "model": "gpt-6-luna"};
- findings: lista de hallazgos, cada uno con id, kind, severity (alta|media|baja|informativa), confidence (0 a 1), title, explanation,
  location {file, start_line, end_line, side: "head"} DENTRO de los rangos del diff del paquete, trigger, evidence, related_requirement,
  status "pendiente" y verification;
- review_status ("completo" o "incompleto") y limitations (qué corriste y qué no).
Sin hallazgos: findings vacía, explicado en limitations. Validalo antes de terminar con:
  oracle-clue validar /home/workstation/Dev/factory-puerta-local/.factory/local/revisores/65b2fca-codex-1/informe.json --paquete /home/workstation/Dev/factory-puerta-local/.factory/cambios/20261101-121356-ih8-puertalocal/candidatos/65b2fca/clue/paquete-codex-1.json --repo /home/workstation/Dev/factory-puerta-local/.factory/local/revisiones/65b2fca-codex-1
y terminá con un resumen corto en español.

Indicaciones de quien pide la revisión:
No cambies la configuración de git de ningún repositorio. Es la segunda ronda de puerta-local: la primera trajo 11 hallazgos (merges sin diff, ASIA, líneas de más de 300 000 caracteres recortadas, triples comillas, rutas con espacios o comillas, SHA-256, mensaje del hook, línea sugerida para un hook ajeno, verificaciones al día no informadas con una que falla). Se arreglaron con --cc, A[KS]IA, líneas enteras, `["']{1,3}`, _ruta, SHA-1 o SHA-256, mensajes y un `&& exit 1` sugerido; las asignaciones con el valor en otra línea quedaron como límite declarado en docs/puerta.md. Verificá que cada arreglo arregla la CLASE del problema y no sólo el caso (por ejemplo: el formato combinado de --cc con 2 o más padres y con -U0, rutas con otros escapes de Git, regex lentas con líneas enormes). Revisá oracle_factory/puerta.py, su cableado en cli.py (puerta, hook pre-push, instalar_pre_push, SOLO_LECTURA), docs/puerta.md, tools/verify_puerta_local.py y tests/test_puerta.py. La puerta bloquea sólo con el código 3; cualquier otro fallo avisa y deja pasar; sólo la guía de agentes vieja bloquea; no debe escribir nada en el proyecto. Buscá errores reales y clasificá por severidad.
