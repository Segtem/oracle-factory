# Capability: cli

## ADDED Requirements

### Requirement: los errores dicen qué pasó y cómo seguir
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
Tipo: funcional
Si `python fabrica.py` corre con un intérprete sin las dependencias de Factory y el clon tiene `.venv/bin/python`, `fabrica.py` SHALL volver a ejecutarse con ese intérprete y los mismos argumentos.

#### Scenario: python del sistema
- GIVEN un clon con `.venv` y un intérprete sin `oracle-metalenguaje`
- WHEN se ejecuta `python fabrica.py estado ID` con ese intérprete
- THEN el comando corre con `.venv/bin/python` y termina como si se hubiera llamado así

### Requirement: el resumen se ve con formato
Tipo: funcional
`resumen --ver` SHALL mostrar `.factory/resumen.md` con `glow` cuando esté instalado y la salida sea una terminal, y como texto en cualquier otro caso. No SHALL escribir otra cosa que lo que ya escribe `resumen`.

#### Scenario: sin glow
- GIVEN un sistema sin `glow`
- WHEN se ejecuta `resumen --ver`
- THEN el contenido del resumen sale como texto por la salida estándar

### Requirement: estado calcula y ofrece el próximo paso
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
Tipo: no funcional
Sin terminal interactiva, con `--agente` o con la salida redirigida, `estado` SHALL sólo imprimir el próximo paso, sin menú ni ejecución.

#### Scenario: agente
- GIVEN un agente que ejecuta `oracle-factory --agente x estado ID`
- WHEN el próximo paso es cerrar
- THEN se imprime el paso y no se pregunta ni se ejecuta nada
