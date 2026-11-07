# Sumar verificar a la puerta local de salida

## Por qué

La puerta local mira secretos y la guía para agentes, el conocimiento y el resumen. No mira los cambios: una revisión que ya no corresponde, un informe tocado después de aprobarse o un cierre que no decidió una persona pasan al remoto sin aviso. `oracle-factory verificar` (ya integrado) lo comprueba de sólo lectura; la puerta es donde se lo ve antes de empujar. Es la otra mitad que dejó anotada la guía de la puerta («un `verificar` para CI se suma acá»).

## Qué cambia

- La puerta corre `oracle-factory verificar` junto a `agentes`, `kb` y `resumen`, con todo lo demás igual.
- Si algún cambio está inconsistente, la puerta **avisa y no bloquea**: nombra `verificar` con su primera línea (cuántos cambios miró y cuántos tienen problemas) y manda a correr `oracle-factory verificar` para ver cuál y por qué.
- Si el proyecto no tiene `.factory/config.json`, la verificación se omite y se dice, como las demás.
- La guía de la puerta (`docs/puerta.md`) y el mensaje del hook cuentan la política real: la guía vieja y un secreto bloquean; un kb o un resumen vencidos y un cambio inconsistente sólo avisan.

## Fuera de alcance

- Bloquear el push por un cambio inconsistente.
- Activar el workflow de CI en este repositorio.
- Cambiar qué comprueba `verificar`.

## Decisiones humanas

- Propongo que `verificar` **avise y no bloquee**: en una rama de trabajo, una revisión desactualizada es lo normal mientras se sigue editando, y bloquear el push sería hostil. Si preferís que bloquee, es una decisión tuya; cambiaría un solo valor de la tabla de verificaciones.
