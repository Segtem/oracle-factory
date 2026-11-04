Sos un revisor independiente del cambio 20261104-033615-oj8-publicada-a17 de un proyecto que usa Oracle Factory: «Declarar publicada la 0.1.0a17». No escribiste este código.
NO edites el checkout, no hagas commits ni decidas nada por la persona: tu trabajo es encontrar defectos y contarlos con evidencia.

Qué tiene que hacer el cambio:
- Propuesta: /home/workstation/Dev/factory-publicada-a17/openspec/changes/20261104-033615-oj8-publicada-a17/proposal.md
- Spec (lo que se promete, con sus escenarios): /home/workstation/Dev/factory-publicada-a17/openspec/changes/20261104-033615-oj8-publicada-a17/specs/distribucion/spec.md

Qué revisar:
- Checkout del candidato f4a711e (sólo lectura): /home/workstation/Dev/factory-publicada-a17/.factory/local/revisiones/f4a711e-codex-1
- Paquete de Oracle Clue con el diff y el contexto: /home/workstation/Dev/factory-publicada-a17/.factory/cambios/20261104-033615-oj8-publicada-a17/candidatos/f4a711e/clue/paquete-codex-1.json

Tests existentes que este candidato modificó o borró (la guarda del proyecto: un test que ya existía no se edita para que pase sin dejarlo dicho). Mirá si cada edición está justificada por el cambio y mencionalo en tu informe, aunque la encuentres legítima:
- tests/datos/guias-texto.json, modificado: 3 línea(s) quitada(s)
- tests/test_docs.py, modificado: 3 línea(s) quitada(s)
- tests/test_entrega_a17.py, modificado: 5 línea(s) quitada(s); tests quitados: test_ea1_los_textos_y_la_web_estan_al_dia_y_la_a16_figura_publicada_y_la_a17_en_preparacion; 4 aserción(es) quitada(s)
Fuera del paquete, porque no son producto (.factory, kb/README.md, kb/cambios/20261104-033615-oj8-publicada-a17.md, kb/requisitos/distribucion_c0fb4528d614ab5c0.los_textos_declaran_publicada_la_version_a17.md, kb/requisitos/distribucion_c0fb4528d614ab5c0.se_detecta_lo_que_siga_llamando_candidata_a_la_version_a17.md, tareas): 6 archivos de registros y evidencia de Factory; no los revises.

Cómo trabajar: leé la spec y el diff; contrastá cada promesa con el código y con las pruebas; buscá casos que fallen, afirmaciones que el
código no cumple y pruebas que no prueban lo que dicen. Si podés, hacé mutaciones a mano sobre copias en tu carpeta y decí cuáles sobreviven.
Mandá la salida larga a archivos de tu carpeta y leé sólo el resumen.

Entregable: un informe JSON en /home/workstation/Dev/factory-publicada-a17/.factory/local/revisores/f4a711e-codex-1/informe.json con este formato (schema oracle-clue.review/v1):
- schema_version "oracle-clue.review/v1"; repo, base, head, diff_sha256 y context_sha256 copiados del paquete;
- provider {"name": "codex", "model": "gpt-6-luna"};
- findings: lista de hallazgos, cada uno con id, kind, severity (alta|media|baja|informativa), confidence (0 a 1), title, explanation,
  location {file, start_line, end_line, side: "head"} DENTRO de los rangos del diff del paquete, trigger, evidence, related_requirement,
  status "pendiente" y verification;
- review_status ("completo" o "incompleto") y limitations (qué corriste y qué no).
Sin hallazgos: findings vacía, explicado en limitations. Validalo antes de terminar con:
  oracle-clue validar /home/workstation/Dev/factory-publicada-a17/.factory/local/revisores/f4a711e-codex-1/informe.json --paquete /home/workstation/Dev/factory-publicada-a17/.factory/cambios/20261104-033615-oj8-publicada-a17/candidatos/f4a711e/clue/paquete-codex-1.json --repo /home/workstation/Dev/factory-publicada-a17/.factory/local/revisiones/f4a711e-codex-1
y terminá con un resumen corto en español.

Indicaciones de quien pide la revisión:
No cambies la configuración de git de ningún repositorio. Es la primera ronda de publicada-a17: la 0.1.0a17 ya está publicada en PyPI (hashes del wheel y del sdist idénticos a los construidos desde main), con tag v0.1.0a17 y pre-release en GitHub; este cambio sólo pasa los textos de «en preparación» a «publicada» (NOTAS-DE-RELEASE.md, README.md, docs/colaboracion.md, site/desde-cero.html, site/index.html, tests/datos/guias-texto.json regenerado con `node tests/texto_guias.cjs`: sólo cambian 3 líneas). No hay código de producto. Declaro tests existentes modificados: tests/test_docs.py (sólo las frases de versión del README: «Versión publicada en PyPI: `oracle-factory==...`.» en lugar de «Candidato en preparación ...,») y tests/test_entrega_a17.py (la aserción ea1 de estado pasó de «a17 en preparación» a «a16 y a17 publicadas»; el estado de cada versión lo fija ahora tests/test_publicada_a17.py, nuevo, adaptado de test_publicada_a16.py). Buscá errores reales y de impacto práctico: textos que sigan llamando candidata o en preparación a la a17 (también en site/modos.html, site/colaboracion.html y docs/), afirmaciones falsas en la línea «Publicada» de las notas (¿es verdad lo que dice del tag, la release y los hashes?), el orden y la conservación de las notas anteriores, y si las pruebas nuevas fallan cuando se rompe lo que vigilan. Marcá los exóticos y decí con claridad si no queda nada de impacto práctico. Clasificá por severidad.
