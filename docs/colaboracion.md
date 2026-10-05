# Dos personas, dos agentes, un producto

El acuerdo de trabajo es sencillo: cada frente tiene una persona responsable, un escritor activo y su propio checkout. Las personas acuerdan el reparto y los relevos; los agentes implementan, prueban y preparan evidencia dentro de ese alcance. Una persona integra las entregas en orden y decide con el equipo qué se acepta.

Este protocolo usa Factory 0.1.0a3, Oracle Task 0.2.0, Oracle Clue 0.1.0a1 y Oracle 0.38.1. La demostración cubre Linux. Los comandos de Git y las CLI comprueban aspectos concretos; la asignación y la recepción de un relevo son acuerdos humanos. Un campo `RESPONSABLE` no bloquea a otro proceso.

## 1. Acordar el reparto antes de escribir

Cada cambio tiene una tarea y un paquete OpenSpec. Dos trabajos independientes tienen IDs distintos, aunque pertenezcan a la misma entrega. Si trabajan sobre el mismo cambio, designen un único ejecutor que muta sus registros; la otra persona puede revisar una instantánea. Para implementar simultáneamente, separen frentes con interfaces y dependencias explícitas.

Creen cada cambio en Factory y completen propuesta/spec antes de implementarlo:

```bash
oracle-factory --proyecto /ruta/producto nuevo --capacidad api "Agregar consulta de notas"
oracle-factory --proyecto /ruta/producto nuevo --capacidad interfaz "Mostrar notas en pantalla"
oracle-factory --proyecto /ruta/producto listar
```

Copien [reparto.md](plantillas/colaboracion/reparto.md) a `tareas/ID_COMPLETO/reparto.md`. Completen persona, agente/sesión, ID, base, rama, checkout, rutas, interfaces, dependencias, revisor e integrador. Ambos confirman el acuerdo por el canal que ya usan y el escritor lo registra. Pueden usar `tasks note ID_COMPLETO "Reparto acordado; ver reparto.md" --proyecto /ruta/producto` para dejar la referencia. El grafo de Task muestra menciones; no comprueba dependencias.

Una persona acepta propuesta/spec con `oracle-factory --proyecto /ruta/producto aprobar-spec ID_COMPLETO`. Después se ejecuta `importar ID_COMPLETO`, se eligen medidas con `medir` y se conserva `sin_medir` donde falta cobertura. Confirmar y compartir estos documentos permite que ambos frentes partan del acuerdo conocido. Preparar una plantilla no equivale a aceptarla.

| Ejemplo | Persona y agente | Escribe | Depende de |
| --- | --- | --- | --- |
| Consulta | A / sesión A1 | API y pruebas de API | Contrato de respuesta acordado |
| Pantalla | B / sesión B1 | Vista y pruebas de vista | Mismo contrato; commit de API para integrar |
| Integración | A, por acuerdo de ambas | Candidato y registros de sus gates | Entregas identificadas de A y B |

La interfaz compartida también es alcance: cambiar `titulo` por `nombre` puede romper la pantalla aunque Git fusione archivos distintos sin conflicto. Si aparece una superposición, detengan sólo ese trabajo, acuerden orden o nuevo reparto y registren la decisión antes de editar.

## 2. Aislar cada frente

En una máquina, desde un repositorio limpio con el acuerdo confirmado, creen worktrees con ramas distintas. Sustituyan `BASE_ACORDADA` por el hash real registrado:

```bash
git worktree add -b trabajo/persona-a ../producto-a BASE_ACORDADA
git worktree add -b trabajo/persona-b ../producto-b BASE_ACORDADA
git worktree add -b trabajo/integracion ../producto-integracion BASE_ACORDADA
git worktree list
```

Cada agente usa la ruta absoluta de su checkout con `--proyecto`. Los worktrees comparten objetos y referencias Git, pero separan archivos de trabajo, HEAD e índice; no usen la misma rama en dos frentes. Factory toma la huella del checkout entero: cambiar otra spec allí puede invalidar una revisión. Separar carpetas de tareas dentro del mismo checkout no resuelve eso.

