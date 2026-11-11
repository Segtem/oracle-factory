# Capability: flujo

## ADDED Requirements

### Requirement: con_almacen_cada_comando_commitea_solo_lo_de_su_cambio
Tipo: funcional
El sistema DEBE, con almacén aparte, hacer que el commit de un comando sobre un cambio NO incluya archivos que pertenecen a otro cambio (los que están bajo su carpeta en `.factory/cambios/`, `tareas/` u `openspec/changes/`, o su nota `kb/cambios/OTRO.md`), aunque hayan cambiado durante el comando, e incluya lo que cambió de su propio cambio y de lo común; esos archivos de otro cambio DEBEN quedar sin commitear para el comando de ese cambio; un comando sin cambio DEBE commitear todo lo que cambió, como en la etapa 4a; y sin almacén aparte nada DEBE cambiar.

#### Scenario: otro cambio escribe mientras tanto
- DADO dos cambios A y B en un almacén conectado
- CUANDO un comando sobre A termina mientras un archivo de B cambió durante ese comando
- ENTONCES el commit de A no lleva el archivo de B, que sigue sin commitear

#### Scenario: lo común sí entra
- DADO un comando sobre A que cambia su registro y un archivo común (por ejemplo `kb/README.md`)
- CUANDO termina
- ENTONCES el commit lleva los dos

#### Scenario: un comando sin cambio
- DADO cambios en archivos de A y de B
- CUANDO termina un comando sin cambio que los produjo
- ENTONCES el commit lleva todo

### Requirement: el_commit_del_almacen_se_hace_con_un_bloqueo_corto
Tipo: funcional
El sistema DEBE, con almacén aparte, hacer la foto final, el `add` y el `commit` de cada comando bajo un bloqueo exclusivo del almacén que se toma sólo para eso, de modo que dos comandos que terminan a la vez commiteen uno después del otro sin fallar por el `index.lock` de Git; NO DEBE tener tomado ese bloqueo mientras el comando trabaja; y si no lo consigue en un plazo, NO DEBE fallar: DEBE avisar y dejar los registros en el disco.

#### Scenario: dos comandos que terminan a la vez
- DADO dos procesos que corren comandos sobre cambios distintos del mismo almacén y llegan juntos al commit
- CUANDO terminan
- ENTONCES cada uno deja su commit con sus archivos y ninguno avisa de un `index.lock`

#### Scenario: el bloqueo no se toma durante el comando
- DADO un comando que todavía trabaja
- CUANDO otro comando llega a su commit
- ENTONCES el segundo commitea sin esperar al primero

#### Scenario: el bloqueo no se consigue
- DADO el bloqueo tomado por otro proceso más allá del plazo
- CUANDO un comando llega a su commit
- ENTONCES termina bien, avisa y los registros quedan en el disco
