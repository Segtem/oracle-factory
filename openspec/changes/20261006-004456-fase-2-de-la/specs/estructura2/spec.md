# Capability: estructura2

## ADDED Requirements

### Requirement: el estado de un cambio nuevo vive en .factory
Tipo: funcional
Un cambio nuevo SHALL guardar su registro, su revisión libre y el veredicto de Oracle en `.factory/cambios/<ID>/`, y dejar en `openspec/changes/<ID>/` sólo el acuerdo (propuesta, diseño, plan y especificación).

#### Scenario: cambio nuevo
- GIVEN un proyecto con `.factory/`
- WHEN se crea un cambio y se recorre su flujo hasta el veredicto
- THEN `factory.json`, `review.md` y `oracle-veredicto.txt` están en `.factory/cambios/<ID>/` y no en `openspec/changes/<ID>/`

### Requirement: un proyecto no migrado sigue funcionando
Tipo: funcional
Si el estado de un cambio está en `openspec/changes/<ID>/`, Factory SHALL leerlo y escribirlo ahí, avisar cómo migrar, y no mover nada por su cuenta.

#### Scenario: cambio anterior a la fase 2
- GIVEN un cambio con su registro en el lugar viejo
- WHEN se ejecuta `estado`, `medir` o `juzgar`
- THEN funcionan como antes, el registro sigue en el lugar viejo y se avisa que existe `migrar`

### Requirement: migrar mueve el estado sin cambiar su contenido
Tipo: funcional
`oracle-factory migrar` SHALL mover el estado de todos los cambios a `.factory/cambios/<ID>/`, reescribir en cada registro sólo las rutas que citan los archivos movidos, y no tocar ningún otro byte; con `--verificar` SHALL informar qué movería sin escribir.

#### Scenario: migración completa
- GIVEN un proyecto con varios cambios en el lugar viejo, algunos con revisión y veredicto
- WHEN se ejecuta `migrar`
- THEN cada cambio tiene su estado en el lugar nuevo, el viejo ya no existe y el registro sólo difiere en las rutas citadas

#### Scenario: vista previa
- GIVEN el mismo proyecto
- WHEN se ejecuta `migrar --verificar`
- THEN lista lo que movería, no cambia ningún archivo y termina con código distinto de cero mientras haya algo por migrar

### Requirement: migrar no pierde ni pisa nada
Tipo: funcional
`migrar` SHALL ser repetible, SHALL recuperarse de una interrupción, y SHALL rechazar el cambio cuyo estado nuevo y viejo existan con contenido distinto en vez de elegir uno.

#### Scenario: segunda ejecución
- GIVEN una migración ya hecha
- WHEN se vuelve a ejecutar
- THEN no cambia ningún archivo y termina con éxito

#### Scenario: interrupción a mitad
- GIVEN una migración cortada después de escribir el estado nuevo de un cambio y antes de borrar el viejo
- WHEN se vuelve a ejecutar
- THEN termina el trabajo sin duplicar nada

#### Scenario: estado en los dos lugares con contenido distinto
- GIVEN un cambio con registro nuevo y viejo que difieren
- WHEN se ejecuta `migrar`
- THEN avisa de ese cambio, no toca sus archivos y termina con código distinto de cero

### Requirement: la migración conserva el significado
Tipo: no funcional
Después de migrar, `estado` de cada cambio SHALL decir lo mismo que antes (salvo las rutas), y las revisiones y los veredictos registrados SHALL seguir vigentes, porque la huella del producto no cambia.

#### Scenario: cambio cerrado
- GIVEN un cambio cerrado con revisión humana y veredicto verde
- WHEN se migra
- THEN `estado` sigue mostrando la fase, las decisiones y los avisos de vigencia que mostraba, y los hashes de sus informes siguen coincidiendo

### Requirement: la configuración del proyecto vive en .factory
Tipo: funcional
La configuración SHALL leerse de `.factory/config.json`; si sólo existe el `factory.json` de la raíz SHALL leerse de ahí con un aviso, y `migrar` SHALL pasarla al lugar nuevo.

#### Scenario: configuración en la raíz
- GIVEN un proyecto con `factory.json` en la raíz que fija el modo por defecto
- WHEN se ejecuta cualquier comando
- THEN se respeta el modo y se avisa que la configuración debería estar en `.factory/config.json`

#### Scenario: configuración en .factory
- GIVEN `.factory/config.json` con `modo_por_defecto`
- WHEN se crea un cambio sin `--modo`
- THEN el cambio nace con ese modo

### Requirement: los comandos de lectura entienden los dos lugares
Tipo: funcional
`listar`, `donde`, `ruta` y `buscar` SHALL funcionar con cambios en el lugar viejo, en el nuevo o mezclados, y `donde` SHALL mostrar la ruta real del estado.

#### Scenario: proyecto con cambios en los dos lugares
- GIVEN un cambio migrado y otro sin migrar
- WHEN se ejecutan `listar`, `donde` y `buscar`
- THEN aparecen los dos y `donde` indica en qué lugar está el estado de cada uno

### Requirement: este repositorio queda migrado y verificado
Tipo: no funcional
Los cambios existentes de este repositorio SHALL migrarse, y un verificador SHALL comprobar que no quedan registros en el lugar viejo, que `tareas/` no cambió y que el `estado` de cada cambio es el mismo antes y después.

#### Scenario: verificación sobre este repositorio
- GIVEN el estado de cada cambio antes de migrar
- WHEN se migra y se consulta de nuevo
- THEN la salida de `estado` es la misma salvo las rutas y `tareas/` no tiene ningún archivo modificado
