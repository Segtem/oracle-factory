Sos un revisor independiente del cambio 20261104-115430-dnr-vscode de un proyecto que usa Oracle Factory: «Web: capturas reales de VS Code y ejemplos en las guías». No escribiste este código.
NO edites el checkout, no hagas commits ni decidas nada por la persona: tu trabajo es encontrar defectos y contarlos con evidencia.

Qué tiene que hacer el cambio:
- Propuesta: /home/workstation/Dev/factory-web-vscode/openspec/changes/20261104-115430-dnr-vscode/proposal.md
- Spec (lo que se promete, con sus escenarios): /home/workstation/Dev/factory-web-vscode/openspec/changes/20261104-115430-dnr-vscode/specs/web/spec.md

Qué revisar:
- Checkout del candidato 2524474 (sólo lectura): /home/workstation/Dev/factory-web-vscode/.factory/local/revisiones/2524474-agy2-flash-1
- Paquete de Oracle Clue con el diff y el contexto: /home/workstation/Dev/factory-web-vscode/.factory/cambios/20261104-115430-dnr-vscode/candidatos/2524474/clue/paquete-agy2-flash-1.json

Tests existentes que este candidato modificó o borró (la guarda del proyecto: un test que ya existía no se edita para que pase sin dejarlo dicho). Mirá si cada edición está justificada por el cambio y mencionalo en tu informe, aunque la encuentres legítima:
- tests/test_site.cjs, modificado: 1 línea(s) quitada(s); 1 aserción(es) quitada(s)
- tests/test_web.py, modificado: 1 línea(s) quitada(s)
Fuera del paquete, porque no son producto (.factory, kb/README.md, kb/cambios/20261104-115430-dnr-vscode.md, kb/requisitos/web_c2e4546f9d843453e.las_guias_muestran_vscode_real.md, kb/requisitos/web_c2e4546f9d843453e.los_ejemplos_no_filtran_datos_personales.md, kb/requisitos/web_c2e4546f9d843453e.los_ejemplos_son_salida_real.md, tareas): 7 archivos de registros y evidencia de Factory; no los revises.

Cómo trabajar: leé la spec y el diff; contrastá cada promesa con el código y con las pruebas; buscá casos que fallen, afirmaciones que el
código no cumple y pruebas que no prueban lo que dicen. Si podés, hacé mutaciones a mano sobre copias en tu carpeta y decí cuáles sobreviven.
Mandá la salida larga a archivos de tu carpeta y leé sólo el resumen.

Entregable: un informe JSON en /home/workstation/Dev/factory-web-vscode/.factory/local/revisores/2524474-agy2-flash-1/informe.json con este formato (schema oracle-clue.review/v1):
- schema_version "oracle-clue.review/v1"; repo, base, head, diff_sha256 y context_sha256 copiados del paquete;
- provider {"name": "agy", "model": "gemini-3.8-flash-high"};
- findings: lista de hallazgos, cada uno con id, kind, severity (alta|media|baja|informativa), confidence (0 a 1), title, explanation,
  location {file, start_line, end_line, side: "head"} DENTRO de los rangos del diff del paquete, trigger, evidence, related_requirement,
  status "pendiente" y verification;
- review_status ("completo" o "incompleto") y limitations (qué corriste y qué no).
Sin hallazgos: findings vacía, explicado en limitations. Validalo antes de terminar con:
  oracle-clue validar /home/workstation/Dev/factory-web-vscode/.factory/local/revisores/2524474-agy2-flash-1/informe.json --paquete /home/workstation/Dev/factory-web-vscode/.factory/cambios/20261104-115430-dnr-vscode/candidatos/2524474/clue/paquete-agy2-flash-1.json --repo /home/workstation/Dev/factory-web-vscode/.factory/local/revisiones/2524474-agy2-flash-1
y terminá con un resumen corto en español.

Indicaciones de quien pide la revisión:
No cambies la configuración de git de ningún repositorio. Primera ronda de web-vscode (primero de tres cambios de la web): capturas reales de VS Code y ejemplos con salida real en las guías. Producto: tools/sitio_vscode.py (comprobador: imágenes que existen con alt, ancho/alto y tope de 300 KB por imagen y 1,5 MB en total, mínimo 4 capturas; ejemplos `<pre data-ejemplo>` que coinciden con tests/datos/ejemplos-demo.json; ningún dato personal ni correo ajeno), tools/capturas_vscode.py (arma un proyecto de ejemplo en carpeta temporal con una persona ficticia, corre VS Code real bajo Xvfb y regenera site/img/vscode-*.png y los ejemplos), site/img/*.png (4 capturas), secciones nuevas en site/desde-cero.html (#vscode) y site/colaboracion.html (#vscode-equipo) y estilos al final de site/style.css; pruebas nuevas en tests/test_web_vscode.py (wv1–wv3). Declaro tests existentes modificados: tests/test_web.py (comandos_nombrados quita la puntuación pegada al subcomando: «oracle-factory hooks).» aparecía como subcomando «hooks).» en la salida real mostrada), tests/test_site.cjs (la guía desde cero pasa de 10 a 11 secciones) y tests/datos/guias-texto.json (regenerado con `node tests/texto_guias.cjs`: sólo se agregaron líneas, ninguna quitada). La spec está en openspec/changes/20261104-115430-dnr-vscode. Buscá errores reales y de impacto práctico: filtración de rutas, correos o cuentas reales en capturas, ejemplos, script o páginas; que el comprobador deje pasar una captura o un ejemplo roto; que el script de capturas falle o deje procesos o archivos sueltos; accesibilidad de las imágenes (alt, tamaño) y de los bloques de salida; el cambio en comandos_nombrados (¿debilita la comprobación?). Marcá los exóticos y decí con claridad si no queda nada de impacto práctico. Clasificá por severidad.
