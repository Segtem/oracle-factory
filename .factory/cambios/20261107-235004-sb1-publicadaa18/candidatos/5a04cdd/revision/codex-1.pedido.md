Sos un revisor independiente del cambio 20261107-235004-sb1-publicadaa18 de un proyecto que usa Oracle Factory: «Declarar publicada la 0.1.0a18». No escribiste este código.
NO edites el checkout, no hagas commits ni decidas nada por la persona: tu trabajo es encontrar defectos y contarlos con evidencia.

Qué tiene que hacer el cambio:
- Propuesta: /home/workstation/Dev/factory-publicada-a18/openspec/changes/20261107-235004-sb1-publicadaa18/proposal.md
- Spec (lo que se promete, con sus escenarios): /home/workstation/Dev/factory-publicada-a18/openspec/changes/20261107-235004-sb1-publicadaa18/specs/distribucion/spec.md

Qué revisar:
- Checkout del candidato 5a04cdd (sólo lectura): /home/workstation/Dev/factory-publicada-a18/.factory/local/revisiones/5a04cdd-codex-1
- Paquete de Oracle Clue con el diff y el contexto: /home/workstation/Dev/factory-publicada-a18/.factory/cambios/20261107-235004-sb1-publicadaa18/candidatos/5a04cdd/clue/paquete-codex-1.json

Tests existentes que este candidato modificó o borró (la guarda del proyecto: un test que ya existía no se edita para que pase sin dejarlo dicho). Mirá si cada edición está justificada por el cambio y mencionalo en tu informe, aunque la encuentres legítima:
- tests/datos/guias-texto.json, modificado: 3 línea(s) quitada(s)
- tests/test_docs.py, modificado: 3 línea(s) quitada(s)
- tests/test_entrega_a18.py, modificado: 5 línea(s) quitada(s); tests quitados: test_ea1_los_textos_y_la_web_estan_al_dia_la_a17_figura_publicada_y_la_a18_preparada; 4 aserción(es) quitada(s)
Fuera del paquete, porque no son producto (.factory, kb/README.md, kb/cambios/20261107-235004-sb1-publicadaa18.md, kb/requisitos/distribucion_ce1b0aba1db172723.los_textos_declaran_publicada_la_version_a18.md, kb/requisitos/distribucion_ce1b0aba1db172723.se_detecta_lo_que_siga_llamando_candidata_a_la_version_a18.md, tareas): 6 archivos de registros y evidencia de Factory; no los revises.

Cómo trabajar: leé la spec y el diff; contrastá cada promesa con el código y con las pruebas; buscá casos que fallen, afirmaciones que el
código no cumple y pruebas que no prueban lo que dicen. Si podés, hacé mutaciones a mano sobre copias en tu carpeta y decí cuáles sobreviven.
Mandá la salida larga a archivos de tu carpeta y leé sólo el resumen.

Entregable: un informe JSON en /home/workstation/Dev/factory-publicada-a18/.factory/local/revisores/5a04cdd-codex-1/informe.json con este formato (schema oracle-clue.review/v1):
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
  oracle-clue validar /home/workstation/Dev/factory-publicada-a18/.factory/local/revisores/5a04cdd-codex-1/informe.json --paquete /home/workstation/Dev/factory-publicada-a18/.factory/cambios/20261107-235004-sb1-publicadaa18/candidatos/5a04cdd/clue/paquete-codex-1.json --repo /home/workstation/Dev/factory-publicada-a18/.factory/local/revisiones/5a04cdd-codex-1
y terminá con un resumen corto en español.

Indicaciones de quien pide la revisión:
Revisá que los textos (NOTAS-DE-RELEASE.md, README.md, docs/colaboracion.md, site/desde-cero.html, site/index.html, tests/datos/guias-texto.json) declaren publicada la 0.1.0a18 sin llamarla candidata ni en preparación, que la línea Publicada de las notas sea verdadera (PyPI e instalación verificados, hashes del release: wheel e2d0ed02…, sdist 7f2f62fa…) y que las pruebas nuevas/editadas (test_publicada_a18, test_entrega_a18, test_docs) no hayan perdido fuerza respecto a las de la a17. No hay código de producto.
