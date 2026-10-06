# Capability: revision-guiada

<!-- Generada por Oracle Factory al cerrar cada cambio: no se edita a mano. -->

## Requirements

### Requirement: preparar documentos pendientes sin aprobar
Origen: 20261004-005956-revision-guiada · revision_guiada_c5794e24f22c4deb6.preparar_documentos_pendientes_sin_aprobar
El sistema SHALL crear, para un cambio abierto con spec aceptada y vigente y contexto Git disponible, un informe guiado y un documento de decisiones nuevos, dejando pendientes las observaciones y decisiones humanas, sin modificar revisiones, juicios ni cierre.

#### Scenario: preparar una revision
- GIVEN un cambio aceptado y un contexto de producto estable
- WHEN se ejecuta revision-preparar con el ID completo
- THEN se imprimen rutas nuevas bajo su tarea, ID y contexto capturados, campos humanos pendientes e instrucciones de siguiente paso.

#### Scenario: preparar otra vez o fallar
- GIVEN documentos previos o una falla al crear la carpeta de preparación
- WHEN se solicita otra preparación
- THEN no se sobrescribe ningún archivo anterior, no se modifica ningún gate y cualquier salida parcial se identifica con sus rutas para recuperación.

### Requirement: validar informe guiado y su alcance declarado
Origen: 20261004-005956-revision-guiada · revision_guiada_c5794e24f22c4deb6.validar_informe_guiado_y_su_alcance_declarado
El sistema SHALL rechazar documentos guiados malformados, de versión desconocida, con campos requeridos pendientes, cambio/contexto diferentes o hallazgos inválidos; SHALL exigir responsable, alcance revisado, comprobaciones y declaración de límites.

#### Scenario: plantilla sin completar
- GIVEN un informe con revisor, completitud o hallazgos en null
- WHEN se intenta registrar la revisión
- THEN se señalan los campos pendientes antes de pedir confirmación, sin alterar la revisión vigente.

#### Scenario: ausencia explicita de hallazgos
- GIVEN un informe completo con lista de hallazgos vacía
- WHEN se solicita aprobar
- THEN se exige un motivo no vacío que explique la ausencia declarada, además de decisiones generales y confirmación humanas; no se infiere aprobación de la lista vacía.

#### Scenario: revision parcial
- GIVEN un informe declarado incompleto y límites explícitos
- WHEN se intenta registrar aprobar
- THEN se rechaza esa decisión; el mismo informe puede registrarse como cambios si sus campos requeridos están completos.

#### Scenario: comprobaciones no satisfactorias
- GIVEN una comprobación declarada falla o no_ejecutada
- WHEN se solicita aprobar aunque no haya hallazgos abiertos
- THEN se rechaza y se muestra la comprobación pendiente; se puede registrar cambios con confirmación humana.

### Requirement: derivar pendientes de decisiones separadas
Origen: 20261004-005956-revision-guiada · revision_guiada_c5794e24f22c4deb6.derivar_pendientes_de_decisiones_separadas
El sistema SHALL validar decisiones humanas separadas, ligadas al SHA-256 exacto del informe, y calcular abiertos como los IDs de hallazgos que carecen de una resolución válida, sin aceptar un conteo manual en modo guiado.

#### Scenario: hallazgo sin resolver
- GIVEN dos hallazgos únicos y una sola resolución válida
- WHEN se prepara la confirmación
- THEN se muestra un hallazgo abierto; se rechaza aprobar y se permite solicitar cambios con confirmación humana.

#### Scenario: decision inconsistente
- GIVEN un hash de otro informe, IDs inexistentes o duplicados, estado desconocido, actor o motivo vacío
- WHEN se valida el documento de decisiones
- THEN se rechaza sin registrar aprobación ni corregir silenciosamente los datos.

#### Scenario: resoluciones completas
- GIVEN todos los hallazgos con decisiones corregido, descartado o riesgo_aceptado y sus motivos y actores
- WHEN una persona solicita aprobar un informe completo
- THEN se muestran por separado esas resoluciones antes de confirmar, sin afirmar que Factory verificó su corrección o autenticó al actor.

