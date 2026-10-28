Sos un revisor independiente del cambio 20261028-143519-qhd-publicadaa15 de un proyecto que usa Oracle Factory: «Declarar publicada la 0.1.0a15 en las notas y los textos». No escribiste este código.
NO edites el checkout, no hagas commits ni decidas nada por la persona: tu trabajo es encontrar defectos y contarlos con evidencia.

Qué tiene que hacer el cambio:
- Propuesta: /home/workstation/Dev/factory-publicada-a15/openspec/changes/20261028-143519-qhd-publicadaa15/proposal.md
- Spec (lo que se promete, con sus escenarios): /home/workstation/Dev/factory-publicada-a15/openspec/changes/20261028-143519-qhd-publicadaa15/specs/distribucion/spec.md

Qué revisar:
- Checkout del candidato 9876790 (sólo lectura): /home/workstation/Dev/factory-publicada-a15/.factory/local/revisiones/9876790-agy-1
- Paquete de Oracle Clue con el diff y el contexto: /home/workstation/Dev/factory-publicada-a15/.factory/cambios/20261028-143519-qhd-publicadaa15/candidatos/9876790/clue/paquete-agy-1.json

Vueltas anteriores de este cambio (ya corregidas; mirá que sigan cerradas y que no haya regresiones):
- .factory/cambios/20261028-143519-qhd-publicadaa15/candidatos/ca6a267/revision/agy-1.json
- .factory/cambios/20261028-143519-qhd-publicadaa15/candidatos/ca6a267/revision/agy2-1.json
Fuera del paquete, porque no son producto (.factory, kb/README.md, kb/cambios/20261028-143519-qhd-publicadaa15.md, kb/requisitos/distribucion_c9b5b7b98ede93100.los_textos_declaran_publicada_la_version_publicada.md, kb/requisitos/distribucion_c9b5b7b98ede93100.un_texto_en_preparacion_de_una_version_publicada_se_detecta.md, tareas): 15 archivos de registros y evidencia de Factory; no los revises.

Cómo trabajar: leé la spec y el diff; contrastá cada promesa con el código y con las pruebas; buscá casos que fallen, afirmaciones que el
código no cumple y pruebas que no prueban lo que dicen. Si podés, hacé mutaciones a mano sobre copias en tu carpeta y decí cuáles sobreviven.
Mandá la salida larga a archivos de tu carpeta y leé sólo el resumen.

Entregable: un informe JSON en /home/workstation/Dev/factory-publicada-a15/.factory/local/revisores/9876790-agy-1/informe.json con este formato (schema oracle-clue.review/v1):
- schema_version "oracle-clue.review/v1"; repo, base, head, diff_sha256 y context_sha256 copiados del paquete;
- provider {"name": "agy", "model": "gemini-3.8-flash-high"};
- findings: lista de hallazgos, cada uno con id, kind, severity (alta|media|baja|informativa), confidence (0 a 1), title, explanation,
  location {file, start_line, end_line, side: "head"} DENTRO de los rangos del diff del paquete, trigger, evidence, related_requirement,
  status "pendiente" y verification;
- review_status ("completo" o "incompleto") y limitations (qué corriste y qué no).
Sin hallazgos: findings vacía, explicado en limitations. Validalo antes de terminar con:
  oracle-clue validar /home/workstation/Dev/factory-publicada-a15/.factory/local/revisores/9876790-agy-1/informe.json --paquete /home/workstation/Dev/factory-publicada-a15/.factory/cambios/20261028-143519-qhd-publicadaa15/candidatos/9876790/clue/paquete-agy-1.json --repo /home/workstation/Dev/factory-publicada-a15/.factory/local/revisiones/9876790-agy-1
y terminá con un resumen corto en español.

Indicaciones de quien pide la revisión:
Vuelta 2: se corrigieron los hallazgos de la vuelta 1 en tools/docs_al_dia.py: patron_preparacion ahora exige la versión en la misma frase (sin confundir el «candidato» de una revisión ni un «estado de preparación» genérico), detecta «0.1.0a15 en preparación» sin paréntesis, «está en preparación», «en preparación: 0.1.0a15» y «cuando se publique la 0.1.0a15»; tests/test_publicada_a15.py tiene frases legítimas e ilegítimas, con límites de distancia y de frase. Cada una de las 9 formas de la regla hace fallar una prueba si se quita. Revisá el cambio contra los requisitos de su spec (openspec/changes/20261028-143519-qhd-publicadaa15/specs/distribucion/spec.md): NOTAS-DE-RELEASE.md (sólo la sección de 0.1.0a15), README.md, docs/colaboracion.md, site/desde-cero.html, site/index.html, tests/datos/guias-texto.json, tools/docs_al_dia.py (preparacion_olvidada y su llamada), tests/test_publicada_a15.py, los cambios en tests/test_entrega_a15.py, tests/test_docs.py y tools/mutar_entrega_a15.py, tools/verify_publicada_a15.py y catalogos/factory_publicada_a15.*.oracle. Mirá especialmente: que cada afirmación sobre la 0.1.0a15 sea verdadera (está publicada en PyPI con wheel y sdist, tiene el tag v0.1.0a15 y una release de GitHub marcada como pre-release; podés verificarlo en https://pypi.org/pypi/oracle-factory/json y con gh si lo tenés), que ningún texto de README, docs o web siga hablando de la 0.1.0a15 como candidata o en preparación, que la regla nueva no dé falsos positivos con la palabra «candidato» en otros sentidos (candidato de revisión) ni falsos negativos con otras formas de decir lo mismo, que las dos reglas (publicación prematura y preparación olvidada) no se contradigan, que la historia de versiones anteriores no cambie y que las pruebas fallen de verdad si se rompe el comportamiento. Para correr pruebas usá exactamente, en primer plano y desde la raíz del checkout: PYTHONPATH=. $PWD/.venv/bin/python -m unittest tests.test_publicada_a15 tests.test_docs tests.test_entrega_a15.EntregaA15.test_ea1_version_coherente_y_estado_declarado </dev/null . No corras la suite completa. No cambies la configuración de git de ningún repositorio. Nombrá archivos con rutas relativas.
