Sos un revisor independiente del cambio 20261108-133915-l4v-origen de un proyecto que usa Oracle Factory: «Medir si los hallazgos de la primera ronda se atrapan leyendo la spec». No escribiste este código.
NO edites el checkout, no hagas commits ni decidas nada por la persona: tu trabajo es encontrar defectos y contarlos con evidencia.

Qué tiene que hacer el cambio:
- Propuesta: /home/workstation/Dev/factory-origen-hallazgos/openspec/changes/20261108-133915-l4v-origen/proposal.md
- Spec (lo que se promete, con sus escenarios): /home/workstation/Dev/factory-origen-hallazgos/openspec/changes/20261108-133915-l4v-origen/specs/practicas/spec.md

Qué revisar:
- Checkout del candidato 065fd88 (sólo lectura): /home/workstation/Dev/factory-origen-hallazgos/.factory/local/revisiones/065fd88-codex-1
- Paquete de Oracle Clue con el diff y el contexto: /home/workstation/Dev/factory-origen-hallazgos/.factory/cambios/20261108-133915-l4v-origen/candidatos/065fd88/clue/paquete-codex-1.json

Vueltas anteriores de este cambio (ya corregidas; mirá que sigan cerradas y que no haya regresiones):
- .factory/cambios/20261108-133915-l4v-origen/candidatos/aa916ee/revision/codex-1.json
- .factory/cambios/20261108-133915-l4v-origen/candidatos/63cecde/revision/codex-1.json
Fuera del paquete, porque no son producto (.factory, kb/README.md, kb/cambios/20261108-133915-l4v-origen.md, kb/requisitos/practicas_c10f87e544968d526.la_medicion_reparte_los_hallazgos_de_la_primera_ronda_segun_se_pudieran_ver_en_la_spec.md, kb/requisitos/practicas_c10f87e544968d526.la_salida_dice_la_regla_y_su_limite.md, kb/requisitos/practicas_c10f87e544968d526.una_muestra_permite_comprobar_la_regla.md, tareas): 19 archivos de registros y evidencia de Factory; no los revises.

Cómo trabajar: leé la spec y el diff; contrastá cada promesa con el código y con las pruebas; buscá casos que fallen, afirmaciones que el
código no cumple y pruebas que no prueban lo que dicen. Si podés, hacé mutaciones a mano sobre copias en tu carpeta y decí cuáles sobreviven.
Mandá la salida larga a archivos de tu carpeta y leé sólo el resumen.

Entregable: un informe JSON en /home/workstation/Dev/factory-origen-hallazgos/.factory/local/revisores/065fd88-codex-1/informe.json con este formato (schema oracle-clue.review/v1):
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
  oracle-clue validar /home/workstation/Dev/factory-origen-hallazgos/.factory/local/revisores/065fd88-codex-1/informe.json --paquete /home/workstation/Dev/factory-origen-hallazgos/.factory/cambios/20261108-133915-l4v-origen/candidatos/065fd88/clue/paquete-codex-1.json --repo /home/workstation/Dev/factory-origen-hallazgos/.factory/local/revisiones/065fd88-codex-1
y terminá con un resumen corto en español.

Indicaciones de quien pide la revisión:
Tercera ronda de origen. Ronda 1: un falso silencio con informes ausentes o JSON roto (arreglado con 'cobertura'). Ronda 2: la cobertura daba por legible cualquier objeto JSON; ahora informe_legible() exige un objeto con 'findings' lista de objetos (la lista vacía vale) y lo usan la cobertura y la lectura de hallazgos; un informe de forma mala no rompe la medición, se cuenta como ilegible y avisa 'la medición está incompleta'. Pruebas nuevas dentro de tests/test_origen.py (16 casos), 12 mutaciones propias sobre la cobertura y el validador, todas detectadas. Sin ediciones a pruebas existentes. Datos reales: 148 hallazgos, 45 candidatos de primera ronda, 0 sin informe, 0 ilegibles. Buscá otras formas de informe o de registro que den un falso cero o un fallo: el campo 'severity' que no es texto, 'title' no texto, un 'factory.json' con 'eventos' que no es lista, 'candidato' de un evento sin informe, y que un informe de hallazgos sin severidad conocida no cuente como alto o medio. Cerrá la clase entera.
