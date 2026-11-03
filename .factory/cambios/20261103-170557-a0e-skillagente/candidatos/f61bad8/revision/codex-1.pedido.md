Sos un revisor independiente del cambio 20261103-170557-a0e-skillagente de un proyecto que usa Oracle Factory: «Una skill de agente con el flujo de Factory». No escribiste este código.
NO edites el checkout, no hagas commits ni decidas nada por la persona: tu trabajo es encontrar defectos y contarlos con evidencia.

Qué tiene que hacer el cambio:
- Propuesta: /home/workstation/Dev/factory-skill-agente/openspec/changes/20261103-170557-a0e-skillagente/proposal.md
- Spec (lo que se promete, con sus escenarios): /home/workstation/Dev/factory-skill-agente/openspec/changes/20261103-170557-a0e-skillagente/specs/practicas/spec.md

Qué revisar:
- Checkout del candidato f61bad8 (sólo lectura): /home/workstation/Dev/factory-skill-agente/.factory/local/revisiones/f61bad8-codex-1
- Paquete de Oracle Clue con el diff y el contexto: /home/workstation/Dev/factory-skill-agente/.factory/cambios/20261103-170557-a0e-skillagente/candidatos/f61bad8/clue/paquete-codex-1.json

Vueltas anteriores de este cambio (ya corregidas; mirá que sigan cerradas y que no haya regresiones):
- .factory/cambios/20261103-170557-a0e-skillagente/candidatos/d206e22/revision/agy2-flash-1.json
- .factory/cambios/20261103-170557-a0e-skillagente/candidatos/d206e22/revision/codex-1.json
Tests existentes que este candidato modificó o borró (la guarda del proyecto: un test que ya existía no se edita para que pase sin dejarlo dicho). Mirá si cada edición está justificada por el cambio y mencionalo en tu informe, aunque la encuentres legítima:
- tests/datos/ayuda-cli.json, modificado: 1 línea(s) quitada(s)
Fuera del paquete, porque no son producto (.factory, kb/README.md, kb/cambios/20261103-170557-a0e-skillagente.md, kb/requisitos/practicas_c8fdb317e7f77a156.el_comando_skill_la_muestra_y_la_instala_sin_pisar_nada_ajeno.md, kb/requisitos/practicas_c8fdb317e7f77a156.la_guia_para_agentes_nombra_la_skill.md, kb/requisitos/practicas_c8fdb317e7f77a156.la_skill_describe_el_flujo_con_los_comandos_y_umbrales_del_codigo.md, tareas): 19 archivos de registros y evidencia de Factory; no los revises.

Cómo trabajar: leé la spec y el diff; contrastá cada promesa con el código y con las pruebas; buscá casos que fallen, afirmaciones que el
código no cumple y pruebas que no prueban lo que dicen. Si podés, hacé mutaciones a mano sobre copias en tu carpeta y decí cuáles sobreviven.
Mandá la salida larga a archivos de tu carpeta y leé sólo el resumen.

Entregable: un informe JSON en /home/workstation/Dev/factory-skill-agente/.factory/local/revisores/f61bad8-codex-1/informe.json con este formato (schema oracle-clue.review/v1):
- schema_version "oracle-clue.review/v1"; repo, base, head, diff_sha256 y context_sha256 copiados del paquete;
- provider {"name": "codex", "model": "gpt-6-luna"};
- findings: lista de hallazgos, cada uno con id, kind, severity (alta|media|baja|informativa), confidence (0 a 1), title, explanation,
  location {file, start_line, end_line, side: "head"} DENTRO de los rangos del diff del paquete, trigger, evidence, related_requirement,
  status "pendiente" y verification;
- review_status ("completo" o "incompleto") y limitations (qué corriste y qué no).
Sin hallazgos: findings vacía, explicado en limitations. Validalo antes de terminar con:
  oracle-clue validar /home/workstation/Dev/factory-skill-agente/.factory/local/revisores/f61bad8-codex-1/informe.json --paquete /home/workstation/Dev/factory-skill-agente/.factory/cambios/20261103-170557-a0e-skillagente/candidatos/f61bad8/clue/paquete-codex-1.json --repo /home/workstation/Dev/factory-skill-agente/.factory/local/revisiones/f61bad8-codex-1
y terminá con un resumen corto en español.

Indicaciones de quien pide la revisión:
No cambies la configuración de git de ningún repositorio. Es la segunda ronda de skill-agente. La primera trajo 8 hallazgos: el paso 5 de la skill decía `--salida` sin la carpeta (ahora el comando completo con `$(.venv/bin/oracle-factory ruta ID evidencia)`), instalar no manejaba un destino que es directorio ni un ancestro que es archivo (ahora SkillError claro), la escritura no era atómica (ahora temporal + os.replace), el contraste no veía comandos en bloques cercados ni encadenados (ahora sí), los números y enlaces con saltos de línea o enlaces Markdown (ahora sí), `--forzar` sin `--instalar` se ignoraba (ahora error) y faltaba la prueba negativa del umbral ligero (hay). Tests existentes modificados: tests/datos/ayuda-cli.json (la ayuda raíz suma «skill» y hay una entrada nueva; nada se quitó), que ya habías visto. Límite declarado: el test de que la skill viaja en el paquete es estático (no construye un wheel). Declaro otra vez que escribí skill.py antes que sus pruebas y lo compensé con mutaciones. Verificá que los arreglos cubren la CLASE entera y buscá errores reales y de impacto práctico en oracle_factory/data/skill/SKILL.md (¿cada afirmación es verdadera según el código y los documentos?), oracle_factory/skill.py, cli.py (comando_skill), agentes.py, docs/agentes.md y tests/test_skill_agente.py; marcá los exóticos y decí con claridad si no queda nada de impacto práctico. Clasificá por severidad.
Contexto de esta ronda: la máquina se colgó y se reinició justo cuando arrancó la evidencia anterior de este mismo candidato (f61bad8); no es un defecto del código. Esta es la misma ronda 2, relanzada.
