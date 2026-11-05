# Capability: revision

<!-- Generada por Oracle Factory al cerrar cada cambio: no se edita a mano. -->

## Requirements

### Requirement: los_binarios_nombrados_no_bloquean
Origen: 20261104-221348-2l1-binarios · revision_cf0b48adb410caef9.los_binarios_nombrados_no_bloquean
Tipo: funcional
El sistema DEBE tratar como cumplida la comprobación de un informe de revisor `incompleto` cuando las únicas omisiones de su paquete son archivos binarios y cada uno está declarado en los límites del informe con una línea de la forma exacta `abierto: RUTA`, y DEBE listar esos binarios entre los límites del informe preparado.

#### Scenario: imágenes que el revisor abrió
- DADO un paquete que omite `site/img/a.png` por no ser UTF-8 y un informe `incompleto` cuyos límites incluyen la línea `abierto: site/img/a.png`
- CUANDO se prepara el informe de la revisión
- ENTONCES la comprobación de ese revisor cumple y los límites del informe mencionan `site/img/a.png`

### Requirement: lo_no_nombrado_sigue_bloqueando
Origen: 20261104-221348-2l1-binarios · revision_cf0b48adb410caef9.lo_no_nombrado_sigue_bloqueando
Tipo: funcional
El sistema DEBE seguir marcando `no_ejecutada` el informe `incompleto` cuando algún binario omitido no está declarado con esa forma exacta (una frase que lo menciona, con o sin negación, no cuenta), cuando el paquete omite algo por otro motivo o cuando no hay omisiones.

#### Scenario: un binario sin nombrar
- DADO un paquete que omite dos binarios y un informe `incompleto` que declara sólo uno
- CUANDO se prepara el informe de la revisión
- ENTONCES la comprobación queda `no_ejecutada`

#### Scenario: incompleto por otro motivo
- DADO un informe `incompleto` en un paquete sin omisiones, o con una omisión que no es binaria
- CUANDO se prepara el informe de la revisión
- ENTONCES la comprobación queda `no_ejecutada`

### Requirement: el_pedido_indica_como_declarar_binarios
Origen: 20261104-221348-2l1-binarios · revision_cf0b48adb410caef9.el_pedido_indica_como_declarar_binarios
Tipo: funcional
El sistema DEBE indicar al revisor, en el pedido, que abra en el checkout cada archivo que el paquete omita por no ser texto y lo declare en sus límites con la línea `abierto: RUTA`.

#### Scenario: el pedido de una revisión
- DADO el texto del pedido a un revisor
- CUANDO se lee
- ENTONCES pide abrir los archivos omitidos por no ser texto y nombrarlos en los límites
