Sos un revisor independiente del cambio 20261027-225048-59a-terminallista de un proyecto que usa Oracle Factory: «Esperar a que la terminal de Factory esté lista antes de escribir un comando». No escribiste este código.
NO edites el checkout, no hagas commits ni decidas nada por la persona: tu trabajo es encontrar defectos y contarlos con evidencia.

Qué tiene que hacer el cambio:
- Propuesta: /home/workstation/Dev/factory-terminal-lista/openspec/changes/20261027-225048-59a-terminallista/proposal.md
- Spec (lo que se promete, con sus escenarios): /home/workstation/Dev/factory-terminal-lista/openspec/changes/20261027-225048-59a-terminallista/specs/ide/spec.md

Qué revisar:
- Checkout del candidato 95d545e (sólo lectura): /home/workstation/Dev/factory-terminal-lista/.factory/local/revisiones/95d545e-agy-1
- Paquete de Oracle Clue con el diff y el contexto: /home/workstation/Dev/factory-terminal-lista/.factory/cambios/20261027-225048-59a-terminallista/candidatos/95d545e/clue/paquete-agy-1.json

Vueltas anteriores de este cambio (ya corregidas; mirá que sigan cerradas y que no haya regresiones):
- .factory/cambios/20261027-225048-59a-terminallista/candidatos/f336999/revision/agy-1.json
- .factory/cambios/20261027-225048-59a-terminallista/candidatos/f336999/revision/agy2-1.json
Fuera del paquete, porque no son producto (.factory, kb/README.md, kb/cambios/20261027-225048-59a-terminallista.md, kb/requisitos/ide_c6fe31e596cc9568e.la_terminal_nueva_espera_a_estar_lista.md, kb/requisitos/ide_c6fe31e596cc9568e.los_comandos_seguidos_se_escriben_en_orden_y_una_vez.md, kb/requisitos/ide_c6fe31e596cc9568e.queda_constancia_en_la_salida.md, kb/requisitos/ide_c6fe31e596cc9568e.una_terminal_lista_recibe_el_comando_enseguida.md, tareas): 21 archivos de registros y evidencia de Factory; no los revises.

Cómo trabajar: leé la spec y el diff; contrastá cada promesa con el código y con las pruebas; buscá casos que fallen, afirmaciones que el
código no cumple y pruebas que no prueban lo que dicen. Si podés, hacé mutaciones a mano sobre copias en tu carpeta y decí cuáles sobreviven.
Mandá la salida larga a archivos de tu carpeta y leé sólo el resumen.

Entregable: un informe JSON en /home/workstation/Dev/factory-terminal-lista/.factory/local/revisores/95d545e-agy-1/informe.json con este formato (schema oracle-clue.review/v1):
- schema_version "oracle-clue.review/v1"; repo, base, head, diff_sha256 y context_sha256 copiados del paquete;
- provider {"name": "agy", "model": "gemini-3.8-flash-high"};
- findings: lista de hallazgos, cada uno con id, kind, severity (alta|media|baja|informativa), confidence (0 a 1), title, explanation,
  location {file, start_line, end_line, side: "head"} DENTRO de los rangos del diff del paquete, trigger, evidence, related_requirement,
  status "pendiente" y verification;
- review_status ("completo" o "incompleto") y limitations (qué corriste y qué no).
Sin hallazgos: findings vacía, explicado en limitations. Validalo antes de terminar con:
  oracle-clue validar /home/workstation/Dev/factory-terminal-lista/.factory/local/revisores/95d545e-agy-1/informe.json --paquete /home/workstation/Dev/factory-terminal-lista/.factory/cambios/20261027-225048-59a-terminallista/candidatos/95d545e/clue/paquete-agy-1.json --repo /home/workstation/Dev/factory-terminal-lista/.factory/local/revisiones/95d545e-agy-1
y terminá con un resumen corto en español.

Indicaciones de quien pide la revisión:
Vuelta 2: se corrigieron los hallazgos de la vuelta 1 (terminal cerrada durante la espera, escribirComando devuelve falso en vez de rechazar, plazo por defecto probado, package.json entre las fuentes, terminal ya cerrada). Revisá el cambio contra los requisitos de su spec (openspec/changes/20261027-225048-59a-terminallista/specs/ide/spec.md): editores/vscode/extension.js (esperarTerminal, escribirEnTerminal, escribirPaso, escribirComando y sus llamadores, incluido el pedido de un invitado de Live Share en liveshare.js), editores/vscode/package.json, tests/terminal_en_node.cjs, tests/test_terminal_lista.py, el cambio de getConfiguration en los otros arneses tests/*_en_node.cjs, tools/verify_terminal_lista.py, catalogos/factory_terminal_lista.*.oracle y la frase nueva de docs/tablero.md. Mirá especialmente: que nunca se escriba antes del aviso o del plazo, que un comando no se pierda ni se duplique ni se desordene (incluidos errores en createTerminal o en sendText, una terminal cerrada mientras se espera y pedidos concurrentes), que una cola rota por un error no bloquee los pedidos siguientes, que la respuesta a un invitado de Live Share siga siendo verdadera o falsa, que el plazo inválido caiga al de por defecto, que la salida no incluya el comando, y que las pruebas fallen de verdad si se rompe el comportamiento. Para correr las pruebas usá exactamente, en primer plano y desde la raíz del checkout: PYTHONPATH=. $PWD/.venv/bin/python -m unittest tests.test_terminal_lista tests.test_vscode tests.test_liveshare </dev/null . No corras la suite completa. No cambies la configuración de git de ningún repositorio. Nombrá archivos con rutas relativas.
