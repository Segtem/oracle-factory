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

### Requirement: un clon recién hecho puede trabajar
Origen: 20261021-101907-clones · colaboracion_cf52b3f5822578a8a.un_clon_recien_hecho_puede_trabajar
Tipo: funcional
`init` SHALL dejar versionables las carpetas que crea, y en un clon recién hecho de un proyecto inicializado (o de uno viejo al que le falten esas carpetas) `nuevo` SHALL poder crear un cambio.

#### Scenario: la segunda persona clona el proyecto
- GIVEN un proyecto recién inicializado y subido, y una persona que lo clona
- WHEN corre nuevo en su clon, y también en un clon de un proyecto viejo sin tareas/
- THEN el cambio se crea en los dos

### Requirement: dos clones no generan el mismo ID
Origen: 20261021-101907-clones · colaboracion_cf52b3f5822578a8a.dos_clones_no_generan_el_mismo_id
Tipo: funcional
El ID de un cambio nuevo SHALL llevar tres caracteres al azar antes del sufijo y SHALL seguir terminando en el sufijo, de modo que dos clones que crean un cambio en el mismo segundo con el mismo sufijo no generen el mismo ID.

#### Scenario: dos cambios en el mismo segundo
- GIVEN dos clones del mismo proyecto
- WHEN los dos crean a la vez un cambio con el mismo sufijo, y se integran
- THEN los IDs son distintos y la integración no choca

### Requirement: escribir a la vez no obliga a repetir
Origen: 20261021-101907-clones · colaboracion_cf52b3f5822578a8a.escribir_a_la_vez_no_obliga_a_repetir
Tipo: funcional
`mensaje`, `tomar` y `soltar` SHALL reintentar solos cuando el registro del cambio cambió mientras escribían, volviendo a leerlo y a comprobar sus reglas, de modo que escrituras simultáneas sobre un mismo registro se guarden todas sin que nadie las repita; y SHALL fallar con un mensaje claro si no lo logran tras varios intentos.

#### Scenario: doce mensajes a la vez
- GIVEN un cambio y doce procesos que dejan un mensaje en su registro a la vez
- WHEN terminan
- THEN el registro tiene los doce mensajes y ninguno falló
