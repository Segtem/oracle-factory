Sos un revisor independiente del cambio 20261106-002754-jzt-paginas de un proyecto que usa Oracle Factory: «Web: un menú, un orden de lectura y toda la documentación». No escribiste este código.
NO edites el checkout, no hagas commits ni decidas nada por la persona: tu trabajo es encontrar defectos y contarlos con evidencia.

Qué tiene que hacer el cambio:
- Propuesta: /home/workstation/Dev/factory-web-paginas/openspec/changes/20261106-002754-jzt-paginas/proposal.md
- Spec (lo que se promete, con sus escenarios): /home/workstation/Dev/factory-web-paginas/openspec/changes/20261106-002754-jzt-paginas/specs/web/spec.md

Qué revisar:
- Checkout del candidato f0d7a17 (sólo lectura): /home/workstation/Dev/factory-web-paginas/.factory/local/revisiones/f0d7a17-codex-1
- Paquete de Oracle Clue con el diff y el contexto: /home/workstation/Dev/factory-web-paginas/.factory/cambios/20261106-002754-jzt-paginas/candidatos/f0d7a17/clue/paquete-codex-1.json

Vueltas anteriores de este cambio (ya corregidas; mirá que sigan cerradas y que no haya regresiones):
- .factory/cambios/20261106-002754-jzt-paginas/candidatos/e8a6907/revision/codex-1.json
- .factory/cambios/20261106-002754-jzt-paginas/candidatos/c2a421f/revision/codex-1.json
- .factory/cambios/20261106-002754-jzt-paginas/candidatos/72e0999/revision/codex-1.json
Tests existentes que este candidato modificó o borró (la guarda del proyecto: un test que ya existía no se edita para que pase sin dejarlo dicho). Mirá si cada edición está justificada por el cambio y mencionalo en tu informe, aunque la encuentres legítima:
- tests/datos/guias-texto.json, modificado: 3 línea(s) quitada(s)
Fuera del paquete, porque no son producto (.factory, kb/README.md, kb/cambios/20261106-002754-jzt-paginas.md, kb/requisitos/web_c3777bed32379e332.cada_pagina_lleva_a_la_siguiente.md, kb/requisitos/web_c3777bed32379e332.el_menu_es_el_mismo_en_todas_las_paginas.md, kb/requisitos/web_c3777bed32379e332.el_sitio_se_usa_en_pantalla_chica.md, kb/requisitos/web_c3777bed32379e332.toda_la_documentacion_esta_en_la_web.md, tareas): 26 archivos de registros y evidencia de Factory; no los revises.

Cómo trabajar: leé la spec y el diff; contrastá cada promesa con el código y con las pruebas; buscá casos que fallen, afirmaciones que el
código no cumple y pruebas que no prueban lo que dicen. Si podés, hacé mutaciones a mano sobre copias en tu carpeta y decí cuáles sobreviven.
Mandá la salida larga a archivos de tu carpeta y leé sólo el resumen.

Entregable: un informe JSON en /home/workstation/Dev/factory-web-paginas/.factory/local/revisores/f0d7a17-codex-1/informe.json con este formato (schema oracle-clue.review/v1):
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
  oracle-clue validar /home/workstation/Dev/factory-web-paginas/.factory/local/revisores/f0d7a17-codex-1/informe.json --paquete /home/workstation/Dev/factory-web-paginas/.factory/cambios/20261106-002754-jzt-paginas/candidatos/f0d7a17/clue/paquete-codex-1.json --repo /home/workstation/Dev/factory-web-paginas/.factory/local/revisiones/f0d7a17-codex-1
y terminá con un resumen corto en español.

Indicaciones de quien pide la revisión:
Ronda 4. La ronda 3 (WPG-005) pidió que cada guía esté en su grupo: ahora el comprobador tiene la tabla GRUPOS. Cerrá la clase: qué más prometen la spec y las páginas (menú, orden de lectura, documentación, pantalla chica) y el comprobador no verifica. Lo que dependa de inyectar a mano HTML raro, marcalo bajo. Declarado: tests/datos/guias-texto.json regenerado (sólo líneas agregadas); ningún test existente editado, sólo una aserción más dentro de un test nuevo de este cambio.
