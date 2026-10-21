# Capability: revisores

<!-- Generada por Oracle Factory al cerrar cada cambio: no se edita a mano. -->

## Requirements

### Requirement: pedir una revisión del candidato actual
Origen: 20261007-192608-revisores · revisores_c466ac292a9f99ce6.pedir_una_revision_del_candidato_actual
Tipo: funcional
`pedir-revision ID --a NOMBRE` SHALL preparar el checkout y el paquete de Oracle Clue del candidato actual en sus rutas (`ruta ID checkout` y `ruta ID clue`), lanzar el comando del revisor NOMBRE con el pedido, esperar a que termine y, si el informe es válido para ese paquete, guardarlo en la carpeta `revision/` del candidato junto con el pedido usado.

#### Scenario: revisión exitosa
- GIVEN un cambio con el producto confirmado y un revisor configurado que deja un informe válido
- WHEN se ejecuta `pedir-revision ID --a ese-revisor`
- THEN el informe y el pedido quedan en `revision/` del candidato y Factory informa cuántos hallazgos trajo

### Requirement: revisores configurables
Origen: 20261007-192608-revisores · revisores_c466ac292a9f99ce6.revisores_configurables
Tipo: funcional
Los revisores SHALL declararse en `.factory/config.json` bajo `revisores`, cada uno con su comando (lista de argumentos con marcadores), proveedor, modelo y tope en minutos; un revisor no declarado o una configuración inválida SHALL rechazarse antes de preparar nada, mostrando cómo declararlo.

#### Scenario: revisor no declarado
- GIVEN una configuración sin el revisor `x`
- WHEN se ejecuta `pedir-revision ID --a x`
- THEN se rechaza con un ejemplo de configuración y no se crea checkout, paquete ni evento

### Requirement: el pedido se genera desde el cambio
Origen: 20261007-192608-revisores · revisores_c466ac292a9f99ce6.el_pedido_se_genera_desde_el_cambio
Tipo: funcional
El pedido SHALL generarse desde una plantilla versionada con la propuesta, la spec, el paquete, el checkout, el formato de informe esperado y las vueltas anteriores del cambio; un proyecto SHALL poder reemplazar la plantilla con `.factory/pedido-revision.md`, y `--pedir` SHALL agregar indicaciones al final.

#### Scenario: plantilla del proyecto e indicaciones
- GIVEN un proyecto con `.factory/pedido-revision.md` propio
- WHEN se pide una revisión con `--pedir "mirá la concurrencia"`
- THEN el pedido usado sale de esa plantilla, termina con esas indicaciones y queda guardado junto al informe

### Requirement: lo que sale mal no se guarda como informe
Origen: 20261007-192608-revisores · revisores_c466ac292a9f99ce6.lo_que_sale_mal_no_se_guarda_como_informe
Tipo: funcional
Si el revisor no deja informe, si Clue lo rechaza o si se pasa del tope, `pedir-revision` SHALL terminar con error sin guardar nada en `revision/`, conservando la salida del revisor para inspeccionar; y si el producto tiene cambios sin commit SHALL rechazarse antes de lanzar al revisor.

#### Scenario: informe que Clue rechaza
- GIVEN un revisor que deja un informe con una ubicación fuera del diff
- WHEN se ejecuta `pedir-revision`
- THEN termina con error, `revision/` no cambia y la salida del revisor queda disponible

#### Scenario: tope superado
- GIVEN un revisor que no termina dentro del tope
- WHEN se ejecuta `pedir-revision`
- THEN se detiene al revisor, termina con error y `revision/` no cambia

### Requirement: el revisor no decide
Origen: 20261007-192608-revisores · revisores_c466ac292a9f99ce6.el_revisor_no_decide
Tipo: no funcional
`pedir-revision` SHALL NOT registrar revisiones, decisiones ni cambios de fase; SHALL dejar en el registro del cambio un evento con el revisor, el proveedor, el modelo, el candidato y el resultado.

#### Scenario: después de una revisión exitosa
- GIVEN un cambio en `requisitos_importados`
- WHEN se pide una revisión que termina bien
- THEN la fase y la revisión registrada no cambian y hay un evento `revision_pedida` con esos datos

