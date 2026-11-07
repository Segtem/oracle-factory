Sos un revisor independiente del cambio 20261107-213354-5pg-entregaa18 de un proyecto que usa Oracle Factory: «Preparar la distribución 0.1.0a18». No escribiste este código.
NO edites el checkout, no hagas commits ni decidas nada por la persona: tu trabajo es encontrar defectos y contarlos con evidencia.

Qué tiene que hacer el cambio:
- Propuesta: /home/workstation/Dev/factory-entrega-a18/openspec/changes/20261107-213354-5pg-entregaa18/proposal.md
- Spec (lo que se promete, con sus escenarios): /home/workstation/Dev/factory-entrega-a18/openspec/changes/20261107-213354-5pg-entregaa18/specs/distribucion/spec.md

Qué revisar:
- Checkout del candidato 9f51311 (sólo lectura): /home/workstation/Dev/factory-entrega-a18/.factory/local/revisiones/9f51311-codex-1
- Paquete de Oracle Clue con el diff y el contexto: /home/workstation/Dev/factory-entrega-a18/.factory/cambios/20261107-213354-5pg-entregaa18/candidatos/9f51311/clue/paquete-codex-1.json

Vueltas anteriores de este cambio (ya corregidas; mirá que sigan cerradas y que no haya regresiones):
- .factory/cambios/20261107-213354-5pg-entregaa18/candidatos/d76cd31/revision/codex-1.json
Tests existentes que este candidato modificó o borró (la guarda del proyecto: un test que ya existía no se edita para que pase sin dejarlo dicho). Mirá si cada edición está justificada por el cambio y mencionalo en tu informe, aunque la encuentres legítima:
- tests/datos/guias-texto.json, modificado: 10 línea(s) quitada(s)
- tests/test_docs.py, modificado: 9 línea(s) quitada(s); 4 aserción(es) quitada(s)
- tests/test_entrega_a18.py (antes tests/test_entrega_a17.py), renombrado: 17 línea(s) quitada(s); tests quitados: test_ea1_los_textos_y_la_web_estan_al_dia_y_la_a16_y_la_a17_figuran_publicadas; 8 aserción(es) quitada(s)
- tests/test_publicada_a17.py, borrado: 127 línea(s) quitada(s); tests quitados: test_pa1_las_notas_declaran_la_version_publicada_con_su_tag_y_su_release, test_pa1_ningun_texto_llama_candidata_a_la_version_publicada, test_pa1_el_readme_y_la_guia_dicen_que_esta_publicada, test_pa1_la_historia_anterior_se_conserva, test_pa2_un_texto_candidata_con_las_notas_publicadas_se_detecta, test_pa2_el_candidato_de_una_revision_y_otros_estados_de_preparacion_no_son_divergencia, test_pa2_una_version_en_preparacion_no_es_divergencia, test_pa2_sin_notas_la_regla_no_inventa_divergencias, test_pa2_la_palabra_candidato_junto_a_otra_version_no_cuenta; 17 aserción(es) quitada(s)
Fuera del paquete, porque no son producto (.factory, kb/README.md, kb/cambios/20261107-213354-5pg-entregaa18.md, kb/requisitos/distribucion_c0803bc5aff1b2bf1.el_wheel_a18_instalado_ofrece_lo_nuevo.md, kb/requisitos/distribucion_c0803bc5aff1b2bf1.la_entrega_a18_registra_sus_hashes_y_sus_limites.md, kb/requisitos/distribucion_c0803bc5aff1b2bf1.la_version_a18_es_coherente_y_declara_su_estado.md, tareas): 13 archivos de registros y evidencia de Factory; no los revises.

Cómo trabajar: leé la spec y el diff; contrastá cada promesa con el código y con las pruebas; buscá casos que fallen, afirmaciones que el
código no cumple y pruebas que no prueban lo que dicen. Si podés, hacé mutaciones a mano sobre copias en tu carpeta y decí cuáles sobreviven.
Mandá la salida larga a archivos de tu carpeta y leé sólo el resumen.

Entregable: un informe JSON en /home/workstation/Dev/factory-entrega-a18/.factory/local/revisores/9f51311-codex-1/informe.json con este formato (schema oracle-clue.review/v1):
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
  oracle-clue validar /home/workstation/Dev/factory-entrega-a18/.factory/local/revisores/9f51311-codex-1/informe.json --paquete /home/workstation/Dev/factory-entrega-a18/.factory/cambios/20261107-213354-5pg-entregaa18/candidatos/9f51311/clue/paquete-codex-1.json --repo /home/workstation/Dev/factory-entrega-a18/.factory/local/revisiones/9f51311-codex-1
y terminá con un resumen corto en español.

Indicaciones de quien pide la revisión:
Segunda ronda. Hallazgo anterior (a18-wheel-destinos-no-ejercitado): el probador ahora ejercita en el wheel instalado 'destinos --sin-consultar --json' y 'desplegar --simular' con una declaración mínima (incluye conjunto), y validar los chequea; mutaciones propias: sin chequeo de destinos y sin chequeo de desplegar son detectadas. Límite conocido: si la observación de 'desplegar --simular' fabricara siempre True el juicio no lo notaría (no hay caso real negativo). Revisá también el resto de la entrega 0.1.0a18 como antes.
