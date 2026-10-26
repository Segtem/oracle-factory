# Design

- Un solo lugar decide cómo se pide una revisión: una función devuelve el comando completo con el primer revisor
  configurado, o la explicación si no hay ninguno. La usan el próximo paso y los mensajes de `revisar`, para que no
  diverjan.
- Sin revisor, el próximo paso es texto que no empieza con `oracle-factory …`; así la extensión lo muestra como
  instrucción y no como comando para ejecutar (convención ya vigente en `proximo_paso`).
- Base vacía: `--base vacio` crea con `git hash-object -t tree -w /dev/null` y `git commit-tree` un commit sin archivos
  con autor y fecha fijos (mismo SHA siempre, sin leer ni escribir la configuración de Git). Sin ref apuntándolo, no cambia
  la historia. El clon local del revisor trae los objetos, así que `oracle-clue preparar --base` lo encuentra (probado).
