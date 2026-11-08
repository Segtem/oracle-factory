Sos un revisor independiente del cambio 20261108-115714-ohv-noaplica de un proyecto que usa Oracle Factory: «El verificador respeta «Pruebas: no aplica»». No escribiste este código.
NO edites el checkout, no hagas commits ni decidas nada por la persona: tu trabajo es encontrar defectos y contarlos con evidencia.

Qué tiene que hacer el cambio:
- Propuesta: /home/workstation/Dev/factory-verificar-no-aplica/openspec/changes/20261108-115714-ohv-noaplica/proposal.md
- Spec (lo que se promete, con sus escenarios): /home/workstation/Dev/factory-verificar-no-aplica/openspec/changes/20261108-115714-ohv-noaplica/specs/practicas/spec.md

Qué revisar:
- Checkout del candidato 4673a3b (sólo lectura): /home/workstation/Dev/factory-verificar-no-aplica/.factory/local/revisiones/4673a3b-codex-1
- Paquete de Oracle Clue con el diff y el contexto: /home/workstation/Dev/factory-verificar-no-aplica/.factory/cambios/20261108-115714-ohv-noaplica/candidatos/4673a3b/clue/paquete-codex-1.json

Tests existentes que este candidato modificó o borró (la guarda del proyecto: un test que ya existía no se edita para que pase sin dejarlo dicho). Mirá si cada edición está justificada por el cambio y mencionalo en tu informe, aunque la encuentres legítima:
- tests/test_verificador_generico.py, modificado: 1 línea(s) quitada(s); 1 aserción(es) quitada(s)
Fuera del paquete, porque no son producto (.factory, kb/README.md, kb/cambios/20261108-115714-ohv-noaplica.md, kb/requisitos/practicas_c7e9c76d84c2a7a09.el_verificador_no_pide_casos_para_un_requisito_exceptuado.md, kb/requisitos/practicas_c7e9c76d84c2a7a09.la_evidencia_y_los_catalogos_cuentan_solo_los_requisitos_con_casos.md, kb/requisitos/practicas_c7e9c76d84c2a7a09.una_excepcion_mal_escrita_no_se_ignora.md, tareas): 7 archivos de registros y evidencia de Factory; no los revises.

Cómo trabajar: leé la spec y el diff; contrastá cada promesa con el código y con las pruebas; buscá casos que fallen, afirmaciones que el
código no cumple y pruebas que no prueban lo que dicen. Si podés, hacé mutaciones a mano sobre copias en tu carpeta y decí cuáles sobreviven.
Mandá la salida larga a archivos de tu carpeta y leé sólo el resumen.

Entregable: un informe JSON en /home/workstation/Dev/factory-verificar-no-aplica/.factory/local/revisores/4673a3b-codex-1/informe.json con este formato (schema oracle-clue.review/v1):
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
  oracle-clue validar /home/workstation/Dev/factory-verificar-no-aplica/.factory/local/revisores/4673a3b-codex-1/informe.json --paquete /home/workstation/Dev/factory-verificar-no-aplica/.factory/cambios/20261108-115714-ohv-noaplica/candidatos/4673a3b/clue/paquete-codex-1.json --repo /home/workstation/Dev/factory-verificar-no-aplica/.factory/local/revisiones/4673a3b-codex-1
y terminá con un resumen corto en español.

Indicaciones de quien pide la revisión:
Cambio chico en tools/verificar_cambio.py: el verificador respeta «Pruebas: no aplica — motivo» (usa oracle_factory/pruebas.py como aprobar-spec). Un requisito exceptuado queda fuera del contrato, de los hechos y de los catálogos, pero cuenta en la numeración test_<letras><n>; un caso que lo nombra y una línea «Pruebas:» mal escrita son error. DECLARO: se editó una prueba existente, test_vg1_un_requisito_que_declara_pruebas_no_aplica_… en tests/test_verificador_generico.py: solo cambió la regex sobre docs/tests.md, que fijaba el límite que este cambio levanta. Mutaciones propias: 6, 5 detectadas; la que sobrevive (retorno de contrato con 'if i in casos' en lugar de 'r not in exceptuados') es equivalente porque un caso para un exceptuado ya falla antes. Buscá: casos de numeración (REMOVED, bloques de código, varias specs en un cambio), una spec con varios archivos donde el slug de un exceptuado coincida con otro, y falsos silencios. Marcá bajos los hallazgos de heurística y cerrá la clase entera.
