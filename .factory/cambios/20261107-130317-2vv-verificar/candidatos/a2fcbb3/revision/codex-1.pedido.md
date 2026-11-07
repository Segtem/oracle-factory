Sos un revisor independiente del cambio 20261107-130317-2vv-verificar de un proyecto que usa Oracle Factory: «Verificar para CI: comprobar de solo lectura que los cambios están consistentes». No escribiste este código.
NO edites el checkout, no hagas commits ni decidas nada por la persona: tu trabajo es encontrar defectos y contarlos con evidencia.

Qué tiene que hacer el cambio:
- Propuesta: /home/workstation/Dev/factory-ci-verificar/openspec/changes/20261107-130317-2vv-verificar/proposal.md
- Spec (lo que se promete, con sus escenarios): /home/workstation/Dev/factory-ci-verificar/openspec/changes/20261107-130317-2vv-verificar/specs/ci/spec.md

Qué revisar:
- Checkout del candidato a2fcbb3 (sólo lectura): /home/workstation/Dev/factory-ci-verificar/.factory/local/revisiones/a2fcbb3-codex-1
- Paquete de Oracle Clue con el diff y el contexto: /home/workstation/Dev/factory-ci-verificar/.factory/cambios/20261107-130317-2vv-verificar/candidatos/a2fcbb3/clue/paquete-codex-1.json

Tests existentes que este candidato modificó o borró (la guarda del proyecto: un test que ya existía no se edita para que pase sin dejarlo dicho). Mirá si cada edición está justificada por el cambio y mencionalo en tu informe, aunque la encuentres legítima:
- tests/datos/ayuda-cli.json, modificado: 2 línea(s) quitada(s)
- tests/test_web_paginas.py, modificado: 1 línea(s) quitada(s); 1 aserción(es) quitada(s)
Fuera del paquete, porque no son producto (.factory, kb/README.md, kb/cambios/20261107-130317-2vv-verificar.md, kb/requisitos/ci_c65ac59b63e44085b.hay_un_ejemplo_de_ci_y_de_hook.md, kb/requisitos/ci_c65ac59b63e44085b.un_cambio_cerrado_tiene_la_decision_de_una_persona.md, kb/requisitos/ci_c65ac59b63e44085b.verificar_dice_si_los_cambios_estan_consistentes.md, kb/requisitos/ci_c65ac59b63e44085b.verificar_no_exige_lo_que_otra_maquina_no_tiene.md, kb/requisitos/ci_c65ac59b63e44085b.verificar_solo_lee_y_no_necesita_a_nadie.md, tareas): 9 archivos de registros y evidencia de Factory; no los revises.

Cómo trabajar: leé la spec y el diff; contrastá cada promesa con el código y con las pruebas; buscá casos que fallen, afirmaciones que el
código no cumple y pruebas que no prueban lo que dicen. Si podés, hacé mutaciones a mano sobre copias en tu carpeta y decí cuáles sobreviven.
Mandá la salida larga a archivos de tu carpeta y leé sólo el resumen.

Entregable: un informe JSON en /home/workstation/Dev/factory-ci-verificar/.factory/local/revisores/a2fcbb3-codex-1/informe.json con este formato (schema oracle-clue.review/v1):
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
  oracle-clue validar /home/workstation/Dev/factory-ci-verificar/.factory/local/revisores/a2fcbb3-codex-1/informe.json --paquete /home/workstation/Dev/factory-ci-verificar/.factory/cambios/20261107-130317-2vv-verificar/candidatos/a2fcbb3/clue/paquete-codex-1.json --repo /home/workstation/Dev/factory-ci-verificar/.factory/local/revisiones/a2fcbb3-codex-1
y terminá con un resumen corto en español.

Indicaciones de quien pide la revisión:
Revisá el comando nuevo 'oracle-factory verificar' (oracle_factory/verificar.py, cableado en cli.py y parser.py, docs/ci.md, docs/plantillas/verificar.yml, tests/test_verificar.py). Debe ser de solo lectura y apto para CI: sale 0/1 y --json; comprueba cambios abiertos (spec, medidas, revisión y juicio vigentes, huellas) y cerrados (huellas e informes, cierre por persona salvo modo autónomo; sin compararlos con el producto actual); hechos ausentes avisan, hechos cambiados fallan. Mirá en especial: (1) que 'lo que falta por hacer' (cli.pendientes y medidas_sin_decision) no se cuente como inconsistencia y que lo que invalida sí; (2) el reemplazo temporal de cli.contexto_producto en verificar.datos (¿es seguro? ¿restaura siempre?); (3) casos raros: registro ilegible, cambio abandonado, proyecto sin Git o sin commits, cambios archivados; (4) que no escriba nada. Declaración para quien revisa: tests existentes editados de forma aditiva: tests/datos/ayuda-cli.json (suma el subcomando verificar) y tests/test_web_paginas.py (el conteo de guías de docs pasa de 13 a 14 por la guía nueva ci.md), mas tools/sitio_paginas.py y site/documentacion.html (la guía figura en la web). Pruebas en tests/test_verificar.py (ci1-ci5).
