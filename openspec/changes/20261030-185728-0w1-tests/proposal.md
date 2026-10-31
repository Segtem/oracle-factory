# Tests unitarios como práctica del desarrollo: el paso de escribirlos primero

## Por qué

Factory exige evidencia medida, pero no dice nada sobre cómo se escribe el código que esa evidencia mide. Los tests unitarios que se escriben hoy existen porque el agente los escribe por costumbre, no porque el flujo los pida. Brian quiere que escribir tests sea, cuando se pueda, parte del desarrollo: un ejercicio para crear buen código, distinto de Oracle (que mide una promesa ante una persona) y de las mutaciones (que miden si los casos detectan fallas). No suplantan a ninguno de los dos.

La investigación reciente lo respalda con una condición: los tests escritos antes y derivados de la spec ayudan a que el código generado sea correcto (TDD para generación de código, arXiv 2402.13521; generación de tests desde la especificación, arXiv 2608.17177), pero un agente que puede editar los tests puede también aflojarlos para que pasen (ImpossibleBench, EvilGenie). Por eso el paso va con una guarda: editar un test que ya existía se avisa a quien revisa.

## Qué cambia

Esta es la primera parte, la más chica, de una práctica que tiene más escalones:

- Las tareas de cada cambio nuevo (`tasks.md`, en español y en inglés) incluyen el paso «Agente: escribir primero los tests de cada escenario de la spec, cuando sea posible, y comprobar que fallan antes de implementar».
- Un documento `docs/tests.md` explica la práctica: qué son los tests unitarios frente a Oracle y las mutaciones, cuándo se escriben primero, qué se hace cuando no es posible, la guarda sobre tests existentes y las fuentes.
- La guía para agentes (`oracle-factory agentes`) dice una línea sobre el paso y la guarda.

Ninguno bloquea nada: es una práctica pedida, no un gate.

## Fuera de alcance

Quedan para cambios siguientes, uno por uno, porque cada uno necesita su decisión: el aviso en `importar`/`medir` cuando un requisito no tiene caso asociado, la excepción «sin tests» declarada con motivo y confirmada por una persona, mostrar las líneas sin caso como punto del revisor, el registro de resultados de mutación, los casos de evidencia ocultos, y la interfaz del tablero para entrar al código creado (tests, trazabilidad, líneas sin caso). Tampoco se escribe ningún generador de tests: los tests son del proyecto y de su lenguaje.

## Decisiones humanas

- ¿Alcanza con empezar por el paso en las tareas y el documento, dejando los avisos y la interfaz del tablero como cambios aparte?
- ¿El paso debe decir «cuando sea posible», o querés una redacción más firme que obligue a declarar por qué no se escribieron tests?
