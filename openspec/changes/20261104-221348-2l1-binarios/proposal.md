# Revisión: los archivos binarios del paquete no impiden aprobar

## Por qué

Un cambio con imágenes (por ejemplo las capturas de `web-vscode`) no se puede aprobar. El paquete de Oracle Clue deja los
archivos que no son UTF-8 como «omitidos», y Clue obliga al revisor a marcar su informe `incompleto`. Factory convierte ese
informe en una comprobación `no_ejecutada` y `revisar` bloquea «Aprobar», aunque el revisor haya abierto cada imagen en el
checkout y lo haya dicho. La persona que decide no puede aprobar un cambio con binarios aunque la revisión haya sido honesta
y completa en todo lo demás.

## Qué cambia

- Factory distingue una omisión por binario de cualquier otra. Si un informe es `incompleto` y las únicas omisiones del
  paquete son archivos binarios que el propio revisor declara en sus límites con una línea `abierto: RUTA`, la comprobación de esa revisión cumple y el
  informe preparado lista esos binarios como límite («revisados directamente en el checkout según el revisor»).
- Si el revisor no declara algún binario omitido con esa forma, o el paquete omite algo por otro motivo, todo sigue igual: `no_ejecutada` y
  no se puede aprobar.
- El pedido al revisor le indica que abra cada binario omitido en el checkout y lo nombre en sus límites.

## Fuera de alcance

- No se cambia Oracle Clue ni se decodifican imágenes en Factory.
- No se acepta un informe `incompleto` por otros motivos, ni se cambia lo que declara la persona en `revisar`.

## Decisiones humanas

- Aprobar esta spec. Límite aceptado: Factory no puede comprobar que el revisor abrió de verdad el binario; confía en que lo
  declare y la persona lo ve en los límites del informe.
