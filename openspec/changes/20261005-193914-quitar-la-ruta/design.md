# Design

Se completa después de la aceptación.

- La ruta privada se toma de la raíz del proyecto y de `/home/workstation`, la que figura en los registros.
- `fuente_relativa` (de portabilidad) ya sabe reescribir una fuente; la herramienta la reutiliza.
- La actualización de hashes recorre `medidas[rid].sha256` de cada `factory.json` y recalcula sobre el nuevo `.requisito`.
- El verificador guarda un resumen de `estado` de cada cambio antes de limpiar.
