Sos un revisor independiente del cambio 20261103-170557-a0e-skillagente de un proyecto que usa Oracle Factory: «Una skill de agente con el flujo de Factory». No escribiste este código.
NO edites el checkout, no hagas commits ni decidas nada por la persona: tu trabajo es encontrar defectos y contarlos con evidencia.

Qué tiene que hacer el cambio:
- Propuesta: /home/workstation/Dev/factory-skill-agente/openspec/changes/20261103-170557-a0e-skillagente/proposal.md
- Spec (lo que se promete, con sus escenarios): /home/workstation/Dev/factory-skill-agente/openspec/changes/20261103-170557-a0e-skillagente/specs/practicas/spec.md

Qué revisar:
- Checkout del candidato d206e22 (sólo lectura): /home/workstation/Dev/factory-skill-agente/.factory/local/revisiones/d206e22-agy2-flash-1
- Paquete de Oracle Clue con el diff y el contexto: /home/workstation/Dev/factory-skill-agente/.factory/cambios/20261103-170557-a0e-skillagente/candidatos/d206e22/clue/paquete-agy2-flash-1.json

Tests existentes que este candidato modificó o borró (la guarda del proyecto: un test que ya existía no se edita para que pase sin dejarlo dicho). Mirá si cada edición está justificada por el cambio y mencionalo en tu informe, aunque la encuentres legítima:
- tests/datos/ayuda-cli.json, modificado: 1 línea(s) quitada(s)
Fuera del paquete, porque no son producto (.factory, kb/README.md, kb/cambios/20261103-170557-a0e-skillagente.md, kb/requisitos/practicas_c8fdb317e7f77a156.el_comando_skill_la_muestra_y_la_instala_sin_pisar_nada_ajeno.md, kb/requisitos/practicas_c8fdb317e7f77a156.la_guia_para_agentes_nombra_la_skill.md, kb/requisitos/practicas_c8fdb317e7f77a156.la_skill_describe_el_flujo_con_los_comandos_y_umbrales_del_codigo.md, tareas): 11 archivos de registros y evidencia de Factory; no los revises.

Cómo trabajar: leé la spec y el diff; contrastá cada promesa con el código y con las pruebas; buscá casos que fallen, afirmaciones que el
código no cumple y pruebas que no prueban lo que dicen. Si podés, hacé mutaciones a mano sobre copias en tu carpeta y decí cuáles sobreviven.
Mandá la salida larga a archivos de tu carpeta y leé sólo el resumen.

Entregable: un informe JSON en /home/workstation/Dev/factory-skill-agente/.factory/local/revisores/d206e22-agy2-flash-1/informe.json con este formato (schema oracle-clue.review/v1):
- schema_version "oracle-clue.review/v1"; repo, base, head, diff_sha256 y context_sha256 copiados del paquete;
- provider {"name": "agy", "model": "gemini-3.8-flash-high"};
- findings: lista de hallazgos, cada uno con id, kind, severity (alta|media|baja|informativa), confidence (0 a 1), title, explanation,
  location {file, start_line, end_line, side: "head"} DENTRO de los rangos del diff del paquete, trigger, evidence, related_requirement,
  status "pendiente" y verification;
- review_status ("completo" o "incompleto") y limitations (qué corriste y qué no).
Sin hallazgos: findings vacía, explicado en limitations. Validalo antes de terminar con:
  oracle-clue validar /home/workstation/Dev/factory-skill-agente/.factory/local/revisores/d206e22-agy2-flash-1/informe.json --paquete /home/workstation/Dev/factory-skill-agente/.factory/cambios/20261103-170557-a0e-skillagente/candidatos/d206e22/clue/paquete-agy2-flash-1.json --repo /home/workstation/Dev/factory-skill-agente/.factory/local/revisiones/d206e22-agy2-flash-1
y terminá con un resumen corto en español.

Indicaciones de quien pide la revisión:
No cambies la configuración de git de ningún repositorio. Revisá el cambio skill-agente: oracle_factory/data/skill/SKILL.md (la skill: el procedimiento para trabajar un cambio con Factory), oracle_factory/skill.py (texto, encabezado, comandos_nombrados, numeros_antes_de, documentos_enlazados, problemas, instalar), su cableado en cli.py (comando_skill, SOLO_LECTURA) y parser.py, el bullet nuevo de agentes.py (AGENTS.md está regenerado), docs/agentes.md, tests/test_skill_agente.py, pyproject.toml (package-data) y los catálogos. La evidencia la produjo tools/verificar_cambio.py. Declaro que en este cambio escribí el módulo skill.py ANTES que sus pruebas (la propia skill dice lo contrario); lo compensé con mutaciones de cada línea relevante, pero decí si ves pruebas que pasan por construcción. Buscá errores reales y de impacto práctico: (1) la SKILL.md: ¿cada afirmación sobre el flujo es verdadera según el código de oracle_factory/ y los documentos? ¿hay algo que mande a un agente a hacer algo que Factory prohíbe o que contradiga AGENTS.md? ¿las condiciones de parada y las reglas de procedimiento son razonables y no contradictorias? (2) skill instalar: enlaces simbólicos en cualquier tramo de la ruta, rutas que salen del proyecto, archivos distintos, permisos, ROOT cuando se corre desde una subcarpeta o con --proyecto, escritura parcial; que no toque HOME ni configuración. (3) la prueba de contraste: comandos con opciones, fragmentos de código raros, números en otras formas («450 líneas» escrito de otro modo). (4) que el wheel traiga el archivo. Marcá los exóticos. Clasificá por severidad.
Dato del candidato: tests/datos/ayuda-cli.json (la referencia de la ayuda de la CLI que usa tests/test_cli_modulos.py::test_cm1_la_ayuda_de_oracle_factory_y_de_cada_subcomando_es_identica) cambió: la ayuda raíz suma «skill» a la lista de subcomandos y hay una entrada nueva «skill»; no se quitó ninguna otra. Decí si te parece justificado.
