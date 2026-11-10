Sos un revisor independiente del cambio 20261110-203907-qfp-partir-cli de un proyecto que usa Oracle Factory: «cli.py: mudar los comandos del proyecto a su módulo para volver a tener margen bajo el tope». No escribiste este código.
NO edites el checkout, no hagas commits ni decidas nada por la persona: tu trabajo es encontrar defectos y contarlos con evidencia.

Qué tiene que hacer el cambio:
- Propuesta: /home/workstation/Dev/factory-partir-cli/openspec/changes/20261110-203907-qfp-partir-cli/proposal.md
- Spec (lo que se promete, con sus escenarios): /home/workstation/Dev/factory-partir-cli/openspec/changes/20261110-203907-qfp-partir-cli/specs/flujo/spec.md

Qué revisar:
- Checkout del candidato 18ec893 (sólo lectura): /home/workstation/Dev/factory-partir-cli/.factory/local/revisiones/18ec893-codex-1
- Paquete de Oracle Clue con el diff y el contexto: /home/workstation/Dev/factory-partir-cli/.factory/cambios/20261110-203907-qfp-partir-cli/candidatos/18ec893/clue/paquete-codex-1.json

Tests existentes que este candidato modificó o borró (la guarda del proyecto: un test que ya existía no se edita para que pase sin dejarlo dicho). Mirá si cada edición está justificada por el cambio y mencionalo en tu informe, aunque la encuentres legítima:
- tests/test_cli_modulos.py, modificado: 2 línea(s) quitada(s)
Fuera del paquete, porque no son producto (.factory, kb/README.md, kb/cambios/20261110-203907-qfp-partir-cli.md, kb/requisitos/flujo_cc3654ad164ff3899.cli_py_queda_con_margen_bajo_su_tope.md, kb/requisitos/flujo_cc3654ad164ff3899.lo_mudado_a_proyecto_sigue_igual.md, tareas): 6 archivos de registros y evidencia de Factory; no los revises.

Cómo trabajar: leé la spec y el diff; contrastá cada promesa con el código y con las pruebas; buscá casos que fallen, afirmaciones que el
código no cumple y pruebas que no prueban lo que dicen. Si podés, hacé mutaciones a mano sobre copias en tu carpeta y decí cuáles sobreviven.
Mandá la salida larga a archivos de tu carpeta y leé sólo el resumen.

Entregable: un informe JSON en /home/workstation/Dev/factory-partir-cli/.factory/local/revisores/18ec893-codex-1/informe.json con este formato (schema oracle-clue.review/v1):
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
  oracle-clue validar /home/workstation/Dev/factory-partir-cli/.factory/local/revisores/18ec893-codex-1/informe.json --paquete /home/workstation/Dev/factory-partir-cli/.factory/cambios/20261110-203907-qfp-partir-cli/candidatos/18ec893/clue/paquete-codex-1.json --repo /home/workstation/Dev/factory-partir-cli/.factory/local/revisiones/18ec893-codex-1
y terminá con un resumen corto en español.

Indicaciones de quien pide la revisión:
Revisá partir-cli: mudanza mecánica, sin cambio de comportamiento. Siete funciones de oracle_factory/cli.py (inicializar, plan_ejemplo, comando_migrar, comando_procedencia, comando_autonomia, comando_desplegar, comando_autopilot) pasan a oracle_factory/proyecto.py, con el mismo patrón que lecturas.py: lo de cli se lee como cli.NOMBRE al usarlo y cli las reexporta con el mismo nombre. La mudanza la hizo un script con el árbol sintáctico (prefija con cli. los nombres propios de cli usados por las funciones, importa directo los módulos de la biblioteca estándar y del paquete, no toca las anotaciones). cli.py pasa de 159984 a 139642 bytes; la suite completa da 1399 OK. tests/test_cli_modulos.py suma proyecto a MODULOS (editada a propósito, para que le apliquen las reglas cm1/cm2). Buscá: un nombre que debió prefijarse y no (o al revés), un valor de cli copiado en vez de leído al usarlo, imports de más o de menos, cambios de firma o de comportamiento, y comentarios o líneas en blanco perdidos o rotos al sacar las funciones de cli.py.
