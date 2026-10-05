# Diseño del corte propuesto

## Diagnóstico y antecedentes

Base local inspeccionada: `6af15e4`, Factory 0.1.0a3. `oracle_factory/cli.py:revisar` sólo verifica informe no vacío y número declarado; el parser usa cero por defecto. `pendientes_actuales` compara contexto, hash de informe y hechos. El registro actual guarda bytes del informe en `review.md`, aunque el original tenga otra extensión. No interpreta su estructura.

`contexto_producto` excluye `tareas/` y algunos archivos generados de la huella del producto. Preparar o archivar allí permite completar registros sin invalidarlos por su propia creación; cualquier commit nuevo sigue cambiando HEAD. No se ampliará la exclusión a documentos del producto para conservar un verde.

Clue 0.1.0a1 separa informe de triage y liga éste al hash exacto del informe. Se inspeccionaron su README, schemas y el protocolo de colaboración `20261004-121432-coordinar-dos`. Factory reutilizará esa distinción conceptual. Este corte no importa, duplica ni valida schemas de Clue; el revisor puede consultar su salida por el flujo ya documentado.

## CLI propuesta

```text
oracle-factory revision-preparar ID
oracle-factory revision ID --formato guiado --informe RUTA_INFORME --decisiones RUTA_DECISIONES --revisor NOMBRE --decision aprobar|cambios
oracle-factory revision ID [--formato libre] --informe RUTA --revisor NOMBRE --decision aprobar|cambios --hallazgos-abiertos N
```

`revision-preparar` escribe en una carpeta nueva con creación exclusiva bajo `tareas/ID/revisiones/`; imprime ambas rutas. No exige haber asociado todas las medidas, pues la revisión puede señalar esa falta, pero sí un cambio abierto, spec aceptada vigente y contexto Git disponible. Mantiene la semántica actual del contexto: HEAD más huella de archivos, incluidos cambios no confirmados. Recomienda confirmar el producto antes de revisar y muestra ambos componentes; no inventa que todo el contenido esté en HEAD.

No se agrega un argumento de base/diff: ese es el trabajo de Clue o del revisor. La plantilla registra el contexto que Factory puede comprobar, no un análisis del diff. Las rutas de entrada se resuelven respecto del proyecto, como hoy, y admiten rutas absolutas de archivos regulares. La salida controlada por Factory se confina a la tarea y rechaza enlaces que escapen.

## Documentos v1

Informe `oracle-factory.revision/v1`, en JSON UTF-8:

| Campo | Preparación | Validación al registrar |
| --- | --- | --- |
| `schema_version` | Identificador fijo | Sólo v1; objeto estricto, sin claves duplicadas/desconocidas |
| `cambio` | ID actual | Coincidencia exacta |
| `contexto` | HEAD y archivos_sha256 | Igual al contexto actual; sin normalizar huellas ajenas |
| `documentos` | Hashes de proposal/spec aceptadas | Iguales a los documentos vigentes |
| `revisor` | null | Texto no vacío, igual al argumento revisor |
| `completa` | null | Booleano explícito; false impide aprobar |
| `archivos_revisados` | null | Lista no vacía de rutas relativas del producto inspeccionado; sin duplicados ni escapes; no prueba lectura real |
| `comprobaciones` | null | Lista no vacía de objetos con descripción, resultado declarado (`cumple`, `falla`, `no_ejecutada`) y evidencia textual no vacía |
| `limites` | null | Lista explícita de textos; vacía significa sin límites adicionales declarados, no cobertura universal; completa=false exige al menos uno |
| `hallazgos` | null | Lista explícita de objetos: id único, descripción, ubicación y evidencia textual no vacías; no se inventa un hallazgo de ejemplo |
| `sin_hallazgos_motivo` | null | Texto no vacío si hallazgos=[]; null si hay hallazgos |

Un resultado `falla` o `no_ejecutada` en comprobaciones impide aprobar en este corte. Se puede registrar `cambios` con el informe completo en estructura, conservando esos resultados y límites. No se exige que todas las rutas revisadas existan en el checkout actual: una revisión puede examinar archivos eliminados; no se siguen ni abren las ubicaciones declaradas de hallazgos para inferir hechos.

En campos humanos obligatorios se rechazan null, texto vacío y el marcador exacto `PENDIENTE` (ignorando espacios externos y mayúsculas). Esto detecta una plantilla incompleta conocida; no decide si cualquier otro texto aporta un análisis útil. Las listas pendientes se representan con null, nunca con hallazgos ficticios ni con un cero preasignado.

Decisiones `oracle-factory.decisiones-revision/v1`, separadas:

