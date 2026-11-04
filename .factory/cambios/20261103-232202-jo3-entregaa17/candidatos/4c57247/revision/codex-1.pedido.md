Sos un revisor independiente del cambio 20261103-232202-jo3-entregaa17 de un proyecto que usa Oracle Factory: «Preparar la distribución 0.1.0a17». No escribiste este código.
NO edites el checkout, no hagas commits ni decidas nada por la persona: tu trabajo es encontrar defectos y contarlos con evidencia.

Qué tiene que hacer el cambio:
- Propuesta: /home/workstation/Dev/factory-entrega-a17/openspec/changes/20261103-232202-jo3-entregaa17/proposal.md
- Spec (lo que se promete, con sus escenarios): /home/workstation/Dev/factory-entrega-a17/openspec/changes/20261103-232202-jo3-entregaa17/specs/distribucion/spec.md

Qué revisar:
- Checkout del candidato 4c57247 (sólo lectura): /home/workstation/Dev/factory-entrega-a17/.factory/local/revisiones/4c57247-codex-1
- Paquete de Oracle Clue con el diff y el contexto: /home/workstation/Dev/factory-entrega-a17/.factory/cambios/20261103-232202-jo3-entregaa17/candidatos/4c57247/clue/paquete-codex-1.json

Tests existentes que este candidato modificó o borró (la guarda del proyecto: un test que ya existía no se edita para que pase sin dejarlo dicho). Mirá si cada edición está justificada por el cambio y mencionalo en tu informe, aunque la encuentres legítima:
- tests/datos/guias-texto.json, modificado: 10 línea(s) quitada(s)
- tests/test_docs.py, modificado: 9 línea(s) quitada(s); 4 aserción(es) quitada(s)
- tests/test_entrega_a16.py, borrado: 259 línea(s) quitada(s); tests quitados: test_ea1_version_coherente_y_estado_declarado, test_ea2_tras_la_limpieza_el_entorno_instalado_se_reconstruye, test_ea2_el_origen_y_la_version_instalados_se_verifican, test_ea2_el_wheel_instalado_ofrece_las_novedades_de_a16, test_ea2_la_validacion_de_las_novedades_rechaza_cada_novedad_que_falta, test_ea2_las_consultas_de_la_entrega_anterior_siguen_en_el_wheel, test_ea3_entrega_registra_pruebas_y_limites, test_ea3_un_arnes_fallido_no_se_registra_como_exitoso; 52 aserción(es) quitada(s)
- tests/test_publicada_a16.py, borrado: 120 línea(s) quitada(s); tests quitados: test_pa1_las_notas_declaran_la_version_publicada_con_su_tag_y_su_release, test_pa1_ningun_texto_llama_candidata_a_la_version_publicada, test_pa1_el_readme_y_la_guia_dicen_que_esta_publicada, test_pa1_la_historia_anterior_se_conserva, test_pa2_un_texto_candidata_con_las_notas_publicadas_se_detecta, test_pa2_el_candidato_de_una_revision_y_otros_estados_de_preparacion_no_son_divergencia, test_pa2_una_version_en_preparacion_no_es_divergencia, test_pa2_sin_notas_la_regla_no_inventa_divergencias, test_pa2_la_palabra_candidato_junto_a_otra_version_no_cuenta; 17 aserción(es) quitada(s)
Fuera del paquete, porque no son producto (.factory, kb/README.md, kb/cambios/20261103-232202-jo3-entregaa17.md, kb/requisitos/distribucion_c4b4c8c6521232d76.el_wheel_a17_instalado_ofrece_lo_nuevo.md, kb/requisitos/distribucion_c4b4c8c6521232d76.la_entrega_a17_registra_sus_hashes_y_sus_limites.md, kb/requisitos/distribucion_c4b4c8c6521232d76.la_version_a17_es_coherente_y_declara_su_estado.md, tareas): 7 archivos de registros y evidencia de Factory; no los revises.

Cómo trabajar: leé la spec y el diff; contrastá cada promesa con el código y con las pruebas; buscá casos que fallen, afirmaciones que el
código no cumple y pruebas que no prueban lo que dicen. Si podés, hacé mutaciones a mano sobre copias en tu carpeta y decí cuáles sobreviven.
Mandá la salida larga a archivos de tu carpeta y leé sólo el resumen.

Entregable: un informe JSON en /home/workstation/Dev/factory-entrega-a17/.factory/local/revisores/4c57247-codex-1/informe.json con este formato (schema oracle-clue.review/v1):
- schema_version "oracle-clue.review/v1"; repo, base, head, diff_sha256 y context_sha256 copiados del paquete;
- provider {"name": "codex", "model": "gpt-6-luna"};
- findings: lista de hallazgos, cada uno con id, kind, severity (alta|media|baja|informativa), confidence (0 a 1), title, explanation,
  location {file, start_line, end_line, side: "head"} DENTRO de los rangos del diff del paquete, trigger, evidence, related_requirement,
  status "pendiente" y verification;
- review_status ("completo" o "incompleto") y limitations (qué corriste y qué no).
Sin hallazgos: findings vacía, explicado en limitations. Validalo antes de terminar con:
  oracle-clue validar /home/workstation/Dev/factory-entrega-a17/.factory/local/revisores/4c57247-codex-1/informe.json --paquete /home/workstation/Dev/factory-entrega-a17/.factory/cambios/20261103-232202-jo3-entregaa17/candidatos/4c57247/clue/paquete-codex-1.json --repo /home/workstation/Dev/factory-entrega-a17/.factory/local/revisiones/4c57247-codex-1
y terminá con un resumen corto en español.

Indicaciones de quien pide la revisión:
No cambies la configuración de git de ningún repositorio. Es la primera (y, si no hay hallazgos medios o altos, única) ronda de entrega-a17, la preparación de la versión 0.1.0a17 (sólo el candidato; la publicación en PyPI, el tag y la release vienen después y no son de este cambio). Declaro lo que cambió y lo que NO es un arreglo de pruebas: (1) borré tests/test_entrega_a16.py y tests/test_publicada_a16.py porque afirmaban que la a16 es la versión actual y fallan al subir la versión; los reemplaza tests/test_entrega_a17.py (mismo precedente: la a16 reemplazó los de la a15). Se mantienen tests/test_entrega_integridad_a16.py y las herramientas a14–a16. (2) tests/test_docs.py cambió sólo las cadenas de versión y las frases «Candidato en preparación»; tests/datos/guias-texto.json se regeneró con `node tests/texto_guias.cjs` y sólo cambian las líneas de versión. (3) La versión sube en pyproject.toml, oracle_factory/__init__.py, uv.lock, README.md, docs/colaboracion.md, site/*.html y NOTAS-DE-RELEASE.md (sección a17 «en preparación»; la a16 figura publicada). (4) tools/probar_entrega_a17.py construye wheel y sdist con uv build, los instala en un entorno limpio y, desde otra carpeta, comprueba versión, origen de la importación, que el wheel trae la skill y que funcionan skill, skill --instalar, puerta y agentes; deja un registro con hashes y límites. Límites declarados: no sube nada a PyPI ni crea tag; el entorno limpio usa la caché de uv. Buscá errores reales y de impacto práctico: afirmaciones falsas en las notas/README/web (¿cada novedad existe en el código?), versiones que quedaron viejas, el probador (¿puede dar «ok» sin que el wheel funcione?), y tests/test_entrega_a17.py. Marcá los exóticos y decí con claridad si no queda nada de impacto práctico. Clasificá por severidad.
