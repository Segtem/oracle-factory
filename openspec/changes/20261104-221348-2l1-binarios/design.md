# Diseño

`material_del_candidato` agrega a cada revisor `omisiones_binarias` (archivos omitidos por alguna de las tres razones con que
Oracle Clue omite un binario: «contenido no UTF-8», «contenido binario», «Git lo clasifica como binario») y `otras_omisiones`
(el resto), leídas del paquete que corresponde al informe. `preparacion.completar` marca la comprobación como `cumple` sólo
si el informe es `incompleto`, hay omisiones binarias, no hay otras y cada ruta está en una línea de `limitations` que es,
entera, `abierto: RUTA` (igualdad exacta con la ruta del paquete). En ese caso agrega un límite con los binarios.

Por qué una forma fija y no leer frases: en las dos primeras rondas, un detector de negaciones («no abrí», «omití», «did not
open») y de bordes de ruta fue dando una forma nueva por ronda. La igualdad exacta no interpreta lenguaje, admite cualquier
ruta (espacios, puntos, `@2x`, Unicode) y no se confunde con rutas como `icons/no.png`. Límite: Factory no comprueba que el
revisor abrió el archivo; la persona lo ve listado en los límites del informe preparado.
