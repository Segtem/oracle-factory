Sos un revisor independiente del cambio 20261104-115430-dnr-vscode de un proyecto que usa Oracle Factory: «Web: capturas reales de VS Code y ejemplos en las guías». No escribiste este código.
NO edites el checkout, no hagas commits ni decidas nada por la persona: tu trabajo es encontrar defectos y contarlos con evidencia.

Qué tiene que hacer el cambio:
- Propuesta: /home/workstation/Dev/factory-web-vscode/openspec/changes/20261104-115430-dnr-vscode/proposal.md
- Spec (lo que se promete, con sus escenarios): /home/workstation/Dev/factory-web-vscode/openspec/changes/20261104-115430-dnr-vscode/specs/web/spec.md

Qué revisar:
- Checkout del candidato 9d492f6 (sólo lectura): /home/workstation/Dev/factory-web-vscode/.factory/local/revisiones/9d492f6-codex-1
- Paquete de Oracle Clue con el diff y el contexto: /home/workstation/Dev/factory-web-vscode/.factory/cambios/20261104-115430-dnr-vscode/candidatos/9d492f6/clue/paquete-codex-1.json

Vueltas anteriores de este cambio (ya corregidas; mirá que sigan cerradas y que no haya regresiones):
- .factory/cambios/20261104-115430-dnr-vscode/candidatos/2524474/revision/agy2-flash-1.json
- .factory/cambios/20261104-115430-dnr-vscode/candidatos/2524474/revision/codex-1.json
- .factory/cambios/20261104-115430-dnr-vscode/candidatos/420f74f/revision/agy2-flash-1.json
- .factory/cambios/20261104-115430-dnr-vscode/candidatos/420f74f/revision/codex-1.json
- .factory/cambios/20261104-115430-dnr-vscode/candidatos/19b9947/revision/agy2-flash-1.json
- .factory/cambios/20261104-115430-dnr-vscode/candidatos/19b9947/revision/codex-1.json
Tests existentes que este candidato modificó o borró (la guarda del proyecto: un test que ya existía no se edita para que pase sin dejarlo dicho). Mirá si cada edición está justificada por el cambio y mencionalo en tu informe, aunque la encuentres legítima:
- tests/test_site.cjs, modificado: 1 línea(s) quitada(s); 1 aserción(es) quitada(s)
- tests/test_web.py, modificado: 1 línea(s) quitada(s)
Fuera del paquete, porque no son producto (.factory, kb/README.md, kb/cambios/20261104-115430-dnr-vscode.md, kb/requisitos/web_c2e4546f9d843453e.las_guias_muestran_vscode_real.md, kb/requisitos/web_c2e4546f9d843453e.los_ejemplos_no_filtran_datos_personales.md, kb/requisitos/web_c2e4546f9d843453e.los_ejemplos_son_salida_real.md, tareas): 40 archivos de registros y evidencia de Factory; no los revises.

Cómo trabajar: leé la spec y el diff; contrastá cada promesa con el código y con las pruebas; buscá casos que fallen, afirmaciones que el
código no cumple y pruebas que no prueban lo que dicen. Si podés, hacé mutaciones a mano sobre copias en tu carpeta y decí cuáles sobreviven.
Mandá la salida larga a archivos de tu carpeta y leé sólo el resumen.

Entregable: un informe JSON en /home/workstation/Dev/factory-web-vscode/.factory/local/revisores/9d492f6-codex-1/informe.json con este formato (schema oracle-clue.review/v1):
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
  oracle-clue validar /home/workstation/Dev/factory-web-vscode/.factory/local/revisores/9d492f6-codex-1/informe.json --paquete /home/workstation/Dev/factory-web-vscode/.factory/cambios/20261104-115430-dnr-vscode/candidatos/9d492f6/clue/paquete-codex-1.json --repo /home/workstation/Dev/factory-web-vscode/.factory/local/revisiones/9d492f6-codex-1
y terminá con un resumen corto en español.

Indicaciones de quien pide la revisión:
Ronda 4, sólo por el paquete: el contenido de web-vscode es el que cerró con 0 hallazgos en la ronda 3, más el merge de main. El paquete omite los cuatro PNG de site/img/ por no ser texto: abrilos en el checkout y declará cada uno con una línea de limitations exacta «abierto: RUTA» (RUTA como figura en el paquete), sin declarar los que no abriste. Mirá también que el merge no haya cambiado nada de web-vscode.
