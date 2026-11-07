# Preparar la distribución 0.1.0a18

## Por qué

La 0.1.0a17 está publicada en PyPI y en GitHub, y Factory siguió mejorando: `destinos` y `desplegar` (despliegue a varios destinos con prueba de que todo quedó funcionando) y su vista en el tablero de VS Code, `oracle-factory verificar` para CI, la puerta local que ahora también corre `verificar` y avisa sin bloquear, la web con menú y orden de lectura, las capturas reales de VS Code, la simulación de concurrencia y los binarios del paquete que ya no impiden aprobar. Quien instale desde PyPI no tiene nada de eso.

## Qué cambia

- La versión pasa a 0.1.0a18 en los metadatos del paquete, en la CLI, en el README, en las notas de versión, en la guía y en la web, y se regenera y versiona el `uv.lock`.
- Las notas dejan de decir que la 0.1.0a17 es la última: está publicada, con su tag y su release. La 0.1.0a18 queda declarada como preparada, no como publicada, hasta que Brian la suba.
- Un probador corto, `tools/probar_entrega_a18.py` (el de la a17 con la versión y los comandos nuevos), construye el wheel y el sdist, los instala en un entorno nuevo y comprueba desde fuera del checkout la versión, el origen de la importación, la skill en el wheel y que funcionan `skill`, `puerta`, `agentes`, `verificar`, `destinos` y la ayuda de los subcomandos nuevos.
- El probador deja un registro con los hashes del wheel y del sdist, las versiones y los límites; la evidencia del cambio la produce `tools/verificar_cambio.py`.
- Las pruebas que sólo afirmaban hechos de la 0.1.0a17 pasan a decir lo de la 0.1.0a18.

## Fuera de alcance

- Publicar en PyPI, crear el tag o la release de GitHub: la subida a PyPI la hace Brian; el tag y la release los hago yo por su pedido explícito («push, tag y release»), después de integrar este cambio.
- Cambiar las versiones de Oracle, Oracle Task u Oracle Clue, ni empaquetar una versión nueva de la extensión de VS Code.
- Un probador parametrizado por versión: queda como idea aparte.

## Decisiones humanas

- Que la 0.1.0a18 salga con todo lo integrado en `main` hasta hoy.
- Que la entrega sea mínima, como la a17.
- Cuándo se publica: Brian ya pidió tag y release tras la integración; PyPI lo sube él.
