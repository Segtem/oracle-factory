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
