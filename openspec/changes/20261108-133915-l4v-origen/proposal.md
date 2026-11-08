# Medir si los hallazgos de la primera ronda se atrapan leyendo la spec

## Por qué

La medición del flujo (2026-11-08, 102 cambios cerrados) muestra que el lazo de rondas de revisión es lo que más pesa en el ciclo: 76 % de la suma de medianas, con una mediana de 2 rondas. La primera ronda trae 5,4 hallazgos en promedio y las siguientes bajan. La pregunta que decide si conviene revisar la spec antes de construir (o reforzar la lista previa) es cuántos de esos hallazgos de la ronda 1 eran casos que se podían ver leyendo la spec y cuántos solo aparecen con el código. Hoy `tools/medir_rondas.py` los clasifica en siete clases, pero no dice cuáles se podían anticipar.

## Qué cambia

- `tools/medir_rondas.py` suma una opción `--origen` que reparte los hallazgos altos y medios de la ronda 1 en grupos según su clase:
  - **atrapable al leer la spec**: las clases que la lista previa ya pregunta (rutas y enlaces, valores raros, falsos avisos o silencios, paridad con otra herramienta);
  - **solo con el código**: pruebas débiles, verificador y evidencia, documentos y mensajes contra el código;
  - **mixto**: el hallazgo cae en clases de los dos grupos;
  - **sin clase**: no cae en ninguna.
  Cada hallazgo se cuenta una vez.
- La salida dice qué clase va en qué grupo y que es una aproximación por texto, no un juicio humano.
- `--muestra N` lista hasta N hallazgos de cada grupo (cambio, ronda y título), en un orden fijo, para que una persona compruebe la regla.
- Sin `--origen` la salida es la de hoy.

## Fuera de alcance

- Cambiar las siete clases ni sus patrones de texto.
- Decidir con el número qué hacer (revisión temprana de la spec, otra lista previa): eso es una decisión posterior de la persona, con este número en la mano.
- Clasificar a mano los hallazgos: la herramienta es de solo lectura y mecánica.

## Decisiones humanas

Ninguna abierta: aprobar la spec es la decisión de la persona. Anotado para quien revise: el reparto de las clases en los dos grupos es una elección de diseño que este cambio fija y deja a la vista con `--muestra`; el límite (clasificación por texto) queda dicho en la salida.
