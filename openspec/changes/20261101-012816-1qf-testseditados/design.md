# Diseño

- La lógica vive en un módulo nuevo, `oracle_factory/alarmas.py`, que recibe la función que corre Git y no importa `cli`.
- La base es la del candidato: `git merge-base <candidato> main`, igual que `datos_trazabilidad` y `pedir_revision`. Los archivos cambiados salen de `git diff --name-status -z -M base candidato` (reusando `trazabilidad.archivos_cambiados`) y, por archivo de pruebas, de `git diff -U0 -M base candidato -- ruta` para contar las líneas quitadas, los `def test_` quitados y las aserciones quitadas.
- `estado` y `estado --json` (clave `tests_editados`) usan el candidato vigente; sin candidato no calculan.
- `pedir_revision` agrega la sección al texto del pedido sólo si hay algo; el resto del pedido no cambia.
- Todo es un aviso: no entra en los pendientes.