En máquinas distintas, cada persona usa un clone propio del repositorio acordado:

```bash
git clone URL_DEL_REPOSITORIO producto-a
git -C producto-a switch -c trabajo/persona-a BASE_ACORDADA
```

La otra persona usa su propia carpeta/rama. Compartan commits mediante el remoto acordado; `git fetch origin` actualiza referencias, pero no modifica el checkout ni confirma un relevo. El envío de ramas debe estar autorizado por el equipo. Los registros locales de Task no se sincronizan por sí solos. Un clon de un proyecto Factory sin cambios todavía no trae `tareas/` (Git no versiona carpetas vacías): ejecuten `oracle-factory init`, que no sobrescribe nada.

Antes de recibir una entrega, revisen `git status --short`, el ID completo y el commit ofrecido. No integren encima de trabajo pendiente. Si estuvieron desconectados, reconcilien asignaciones y referencias antes de continuar. Ante dos tareas nuevas con el mismo ID, conserven ambos originales, creen una identidad nueva para una de ellas y actualicen todas sus referencias —incluido su paquete Factory si existe— con revisión humana. No fusionen dos identidades como si fueran la misma tarea. Esa migración no tiene un comando automático en este corte; el caso C4 de la demostración la recorre para una tarea Task (reservar el ID nuevo con `tasks new`, mover el registro con `git mv`, actualizar referencias y comprobar con `tasks refs`) y para un cambio Factory que todavía no tiene la spec aceptada (crear el cambio nuevo con `nuevo`, trasladar su propuesta y su spec, retirar el que choca y comprobar con `listar`). Si el cambio ya tenía spec aceptada o requisitos importados, la aceptación está ligada a las rutas del ID viejo: hay que aceptar la spec otra vez e importar de nuevo, y eso la demostración no lo observa.

## 3. Entregar y retomar sin perder contexto

Copien [relevo.md](plantillas/colaboracion/relevo.md) a un nombre nuevo dentro de la tarea, por ejemplo `relevo-a1-b1.md`. Registren:

- Base y HEAD completos, rama y checkout; qué se terminó y qué archivos siguen pendientes.
- Comandos de prueba, resultados, artefactos y SHA-256; bloqueos y decisiones humanas pendientes.
- Emisor, receptor, próxima acción y estado de recepción.

El emisor detiene las escrituras de ese frente al ofrecer el relevo. El receptor lee la entrega sobre el commit indicado y confirma recepción; el escritor registra el cambio de responsable antes de que el receptor edite. Si no puede confirmar, el frente queda en espera o se acuerda cancelar la entrega y devolverlo al emisor. La ausencia de respuesta no es recepción.

Si se interrumpe una sesión, inspeccionen el proceso y el checkout antes de retomar. Conserven cambios sin commit y cualquier índice pendiente. Un lock residual de `medir` no informa por sí solo si el proceso sigue vivo: verifiquen que terminó, acuerden quién recupera el trabajo y documenten la retirada de ese archivo concreto. Su antigüedad no autoriza borrarlo. El lock sólo cubre ciertas operaciones locales de `medir`, no todas las escrituras de Factory ni otros clones.

Para que dos revisores aporten notas a la vez, usen archivos nuevos por autor/sesión; el escritor designado incorpora las referencias a `TAREA.md`. Task reemplaza ese documento atómicamente, pero dos lecturas seguidas de escritura pueden perder una actualización. No ejecuten `tasks note` o mutaciones de Factory concurrentes sobre el mismo registro.

## 4. Revisar el candidato de la otra persona

Confirmen el producto y mantengan estable el checkout de revisión. Elijan una base explícita que difiera de HEAD; no supongan que `HEAD~1` representa todo el trabajo. Seleccionen propuesta/spec y evidencia que necesite quien revisa.

