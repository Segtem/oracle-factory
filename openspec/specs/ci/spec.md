# Capability: ci

<!-- Generada por Oracle Factory al cerrar cada cambio: no se edita a mano. -->

## Requirements

### Requirement: verificar_dice_si_los_cambios_estan_consistentes
Origen: 20261107-130317-2vv-verificar · ci_c65ac59b63e44085b.verificar_dice_si_los_cambios_estan_consistentes
Tipo: funcional
El sistema DEBE ofrecer `oracle-factory verificar`, que recorre los cambios del proyecto y sale con 0 si todos están consistentes y con 1 si alguno no lo está, nombrando el cambio y qué falta, y DEBE ofrecer lo mismo con `--json` en un objeto con esquema versionado.

#### Scenario: todo consistente
- DADO un proyecto con un cambio abierto y vigente y otro cerrado por una persona
- CUANDO se corre `oracle-factory verificar`
- ENTONCES sale con 0 y dice cuántos cambios miró

#### Scenario: una revisión que ya no corresponde
- DADO un cambio abierto con la revisión registrada y después el producto modificado
- CUANDO se corre `oracle-factory verificar`
- ENTONCES sale con 1 y nombra el cambio y «revision desactualizado respecto del producto»

#### Scenario: un informe tocado después de aprobarse
- DADO un cambio cuyo informe de revisión se editó después de registrarse
- CUANDO se corre `oracle-factory verificar --json`
- ENTONCES el objeto lista el cambio con el problema «informe de revisión cambiado o sin huella» y el código es 1

### Requirement: verificar_solo_lee_y_no_necesita_a_nadie
Origen: 20261107-130317-2vv-verificar · ci_c65ac59b63e44085b.verificar_solo_lee_y_no_necesita_a_nadie
Tipo: funcional
El sistema DEBE correr `verificar` sin terminal, sin identidad de agente y sin red, y NO DEBE escribir ningún archivo del proyecto ni registrar ninguna acción.

#### Scenario: el árbol queda igual
- DADO un proyecto con cambios abiertos y cerrados
- CUANDO se corre `oracle-factory verificar` con la entrada cerrada y sin `--agente`
- ENTONCES el contenido del proyecto y los registros de los cambios son idénticos antes y después

### Requirement: un_cambio_cerrado_tiene_la_decision_de_una_persona
Origen: 20261107-130317-2vv-verificar · ci_c65ac59b63e44085b.un_cambio_cerrado_tiene_la_decision_de_una_persona
Tipo: funcional
El sistema DEBE marcar como inconsistente un cambio cerrado cuyo cierre no lo decidió una persona —salvo en modo autónomo, donde el cierre de un agente es legítimo—, y NO DEBE comparar un cambio cerrado con el producto actual, porque integrarlo lo deja distinto por diseño.

#### Scenario: un cierre sin persona
- DADO un cambio cerrado cuyo registro tiene un cierre de un agente
- CUANDO se corre `oracle-factory verificar`
- ENTONCES sale con 1 y nombra el cambio y que su cierre no lo decidió una persona

#### Scenario: un agente cerró en modo autónomo
- DADO un cambio en modo autónomo cuyo cierre lo decidió un agente
- CUANDO se corre `oracle-factory verificar`
- ENTONCES no lo marca por ese cierre

#### Scenario: un cambio integrado hace tiempo
- DADO un cambio cerrado por una persona e integrado, con el producto cambiado después
- CUANDO se corre `oracle-factory verificar`
- ENTONCES no lo marca por estar «desactualizado»

### Requirement: verificar_no_exige_lo_que_otra_maquina_no_tiene
Origen: 20261107-130317-2vv-verificar · ci_c65ac59b63e44085b.verificar_no_exige_lo_que_otra_maquina_no_tiene
Tipo: funcional
El sistema DEBE avisar, sin fallar, de los hechos de evidencia que no están en esta máquina, porque un clon limpio o un CI no los tienen, y DEBE seguir fallando por una huella que no coincide.

#### Scenario: hechos ausentes en un clon limpio
- DADO un cambio abierto vigente cuyos hechos están en una carpeta que este clon no tiene
- CUANDO se corre `oracle-factory verificar`
- ENTONCES sale con 0 y lista un aviso con el cambio y los hechos ausentes

#### Scenario: hechos presentes pero cambiados
- DADO un cambio con los hechos presentes y distintos de su huella
- CUANDO se corre `oracle-factory verificar`
- ENTONCES sale con 1 y lo nombra

### Requirement: hay_un_ejemplo_de_ci_y_de_hook
Origen: 20261107-130317-2vv-verificar · ci_c65ac59b63e44085b.hay_un_ejemplo_de_ci_y_de_hook
Tipo: funcional
El sistema DEBE traer una plantilla de workflow de GitHub Actions que corre `oracle-factory verificar` con permisos de sólo lectura y sin secretos, y una guía `docs/ci.md` que explica ese workflow y el uso de `verificar` en un hook `pre-push`.

#### Scenario: la plantilla sólo lee
- DADO la plantilla de workflow
- CUANDO se lee
- ENTONCES corre `oracle-factory verificar`, declara `contents: read` y no usa ningún secreto ni permiso de escritura

#### Scenario: la guía enseña lo que hay
- DADO `docs/ci.md`
- CUANDO se lee
- ENTONCES nombra la plantilla, el comando y su código de salida, y que el hook se saltea con `--no-verify`
