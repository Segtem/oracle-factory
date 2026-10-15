Sos un revisor independiente del cambio 20261015-001533-evidencia-fuera de un proyecto que usa Oracle Factory: «buscar no recorre la evidencia ni los paquetes de Clue». No escribiste este código.
NO edites el checkout, no hagas commits ni decidas nada por la persona: tu trabajo es encontrar defectos y contarlos con evidencia.

Qué tiene que hacer el cambio:
- Propuesta: /home/workstation/Dev/factory-evidencia-fuera/openspec/changes/20261015-001533-evidencia-fuera/proposal.md
- Spec (lo que se promete, con sus escenarios): /home/workstation/Dev/factory-evidencia-fuera/openspec/changes/20261015-001533-evidencia-fuera/specs/estructura/spec.md

Qué revisar:
- Checkout del candidato 1d78024 (sólo lectura): /home/workstation/Dev/factory-evidencia-fuera/.factory/local/revisiones/1d78024
- Paquete de Oracle Clue con el diff y el contexto: /home/workstation/Dev/factory-evidencia-fuera/.factory/cambios/20261015-001533-evidencia-fuera/candidatos/1d78024/clue/paquete-agy-1.json

Fuera del paquete, porque no son producto (.factory, tareas): 2 archivos de registros y evidencia de Factory; no los revises.

Cómo trabajar: leé la spec y el diff; contrastá cada promesa con el código y con las pruebas; buscá casos que fallen, afirmaciones que el
código no cumple y pruebas que no prueban lo que dicen. Si podés, hacé mutaciones a mano sobre copias en tu carpeta y decí cuáles sobreviven.
Mandá la salida larga a archivos de tu carpeta y leé sólo el resumen.

Entregable: un informe JSON en /home/workstation/Dev/factory-evidencia-fuera/.factory/local/revisores/1d78024-agy-1/informe.json con este formato (schema oracle-clue.review/v1):
- schema_version "oracle-clue.review/v1"; repo, base, head, diff_sha256 y context_sha256 copiados del paquete;
- provider {"name": "agy", "model": "gemini-3.8-flash-high"};
- findings: lista de hallazgos, cada uno con id, kind, severity (alta|media|baja|informativa), confidence (0 a 1), title, explanation,
  location {file, start_line, end_line, side: "head"} DENTRO de los rangos del diff del paquete, trigger, evidence, related_requirement,
  status "pendiente" y verification;
- review_status ("completo" o "incompleto") y limitations (qué corriste y qué no).
Sin hallazgos: findings vacía, explicado en limitations. Validalo antes de terminar con:
  oracle-clue validar /home/workstation/Dev/factory-evidencia-fuera/.factory/local/revisores/1d78024-agy-1/informe.json --paquete /home/workstation/Dev/factory-evidencia-fuera/.factory/cambios/20261015-001533-evidencia-fuera/candidatos/1d78024/clue/paquete-agy-1.json --repo /home/workstation/Dev/factory-evidencia-fuera/.factory/local/revisiones/1d78024
y terminá con un resumen corto en español.

Indicaciones de quien pide la revisión:
Vuelta 1. Revisá la implementación (oracle_factory/estructura.py: buscar) contra el requisito MODIFIED «buscar en todo el proyecto», y si tests/test_evidencia_fuera.py y los casos e8 de tests/test_estructura.py prueban de verdad cada escenario; revisá también tools/verify_evidencia_fuera.py y los catálogos factory_busqueda. Mirá especialmente: rutas de evidencia o paquetes que se sigan recorriendo, informes o pedidos de revision/ que se dejen de recorrer por error, el conteo de omitidos por tamaño, y otros lugares (resumen, donde) que la propuesta no toca. Para correr las pruebas usá exactamente, en primer plano: cd /home/workstation/Dev/factory-evidencia-fuera && /home/workstation/Dev/factory-evidencia-fuera/.venv/bin/python -m unittest tests.test_evidencia_fuera tests.test_estructura </dev/null . No corras tools/verify_*.py ni la suite completa. Nombrá archivos con rutas relativas.
