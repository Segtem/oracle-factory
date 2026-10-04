# Capability: colaboracion

Esta spec define el entregable propuesto (guía, plantillas y demostración), no funcionalidades ya disponibles. SHALL expresa una obligación del entregable; las acciones humanas indicadas no son bloqueos de software.

### Requirement: reparto explicito del trabajo
El protocolo SHALL registrar para cada frente el ID de tarea/cambio, persona responsable, agente o sesión, base Git, rama, checkout, alcance e interfaces compartidas, dependencias, revisor, integrador y próximo paso, con un único escritor activo de sus registros.

#### Scenario: dos frentes independientes
- GIVEN dos cambios aceptados y dos personas con sus agentes
- WHEN se reparte el trabajo
- THEN cada frente tiene registro completo y distinto checkout/rama, y las dependencias se enlazan por ID completo sin atribuir al grafo de Task validación de dependencias.

#### Scenario: mismo cambio o alcance superpuesto
- GIVEN dos participantes que quieren modificar el mismo registro o interfaz
- WHEN detectan la superposición
- THEN acuerdan un escritor y orden, o separan cambios con contratos explícitos antes de editar, dejando constancia de la decisión humana.

### Requirement: aislamiento y sincronizacion explicitos
La guía SHALL describir worktrees en una máquina y clones en máquinas distintas, y distinguir aislamiento de archivos, intercambio mediante Git y acuerdo humano sobre la asignación.

#### Scenario: avance paralelo
- GIVEN dos checkouts desde una base conocida
- WHEN A modifica su frente mientras B trabaja en el suyo
- THEN el índice, HEAD y archivos de B no cambian por la edición de A y la entrega registra el commit que debe incorporar la otra persona.

#### Scenario: dos clones sin sincronizar
- GIVEN registros divergentes o IDs iguales creados independientemente
- WHEN se prepara el intercambio
- THEN el protocolo exige reconciliar identidad, referencias y asignación antes de integrar, preservando ambas contribuciones y sin prometer reserva global por crear una tarea local.

### Requirement: relevo recuperable
La plantilla de relevo SHALL registrar emisor, receptor, tarea, rama, base/HEAD, archivos pendientes, alcance completado, pruebas y evidencia con rutas/huellas, bloqueos, decisiones humanas pendientes y próxima acción; SHALL distinguir entrega propuesta de recepción confirmada.

#### Scenario: cambio de persona o sesion
- GIVEN un frente en curso
- WHEN A entrega y B confirma recepción sobre el commit indicado
- THEN el registro identifica a B como escritor siguiente, conserva lo pendiente y A deja de mutar ese frente.

#### Scenario: interrupcion sin entrega
- GIVEN una sesión interrumpida o un lock local residual
- WHEN otra persona retoma
- THEN inspecciona procesos, checkout y cambios pendientes, acuerda la reasignación y registra la recuperación sin borrar por tiempo transcurrido el bloqueo ni el trabajo anterior.

### Requirement: revision vinculada a una version
La guía SHALL preparar con Clue una revisión de commits base/HEAD explícitos, conservar paquete e informe originales, separar el triage humano y comprobar su vigencia antes de registrar la decisión en Factory.

#### Scenario: revision cruzada
- GIVEN un candidato confirmado y contexto seleccionado
- WHEN la otra persona revisa con asistencia de su agente
- THEN el informe corresponde al paquete validado, los hallazgos conservan sus IDs y la persona registra decisiones separadas, sin interpretar un informe vacío como aprobación.

#### Scenario: otro checkout o candidato modificado
- GIVEN un paquete que incluye la ruta del repositorio original
- WHEN cambia HEAD, contexto o ruta de checkout
- THEN se valida en el checkout original conservado o se genera un nuevo paquete e informe correspondiente, sin editar huellas para aparentar equivalencia ni atribuir a Factory validación automática de Clue.

### Requirement: integracion serializada y evidencia vigente
El protocolo SHALL designar un integrador humano por candidato, serializar sus mutaciones de Factory y verificar el producto resultante antes del cierre.

#### Scenario: dos entregas listas
- GIVEN A y B con entregas identificadas
- WHEN se integran en el orden acordado
- THEN se conservan ambos aportes, se registra el commit resultante y se ejecutan pruebas y revisión sobre ese candidato; un merge sin conflictos textuales no sustituye comprobar compatibilidad.

#### Scenario: cambia el candidato revisado
- GIVEN una revisión o juicio previo
- WHEN un merge, rebase, corrección, cambio de spec o medidas altera el contexto aplicable
- THEN se comprueba estado y se renuevan los gates invalidados; si cambió proposal/spec se requiere nueva aceptación e importación, y no se copia un verde de una rama para cerrar otra versión.

#### Scenario: falta autoridad o cobertura
- GIVEN un informe favorable pero falta decisión humana, cobertura o evidencia vigente
- WHEN se considera cerrar el cambio
- THEN la tarea permanece abierta y se explicita el pendiente, usando cerrar de Factory para el cierre del flujo y sin sustituirlo por close del tracker.

### Requirement: demostracion reproducible con limites
El entregable SHALL incluir un arnés en repositorios temporales, hechos observados por caso y una matriz de cobertura que distinga pruebas automáticas de pasos humanos pendientes.

#### Scenario: evaluar el protocolo
- GIVEN versiones y casos fijados en design.md
- WHEN se ejecuta el arnés
- THEN registra entradas, comandos, códigos, commits y artefactos de cada caso, falla ante casos omitidos o fallidos y deja sin medir lo no observado, sin tratar aprobaciones fixture como autorizaciones reales.

#### Scenario: validar la experiencia con personas
- GIVEN la demostración automatizada completa
- WHEN dos personas realizan el piloto con sus agentes
- THEN se registran relevos, bloqueos, decisiones y dificultades observadas por separado; hasta realizarlo, la usabilidad humana permanece pendiente y no se declara demostrada por la simulación.
