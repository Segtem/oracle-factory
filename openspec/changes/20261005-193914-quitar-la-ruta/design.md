# Design

Se completa después de la aceptación.

- La ruta privada se toma de la raíz del proyecto y de `/home/workstation`, la que figura en los registros.
- `fuente_relativa` (de portabilidad) ya sabe reescribir una fuente; la herramienta la reutiliza.
- La actualización de hashes recorre `medidas[rid].sha256` de cada `factory.json` y recalcula sobre el nuevo `.requisito`.
- El verificador guarda un resumen de `estado` de cada cambio antes de limpiar.

## Correcciones tras la revisión independiente (R2)

- **Alcance medido al aplicar:** 49 archivos (41 requisitos, 5 requisitos previos y 3 `factory.json` con ruta de hechos o con una decisión cuyo hash cambió), no los 46 de la propuesta; tres fuentes llevaban `/tmp/oracle-release-work/…` y se limpiaron igual, porque la herramienta no busca «la ruta privada» sino cualquier ruta absoluta anclada en `openspec/changes/<ID>/` o `tareas/<ID>/`.
- **Una fuente que no se sabe reescribir se avisa:** si la ruta absoluta no tiene esa forma o la relativa no existe en el proyecto, no se inventa nada, la herramienta sale con 1 y `--verificar` la cuenta como pendiente.
- **Sin decisión actualizada no se reescribe el requisito:** si un `factory.json` no se puede tocar, los requisitos cuyas decisiones guarda quedan como estaban.
- **Si se corta a mitad:** primero se escriben los `factory.json` (con el hash nuevo) y después los requisitos, cada archivo con reemplazo atómico; la corrida siguiente termina el trabajo sin duplicar el evento.
- **El evento no es una decisión:** `rutas_limpiadas` lleva `forma: migracion`.
- **El verificador compara `estado` de verdad:** de cada cambio que ya estaba en la base indicada con `--antes` (el commit justo antes de aplicar la limpieza), salvo los que se excluyen con `--excluir`. Contra `main` no sirve: el último cambio integrado figura «al día» sólo mientras ningún archivo del producto cambie, y limpiar archivos del producto lo vuelve «desactualizado», como cualquier otro commit.
