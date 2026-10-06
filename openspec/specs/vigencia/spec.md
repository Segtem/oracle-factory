# Capability: vigencia

<!-- Generada por Oracle Factory al cerrar cada cambio: no se edita a mano. -->

## Requirements

### Requirement: vigencia por contenido del producto
Origen: 20261005-154433-la-vigencia-de · vigencia_c82d7f5b48fbc29ba.vigencia_por_contenido_del_producto
Tipo: funcional
Factory SHALL considerar vigentes la revisión y el veredicto de Oracle mientras la huella de archivos del producto coincida con la que tenían al registrarse, aunque el `HEAD` actual sea otro, y SHALL considerarlos desactualizados cuando esa huella cambie.

#### Scenario: commit posterior que no toca el producto
- GIVEN una revisión registrada y un commit posterior que sólo cambia `tareas/` o los registros de Factory
- WHEN se consulta `estado` o se intenta cerrar
- THEN la revisión sigue vigente y no se pide renovarla

#### Scenario: cambia un archivo del producto
- GIVEN una revisión registrada
- WHEN cambia un archivo del producto, con o sin commit
- THEN la revisión queda desactualizada y el cierre se rechaza

#### Scenario: mismo contenido por otra historia
- GIVEN una revisión registrada
- WHEN el `HEAD` cambia por un merge o un rebase que deja idénticos los archivos del producto
- THEN la revisión sigue vigente

### Requirement: el commit observado se conserva y se muestra
Origen: 20261005-154433-la-vigencia-de · vigencia_c82d7f5b48fbc29ba.el_commit_observado_se_conserva_y_se_muestra
Tipo: funcional
Cada registro de revisión y de veredicto SHALL seguir guardando el `HEAD` observado, y `estado` y el cierre SHALL mostrarlo y avisar cuando el `HEAD` actual es otro con el producto idéntico.

#### Scenario: aviso de HEAD distinto
- GIVEN una revisión vigente registrada en un commit distinto del actual
- WHEN se consulta `estado`
- THEN aparece el commit revisado, el commit actual y que el producto es idéntico

#### Scenario: HEAD igual
- GIVEN una revisión registrada en el commit actual
- WHEN se consulta `estado`
- THEN no aparece ningún aviso

### Requirement: informe guiado vinculado al contenido
Origen: 20261005-154433-la-vigencia-de · vigencia_c82d7f5b48fbc29ba.informe_guiado_vinculado_al_contenido
Tipo: funcional
`revision --formato guiado` SHALL aceptar un informe preparado en un `HEAD` distinto del actual si su huella de archivos coincide con la actual, y SHALL rechazarlo, sin modificar el registro, si la huella difiere.

#### Scenario: informe preparado antes de un commit de registros
- GIVEN un informe preparado y completado, y un commit posterior que no toca el producto
- WHEN se registra la revisión
- THEN se acepta y queda registrado el `HEAD` actual y el de preparación

#### Scenario: informe de otro producto
- GIVEN un informe preparado y un cambio posterior en un archivo del producto
- WHEN se intenta registrar
- THEN Factory lo rechaza e indica que hay que preparar una revisión nueva

### Requirement: respetar los registros existentes
Origen: 20261005-154433-la-vigencia-de · vigencia_c82d7f5b48fbc29ba.respetar_los_registros_existentes
Tipo: no funcional
Factory SHALL NOT exigir migración de los registros existentes y SHALL NOT cambiar qué archivos cuentan como producto.

#### Scenario: registro anterior a este cambio
- GIVEN una revisión registrada antes de este cambio y un producto sin modificar
- WHEN se evalúa con la regla nueva
- THEN es vigente sin tocar su registro
