Sos un revisor independiente del cambio 20261110-095631-0w3-entorno-agente de un proyecto que usa Oracle Factory: «Autopilot: el agente lanzado recibe un entorno filtrado y una guía de permisos sin Python abierto». No escribiste este código.
NO edites el checkout, no hagas commits ni decidas nada por la persona: tu trabajo es encontrar defectos y contarlos con evidencia.

Qué tiene que hacer el cambio:
- Propuesta: /home/workstation/Dev/factory-entorno-agente/openspec/changes/20261110-095631-0w3-entorno-agente/proposal.md
- Spec (lo que se promete, con sus escenarios): /home/workstation/Dev/factory-entorno-agente/openspec/changes/20261110-095631-0w3-entorno-agente/specs/flujo/spec.md

Qué revisar:
- Checkout del candidato b2dee68 (sólo lectura): /home/workstation/Dev/factory-entorno-agente/.factory/local/revisiones/b2dee68-codex-1
- Paquete de Oracle Clue con el diff y el contexto: /home/workstation/Dev/factory-entorno-agente/.factory/cambios/20261110-095631-0w3-entorno-agente/candidatos/b2dee68/clue/paquete-codex-1.json

Tests existentes que este candidato modificó o borró (la guarda del proyecto: un test que ya existía no se edita para que pase sin dejarlo dicho). Mirá si cada edición está justificada por el cambio y mencionalo en tu informe, aunque la encuentres legítima:
- tests/datos/ayuda-cli.json, modificado: 1 línea(s) quitada(s)
Fuera del paquete, porque no son producto (.factory, kb/README.md, kb/cambios/20261110-095631-0w3-entorno-agente.md, kb/requisitos/flujo_c93a1d23e9668d672.el_agente_lanzado_recibe_un_entorno_minimo.md, kb/requisitos/flujo_c93a1d23e9668d672.entorno_explicito_por_corrida.md, kb/requisitos/flujo_c93a1d23e9668d672.la_guia_de_permisos_no_abre_python.md, tareas): 11 archivos de registros y evidencia de Factory; no los revises.

Cómo trabajar: leé la spec y el diff; contrastá cada promesa con el código y con las pruebas; buscá casos que fallen, afirmaciones que el
código no cumple y pruebas que no prueban lo que dicen. Si podés, hacé mutaciones a mano sobre copias en tu carpeta y decí cuáles sobreviven.
Mandá la salida larga a archivos de tu carpeta y leé sólo el resumen.

Entregable: un informe JSON en /home/workstation/Dev/factory-entorno-agente/.factory/local/revisores/b2dee68-codex-1/informe.json con este formato (schema oracle-clue.review/v1):
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
  oracle-clue validar /home/workstation/Dev/factory-entorno-agente/.factory/local/revisores/b2dee68-codex-1/informe.json --paquete /home/workstation/Dev/factory-entorno-agente/.factory/cambios/20261110-095631-0w3-entorno-agente/candidatos/b2dee68/clue/paquete-codex-1.json --repo /home/workstation/Dev/factory-entorno-agente/.factory/local/revisiones/b2dee68-codex-1
y terminá con un resumen corto en español.

Indicaciones de quien pide la revisión:
Revisá entorno-agente: arreglo de seguridad del conductor. Hasta ahora autopilot --ejecutar --lanzar le pasaba al agente lanzado TODO el entorno de la persona ({**os.environ,...}: claves de API, tokens) y la guía de permisos recomendaba Bash(.venv/bin/python:*), que deja correr cualquier Python (red, leer el entorno, git push). Ahora oracle_factory/conductor.py tiene entorno_del_agente(): una LISTA DE PERMITIDOS (PATH, HOME, USER, LOGNAME, SHELL, LANG, LANGUAGE, TERM, TZ, TMPDIR, BASH_DEFAULT_TIMEOUT_MS, BASH_MAX_TIMEOUT_MS, prefijos LC_ y XDG_) más lo que la persona entregue con --entorno NOMBRE (repetible, sólo con --lanzar, por corrida, no se guarda) más FACTORY_AGENTE, que gana siempre; los comandos mecánicos de Factory no cambian; docs/modos.md muestra la guía con Python acotado a -m unittest y tools/verificar_cambio.py. Spec: openspec/changes/20261110-095631-0w3-entorno-agente/specs/flujo/spec.md. Buscá: formas en que una variable no permitida llegue igual al agente (HOME apunta a donde hay credenciales: es un límite conocido y declarado; ¿algo más? por ejemplo variables que arrastren otras, PATH con directorios peligrosos, el --entorno que acepta nombres raros, comparaciones de mayúsculas/minúsculas, Windows), huecos en la validación de --entorno, el orden de la validación respecto de lo que se escribe, y huecos de prueba en tests/test_entorno_agente.py. tests/datos/ayuda-cli.json cambió porque se agregó --entorno (regenerado). Es camino completo (toca cli.py) y agy no tiene cuota, así que sos el único revisor.
