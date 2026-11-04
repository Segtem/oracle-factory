# Diseño

`material_del_candidato` agrega a cada revisor `omisiones_binarias` (archivos omitidos por «contenido no UTF-8») y
`otras_omisiones` (el resto), leídas del paquete que corresponde al informe. `preparacion.completar` marca la comprobación
como `cumple` sólo si el informe es `incompleto`, hay omisiones binarias, no hay otras y cada ruta aparece en alguna
de sus `limitations`. En ese caso agrega un límite con los binarios. La plantilla del pedido pide nombrarlos.
