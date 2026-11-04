Sos un revisor independiente del cambio 20261104-033615-oj8-publicada-a17 de un proyecto que usa Oracle Factory: «Declarar publicada la 0.1.0a17». No escribiste este código.
NO edites el checkout, no hagas commits ni decidas nada por la persona: tu trabajo es encontrar defectos y contarlos con evidencia.

Qué tiene que hacer el cambio:
- Propuesta: /home/workstation/Dev/factory-publicada-a17/openspec/changes/20261104-033615-oj8-publicada-a17/proposal.md
- Spec (lo que se promete, con sus escenarios): /home/workstation/Dev/factory-publicada-a17/openspec/changes/20261104-033615-oj8-publicada-a17/specs/distribucion/spec.md

Qué revisar:
- Checkout del candidato bdb910d (sólo lectura): /home/workstation/Dev/factory-publicada-a17/.factory/local/revisiones/bdb910d-codex-1
- Paquete de Oracle Clue con el diff y el contexto: /home/workstation/Dev/factory-publicada-a17/.factory/cambios/20261104-033615-oj8-publicada-a17/candidatos/bdb910d/clue/paquete-codex-1.json

Vueltas anteriores de este cambio (ya corregidas; mirá que sigan cerradas y que no haya regresiones):
- .factory/cambios/20261104-033615-oj8-publicada-a17/candidatos/f4a711e/revision/codex-1.json
Tests existentes que este candidato modificó o borró (la guarda del proyecto: un test que ya existía no se edita para que pase sin dejarlo dicho). Mirá si cada edición está justificada por el cambio y mencionalo en tu informe, aunque la encuentres legítima:
- tests/datos/guias-texto.json, modificado: 3 línea(s) quitada(s)
- tests/test_docs.py, modificado: 3 línea(s) quitada(s)
- tests/test_entrega_a17.py, modificado: 5 línea(s) quitada(s); tests quitados: test_ea1_los_textos_y_la_web_estan_al_dia_y_la_a16_figura_publicada_y_la_a17_en_preparacion; 4 aserción(es) quitada(s)
Fuera del paquete, porque no son producto (.factory, kb/README.md, kb/cambios/20261104-033615-oj8-publicada-a17.md, kb/requisitos/distribucion_c0fb4528d614ab5c0.los_textos_declaran_publicada_la_version_a17.md, kb/requisitos/distribucion_c0fb4528d614ab5c0.se_detecta_lo_que_siga_llamando_candidata_a_la_version_a17.md, tareas): 12 archivos de registros y evidencia de Factory; no los revises.

Cómo trabajar: leé la spec y el diff; contrastá cada promesa con el código y con las pruebas; buscá casos que fallen, afirmaciones que el
código no cumple y pruebas que no prueban lo que dicen. Si podés, hacé mutaciones a mano sobre copias en tu carpeta y decí cuáles sobreviven.
Mandá la salida larga a archivos de tu carpeta y leé sólo el resumen.

Entregable: un informe JSON en /home/workstation/Dev/factory-publicada-a17/.factory/local/revisores/bdb910d-codex-1/informe.json con este formato (schema oracle-clue.review/v1):
- schema_version "oracle-clue.review/v1"; repo, base, head, diff_sha256 y context_sha256 copiados del paquete;
- provider {"name": "codex", "model": "gpt-6-luna"};
- findings: lista de hallazgos, cada uno con id, kind, severity (alta|media|baja|informativa), confidence (0 a 1), title, explanation,
  location {file, start_line, end_line, side: "head"} DENTRO de los rangos del diff del paquete, trigger, evidence, related_requirement,
  status "pendiente" y verification;
- review_status ("completo" o "incompleto") y limitations (qué corriste y qué no).
Sin hallazgos: findings vacía, explicado en limitations. Validalo antes de terminar con:
  oracle-clue validar /home/workstation/Dev/factory-publicada-a17/.factory/local/revisores/bdb910d-codex-1/informe.json --paquete /home/workstation/Dev/factory-publicada-a17/.factory/cambios/20261104-033615-oj8-publicada-a17/candidatos/bdb910d/clue/paquete-codex-1.json --repo /home/workstation/Dev/factory-publicada-a17/.factory/local/revisiones/bdb910d-codex-1
y terminá con un resumen corto en español.

Indicaciones de quien pide la revisión:
No cambies la configuración de git de ningún repositorio. Es la segunda ronda de publicada-a17 (la 0.1.0a17 ya está publicada en PyPI, con tag y release; el cambio sólo pasa textos de «en preparación» a «publicada»). La primera trajo 1 hallazgo medio de codex (PA17-001): tools/docs_al_dia.py no detectaba la forma «Esta versión candidata es la 0.1.0a17». Lo arreglé con una forma nueva en patron_preparacion (`versión candidata ... <versión>` en la misma frase, sin confundir «el candidato ca6a267 de la versión 0.1.0a17», que sigue sin ser divergencia), con frases positivas y legítimas nuevas en tests/test_publicada_a17.py y dos mutaciones detectadas (sacar la forma; volverla permisiva `candidat[oa]...versión`). Declaro: tools/docs_al_dia.py cambió una línea (agrega esa forma; no es código de producto de oracle_factory/); tests existentes modificados desde la ronda 1: ninguno nuevo (siguen test_docs.py —sólo frases de versión del README— y test_entrega_a17.py —aserción ea1 de estado—). Verificá que el arreglo cubre la CLASE entera (otras formas corrientes de llamar candidata o en preparación a una versión que el patrón no vea; falsos positivos en textos reales de README, docs/ y site/) y buscá errores reales y de impacto práctico; marcá los exóticos y decí con claridad si no queda nada de impacto práctico. Clasificá por severidad.
