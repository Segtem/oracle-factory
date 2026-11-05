# Diseño

`material_del_candidato` agrega a cada revisor `omisiones_binarias` (archivos omitidos por «contenido no UTF-8») y
`otras_omisiones` (el resto), leídas del paquete que corresponde al informe. `preparacion.completar` marca la comprobación
como `cumple` sólo si el informe es `incompleto`, hay omisiones binarias, no hay otras y cada ruta aparece en alguna
de sus `limitations`. En ese caso agrega un límite con los binarios. La plantilla del pedido pide nombrarlos.

Ronda 1: son binarios las tres razones con que Clue omite uno («contenido no UTF-8», «contenido binario», «Git lo clasifica como
binario»). La ruta cuenta como nombrada sólo en una frase sin negación («no abrí», «sin revisar»); es una heurística de
palabras que no entiende la frase, y por eso los binarios quedan listados en el informe para que la persona los vea. La
ruta puede llevar prefijo (absoluta o `./`) pero no letras pegadas delante.
