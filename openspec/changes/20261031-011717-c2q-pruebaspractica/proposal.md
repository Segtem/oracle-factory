# Pedir las pruebas como práctica de desarrollo, sin bloquear

## Por qué

Factory exige evidencia de que cada promesa se cumple, pero no pide que quien desarrolla escriba pruebas unitarias mientras construye: hoy las escribe el agente por costumbre y nada en el proceso lo recuerda ni lo deja a la vista. Las pruebas no reemplazan a Oracle ni a las mutaciones: son un ejercicio de desarrollo para crear mejor código, y protegen contra regresiones. La investigación reciente indica que partir de la especificación para escribir las pruebas mejora la calidad del código y la detección de errores, y que un agente que escribe código y pruebas a la vez puede dejar pruebas que pasan por construcción. Conviene que el proceso lo recuerde, lo muestre y deje constancia cuando no se puede.

## Qué cambia

- La plantilla de tareas de un cambio nuevo, en español y en inglés, incluye el paso de escribir primero las pruebas de cada escenario de la spec.
- `estado` avisa, sin bloquear nada, de los requisitos del cambio que no tienen ningún caso de prueba en la trazabilidad del candidato vigente, o de que el candidato no tiene trazabilidad. El aviso aparece también en el JSON.
- Un requisito puede declarar en su spec una excepción, con una línea `Pruebas: no aplica — motivo`. La persona la acepta al aprobar la spec, `estado` la muestra con su motivo y ese requisito deja de avisar.

## Fuera de alcance

- Generar pruebas: las escribe quien desarrolla.
- Exigir un lenguaje o un marco de pruebas: el sensor sigue siendo del proyecto.
- Bloquear el cierre o la revisión por falta de pruebas; se evalúa después de ver cómo se usa.
- Marcar las líneas cambiadas que ningún caso ejecuta, avisar de pruebas existentes modificadas y la interfaz del tablero para entrar al código: son cambios siguientes.

## Decisiones humanas

- Que la excepción sea una línea de la spec y que aprobarla sea aprobar el motivo.
- Que por ahora el aviso no bloquee.