```bash
oracle-clue preparar --repo /ruta/producto-a --base BASE_DE_REVISION --contexto openspec/changes/ID_COMPLETO/specs/api/spec.md --salida /ruta/revisiones/entrega-a-contexto.json
```

La carpeta de salida debe existir fuera del repo revisado y el archivo debe ser nuevo. La persona B, con ayuda de su agente, lee el paquete y produce un informe conforme al [schema de Clue 0.1.0a1](https://github.com/Segtem/oracle-clue/blob/v0.1.0a1/docs/hallazgos.schema.json). Clue prepara contexto y valida integridad; esta versión no produce análisis de IA. Un informe vacío no acepta la entrega. Las omisiones exigen declarar revisión incompleta y sus límites.

```bash
oracle-clue validar /ruta/revisiones/entrega-a-informe.json --paquete /ruta/revisiones/entrega-a-contexto.json --repo /ruta/producto-a
```

Una persona decide cada hallazgo y registra el triage por separado, según el [schema de triage](https://github.com/Segtem/oracle-clue/blob/v0.1.0a1/docs/triage.schema.json). No cambien el estado `pendiente` del informe original para simular decisiones:

```bash
oracle-clue validar /ruta/revisiones/entrega-a-informe.json --paquete /ruta/revisiones/entrega-a-contexto.json --repo /ruta/producto-a --triage /ruta/revisiones/entrega-a-decisiones.json
```

Conserven paquete, informe y triage originales con sus hashes. El paquete incluye la ruta absoluta del repo: en otro checkout, incluso con el mismo HEAD, Clue exige un paquete e informe correspondientes a esa ruta. Pueden revisar a distancia el paquete original y validarlo en origen mientras permanezca estable. Si regeneran el paquete en otro checkout, la persona reevalúa el contexto y vincula el nuevo informe; no editen huellas del anterior para hacerlo pasar.

Una corrección cambia el candidato: vuelvan a preparar y revisar. Clue valida la integridad del triage, no autentica a su actor ni decide que la resolución sea suficiente. Factory tampoco valida automáticamente los schemas de Clue; registrar un informe en Factory es un paso posterior y humano.

## 5. Integrar una entrega por vez

El integrador copia [integracion.md](plantillas/colaboracion/integracion.md) a la tarea de la entrega. Registra orden, commits ofrecidos, revisiones, decisiones y resultado. Desde un checkout limpio, incorpora el primer commit/rama con `git merge --no-ff COMMIT_ENTREGA_A`; luego incorpora B según el orden acordado. Ante conflicto, conserva los commits originales y acuerda la resolución con los responsables. Ejecuta también las pruebas de compatibilidad después de un merge limpio.

Los archivos `factory.json` de las ramas son antecedentes del flujo, no votos que se puedan sumar. Si divergen, preserven copias y acuerden cuál continúa la historia del mismo cambio; no elijan el JSON con la fase más avanzada. No reconstruyan aprobaciones ni borren registros para forzar un verde. Para cambios distintos conserven ambos paquetes y evalúen cada cambio pendiente sobre el candidato integrado.

```bash
oracle-factory --proyecto /ruta/producto-integracion estado ID_COMPLETO
```

Un merge, rebase o commit nuevo cambia HEAD y vuelve obsoletos revisión/juicio anteriores. Un cambio de propuesta/spec exige nueva aceptación e importación; nuevas medidas invalidan revisión/juicio. Los nuevos requisitos vuelven a quedar sin medir cuando corresponde. Terminen las correcciones y los documentos del producto antes de fijar el candidato final.

Sobre ese candidato, ejecuten las pruebas y el sensor, registrando comando, entradas, salida y commit observado. Renueven la revisión de Clue sobre el resultado integrado. Guarden los artefactos junto al cambio —por ejemplo como adjuntos de su tarea, con nombres por versión— antes de registrar su decisión en Factory. Agregar un adjunto bajo `tareas/` no cambia la huella de archivos del producto, pero hacer un commit nuevo sí cambia HEAD.

Una vez que la persona resolvió los hallazgos y acepta la revisión, registra la decisión. Estos comandos son pasos humanos del proyecto real; las frases de confirmación deben escribirlas las personas:

```bash
oracle-factory --proyecto /ruta/producto-integracion revision ID_COMPLETO --informe tareas/ID_COMPLETO/revision-candidato.json --revisor "NOMBRE_REAL" --decision aprobar --hallazgos-abiertos 0
oracle-factory --proyecto /ruta/producto-integracion juzgar ID_COMPLETO --con tareas/ID_COMPLETO/hechos-candidato.json
oracle-factory --proyecto /ruta/producto-integracion estado ID_COMPLETO
oracle-factory --proyecto /ruta/producto-integracion cerrar ID_COMPLETO
```

Si quedan hallazgos, registren `--decision cambios` con la cantidad real y corrijan antes de repetir el ciclo. No usen `tasks close` para saltar los gates de Factory. Oracle sólo juzga hechos y requisitos medidos; un verde de seguimiento de Task no prueba que el producto funcione. Factory todavía no ejecuta el sensor ni demuestra automáticamente que un JSON venga del candidato actual.

El commit que archiva el cierre puede ser posterior al commit del producto juzgado. Registre ambos en la entrega sin presentarlos como idénticos. Si el producto vuelve a cambiar, corresponde otro ciclo; el historial de cierre anterior no aprueba código nuevo.

## Demostración y piloto

Desde un checkout de Factory, use un Python con sus dependencias fijadas y Clue instalado por separado. Por ejemplo, prepare un entorno local con `uv venv .venv` y `uv pip install --python .venv/bin/python -e .`, e instale `oracle-clue==0.1.0a1` como herramienta. Ejecute:

```bash
.venv/bin/python tools/verify_collaboration.py --clue oracle-clue --salida /tmp/evidencia-colaboracion-01
```

La salida debe ser una carpeta nueva. El arnés ejecuta Git, Task, Clue, Factory y Oracle en repositorios temporales, sin publicar ramas. Guarda `resultado.json`, `hechos.json`, comandos, versiones y artefactos con hashes. Los repositorios temporales se eliminan al terminar; los logs incluyen sus rutas originales y los artefactos preservados permiten inspeccionar lo observado. Las confirmaciones e informes son fixtures rotulados, válidos sólo dentro de esa simulación.

| Caso | Comprobación automatizada | Lo que requiere personas |
| --- | --- | --- |
| C1 | Aislamiento de archivos/índice/HEAD y conservación de dos entregas | Acordar reparto |
| C2 | Conflicto textual e incompatibilidad sin conflicto; resolución fixture conservada | Decidir cómo resolver y reasignar |
| C3 | Plantilla de relevo, pendientes preservados y recuperación de lock fixture | Confirmar recepción y fin de proceso real |
| C4 | Clones con registros divergentes, conciliación y referencias | Reconciliar identidades/asignaciones reales |
| C5 | Informe/triage válido y rechazos por cambio de ruta o versión | Calidad de revisión y resolución de hallazgos |
| C6 | Revisión/juicio obsoletos tras integrar y renovación del candidato | Autorizar integración y revisión real |
| C7 | Cambio de spec/medidas invalida gates | Aceptar contrato y pertinencia de medidas |
| C8 | Cierre rechazado sin aprobación, revisión o cobertura | Confirmar cierre real |
| C9 | Casos exactos, sin duplicados/omisiones, hashes y límites | Pilotear y valorar facilidad de uso |

Una ejecución exitosa sólo acredita esos casos. Para probar la experiencia, dos personas completan [piloto.md](plantillas/colaboracion/piloto.md) con sus agentes: reparto, una entrega por persona, un relevo, un solapamiento y la integración. Registren tiempos de espera observados, confusiones, decisiones y evidencia; no infieran productividad general de un piloto. Hasta realizarlo, esa parte queda pendiente y sin medir.
