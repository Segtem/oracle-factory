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

### Requirement: la plantilla de un cambio nuevo trae la forma de OpenSpec
Origen: 20261015-105600-cli-piloto · cli_c28628c0586fe682a.la_plantilla_de_un_cambio_nuevo_trae_la_forma_de_openspec
Tipo: funcional
`oracle-factory nuevo` SHALL crear una spec con `## ADDED Requirements` y un requisito con `Tipo: funcional`, y una propuesta cuyas decisiones humanas no nombran a una persona en particular. Mientras tengan TODO, `aprobar-spec` SHALL seguir rechazándolas.

#### Scenario: un cambio recién creado
- GIVEN un proyecto Factory
- WHEN se crea un cambio con nuevo
- THEN la spec trae ## ADDED Requirements y Tipo: funcional, la propuesta no nombra a Brian, y aprobar-spec la rechaza por los TODO

#### Scenario: la plantilla completada se importa
- GIVEN un cambio recién creado cuyos TODO se completaron sin tocar la estructura de la plantilla
- WHEN se aprueba la spec y se importan los requisitos
- THEN se importa un requisito funcional

### Requirement: medir dice qué medidas reemplaza
Origen: 20261015-105600-cli-piloto · cli_c28628c0586fe682a.medir_dice_que_medidas_reemplaza
Tipo: funcional
Cuando un requisito ya tiene medidas y `medir` le asocia otras, `medir` SHALL nombrar las medidas que tenía y las nuevas, y SHALL señalar cada medida que deja de usar y que ningún otro requisito del proyecto usa.

#### Scenario: reemplazar las medidas de un requisito
- GIVEN un requisito medido con dos medidas, una de ellas usada también por otro requisito
- WHEN se le asocia una sola medida distinta
- THEN la salida nombra las dos anteriores y la nueva, y señala sin requisito sólo la que nadie más usa

#### Scenario: la primera vez no hay nada que reemplazar
- GIVEN un requisito sin medidas
- WHEN se le asocian medidas
- THEN la salida no habla de reemplazo

### Requirement: medir --listar separa las medidas del proyecto de las del catálogo base
Origen: 20261015-105600-cli-piloto · cli_c28628c0586fe682a.medir_listar_separa_las_medidas_del_proyecto_de_las_del_catalogo_base
Tipo: funcional
`medir ID --listar` SHALL mostrar primero las medidas del proyecto, con archivo, umbral, ámbito y alcance, y después, en una sección propia y una línea cada una, las del catálogo base de Oracle.

#### Scenario: un proyecto con medidas propias
- GIVEN un proyecto con medidas propias y el catálogo base de Oracle
- WHEN se lista con medir --listar
- THEN las medidas del proyecto van primero y con su detalle, y las del catálogo base van después, en su sección, una por línea

### Requirement: la_cli_se_comporta_igual_tras_partirse
Origen: 20261028-222656-b2m-clidividido · cli_c42e351e8ad805f36.la_cli_se_comporta_igual_tras_partirse
Tipo: funcional
El sistema DEBE conservar, tras partir cli.py en módulos, todos los nombres que oracle_factory.cli exportaba con las mismas firmas, la misma ayuda en cada subcomando y el mismo comportamiento ante las pruebas existentes, sin modificarlas.

#### Scenario: los nombres y las firmas
- DADO la lista de nombres de primer nivel de cli y la firma de cada función, tomada antes de mover nada
- CUANDO se parte cli.py
- ENTONCES todos los nombres siguen en oracle_factory.cli, son los mismos objetos que usa el código movido y sus firmas son idénticas

#### Scenario: la ayuda
- DADO el texto de ayuda de oracle-factory y de cada subcomando con un ancho de terminal fijo, tomado antes de mover nada
- CUANDO se parte cli.py
- ENTONCES la ayuda de cada uno es idéntica

#### Scenario: las pruebas existentes
- DADO la suite completa anterior al cambio
- CUANDO se corre sobre el código partido
- ENTONCES pasan todas, sin ninguna omitida

### Requirement: lo_movido_lee_a_cli_en_el_momento_de_usarlo
Origen: 20261028-222656-b2m-clidividido · cli_c42e351e8ad805f36.lo_movido_lee_a_cli_en_el_momento_de_usarlo
Tipo: funcional
El sistema DEBE hacer que el código movido a otros módulos lea los valores y las funciones de cli en el momento de usarlos, de modo que un valor cambiado en cli, como la raíz del proyecto en una prueba, valga también para lo movido.

#### Scenario: un valor cambiado en cli
- DADO un valor de cli cambiado temporalmente, como su raíz o una función auxiliar
- CUANDO se ejecuta una función movida que lo usa
- ENTONCES usa el valor cambiado y no el original

#### Scenario: ningún nombre de cli queda copiado
- DADO el código fuente de los módulos nuevos
- CUANDO se lo analiza
- ENTONCES ninguna función movida usa un nombre definido en cli como si fuera propio, sino a través de cli

### Requirement: ningun_archivo_fuente_pasa_del_tope
Origen: 20261028-222656-b2m-clidividido · cli_c42e351e8ad805f36.ningun_archivo_fuente_pasa_del_tope
Tipo: funcional
El sistema DEBE mantener cada archivo fuente del paquete por debajo de 200000 bytes y cli.py por debajo de 160000, para quedar lejos del límite de 256000 de Oracle Clue.

#### Scenario: los tamaños actuales
- DADO el paquete oracle_factory tras partir cli.py
- CUANDO se miden sus archivos fuente
- ENTONCES cli.py mide menos de 160000 bytes y ninguno mide 200000 o más

#### Scenario: un archivo que crece de más
- DADO un archivo fuente del paquete que supera 200000 bytes
- CUANDO se corre la prueba de tamaños
- ENTONCES falla nombrando el archivo, su tamaño y el límite de Clue
