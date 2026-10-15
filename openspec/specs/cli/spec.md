# Capability: cli

<!-- Generada por Oracle Factory al cerrar cada cambio: no se edita a mano. -->

## Requirements

### Requirement: los errores dicen qué pasó y cómo seguir
Origen: 20261008-123018-cli-humana · cli_c3bcb178e77c1d111.los_errores_dicen_que_paso_y_como_seguir
Tipo: funcional
Cuando Factory rechaza algo por una causa que conoce, el mensaje SHALL nombrarla y decir cómo seguir:
- al rechazar una aprobación de revisión, cuáles comprobaciones no cumplen, qué hallazgos siguen abiertos o que la revisión está incompleta;
- en `revision-preparar` sin candidato vigente, un aviso de que el informe queda sin informes de revisores ni evidencia y de qué hacer;
- sin `oracle-metalenguaje` en el intérprete, qué falta y cómo seguir, sin traceback.

#### Scenario: aprobar con una comprobación que falla
- GIVEN un informe guiado con una comprobación en `falla`
- WHEN se pide registrar la revisión con la decisión aprobar
- THEN el rechazo nombra esa comprobación

#### Scenario: falta Oracle
- GIVEN un intérprete sin `oracle-metalenguaje`
- WHEN se ejecuta un comando que lo necesita
- THEN sale un mensaje que nombra el paquete y cómo seguir, sin traceback

### Requirement: fabrica.py usa el entorno del proyecto
Origen: 20261008-123018-cli-humana · cli_c3bcb178e77c1d111.fabrica_py_usa_el_entorno_del_proyecto
Tipo: funcional
Si `python fabrica.py` corre con un intérprete sin las dependencias de Factory y el clon tiene `.venv/bin/python`, `fabrica.py` SHALL volver a ejecutarse con ese intérprete y los mismos argumentos.

#### Scenario: python del sistema
- GIVEN un clon con `.venv` y un intérprete sin `oracle-metalenguaje`
- WHEN se ejecuta `python fabrica.py estado ID` con ese intérprete
- THEN el comando corre con `.venv/bin/python` y termina como si se hubiera llamado así

### Requirement: el resumen se ve con formato
Origen: 20261008-123018-cli-humana · cli_c3bcb178e77c1d111.el_resumen_se_ve_con_formato
Tipo: funcional
`resumen --ver` SHALL mostrar `.factory/resumen.md` con `glow` cuando esté instalado y la salida sea una terminal, y como texto en cualquier otro caso. No SHALL escribir otra cosa que lo que ya escribe `resumen`.

#### Scenario: sin glow
- GIVEN un sistema sin `glow`
- WHEN se ejecuta `resumen --ver`
- THEN el contenido del resumen sale como texto por la salida estándar

### Requirement: estado calcula y ofrece el próximo paso
Origen: 20261008-123018-cli-humana · cli_c3bcb178e77c1d111.estado_calcula_y_ofrece_el_proximo_paso
Tipo: funcional
`estado ID` SHALL calcular el próximo paso según lo que falta:
- aprobar la spec;
- importar;
- confirmar las medidas propuestas;
- elegir medidas;
- pedir una revisión;
- revisar;
- juzgar;
- cerrar.

En una terminal y sin `--agente`, cuando ese paso es un comando completo, `estado` SHALL ofrecer ejecutarlo desde un menú; elegir salir, o cualquier otra respuesta, no ejecuta nada.

#### Scenario: listo para cerrar
- GIVEN un cambio con revisión aprobada y Oracle en verde
- WHEN la persona ejecuta `estado ID` en una terminal
- THEN el próximo paso es `oracle-factory cerrar ID` y elegirlo en el menú lleva al menú de cierre

#### Scenario: medidas propuestas
- GIVEN un cambio con medidas propuestas por el agente sin confirmar
- WHEN se ejecuta `estado ID`
- THEN el próximo paso es `oracle-factory medir ID --confirmar`

### Requirement: el próximo paso no se ejecuta solo
Origen: 20261008-123018-cli-humana · cli_c3bcb178e77c1d111.el_proximo_paso_no_se_ejecuta_solo
Tipo: no funcional
Sin terminal interactiva, con `--agente` o con la salida redirigida, `estado` SHALL sólo imprimir el próximo paso, sin menú ni ejecución.

#### Scenario: agente
- GIVEN un agente que ejecuta `oracle-factory --agente x estado ID`
- WHEN el próximo paso es cerrar
- THEN se imprime el paso y no se pregunta ni se ejecuta nada

