# Tests unitarios en Factory

Factory pide evidencia medida, pero no dice cómo se escribe el código que esa evidencia mide. Esta página fija una práctica: escribir tests unitarios como parte del desarrollo, **cuando sea posible**. No bloquea nada.

## Tres capas, tres preguntas

| Capa | Qué pregunta responde | Quién decide |
| --- | --- | --- |
| Tests unitarios | ¿El código hace lo que sus escenarios dicen, hoy y mañana? Sirven para diseñar y para no romper lo que andaba. | Quien desarrolla |
| Mutaciones | ¿Los casos detectan una falla si la introduzco? | Quien desarrolla, con la herramienta del proyecto |
| Oracle | ¿La promesa del requisito se cumple, medida sobre evidencia? | Una persona, desde su terminal |

Los tests unitarios no suplantan a Oracle ni a las mutaciones: que pasen no prueba que la promesa esté bien medida. Son un ejercicio para crear buen código.

## El paso

Las tareas de cada cambio nuevo traen el paso «escribir primero los tests de cada escenario de la spec, cuando sea posible, y comprobar que fallan antes de implementar». Que fallen primero es la comprobación: un test que nunca falló no prueba nada. El paso no bloquea: `importar`, `medir`, `revisar`, `juzgar` y `cerrar` no lo miran.

Cuando no es posible (un cambio sólo de texto, un sensor que sólo corre en el motor), se declara en la spec, en la cabecera del requisito, con la línea `Pruebas: no aplica — motivo`; como la spec la aprueba una persona, aprobarla es aprobar el motivo (ver [la trazabilidad](trazabilidad.md)). `oracle-factory estado ID` avisa, sin bloquear nada, de los requisitos que no tienen ningún caso de prueba en la trazabilidad del candidato y de los que lo declararon con su motivo.

## La guarda: un test que ya existía

Un agente que puede editar los tests puede aflojarlos hasta que pasen. Por eso: un test que ya existía no se edita para que pase sin dejarlo dicho a quien revisa. Agregar tests es libre; cambiar o borrar uno existente se nombra en el informe de la revisión.

Factory lo hace visible sin bloquear nada: `oracle-factory estado ID` (y `estado ID --json`, en la clave `tests_editados`) avisa de los archivos de pruebas que existían en la base del candidato y que el candidato borró, renombró o a los que les quitó líneas, con los tests y las aserciones quitadas; y el pedido que recibe el revisor lleva la misma lista, con la indicación de mencionarla en su informe. Agregar tests, o archivos de pruebas nuevos, no avisa. Un renombre avisa siempre, aunque no se haya quitado ninguna línea, porque mover un test a un archivo que nadie ejecuta lo desactiva; y un archivo cuenta como «de pruebas» por su ruta en la base (lo que ya existía), de modo que un archivo de producto renombrado a `tests/` no avisa. Sólo se miran los archivos del producto: los registros generados (`kb/`, `.factory/`, `tareas/`) no cuentan. El conteo de aserciones quitadas es **aproximado**: las aserciones se reconocen por patrones de lenguaje (`assert`, `expect(`, `ASSERT_*`, `t.Error*` y `t.Fatal*` de Go, `pytest.raises`, `.fail(`). Es un aviso y no un juicio: renombrar o simplificar puede ser legítimo, y quien revisa decide. Un archivo cuenta como de pruebas por su ruta (una carpeta `tests` o `test`, o un nombre `test_*`, `*_test.*` o `*.test.*`); otras convenciones, como `__tests__` o `*.spec.*`, no se miran todavía.

## Otras dos alarmas: el bucle y el tamaño

Con la misma idea (avisar sin bloquear), `oracle-factory estado ID` avisa de dos señales del flujo, y las lleva en su JSON (`estado ID --json`) en las claves `bucle_de_revision` y `cambio_grande`, cada una con el valor, el umbral y si avisa (o `null` si no se pudo calcular):

- **Bucle de revisión:** el cambio lleva 4 rondas o más. Una ronda es un candidato distinto al que se pidió revisión (varios revisores de un mismo candidato son una ronda). El aviso sugiere parar a arreglar la clase del problema entera y mirar la [lista previa](lista-previa.md) antes de pedir otra.
- **Cambio grande:** el candidato agrega más de 450 líneas en archivos de producto, sin contar los archivos de pruebas ni los registros generados. El aviso sugiere partir el cambio.

## Los frenos: cuándo parar y pedir a una persona

`estado ID --json` lleva además la clave `frenos`: una lista de `{id, motivo}`, vacía si no hay ninguno, y `estado` muestra cada uno como un aviso que empieza con «FRENO:». Es la lista que un agente que construye solo (el modo autopilot) tiene que obedecer: en cuanto hay un freno, para y le devuelve la decisión a una persona. Los frenos no bloquean ningún comando ni cambian el próximo paso: se calculan en cada consulta, no se guardan, y un dato que no se puede leer no produce un freno. Dos frenos ceden ante una revisión aprobada y vigente (decisión `aprobar`, del mismo producto que el candidato actual y sin problemas), porque una persona ya miró: `hallazgo_alto_abierto` y `prueba_existente_editada` (el aviso «test existente editado» sigue mostrándose); si el candidato cambia, la revisión deja de ser vigente y vuelven.

