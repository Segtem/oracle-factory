Sos un revisor independiente del cambio 20261104-115430-dnr-vscode de un proyecto que usa Oracle Factory: «Web: capturas reales de VS Code y ejemplos en las guías». No escribiste este código.
NO edites el checkout, no hagas commits ni decidas nada por la persona: tu trabajo es encontrar defectos y contarlos con evidencia.

Qué tiene que hacer el cambio:
- Propuesta: /home/workstation/Dev/factory-web-vscode/openspec/changes/20261104-115430-dnr-vscode/proposal.md
- Spec (lo que se promete, con sus escenarios): /home/workstation/Dev/factory-web-vscode/openspec/changes/20261104-115430-dnr-vscode/specs/web/spec.md

Qué revisar:
- Checkout del candidato 19b9947 (sólo lectura): /home/workstation/Dev/factory-web-vscode/.factory/local/revisiones/19b9947-codex-1
- Paquete de Oracle Clue con el diff y el contexto: /home/workstation/Dev/factory-web-vscode/.factory/cambios/20261104-115430-dnr-vscode/candidatos/19b9947/clue/paquete-codex-1.json

Vueltas anteriores de este cambio (ya corregidas; mirá que sigan cerradas y que no haya regresiones):
- .factory/cambios/20261104-115430-dnr-vscode/candidatos/2524474/revision/agy2-flash-1.json
- .factory/cambios/20261104-115430-dnr-vscode/candidatos/2524474/revision/codex-1.json
- .factory/cambios/20261104-115430-dnr-vscode/candidatos/420f74f/revision/agy2-flash-1.json
- .factory/cambios/20261104-115430-dnr-vscode/candidatos/420f74f/revision/codex-1.json
Tests existentes que este candidato modificó o borró (la guarda del proyecto: un test que ya existía no se edita para que pase sin dejarlo dicho). Mirá si cada edición está justificada por el cambio y mencionalo en tu informe, aunque la encuentres legítima:
- tests/test_site.cjs, modificado: 1 línea(s) quitada(s); 1 aserción(es) quitada(s)
- tests/test_web.py, modificado: 1 línea(s) quitada(s)
Fuera del paquete, porque no son producto (.factory, kb/README.md, kb/cambios/20261104-115430-dnr-vscode.md, kb/requisitos/web_c2e4546f9d843453e.las_guias_muestran_vscode_real.md, kb/requisitos/web_c2e4546f9d843453e.los_ejemplos_no_filtran_datos_personales.md, kb/requisitos/web_c2e4546f9d843453e.los_ejemplos_son_salida_real.md, tareas): 23 archivos de registros y evidencia de Factory; no los revises.

Cómo trabajar: leé la spec y el diff; contrastá cada promesa con el código y con las pruebas; buscá casos que fallen, afirmaciones que el
código no cumple y pruebas que no prueban lo que dicen. Si podés, hacé mutaciones a mano sobre copias en tu carpeta y decí cuáles sobreviven.
Mandá la salida larga a archivos de tu carpeta y leé sólo el resumen.

Entregable: un informe JSON en /home/workstation/Dev/factory-web-vscode/.factory/local/revisores/19b9947-codex-1/informe.json con este formato (schema oracle-clue.review/v1):
- schema_version "oracle-clue.review/v1"; repo, base, head, diff_sha256 y context_sha256 copiados del paquete;
- provider {"name": "codex", "model": "gpt-6-luna"};
- findings: lista de hallazgos, cada uno con id, kind, severity (alta|media|baja|informativa), confidence (0 a 1), title, explanation,
  location {file, start_line, end_line, side: "head"} DENTRO de los rangos del diff del paquete, trigger, evidence, related_requirement,
  status "pendiente" y verification;
- review_status ("completo" o "incompleto") y limitations (qué corriste y qué no).
Sin hallazgos: findings vacía, explicado en limitations. Validalo antes de terminar con:
  oracle-clue validar /home/workstation/Dev/factory-web-vscode/.factory/local/revisores/19b9947-codex-1/informe.json --paquete /home/workstation/Dev/factory-web-vscode/.factory/cambios/20261104-115430-dnr-vscode/candidatos/19b9947/clue/paquete-codex-1.json --repo /home/workstation/Dev/factory-web-vscode/.factory/local/revisiones/19b9947-codex-1
y terminá con un resumen corto en español.

Indicaciones de quien pide la revisión:
No cambies la configuración de git de ningún repositorio. Tercera ronda de web-vscode (capturas reales de VS Code y ejemplos con salida real en las guías). La ronda 2 dejó un único medio, de codex: medidas_png sólo buscaba la firma, IHDR en posición fija y el cierre IEND, y aceptaba firma+IHDR+basura+IEND. Arreglo de la clase entera en tools/sitio_vscode.py: medidas_png recorre los bloques PNG con su longitud y su CRC (zlib.crc32), exige IHDR primero de 13 bytes con ancho y alto no cero, al menos un IDAT, IEND al final y nada después; no decodifica píxeles (límite declarado con un comentario). tests/test_web_vscode.py suma casos: basura entre IHDR e IEND, un byte cambiado (CRC), sin IDAT y bytes después del cierre, con mutaciones comprobadas (sin CRC, sin IDAT, sin fin exacto, sin IEND al final: todas se detectan). Nada más cambió desde la ronda 2 (los catálogos no cambiaron). Los tests existentes modificados siguen siendo tests/test_web.py, tests/test_site.cjs y tests/datos/guias-texto.json (sólo líneas agregadas). Buscá errores reales y de impacto práctico; no repitas lo ya cerrado. Marcá los exóticos y decí con claridad si no queda nada de impacto práctico. Clasificá por severidad.
