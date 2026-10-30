Sos un revisor independiente del cambio 20261030-171836-7e4-publicadaa16 de un proyecto que usa Oracle Factory: «Declarar publicada la 0.1.0a16 en las notas y los textos». No escribiste este código.
NO edites el checkout, no hagas commits ni decidas nada por la persona: tu trabajo es encontrar defectos y contarlos con evidencia.

Qué tiene que hacer el cambio:
- Propuesta: /home/workstation/Dev/factory-publicada-a16/openspec/changes/20261030-171836-7e4-publicadaa16/proposal.md
- Spec (lo que se promete, con sus escenarios): /home/workstation/Dev/factory-publicada-a16/openspec/changes/20261030-171836-7e4-publicadaa16/specs/distribucion/spec.md

Qué revisar:
- Checkout del candidato 6416c61 (sólo lectura): /home/workstation/Dev/factory-publicada-a16/.factory/local/revisiones/6416c61-agy2-1
- Paquete de Oracle Clue con el diff y el contexto: /home/workstation/Dev/factory-publicada-a16/.factory/cambios/20261030-171836-7e4-publicadaa16/candidatos/6416c61/clue/paquete-agy2-1.json

Fuera del paquete, porque no son producto (.factory, kb/README.md, kb/cambios/20261030-171836-7e4-publicadaa16.md, kb/requisitos/distribucion_ca0259b11065d4ec5.los_textos_declaran_publicada_la_version_a16_publicada.md, kb/requisitos/distribucion_ca0259b11065d4ec5.un_texto_en_preparacion_de_la_version_a16_publicada_se_detecta.md, tareas): 6 archivos de registros y evidencia de Factory; no los revises.

Cómo trabajar: leé la spec y el diff; contrastá cada promesa con el código y con las pruebas; buscá casos que fallen, afirmaciones que el
código no cumple y pruebas que no prueban lo que dicen. Si podés, hacé mutaciones a mano sobre copias en tu carpeta y decí cuáles sobreviven.
Mandá la salida larga a archivos de tu carpeta y leé sólo el resumen.

Entregable: un informe JSON en /home/workstation/Dev/factory-publicada-a16/.factory/local/revisores/6416c61-agy2-1/informe.json con este formato (schema oracle-clue.review/v1):
- schema_version "oracle-clue.review/v1"; repo, base, head, diff_sha256 y context_sha256 copiados del paquete;
- provider {"name": "agy", "model": "gemini-3.8-flash-high"};
- findings: lista de hallazgos, cada uno con id, kind, severity (alta|media|baja|informativa), confidence (0 a 1), title, explanation,
  location {file, start_line, end_line, side: "head"} DENTRO de los rangos del diff del paquete, trigger, evidence, related_requirement,
  status "pendiente" y verification;
- review_status ("completo" o "incompleto") y limitations (qué corriste y qué no).
Sin hallazgos: findings vacía, explicado en limitations. Validalo antes de terminar con:
  oracle-clue validar /home/workstation/Dev/factory-publicada-a16/.factory/local/revisores/6416c61-agy2-1/informe.json --paquete /home/workstation/Dev/factory-publicada-a16/.factory/cambios/20261030-171836-7e4-publicadaa16/candidatos/6416c61/clue/paquete-agy2-1.json --repo /home/workstation/Dev/factory-publicada-a16/.factory/local/revisiones/6416c61-agy2-1
y terminá con un resumen corto en español.

Indicaciones de quien pide la revisión:
No cambies la configuración de git de ningún repositorio. Revisá el cambio publicada-a16: los textos que declaran publicada la 0.1.0a16 (NOTAS-DE-RELEASE.md, README.md, docs/colaboracion.md, site/, tests/datos/guias-texto.json), las pruebas tests/test_publicada_a16.py y tests/test_entrega_a16.py (parte de estado publicado y de uv.lock), tools/verify_publicada_a16.py y los catálogos. Buscá errores reales: afirmaciones de publicación sin respaldo, textos que sigan diciendo en preparación, historia anterior alterada, pruebas que pasen por construcción; clasificá por severidad.