### Requirement: registrar confirmacion humana informada
Origen: 20261004-005956-revision-guiada · revision_guiada_c5794e24f22c4deb6.registrar_confirmacion_humana_informada
El sistema SHALL mostrar la versión revisada, tipo de registro, responsable, alcance, límites, pendientes y decisión solicitada antes de exigir la confirmación humana, revalidando contexto y documentos después de recibirla.

#### Scenario: cancelar o modificar entradas
- GIVEN una revisión anterior y un nuevo registro pendiente de confirmación
- WHEN la persona cancela o cambian informe, decisiones, spec o contexto durante la confirmación
- THEN no se sustituye la revisión anterior y se informa qué debe corregirse o volver a revisarse.

#### Scenario: registrar nueva revision
- GIVEN documentos consistentes con el candidato actual y una confirmación coincidente
- WHEN se registra la decisión humana
- THEN se guarda el commit/contexto observado y la decisión, se invalida el juicio previo y se conserva el informe como evidencia, sin cerrar la tarea.

### Requirement: conservar evidencia y comprobar vigencia
Origen: 20261004-005956-revision-guiada · revision_guiada_c5794e24f22c4deb6.conservar_evidencia_y_comprobar_vigencia
El sistema SHALL conservar copias inmutables por registro del informe guiado y sus decisiones, registrar sus hashes y bloquear el cierre si falta o cambia una copia o si el contexto revisado dejó de ser vigente.

#### Scenario: cambiar evidencia archivada
- GIVEN una revisión guiada registrada
- WHEN se altera o elimina uno de los dos documentos archivados
- THEN estado y cerrar informan evidencia no vigente y no permiten cerrar con ese registro.

#### Scenario: falla durante el archivo
- GIVEN una revisión previa y una falla de escritura al archivar la nueva
- WHEN el registro no alcanza a completarse
- THEN no se publica un nuevo gate aprobado sin sus dos documentos íntegros, se conserva el registro previo y se informa cualquier archivo residual; no se promete transacción entre archivos y nota del tracker.

### Requirement: mantener formato libre con declaracion explicita
Origen: 20261004-005956-revision-guiada · revision_guiada_c5794e24f22c4deb6.mantener_formato_libre_con_declaracion_explicita
El sistema SHALL mantener los registros libres y los históricos como declaraciones humanas, distinguirlos del modo guiado y exigir una cantidad explícita de hallazgos abiertos para nuevos registros libres, sin reinterpretar texto como informe estructurado.

#### Scenario: comando libre existente
- GIVEN un informe no vacío y el comando revision con revisor, decision y hallazgos-abiertos explícitos
- WHEN se registra sin formato o con formato libre
- THEN mantiene el flujo existente y muestra que sólo valida existencia, huella, contexto y declaración humana, sin certificar el contenido.

#### Scenario: conteo omitido o modo incompatible
- GIVEN modo libre sin hallazgos-abiertos, o modo guiado con conteo manual, o un formato desconocido
- WHEN se invoca revision
- THEN se rechaza con instrucciones concretas sin guardar cambios ni cambiar de formato silenciosamente.

### Requirement: explicar y verificar los limites del recorrido
Origen: 20261004-005956-revision-guiada · revision_guiada_c5794e24f22c4deb6.explicar_y_verificar_los_limites_del_recorrido
El entregable SHALL documentar preparación, completado, decisión y renovación con ejemplos pendientes y casos reproducibles, distinguiendo validación estructural de análisis del código y decisiones humanas.

#### Scenario: usar el recorrido guiado
- GIVEN la versión de Factory que incorpora estos comandos
- WHEN una persona sigue la guía
- THEN identifica qué completar, qué valida cada comando, cómo registrar cambios pendientes y cómo renovar una revisión obsoleta, sin depender de capacidades de Clue no integradas.

#### Scenario: validar la implementacion
- GIVEN pruebas en repositorios temporales con herramientas reales
- WHEN se ejecutan los casos acordados
- THEN la evidencia identifica caso, resultado, versión y límites; las aprobaciones fixture no se atribuyen a cambios reales ni a un piloto humano.
