Sos un revisor independiente del cambio 20261104-033615-oj8-publicada-a17 de un proyecto que usa Oracle Factory: «Declarar publicada la 0.1.0a17». No escribiste este código.
NO edites el checkout, no hagas commits ni decidas nada por la persona: tu trabajo es encontrar defectos y contarlos con evidencia.

Qué tiene que hacer el cambio:
- Propuesta: /home/workstation/Dev/factory-publicada-a17/openspec/changes/20261104-033615-oj8-publicada-a17/proposal.md
- Spec (lo que se promete, con sus escenarios): /home/workstation/Dev/factory-publicada-a17/openspec/changes/20261104-033615-oj8-publicada-a17/specs/distribucion/spec.md

Qué revisar:
- Checkout del candidato d77b0cf (sólo lectura): /home/workstation/Dev/factory-publicada-a17/.factory/local/revisiones/d77b0cf-agy2-flash-1
- Paquete de Oracle Clue con el diff y el contexto: /home/workstation/Dev/factory-publicada-a17/.factory/cambios/20261104-033615-oj8-publicada-a17/candidatos/d77b0cf/clue/paquete-agy2-flash-1.json

Vueltas anteriores de este cambio (ya corregidas; mirá que sigan cerradas y que no haya regresiones):
- .factory/cambios/20261104-033615-oj8-publicada-a17/candidatos/f4a711e/revision/codex-1.json
- .factory/cambios/20261104-033615-oj8-publicada-a17/candidatos/bdb910d/revision/agy2-flash-1.json
- .factory/cambios/20261104-033615-oj8-publicada-a17/candidatos/bdb910d/revision/codex-1.json
Tests existentes que este candidato modificó o borró (la guarda del proyecto: un test que ya existía no se edita para que pase sin dejarlo dicho). Mirá si cada edición está justificada por el cambio y mencionalo en tu informe, aunque la encuentres legítima:
- tests/datos/guias-texto.json, modificado: 3 línea(s) quitada(s)
- tests/test_docs.py, modificado: 3 línea(s) quitada(s)
- tests/test_entrega_a17.py, modificado: 5 línea(s) quitada(s); tests quitados: test_ea1_los_textos_y_la_web_estan_al_dia_y_la_a16_figura_publicada_y_la_a17_en_preparacion; 4 aserción(es) quitada(s)
Fuera del paquete, porque no son producto (.factory, kb/README.md, kb/cambios/20261104-033615-oj8-publicada-a17.md, kb/requisitos/distribucion_c0fb4528d614ab5c0.los_textos_declaran_publicada_la_version_a17.md, kb/requisitos/distribucion_c0fb4528d614ab5c0.se_detecta_lo_que_siga_llamando_candidata_a_la_version_a17.md, tareas): 20 archivos de registros y evidencia de Factory; no los revises.

Cómo trabajar: leé la spec y el diff; contrastá cada promesa con el código y con las pruebas; buscá casos que fallen, afirmaciones que el
código no cumple y pruebas que no prueban lo que dicen. Si podés, hacé mutaciones a mano sobre copias en tu carpeta y decí cuáles sobreviven.
Mandá la salida larga a archivos de tu carpeta y leé sólo el resumen.

Entregable: un informe JSON en /home/workstation/Dev/factory-publicada-a17/.factory/local/revisores/d77b0cf-agy2-flash-1/informe.json con este formato (schema oracle-clue.review/v1):
- schema_version "oracle-clue.review/v1"; repo, base, head, diff_sha256 y context_sha256 copiados del paquete;
- provider {"name": "agy", "model": "gemini-3.8-flash-high"};
- findings: lista de hallazgos, cada uno con id, kind, severity (alta|media|baja|informativa), confidence (0 a 1), title, explanation,
  location {file, start_line, end_line, side: "head"} DENTRO de los rangos del diff del paquete, trigger, evidence, related_requirement,
  status "pendiente" y verification;
- review_status ("completo" o "incompleto") y limitations (qué corriste y qué no).
Sin hallazgos: findings vacía, explicado en limitations. Validalo antes de terminar con:
  oracle-clue validar /home/workstation/Dev/factory-publicada-a17/.factory/local/revisores/d77b0cf-agy2-flash-1/informe.json --paquete /home/workstation/Dev/factory-publicada-a17/.factory/cambios/20261104-033615-oj8-publicada-a17/candidatos/d77b0cf/clue/paquete-agy2-flash-1.json --repo /home/workstation/Dev/factory-publicada-a17/.factory/local/revisiones/d77b0cf-agy2-flash-1
y terminá con un resumen corto en español.

Indicaciones de quien pide la revisión:
No cambies la configuración de git de ningún repositorio. Es la tercera ronda de publicada-a17 (la 0.1.0a17 ya está publicada en PyPI, con tag y release; el cambio pasa textos de «en preparación» a «publicada» y mejora la regla que detecta lo que siga llamándola candidata). Ronda 1: PA17-001 (media, codex) «Esta versión candidata es la 0.1.0a17» no se detectaba → agregué la forma `versión candidata … <v>`. Ronda 2: PA17-002 (media, codex) «La candidata a versión 0.1.0a17 está lista» no se detectaba → agregué la forma `candidata a [ser|publicar] [la|el] [versión] <v>`, que cierra la familia «candidata a …». Decisión de diseño declarada: el pasado («fue/era candidata») NO se marca porque es historia legítima una vez publicada; «el candidato de la versión X que se revisó fue el ca6a267» y «candidato a revisar de la versión X» tampoco (son el candidato de una revisión). Cada forma tiene frases positivas y legítimas en tests/test_publicada_a17.py y mutaciones detectadas (sacar la forma; volverla permisiva). Declaro: tools/docs_al_dia.py suma dos líneas de patrón (no es código de oracle_factory/); no hay tests existentes nuevos modificados (siguen test_docs.py —frases de versión del README— y test_entrega_a17.py —aserción ea1 de estado—). Para no seguir descubriendo una forma por ronda: intentá generar activamente otras construcciones corrientes en español con «candidat[oa]», «preparación», «próxima versión», «pre-lanzamiento», «aún no publicada» junto a la versión 0.1.0a17 y probalas contra `docs_al_dia.patron_preparacion('0.1.0a17')`; informá sólo las que un texto real del README, docs/ o site/ podría contener, y los falsos positivos sobre los textos actuales. Decí con claridad si no queda nada de impacto práctico. Clasificá por severidad.
