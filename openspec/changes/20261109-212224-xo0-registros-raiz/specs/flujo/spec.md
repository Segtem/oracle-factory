# Capability: flujo

## ADDED Requirements

### Requirement: sin_registros_aparte_nada_cambia
Tipo: funcional
El sistema DEBE tener la raíz de los registros igual a la raíz del producto cuando no se da `--registros`, y en ese caso todos los comandos DEBEN comportarse exactamente como antes (mismas rutas, mismas salidas, mismos registros).

#### Scenario: sin la opción
- DADO un proyecto Factory como los de hoy
- CUANDO se corre cualquier comando sin `--registros`
- ENTONCES la raíz de los registros es la raíz del proyecto y el resultado es el de siempre

### Requirement: con_registros_aparte_el_repo_del_producto_queda_limpio
Tipo: funcional
El sistema DEBE, con `--registros RUTA`, guardar bajo RUTA todo lo que hoy guarda como registro (configuración, carpetas de los cambios, tareas, acuerdos de `openspec/`, conocimiento generado y proyecto Oracle con sus requisitos y catálogos), con las mismas rutas relativas que hoy bajo la raíz del proyecto, y DEBE no crear ni modificar ningún archivo en la raíz del producto con `init`, `nuevo`, `aprobar-spec`, `importar`, `medir`, `mensaje`, `tomar`, `soltar`, `listar` ni `estado`.

#### Scenario: un cambio completo hasta las medidas
- DADO un repo de producto limpio y una carpeta de almacén vacía
- CUANDO se corre `init --registros ALMACEN`, `nuevo`, `aprobar-spec`, `importar` y `medir` con `--registros ALMACEN`
- ENTONCES los registros están bajo ALMACEN y `git status` del producto sigue limpio y sin archivos nuevos

#### Scenario: el producto con su propio git
- DADO el mismo producto con commits propios
- CUANDO se corren esos comandos
- ENTONCES el historial y el árbol de trabajo del producto no cambian

### Requirement: con_registros_aparte_lo_que_necesita_candidato_no_inventa_uno
Tipo: funcional
El sistema DEBE, con `--registros` distinto de la raíz del producto, rechazar `pedir-revision`, `revision-preparar`, `revision`, `revisar`, `juzgar` y `cerrar` con un mensaje que diga que todavía no se admiten con registros aparte (etapa 3 de 6), sin escribir nada y con código de salida distinto de cero, y DEBE hacer que `estado` muestre el cambio sin candidato vigente en vez de fallar.

#### Scenario: un comando de candidato
- DADO un cambio en un almacén aparte
- CUANDO se corre `juzgar --registros ALMACEN`
- ENTONCES falla con el mensaje de la etapa 3 y no cambia ningún archivo, ni del almacén ni del producto

#### Scenario: estado sin candidato
- DADO el mismo cambio
- CUANDO se corre `estado --registros ALMACEN`
- ENTONCES muestra el cambio, sin candidato vigente, y no escribe nada