### Requirement: estado se lee como JSON
Origen: 20261013-153440-cli-json · cli_c38d280a51dea748e.estado_se_lee_como_json
Tipo: funcional
`oracle-factory estado ID --json` SHALL imprimir en stdout un único objeto JSON con `esquema` igual a `oracle-factory.estado/1` y, como mínimo: `id`, `titulo`, `fase`, `modo`, `candidato` (el vigente o null), `requisitos` (cada uno con sus medidas y la decisión que las respalda), `pendientes`, `proximo_paso`, `decisiones` (spec, revisión, cierre y abandono, cada una con actor, tipo de actor, forma, cuándo y motivo si lo tiene), `revision` y `oracle` (cada uno con el commit al que se refiere y si sigue vigente para el producto actual) y `aceptados`. SHALL NOT ofrecer ejecutar el próximo paso ni leer de la terminal, y SHALL NOT escribir archivos.

#### Scenario: un cambio en revisión
- GIVEN un cambio con medidas confirmadas y una revisión registrada
- WHEN se pide estado con --json
- THEN la salida es un objeto JSON con el esquema, las medidas con quién las confirmó, la revisión con su commit y vigencia, y el próximo paso, sin preguntar nada

#### Scenario: la revisión vence
- GIVEN un cambio con una revisión registrada
- WHEN cambia el producto y se pide estado con --json
- THEN la revisión figura como no vigente

#### Scenario: un cambio abandonado
- GIVEN un cambio abandonado
- WHEN se pide estado con --json
- THEN la fase es abandonada, la decisión de abandono tiene su motivo y el próximo paso es null

### Requirement: donde y resumen se leen como JSON
Origen: 20261014-204205-donde-no-valido · cli_cbf3493a6abe9eeec.donde_y_resumen_se_leen_como_json
Tipo: funcional
`oracle-factory donde ID --json` SHALL imprimir un objeto con `esquema` `oracle-factory.donde/1` y la lista de artefactos, cada uno con gate, ruta, situación (`existe`, `ausente`, `historico` o `no_valido`) y nota. `historico` es lo que hay en la carpeta de la tarea además de su nota (`TAREA.md`); `no_valido`, una entrada del registro del cambio que no se puede leer como ruta. `ausente` es un artefacto que el cambio espera y no está en el disco: los fijos de su convención (propuesta, diseño, tareas, la nota de la tarea) o uno que un registro nombra, como los hechos de un juicio; lo que todavía no se produjo, como la evidencia de un candidato sin sensor corrido, no se lista. `oracle-factory resumen --json` SHALL imprimir un objeto con `esquema` `oracle-factory.resumen/1` con lo vigente por capacidad (cada requisito con su requisito de Oracle, tipo, medidas, veredicto al cerrar y cambio de origen), los cambios abiertos con sus pendientes, los abandonados con su motivo, las carpetas sin registro, los riesgos aceptados y los límites; SHALL NOT escribir el resumen en disco, y las mismas entradas SHALL dar los mismos bytes.

#### Scenario: donde con un artefacto ausente
- GIVEN un cambio con un juicio registrado cuyos hechos ya no están
- WHEN se pide donde con --json
- THEN esos hechos figuran con gate juicio y situación ausente, y cada artefacto que no es histórico ni inválido figura como existe si está en el disco y como ausente si no

#### Scenario: donde con una entrada inválida
- GIVEN un cambio cuyo registro tiene un campo con un valor que no es una ruta, y archivos en la carpeta de su tarea además de la nota
- WHEN se pide donde con --json
- THEN ese campo figura con situación no_valido, esos archivos figuran como historico, y los demás artefactos se siguen listando

#### Scenario: resumen sin escribir
- GIVEN un proyecto con un cambio cerrado y uno abierto con dos requisitos que tienen el mismo pendiente de medidas
- WHEN se pide resumen con --json dos veces
- THEN las dos salidas son idénticas, nombran el requisito de Oracle vigente del cambio cerrado y el cambio abierto con los pendientes de estado, con los de medidas que dicen lo mismo de varios requisitos juntos en un renglón, y .factory/resumen.md no cambia

### Requirement: la salida de texto no cambia y los errores no se mezclan con el JSON
Origen: 20261013-153440-cli-json · cli_c38d280a51dea748e.la_salida_de_texto_no_cambia_y_los_errores_no_se_mezclan_con_el_json
Tipo: funcional
Sin `--json`, `estado`, `donde` y `resumen` SHALL imprimir lo mismo que antes de este cambio. Con `--json`, un error SHALL ir a stderr con código 1 y stdout SHALL quedar vacío.

#### Scenario: el texto sigue igual
- GIVEN un cambio
- WHEN se pide estado, donde y resumen sin --json
- THEN la salida es la misma que antes de este cambio

#### Scenario: un cambio inexistente
- WHEN se pide estado con --json de un ID que no existe
- THEN stdout está vacío, el error va a stderr y el código es 1