| Campo | Preparación | Validación al registrar |
| --- | --- | --- |
| `schema_version` | Identificador fijo | Sólo v1, objeto estricto |
| `informe_sha256` | null | Hash de bytes finales del informe; recalcular tras cualquier edición |
| `actor` | null | Persona que asume la decisión general, no identidad autenticada |
| `motivo` | null | Motivo no vacío de la decisión general |
| `decisiones` | null | Lista explícita, posiblemente vacía; cada objeto contiene hallazgo_id, estado, motivo, actor y fecha ISO 8601 con zona |

Estados de resolución: `corregido`, `descartado`, `riesgo_aceptado`. Un ID sin resolución queda abierto. No se acepta una decisión con ID desconocido o repetido ni una resolución sin actor/motivo/fecha. Factory no verifica que el texto de un motivo sea convincente ni que la corrección funcione; `corregido` es una declaración humana. Si corregir cambió el producto, hay que preparar revisión del contexto nuevo.

La decisión general se solicita por `--decision` y se muestra junto al actor/motivo del documento, sin duplicarla como campo editable que pueda contradecir el argumento. `--revisor` identifica al autor del análisis; el actor de decisiones puede ser otra persona. El usuario del sistema que confirma se registra como hoy, sin autenticar independientemente a ninguna de esas personas.

Después de completar el informe, la guía muestra cómo obtener su SHA-256 con Python o una herramienta del sistema y escribirlo en decisiones. No prellenar el hash de una plantilla incompleta ni autocompletar resoluciones. Una nueva preparación mantiene todos los campos humanos pendientes; no hereda decisiones de un informe anterior.

## Registro, conservación y fallas

1. Leer estado vigente y ambos documentos, comprobar sintaxis, campos y hashes. Capturar los bytes y contexto que se presentan.
2. Calcular abiertos por IDs y mostrar resumen legible, con estados de resolución separados, límites, comprobaciones no satisfactorias y decisión solicitada. Rechazar aprobar cuando quedan abiertos, revisión incompleta o comprobaciones no satisfactorias.
3. Pedir la confirmación existente `REGISTRAR REVISION ID`. Tras recibirla, volver a comprobar bytes de ambos documentos, propuesta/spec, contexto y registro de Factory. Detectar un cambio y pedir reintento sin sustituir el registro previo. Esta comprobación no equivale a un lock general del repositorio ni cubre editores externos de manera transaccional.
4. Archivar copias en una carpeta nueva de la tarea con informe/decisiones, usando creación exclusiva. Si falla, conservar el registro previo y señalar residuos. Registrar el nuevo estado sólo después de disponer de ambas copias íntegras, mediante reemplazo atómico del archivo de estado. Conservar la evidencia histórica; no reescribir el informe para añadir decisiones.
5. Guardar en `revision` formato, responsable, decisión, abiertos derivados, contexto, rutas y hashes de ambas copias. Invalidar `oracle` al reemplazar la revisión, agregar evento y nota al tracker. Si falla la nota después de guardar, indicar explícitamente que la revisión quedó registrada y la nota pendiente; no reportar una transacción revertida.
6. Para registros guiados, `estado`/`cerrar` comprueban también decisiones y su hash. Cambiar los originales después del archivo no cambia la evidencia ya registrada; alterar las copias archivadas sí la invalida.

Modo libre e históricos: mantienen sus contratos y rutas actuales; se etiquetan como `libre` o `libre histórico`, y no adquieren garantía estructural retroactiva. Los nuevos registros libres requieren conteo explícito. En ningún modo el parser convierte un error guiado en registro libre automáticamente. El registro guiado no requiere Clue instalado.

## Evidencia propuesta

| Casos | Observación |
| --- | --- |
| G1 | Preparar dos veces conserva anteriores, crea pendientes y no altera gates; errores de destino muestran recuperación |
| G2 | Rechazo de nulls, JSON inválido, claves duplicadas, versión/campos desconocidos y cambio/contexto ajenos |
| G3 | Hallazgos vacíos requieren motivo; completa=false o comprobaciones fallidas/no ejecutadas bloquean aprobar |
| G4 | Hash incorrecto, IDs/decisiones repetidos o desconocidos, motivos/actores/fechas inválidos se rechazan; abiertos se derivan |
| G5 | Cancelación y edición durante confirmación conservan registro anterior; nueva revisión invalida juicio |
| G6 | Copias archivadas conservadas, hashes verificados al cerrar, fallas de escritura/nota diagnosticadas sin falso éxito |
| G7 | Libre explícito compatible, conteo omitido rechazado, históricos rotulados, guiado con conteo manual rechazado |
| G8 | Recorrido completo en fixture temporal y guías coherentes con versiones; sin confirmaciones reales simuladas |

Estas son medidas candidatas, no asociaciones actuales. Tras aceptar la spec, importar con `fabrica.py importar`, elegir medidas y conservar sin medir lo que no se observe. Pruebas de estructuras y estados no prueban competencia del revisor ni calidad de sus conclusiones. La claridad para principiantes necesita una observación humana propia.