- `juicios_rojos`: los dos últimos juicios de Oracle (`juzgar`) terminaron en rojo.
- `hallazgo_alto_abierto`: un informe del candidato vigente trae un hallazgo de severidad alta y no hay una revisión aprobada y vigente.
- `prueba_existente_editada`: el candidato editó o borró tests que ya existían (la alarma de arriba).
- `cambio_grande` y `bucle_de_revision`: las dos alarmas anteriores, con los mismos umbrales.

Los dos números son referencias sacadas de 20 cambios cerrados (`tools/medir_rondas.py`): hasta unas 450 líneas la mediana fue de 2 rondas, y por encima, de 3; y los cambios de 5 o 6 rondas fueron bucles que parchaban la misma clase de problema caso por caso. Son una pauta y no una ley: un cambio de 600 líneas puede estar bien si es mecánico.

## La evidencia de un cambio, sin un verificador por cambio

Hasta ahora cada cambio traía su `tools/verify_<x>.py` y sus catálogos, casi iguales entre sí. `tools/verificar_cambio.py` los reemplaza en los cambios que vengan (los verificadores existentes siguen como están):

```bash
.venv/bin/python tools/verificar_cambio.py ID --pruebas test_x --catalogos      # escribe catalogos/factory_x.*.oracle
.venv/bin/python tools/verificar_cambio.py ID --pruebas test_x --salida $(oracle-factory ruta ID evidencia)
```

La convención: una prueba `test_<letras><n>_…` (dos o tres letras minúsculas y el número) prueba el requisito número `n` de la spec del cambio, en el orden en que la spec los lista; el módulo es `tests/test_x.py`. La herramienta lee los nombres con `ast` (un nombre dentro de un texto no cuenta) y falla, sin declarar éxito, si un requisito no tiene casos, si un caso nombra un número que no corresponde a ningún requisito o si no hay casos. La evidencia es la de siempre —`suite.txt`, `hechos.json`, `trazabilidad.json` y `resultado.json`— y el éxito exige que todos los casos pasen, que la corrida sea exactamente la esperada, que las fuentes no cambien mientras corre y que la trazabilidad esté bien. Los catálogos de `--catalogos` cuentan los casos de cada requisito; escribirlos otra vez con los mismos casos no cambia nada, y los catálogos del mismo módulo que la spec ya no pide (un requisito renombrado o quitado) se retiran y se nombran en la salida, porque seguirían siendo medidas activas. Si `catalogos/` o alguno de los catálogos del cambio es un enlace simbólico, la herramienta se niega a escribir (sale con el código 2 y no toca nada): escribir seguiría el enlace y modificaría un archivo de afuera. Las medidas siguen proponiéndose y confirmándose como siempre.

Los nombres de los requisitos se comparan como los importa Factory (pasados a slug), los de una sección `REMOVED` o dentro de un bloque de código no cuentan y un requisito repetido es un error. Una subclase cuenta los casos que hereda de otra clase (o de un mixin sin base) del mismo módulo, porque unittest también los corre en ella. El `--alcance` de los catálogos no admite comillas dobles, barras invertidas ni caracteres que no se imprimen (tabulaciones, saltos de línea, separadores Unicode): el catálogo lo escribe entre comillas. Un requisito que declara `Pruebas: no aplica — motivo` no necesita casos: el verificador lo deja fuera de los hechos y de los catálogos (la corrida completa cuenta sólo los casos de los demás), pero conserva la numeración, así que `test_<letras><n>_…` sigue siendo el requisito `n` de la spec. Un caso que nombra un requisito exceptuado es un error, y también lo es una línea `Pruebas:` mal escrita, con el mismo mensaje que da `aprobar-spec`. **Límite:** el requisito exceptuado queda sin medida de esta herramienta; la persona decide con qué otra lo cubre o lo deja «sin medir». Si todos los requisitos están exceptuados no hay evidencia que producir y el verificador falla.

## Fuentes

- arXiv 2402.13521: TDD para generación de código; los tests dados de antemano mejoran la corrección.
- arXiv 2608.17177: generación de tests a partir de la especificación.
- arXiv 2501.12862: pruebas guiadas por mutaciones.
- arXiv 2510.09907: pruebas basadas en propiedades con agentes.
- ImpossibleBench y EvilGenie: agentes que modifican o esquivan los tests para que pasen.

## Qué falta

Quedan para cambios aparte, cada uno con su decisión: mostrar al revisor las líneas cambiadas que ningún caso ejecuta, la alarma de cambio de alcance (archivos que la propuesta no menciona) y una vista del tablero para entrar al código creado.
