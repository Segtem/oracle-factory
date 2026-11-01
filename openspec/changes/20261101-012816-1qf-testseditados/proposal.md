# Avisar de los tests que ya existían y el cambio modificó o borró

## Por qué

La guía para agentes y `docs/tests.md` dicen que un test que ya existía no se edita para que pase sin dejarlo dicho a quien revisa. Hoy es sólo una regla escrita: nada la hace visible. Un agente que escribe el código y las pruebas a la vez puede aflojar un test, borrarlo o quitarle una aserción hasta ponerlo en verde, y quien revisa tiene que descubrirlo leyendo todo el diff. Los estudios que revisamos sobre agentes que escriben código (ImpossibleBench, EvilGenie) encuentran justamente eso: modelos que editan o esquivan los tests para que pasen. Y las skills de pair programming que estudiamos lo tratan como una de sus tres alarmas y una condición de parada. Detectarlo es barato porque Git ya sabe qué líneas se quitaron.

## Qué cambia

- `oracle-factory estado ID` avisa, sin bloquear nada, de los archivos de pruebas que existían en la base del candidato y que el candidato borró, renombró o a los que les quitó líneas, nombrando los tests y las aserciones quitadas. Agregar tests, o archivos de pruebas nuevos, no avisa. El aviso también sale en el JSON de `estado`.
- El pedido que recibe el revisor (`pedir-revision`) incluye esa lista con la indicación de nombrarla en su informe, de modo que la guarda sea visible a quien revisa. Si no hay tests editados, el pedido no cambia.
- Un archivo cuenta como de pruebas por su ruta: una carpeta `tests` o `test`, o un nombre `test_*`, `*_test.*` o `*.test.*`.

## Fuera de alcance

- Bloquear la revisión, el cierre o la integración por tests editados: es un aviso, y puede haber motivos legítimos (renombrar, simplificar, cambiar un comportamiento prometido).
- Juzgar si la edición fue legítima: eso es de quien revisa.
- Las otras alarmas (bucle de rondas, cambio de alcance, tamaño del cambio): son cambios siguientes.
- Detectar tests debilitados sin quitar líneas, por ejemplo cambiando un valor esperado en la misma línea: se ve como una línea quitada y una agregada, y se cuenta como quitada.

## Decisiones humanas

- Que sea un aviso y no un bloqueo.
- Que el pedido al revisor lleve la lista (a diferencia de la lista previa, que es para quien escribe).
