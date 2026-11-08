Sos un revisor independiente del cambio 20261108-133915-l4v-origen de un proyecto que usa Oracle Factory: «Medir si los hallazgos de la primera ronda se atrapan leyendo la spec». No escribiste este código.
NO edites el checkout, no hagas commits ni decidas nada por la persona: tu trabajo es encontrar defectos y contarlos con evidencia.

Qué tiene que hacer el cambio:
- Propuesta: /home/workstation/Dev/factory-origen-hallazgos/openspec/changes/20261108-133915-l4v-origen/proposal.md
- Spec (lo que se promete, con sus escenarios): /home/workstation/Dev/factory-origen-hallazgos/openspec/changes/20261108-133915-l4v-origen/specs/practicas/spec.md

Qué revisar:
- Checkout del candidato 790face (sólo lectura): /home/workstation/Dev/factory-origen-hallazgos/.factory/local/revisiones/790face-codex-1
- Paquete de Oracle Clue con el diff y el contexto: /home/workstation/Dev/factory-origen-hallazgos/.factory/cambios/20261108-133915-l4v-origen/candidatos/790face/clue/paquete-codex-1.json

Vueltas anteriores de este cambio (ya corregidas; mirá que sigan cerradas y que no haya regresiones):
- .factory/cambios/20261108-133915-l4v-origen/candidatos/aa916ee/revision/codex-1.json
- .factory/cambios/20261108-133915-l4v-origen/candidatos/63cecde/revision/codex-1.json
- .factory/cambios/20261108-133915-l4v-origen/candidatos/065fd88/revision/codex-1.json
Fuera del paquete, porque no son producto (.factory, kb/README.md, kb/cambios/20261108-133915-l4v-origen.md, kb/requisitos/practicas_c10f87e544968d526.la_medicion_reparte_los_hallazgos_de_la_primera_ronda_segun_se_pudieran_ver_en_la_spec.md, kb/requisitos/practicas_c10f87e544968d526.la_salida_dice_la_regla_y_su_limite.md, kb/requisitos/practicas_c10f87e544968d526.una_muestra_permite_comprobar_la_regla.md, tareas): 25 archivos de registros y evidencia de Factory; no los revises.

Cómo trabajar: leé la spec y el diff; contrastá cada promesa con el código y con las pruebas; buscá casos que fallen, afirmaciones que el
código no cumple y pruebas que no prueban lo que dicen. Si podés, hacé mutaciones a mano sobre copias en tu carpeta y decí cuáles sobreviven.
Mandá la salida larga a archivos de tu carpeta y leé sólo el resumen.

Entregable: un informe JSON en /home/workstation/Dev/factory-origen-hallazgos/.factory/local/revisores/790face-codex-1/informe.json con este formato (schema oracle-clue.review/v1):
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
  oracle-clue validar /home/workstation/Dev/factory-origen-hallazgos/.factory/local/revisores/790face-codex-1/informe.json --paquete /home/workstation/Dev/factory-origen-hallazgos/.factory/cambios/20261108-133915-l4v-origen/candidatos/790face/clue/paquete-codex-1.json --repo /home/workstation/Dev/factory-origen-hallazgos/.factory/local/revisiones/790face-codex-1
y terminá con un resumen corto en español.

Indicaciones de quien pide la revisión:
Cuarta ronda de origen. Rondas 1 a 3 fueron una misma clase: un parseo tolerante que daba un falso cero (informe ausente, informe de forma mala, registro malformado, severidad no textual). Cerrada con validación estricta: hallazgo_legible (título de texto y severidad conocida), informe_legible (findings lista de hallazgos legibles), registro_legible (eventos lista de objetos) y una fecha que no es fecha cuenta como registro ilegible. Todo lo ilegible se cuenta en 'cobertura' (candidatos_primera_ronda, sin_informe_legible, informes_ilegibles, registros_ilegibles) y avisa 'la medición está incompleta'. 18 casos propios, 20 mutaciones propias sobre cobertura y validadores, todas detectadas; sin ediciones a pruebas existentes. Datos reales: 148 hallazgos, 45 candidatos, 0 ilegibles de cualquier tipo. Buscá lo que quede de esa clase: 'explanation' no texto (se corta a 600 caracteres), 'eventos' con 'accion' no texto, candidato con identificador no texto o repetido, un informe de otro cambio, nombres de carpeta raros, y una diferencia entre el filtro de fecha y la cobertura. Si encontrás algo, decí si es de la misma clase para cerrarla entera de una vez.
