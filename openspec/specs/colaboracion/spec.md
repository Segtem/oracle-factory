# Capability: colaboracion

<!-- Generada por Oracle Factory al cerrar cada cambio: no se edita a mano. -->

## Requirements

### Requirement: un cambio dice quién lo tiene
Origen: 20261019-232444-quien · colaboracion_c46e4f59890d8fbf2.un_cambio_dice_quien_lo_tiene
Tipo: funcional
`oracle-factory tomar ID` SHALL registrar como responsable a la persona que lo corre desde su terminal, con los agentes que declara con `--con`, y `soltar ID` SHALL liberarlo. Si otra persona ya es responsable, `tomar` SHALL NOT reemplazarla salvo con `--relevo`, que SHALL dejar constancia de quién lo tenía. Un agente con `--agente` SHALL NOT quedar como responsable: SHALL quedar sumado como agente del cambio. Sin terminal ni `--agente`, `tomar` SHALL negarse.

#### Scenario: tomar, soltar y relevar
- GIVEN un cambio abierto sin responsable
- WHEN una persona corre tomar ID --con claude-code, otra persona intenta tomarlo y después lo toma con --relevo, y la última lo suelta
- THEN el registro dice quién lo tomó con qué agente, el segundo intento sin --relevo se niega sin cambiar nada, el relevo dice de quién venía y al soltarlo queda sin responsable

#### Scenario: un agente se suma
- GIVEN un cambio con una persona responsable
- WHEN un agente corre --agente codex tomar ID, y alguien corre tomar sin terminal ni --agente
- THEN codex queda como agente del cambio y la persona sigue responsable, y el segundo se niega

### Requirement: estado y el tablero muestran quién trabaja en qué
Origen: 20261019-232444-quien · colaboracion_c46e4f59890d8fbf2.estado_y_el_tablero_muestran_quien_trabaja_en_que
Tipo: funcional
`estado` (y `--json`) SHALL mostrar por cambio la persona responsable y desde cuándo, los agentes declarados y los que actuaron en las últimas 24 horas con su última acción, y los revisores lanzados sin resultado. El tablero SHALL mostrarlo en cada cambio y SHALL mostrar, para el proyecto, los cambios abiertos agrupados por responsable, con los que no tienen responsable aparte.

#### Scenario: un cambio con persona, agentes y un revisor en curso
- GIVEN un cambio tomado por una persona con claude-code, con una acción reciente de codex y un revisor lanzado sin resultado
- WHEN se pide oracle-factory estado ID --json y tablero --json
- THEN aparecen la persona, claude-code y codex con su última acción, y el revisor en curso

#### Scenario: quién está en qué en el proyecto
- GIVEN dos cambios abiertos, uno tomado y otro sin responsable
- WHEN se abre el tablero
- THEN el tomado aparece bajo su persona y el otro como sin responsable

### Requirement: el trailer elige bien el cambio
Origen: 20261019-232444-quien · colaboracion_c46e4f59890d8fbf2.el_trailer_elige_bien_el_cambio
Tipo: funcional
El hook SHALL elegir el cambio del trailer `Cambio:` en este orden: si el mensaje nombra el ID de un cambio del proyecto, ése (y si nombra varios, ninguno); si no, el único cambio abierto del checkout; si hay varios abiertos, el único que tiene como responsable a la persona que hace el commit (su nombre en la configuración de Git). En cualquier otro caso SHALL NOT agregar el trailer.

#### Scenario: un merge que nombra el cambio que integra
- GIVEN un checkout con un cambio abierto A y un commit cuyo mensaje dice «Integrar <ID de B>», con B cerrado
- WHEN se hace el commit
- THEN lleva «Cambio: <ID de B>», no el de A

#### Scenario: varios abiertos y uno tomado por quien commitea
- GIVEN dos cambios abiertos, uno tomado por la persona que hace el commit y otro sin responsable
- WHEN esa persona hace un commit que no nombra ningún cambio
- THEN lleva el cambio que tomó; y si no tomó ninguno, no lleva trailer
