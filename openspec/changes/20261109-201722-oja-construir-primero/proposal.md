# Autopilot: ante medir --listar sin medidas todavía el conductor delega construir primero

## Por qué

En la primera prueba real de `autopilot --ejecutar --lanzar` el conductor, recién importados los requisitos, le pidió al agente «elegí las medidas de cada requisito». Todavía no había pruebas ni catálogos, así que el agente contestó con razón que no había ninguna medida posible, y el conductor se frenó por «sin progreso». Las medidas se eligen sobre catálogos que salen de las pruebas del cambio: antes hay que construir.

## Qué cambia

La instrucción que el conductor delega ante `medir ID --listar` dice, en orden: construir primero lo que falte (las pruebas antes que el código y los catálogos de los requisitos, sin correr todavía la evidencia completa: va después de que una persona confirme las medidas); después elegir las medidas de cada requisito y proponerlas; y que confirmarlas es de una persona. La acción sigue siendo `delegar_al_agente` y el motivo no cambia.

## Fuera de alcance

- Detectar con datos si ya hay catálogos: el agente lo decide mirando el cambio.
- Cualquier otro paso del conductor.

## Decisiones humanas

Ninguna nueva.
