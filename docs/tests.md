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

Cuando no es posible (un cambio sólo de texto, un sensor que sólo corre en el motor), se deja dicho en la tarea o en el mensaje del cambio y se sigue.

## La guarda: un test que ya existía

Un agente que puede editar los tests puede aflojarlos hasta que pasen. Por eso: un test que ya existía no se edita para que pase sin dejarlo dicho a quien revisa. Agregar tests es libre; cambiar o borrar uno existente se nombra en el informe de la revisión.

## Fuentes

- arXiv 2402.13521: TDD para generación de código; los tests dados de antemano mejoran la corrección.
- arXiv 2608.17177: generación de tests a partir de la especificación.
- arXiv 2501.12862: pruebas guiadas por mutaciones.
- arXiv 2510.09907: pruebas basadas en propiedades con agentes.
- ImpossibleBench y EvilGenie: agentes que modifican o esquivan los tests para que pasen.

## Qué viene

Quedan para cambios aparte, cada uno con su decisión: avisar cuando un requisito no tiene caso asociado, declarar una excepción «sin tests» confirmada por una persona, mostrar las líneas sin caso al revisor y una vista del tablero para entrar al código creado.