### Requirement: las vueltas anteriores se muestran sin decidirse otra vez
Origen: 20261007-192608-revisores · revisores_c466ac292a9f99ce6.las_vueltas_anteriores_se_muestran_sin_decidirse_otra_vez
Tipo: funcional
`revision-preparar` SHALL agregar una comprobación por cada vuelta anterior del mismo cambio (candidato, revisor y hallazgos) sin agregar sus hallazgos al informe ni al borrador de decisiones.

#### Scenario: tres vueltas
- GIVEN un cambio con informes de revisores en tres candidatos sucesivos
- WHEN se prepara la revisión del último
- THEN el informe tiene los hallazgos del último y una comprobación por cada una de las dos vueltas anteriores

### Requirement: este cambio se revisa con pedir-revision
Origen: 20261007-192608-revisores · revisores_c466ac292a9f99ce6.este_cambio_se_revisa_con_pedir_revision
Tipo: no funcional
La revisión independiente de este cambio SHALL pedirse con `pedir-revision`, y sus informes y pedidos SHALL quedar en la carpeta de su candidato.

#### Scenario: el propio cambio
- GIVEN este cambio listo para revisar
- WHEN se consulta la carpeta de su candidato
- THEN tiene al menos un informe de revisor y el pedido con que se obtuvo

### Requirement: el corte de vueltas sigue la severidad
Origen: 20261014-140627-severidad-ausente · revisores_cd964f597ba125312.el_corte_de_vueltas_sigue_la_severidad
Tipo: funcional
Después de guardar un informe, `pedir-revision` SHALL mostrar cuántos hallazgos trae por severidad. Si entre los informes del candidato vigente no queda ningún hallazgo de severidad media o alta sin un riesgo aceptado que coincida, SHALL decir que no hace falta otra vuelta y que los bajos los decide una persona en `revisar`; si queda alguno, SHALL pedir corregirlo y pedir otra vuelta. `estado` SHALL sugerir el mismo próximo paso. Un informe con un hallazgo sin severidad o con una desconocida SHALL NOT guardarse; uno guardado que la pierde SHALL NOT usarse para decidir la vuelta, y `estado` SHALL avisar por qué.

#### Scenario: sólo quedan bajos
- GIVEN un candidato cuyos informes traen sólo hallazgos bajos
- WHEN termina pedir-revision
- THEN la salida cuenta los bajos y sugiere revisar en vez de otra vuelta, y estado sugiere revisar

#### Scenario: queda uno medio
- GIVEN un candidato con un informe que trae un hallazgo medio y otro con sólo bajos
- WHEN termina pedir-revision
- THEN la salida pide corregir el hallazgo medio y pedir otra vuelta, y estado sugiere lo mismo

#### Scenario: un informe sin severidad no se guarda
- GIVEN un revisor que deja un hallazgo sin severidad, o con una que no existe
- WHEN termina pedir-revision
- THEN falla diciendo que Clue rechazó el informe, y revision/ no cambia

#### Scenario: un informe guardado que pierde la severidad
- GIVEN un informe guardado con un hallazgo medio, editado después para quitarle la severidad
- WHEN la persona pide estado
- THEN ese informe no se usa para decidir la vuelta y el aviso dice que no pasa la validación de Clue

### Requirement: un riesgo aceptado persiste entre vueltas
Origen: 20261013-115616-vueltas-severidad · revisores_c54735f6bdc173577.un_riesgo_aceptado_persiste_entre_vueltas
Tipo: funcional
Cuando una persona acepta un riesgo en `revisar`, el registro del cambio SHALL guardarlo con su archivo, título, motivo, persona, fecha y candidato, aunque la revisión termine pidiendo cambios. `pedir-revision` SHALL incluir los riesgos aceptados vigentes del cambio en el pedido a cada revisor. Un hallazgo medio o alto que coincide con un riesgo aceptado SHALL NOT pedir otra vuelta.

#### Scenario: aceptado en una vuelta, presente en el pedido siguiente
- GIVEN una persona que aceptó un riesgo en la revisión de un candidato
- WHEN se pide una revisión del candidato siguiente
- THEN el pedido al revisor nombra ese riesgo, su archivo y su motivo

