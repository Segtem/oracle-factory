Sos un revisor independiente del cambio 20261028-150627-lva-procedencia de un proyecto que usa Oracle Factory: «Registrar la procedencia de las dependencias de cada candidato». No escribiste este código.
NO edites el checkout, no hagas commits ni decidas nada por la persona: tu trabajo es encontrar defectos y contarlos con evidencia.

Qué tiene que hacer el cambio:
- Propuesta: /home/workstation/Dev/factory-procedencia/openspec/changes/20261028-150627-lva-procedencia/proposal.md
- Spec (lo que se promete, con sus escenarios): /home/workstation/Dev/factory-procedencia/openspec/changes/20261028-150627-lva-procedencia/specs/procedencia/spec.md

Qué revisar:
- Checkout del candidato 9fd80f0 (sólo lectura): /home/workstation/Dev/factory-procedencia/.factory/local/revisiones/9fd80f0-agy-1
- Paquete de Oracle Clue con el diff y el contexto: /home/workstation/Dev/factory-procedencia/.factory/cambios/20261028-150627-lva-procedencia/candidatos/9fd80f0/clue/paquete-agy-1.json

Vueltas anteriores de este cambio (ya corregidas; mirá que sigan cerradas y que no haya regresiones):
- .factory/cambios/20261028-150627-lva-procedencia/candidatos/9ff21ae/revision/agy-1.json
- .factory/cambios/20261028-150627-lva-procedencia/candidatos/9ff21ae/revision/agy2-1.json
Fuera del paquete, porque no son producto (.factory, kb/README.md, kb/cambios/20261028-150627-lva-procedencia.md, kb/requisitos/procedencia_c3331f4b36e5b7938.el_inventario_dice_que_hay_y_de_donde_viene.md, kb/requisitos/procedencia_c3331f4b36e5b7938.el_inventario_queda_en_el_candidato.md, kb/requisitos/procedencia_c3331f4b36e5b7938.se_audita_contra_avisos_sin_red.md, kb/requisitos/procedencia_c3331f4b36e5b7938.se_busca_quien_uso_una_dependencia.md, kb/requisitos/procedencia_c3331f4b36e5b7938.un_lock_desactualizado_se_declara_no_confiable.md, tareas): 22 archivos de registros y evidencia de Factory; no los revises.

Cómo trabajar: leé la spec y el diff; contrastá cada promesa con el código y con las pruebas; buscá casos que fallen, afirmaciones que el
código no cumple y pruebas que no prueban lo que dicen. Si podés, hacé mutaciones a mano sobre copias en tu carpeta y decí cuáles sobreviven.
Mandá la salida larga a archivos de tu carpeta y leé sólo el resumen.

Entregable: un informe JSON en /home/workstation/Dev/factory-procedencia/.factory/local/revisores/9fd80f0-agy-1/informe.json con este formato (schema oracle-clue.review/v1):
- schema_version "oracle-clue.review/v1"; repo, base, head, diff_sha256 y context_sha256 copiados del paquete;
- provider {"name": "agy", "model": "gemini-3.8-flash-high"};
- findings: lista de hallazgos, cada uno con id, kind, severity (alta|media|baja|informativa), confidence (0 a 1), title, explanation,
  location {file, start_line, end_line, side: "head"} DENTRO de los rangos del diff del paquete, trigger, evidence, related_requirement,
  status "pendiente" y verification;
- review_status ("completo" o "incompleto") y limitations (qué corriste y qué no).
Sin hallazgos: findings vacía, explicado en limitations. Validalo antes de terminar con:
  oracle-clue validar /home/workstation/Dev/factory-procedencia/.factory/local/revisores/9fd80f0-agy-1/informe.json --paquete /home/workstation/Dev/factory-procedencia/.factory/cambios/20261028-150627-lva-procedencia/candidatos/9fd80f0/clue/paquete-agy-1.json --repo /home/workstation/Dev/factory-procedencia/.factory/local/revisiones/9fd80f0-agy-1
y terminá con un resumen corto en español.

Indicaciones de quien pide la revisión:
Vuelta 2: se corrigieron los hallazgos de la vuelta 1 en oracle_factory/procedencia.py y oracle_factory/cli.py: los rangos OSV se validan (events vacío, nulo, de más de una clave, tipos y valores) y un aviso sin versiones ni rangos aplicables no se da por limpio; introduced «0» cubre desde el principio incluidas las pre-releases de la serie 0; los eventos en la misma versión se ordenan con desempate (introduced, limit/last_affected, fixed); un pyproject.toml ausente o enlazado se declara como diferencia; la ruta del archivo de avisos se revisa por enlaces en los directorios del camino dentro del proyecto; la ruta del evento va en POSIX. Hay 75 pruebas y más de 90 mutaciones, todas detectadas. Revisá el cambio contra los requisitos de su spec (openspec/changes/20261028-150627-lva-procedencia/specs/procedencia/spec.md): oracle_factory/procedencia.py, en oracle_factory/cli.py la función comando_procedencia y el subcomando procedencia (el resto de la lógica de buscar y auditar vive en oracle_factory/procedencia.py: guardados, sin_enlaces, informe_buscar e informe_auditar; cli.py quedó bajo el límite de 256000 bytes de Oracle Clue), tests/test_procedencia.py, tools/verify_procedencia.py, catalogos/factory_procedencia.*.oracle, docs/procedencia.md, el cambio en README.md y la etiqueta nueva de editores/vscode/tablero.js. Mirá especialmente: que el inventario sea correcto y determinista (CycloneDX 1.5 válido en lo que usa, orden, hashes, purl con nombres y versiones raros), que un lock desactualizado o ausente jamás se presente como confiable, que ninguna ruta lea o escriba fuera del proyecto (enlaces simbólicos en uv.lock, pyproject.toml, el archivo de avisos, las carpetas de candidatos y los inventarios guardados), que el Python indicado con --python no pueda ejecutar nada más que lo previsto, que la comparación de versiones al estilo PEP 440 y la evaluación de los rangos OSV (introduced, fixed, last_affected, eventos desordenados, pre-releases, versiones locales y las corregidas por Lightwell) sean correctas, que un archivo de avisos inválido falle y no se lea como limpio, que no se use la red, que --buscar y --auditar no mezclen candidatos ni cambios, que el evento del registro no rompa nada (tablero, resumen, kb, MCP) y que las pruebas fallen de verdad si se rompe el comportamiento. Para correr pruebas usá exactamente, en primer plano y desde la raíz del checkout: PYTHONPATH=. $PWD/.venv/bin/python -m unittest tests.test_procedencia tests.test_docs </dev/null . No corras la suite completa. No cambies la configuración de git de ningún repositorio. Nombrá archivos con rutas relativas.
