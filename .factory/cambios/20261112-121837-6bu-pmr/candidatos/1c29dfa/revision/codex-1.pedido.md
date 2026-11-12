Sos un revisor independiente del cambio 20261112-121837-6bu-pmr de un proyecto que usa Oracle Factory: «Registros fuera del repo del producto: preparar la migración real de Factory». No escribiste este código.
NO edites el checkout, no hagas commits ni decidas nada por la persona: tu trabajo es encontrar defectos y contarlos con evidencia.

Qué tiene que hacer el cambio:
- Propuesta: /home/workstation/Dev/factory-preparar-migracion/openspec/changes/20261112-121837-6bu-pmr/proposal.md
- Spec (lo que se promete, con sus escenarios): /home/workstation/Dev/factory-preparar-migracion/openspec/changes/20261112-121837-6bu-pmr/specs/flujo/spec.md

Qué revisar:
- Checkout del candidato 1c29dfa (sólo lectura): /home/workstation/Dev/factory-preparar-migracion/.factory/local/revisiones/1c29dfa-codex-1
- Paquete de Oracle Clue con el diff y el contexto: /home/workstation/Dev/factory-preparar-migracion/.factory/cambios/20261112-121837-6bu-pmr/candidatos/1c29dfa/clue/paquete-codex-1.json

Tests existentes que este candidato modificó o borró (la guarda del proyecto: un test que ya existía no se edita para que pase sin dejarlo dicho). Mirá si cada edición está justificada por el cambio y mencionalo en tu informe, aunque la encuentres legítima:
- tests/datos/ayuda-cli.json, modificado: 1 línea(s) quitada(s)
- tests/datos/nombres-cli.json, modificado: 1 línea(s) quitada(s)
- tests/test_almacen_migrar.py, modificado: 1 línea(s) quitada(s); 1 aserción(es) quitada(s)
- tests/test_portabilidad.py, modificado: 1 línea(s) quitada(s)
- tests/test_verificador_generico.py, modificado: 1 línea(s) quitada(s)
Fuera del paquete, porque no son producto (.factory, kb/README.md, kb/cambios/20261112-121837-6bu-pmr.md, kb/requisitos/flujo_c281f4f7154afdb2f.agentes_en_el_repo_mantiene_una_guia_versionada.md, kb/requisitos/flujo_c281f4f7154afdb2f.la_puerta_funciona_con_el_producto_conectado.md, kb/requisitos/flujo_c281f4f7154afdb2f.las_pruebas_y_herramientas_leen_los_registros_del_almacen.md, kb/requisitos/flujo_c281f4f7154afdb2f.migrar_limpia_lo_de_factory_del_producto.md, tareas): 8 archivos de registros y evidencia de Factory; no los revises.

Cómo trabajar: leé la spec y el diff; contrastá cada promesa con el código y con las pruebas; buscá casos que fallen, afirmaciones que el
código no cumple y pruebas que no prueban lo que dicen. Si podés, hacé mutaciones a mano sobre copias en tu carpeta y decí cuáles sobreviven.
Mandá la salida larga a archivos de tu carpeta y leé sólo el resumen.

Entregable: un informe JSON en /home/workstation/Dev/factory-preparar-migracion/.factory/local/revisores/1c29dfa-codex-1/informe.json con este formato (schema oracle-clue.review/v1):
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
  oracle-clue validar /home/workstation/Dev/factory-preparar-migracion/.factory/local/revisores/1c29dfa-codex-1/informe.json --paquete /home/workstation/Dev/factory-preparar-migracion/.factory/cambios/20261112-121837-6bu-pmr/candidatos/1c29dfa/clue/paquete-codex-1.json --repo /home/workstation/Dev/factory-preparar-migracion/.factory/local/revisiones/1c29dfa-codex-1
y terminá con un resumen corto en español.

Indicaciones de quien pide la revisión:
Pruebas existentes editadas (declaradas): tests/test_portabilidad.py p6 y tests/test_verificador_generico.py vg3 (leen requisitos/ y catalogos/ con almacenes.registros_de, para que sigan valiendo con el repo conectado a un almacén); tests/test_almacen_migrar.py mg1 (la baja ya no cuenta .gitignore/.gitattributes, que ahora migrar limpia: los cubre pm2); tests/datos/ayuda-cli.json y nombres-cli.json (la opción --en-el-repo). Mirá en especial: (1) que migrar saque SOLO las líneas y hooks de Factory y nunca algo del equipo, y que lo deje todo en el índice o diga cómo terminar; (2) que la puerta con el producto conectado busque secretos en el repo del producto (antes los buscaba en el almacén y dejaba pasar en silencio); (3) que agentes --en-el-repo sólo lo pueda una persona y no excluya la guía. Antes de pedir otra ronda arreglo la clase entera de cada hallazgo.