#### Scenario: un medio aceptado no pide otra vuelta
- GIVEN un riesgo medio aceptado en una vuelta anterior
- WHEN el mismo hallazgo vuelve en el informe del candidato nuevo
- THEN pedir-revision no pide otra vuelta por ese hallazgo

### Requirement: revisar reconoce un riesgo ya aceptado
Origen: 20261013-115616-vueltas-severidad · revisores_c54735f6bdc173577.revisar_reconoce_un_riesgo_ya_aceptado
Tipo: funcional
En `revisar`, un hallazgo con el mismo archivo y el mismo título normalizado (minúsculas, sin puntuación y con espacios simples) que un riesgo aceptado SHALL mostrarse como ya aceptado, con quién, cuándo y por qué. La persona SHALL elegir entre mantenerlo, que lo registra como riesgo aceptado con el mismo motivo, o revocarlo, que lo saca de los aceptados y lo decide como un hallazgo nuevo. Un hallazgo que no coincide SHALL decidirse como hoy.

#### Scenario: mantener un riesgo aceptado
- GIVEN un riesgo aceptado y un hallazgo nuevo que coincide
- WHEN la persona elige mantenerlo
- THEN la decisión del hallazgo es riesgo aceptado con el motivo anterior, y el riesgo sigue vigente

#### Scenario: revocar un riesgo aceptado
- GIVEN un riesgo aceptado y un hallazgo nuevo que coincide
- WHEN la persona elige revocarlo y lo deja abierto
- THEN el riesgo deja de estar aceptado y el hallazgo queda abierto

#### Scenario: un título distinto no coincide
- GIVEN un riesgo aceptado
- WHEN vuelve un hallazgo del mismo archivo con otro título
- THEN revisar lo presenta como un hallazgo nuevo

### Requirement: el paquete de revisión excluye lo que no es producto
Origen: 20261014-000054-paquete-producto · revisores_c90ab53abb4ca96d7.el_paquete_de_revision_excluye_lo_que_no_es_producto
Tipo: funcional
`pedir-revision` SHALL preparar el paquete de Clue excluyendo `.factory/`, `tareas/` y todo otro archivo del diff que no cuente en la huella del producto. El paquete SHALL nombrar esas exclusiones y los archivos que dejaron afuera, y el pedido al revisor SHALL decir que no forman parte de lo revisado.

#### Scenario: un candidato con registros de vueltas anteriores
- GIVEN un candidato cuyo diff contra la base trae un cambio de producto, informes y evidencia en .factory/ y una nota en tareas/
- WHEN se pide una revisión
- THEN el paquete contiene sólo el archivo de producto, nombra .factory y tareas como exclusiones con sus archivos, y el pedido lo dice

#### Scenario: un registro fuera de esas carpetas
- GIVEN un candidato que además cambia un archivo que no es producto fuera de .factory/ y tareas/
- WHEN se pide una revisión
- THEN ese archivo también queda excluido

### Requirement: Factory comprueba las exclusiones del paquete
Origen: 20261014-000054-paquete-producto · revisores_c90ab53abb4ca96d7.factory_comprueba_las_exclusiones_del_paquete
Tipo: funcional
Un paquete cuyas exclusiones dejan afuera un archivo del producto SHALL NOT usarse: `pedir-revision` SHALL fallar sin guardar el informe, y la preparación de la revisión SHALL no usar el informe de ese paquete y avisar por qué. Los paquetes sin exclusiones de vueltas anteriores SHALL seguir usándose.

#### Scenario: un paquete que excluye producto
- GIVEN un informe guardado cuyo paquete excluye un archivo del producto
- WHEN se prepara la revisión
- THEN ese informe no se usa y el aviso nombra el archivo

#### Scenario: un paquete anterior sin exclusiones
- GIVEN un informe guardado con un paquete preparado sin exclusiones
- WHEN se prepara la revisión con oracle-clue 0.1.0a2
- THEN el informe se usa como antes

