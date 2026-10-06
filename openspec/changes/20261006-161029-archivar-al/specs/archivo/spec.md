# Capability: archivo

## ADDED Requirements

### Requirement: la spec de un cambio se fusiona al cerrarlo
Tipo: funcional
Al cerrar un cambio, Factory SHALL fusionar su spec en `openspec/specs/<capacidad>/spec.md`: `ADDED` agrega, `MODIFIED` reemplaza el requisito del mismo nombre, `REMOVED` lo quita y una spec sin encabezados de delta cuenta como `ADDED`; cada requisito vigente SHALL indicar el cambio y el requisito de Oracle del que viene.

#### Scenario: primer cambio de una capacidad
- GIVEN un cambio con requisitos agregados de una capacidad sin spec consolidada
- WHEN la persona lo cierra
- THEN `openspec/specs/<capacidad>/spec.md` tiene esos requisitos, cada uno con su cambio y su requisito de Oracle

#### Scenario: un cambio que modifica y quita requisitos
- GIVEN una capacidad con spec consolidada y un cambio con requisitos `MODIFIED` y `REMOVED` de esa capacidad
- WHEN la persona lo cierra
- THEN el requisito modificado tiene el texto nuevo y el cambio nuevo como origen, y el quitado ya no está

### Requirement: un conflicto impide cerrar
Tipo: funcional
Si la fusión no es posible (agregar un requisito con un nombre que ya existe en la capacidad, modificar o quitar uno que no existe, repetir un nombre en la spec del cambio o usar `RENAMED`), o si la spec consolidada en disco no es la que generó Factory, `cerrar` SHALL rechazarse antes de pedir la confirmación y de modificar cualquier archivo, y SHALL nombrar el requisito o el archivo en conflicto.

#### Scenario: agregar un requisito que ya existe
- GIVEN una capacidad con el requisito «X» y un cambio que agrega «X»
- WHEN la persona intenta cerrarlo
- THEN el cierre se rechaza nombrando «X», y ni el registro ni la spec consolidada cambian

#### Scenario: modificar un requisito que no existe
- GIVEN una capacidad sin el requisito «Y» y un cambio que modifica «Y»
- WHEN se intenta archivarlo
- THEN se rechaza nombrando «Y» y nada cambia

#### Scenario: spec consolidada editada a mano
- GIVEN una spec consolidada que alguien editó a mano
- WHEN se intenta cerrar o archivar un cambio de esa capacidad
- THEN se rechaza antes de preguntar, nombrando el archivo, y la edición no se pisa

### Requirement: lo cerrado no se mueve ni se reescribe
Tipo: no funcional
Archivar SHALL NOT mover ni modificar la carpeta del cambio, sus requisitos de Oracle, ni archivos de `tareas/`; en el registro del cambio SHALL sólo agregarse la marca de archivado.

#### Scenario: cambio archivado
- GIVEN un cambio cerrado y archivado
- WHEN se comparan sus archivos con los de antes de archivar
- THEN sólo cambió su registro (con el evento de archivo), y `estado` de los demás cambios dice lo mismo

### Requirement: se distingue lo vigente de lo reemplazado
Tipo: funcional
Para cada requisito de Oracle de un cambio archivado, Factory SHALL poder decir si está vigente o fue reemplazado, y por qué cambio.

#### Scenario: requisito reemplazado
- GIVEN un requisito que un cambio posterior modificó o quitó
- WHEN se consulta el estado del cambio que lo había agregado
- THEN el requisito figura como reemplazado, con el cambio que lo reemplazó

### Requirement: una capacidad con un solo nombre
Tipo: funcional
Un mapeo de capacidades del proyecto SHALL permitir que un cambio declarado con un nombre se fusione en la spec consolidada de otro, y `nuevo` SHALL avisar cuando la capacidad pedida es un alias del mapeo.

#### Scenario: capacidad con alias
- GIVEN el mapeo `estructura2` → `estructura`
- WHEN se cierra un cambio de `estructura2`
- THEN sus requisitos quedan en `openspec/specs/estructura/spec.md`

### Requirement: este repositorio queda archivado
Tipo: no funcional
Los cambios cerrados de este repositorio SHALL archivarse en el orden en que se cerraron con el mapeo aceptado, de forma repetible, y un verificador SHALL comprobar que cada cambio cerrado está archivado, que cada requisito vigente apunta a un requisito de Oracle existente y que nada de lo cerrado cambió salvo la marca de archivo.

#### Scenario: verificación sobre este repositorio
- GIVEN los cambios cerrados antes de archivar
- WHEN se archivan y se vuelve a archivar
- THEN la segunda vez no cambia nada, y el verificador da éxito

### Requirement: los comandos de lectura muestran el archivo
Tipo: funcional
`listar` SHALL distinguir los cambios archivados, `donde` SHALL mostrar la spec consolidada en la que se fusionó el cambio, y `buscar` SHALL buscar también en `openspec/specs/`.

#### Scenario: consultar un cambio archivado
- GIVEN un cambio archivado
- WHEN se ejecutan `listar`, `donde` y `buscar` con un texto de su spec
- THEN `listar` lo marca archivado, `donde` muestra la spec consolidada y `buscar` encuentra el texto en ella