### Requirement: pedidos de revisión simultáneos sobre el mismo candidato
Origen: 20261014-100834-revision-simultanea · revisores_c087c391047678495.pedidos_de_revision_simultaneos_sobre_el_mismo_candidato
Tipo: funcional
Dos `pedir-revision` lanzados a la vez sobre el mismo candidato SHALL terminar los dos: el checkout de revisión se crea una sola vez, cada pedido usa un paquete y un número propios, y el registro del cambio guarda el evento de cada uno.

#### Scenario: dos revisores distintos a la vez
- GIVEN un candidato sin checkout de revisión y dos revisores configurados
- WHEN se piden las dos revisiones al mismo tiempo
- THEN las dos guardan su informe y el registro tiene los dos eventos

#### Scenario: el mismo revisor dos veces a la vez
- GIVEN un revisor configurado
- WHEN se le piden dos revisiones del mismo candidato al mismo tiempo
- THEN quedan dos paquetes y dos informes con números distintos

### Requirement: un pedido interrumpido no traba los siguientes
Origen: 20261014-100834-revision-simultanea · revisores_c087c391047678495.un_pedido_interrumpido_no_traba_los_siguientes
Tipo: funcional
El turno entre pedidos SHALL soltarse cuando el proceso que lo tiene termina, de cualquier forma: un pedido interrumpido no SHALL dejar nada que haya que retirar a mano.

#### Scenario: un bloqueo de un pedido que murió
- GIVEN el archivo de bloqueo de un pedido anterior que se cortó
- WHEN se pide una revisión
- THEN el pedido termina sin esperar ni pedir que se borre el bloqueo

### Requirement: estado ofrece revisar cuando quedan hallazgos medios
Origen: 20261014-125953-estado-revisar-medios · revisores_ce00c589ba010487c.estado_ofrece_revisar_cuando_quedan_hallazgos_medios
Tipo: funcional
Con hallazgos medios o más sin aceptar en el candidato vigente, `estado` SHALL mostrar, además de corregir y pedir otra vuelta, que se pueden aceptar como riesgo o descartar con motivo con `oracle-factory revisar ID`; en una terminal, su menú SHALL ofrecer ejecutar ese comando; `estado --json` SHALL listarlo en `alternativas`, y `pedir-revision` SHALL decirlo al guardar un informe que deja medios sin aceptar. Sin medios pendientes no SHALL haber alternativa.

#### Scenario: quedan hallazgos medios sin aceptar
- GIVEN un candidato con un informe guardado que trae un hallazgo medio sin aceptar
- WHEN la persona pide estado, en texto y en JSON
- THEN el próximo paso sigue siendo corregir y pedir otra vuelta, y la alternativa es oracle-factory revisar ID

#### Scenario: el menú de estado ofrece revisar
- GIVEN ese mismo candidato, en una terminal
- WHEN la persona elige ejecutar la alternativa en el menú de estado
- THEN se abre revisar

#### Scenario: pedir-revision lo dice
- GIVEN un candidato
- WHEN pedir-revision guarda un informe con un hallazgo medio
- THEN dice que se puede corregir y pedir otra vuelta, o aceptar o descartar con oracle-factory revisar ID

#### Scenario: sin hallazgos medios no hay alternativa
- GIVEN un candidato cuyos informes sólo traen hallazgos bajos
- WHEN la persona pide estado
- THEN el próximo paso es oracle-factory revisar ID y no hay alternativas

### Requirement: el checkout de un revisor no toca el repositorio
Origen: 20261020-200030-aislar · revisores_c0acaae89b46617f5.el_checkout_de_un_revisor_no_toca_el_repositorio
Tipo: funcional
`pedir-revision` SHALL darle a cada revisor un checkout del candidato que sea un repositorio aparte, sin copiar objetos: lo que el revisor haga con git en ese checkout (cambiar su configuración, crear ramas, hacer commits) SHALL NOT cambiar la configuración, las ramas ni el HEAD del repositorio del proyecto ni de sus worktrees, y su informe SHALL validarse como siempre.

#### Scenario: un revisor que juega con git en su checkout
- GIVEN un cambio con un candidato y un revisor que en su checkout cambia user.name, crea una rama y hace un commit
- WHEN se pide la revisión con pedir-revision
- THEN el repositorio sigue con su user.name, sin esa rama y en el mismo HEAD, y el informe del revisor queda validado
