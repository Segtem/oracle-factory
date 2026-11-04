# Preparar la distribución 0.1.0a17

## Por qué

La 0.1.0a16 está publicada en PyPI y en GitHub, y Factory siguió mejorando: `puerta` y el hook pre-push que corre al empujar, las alarmas de bucle y de tamaño, el camino ligero de revisión, el verificador reutilizable `tools/verificar_cambio.py`, las pruebas de contrato entre la CLI y la extensión de VS Code y la skill de agente (`oracle-factory skill`). Quien instale desde PyPI no tiene nada de eso. La skill trae además un archivo de datos dentro del paquete, y hasta ahora sólo una prueba estática (que mira `pyproject.toml`) respaldaba que viaja en el wheel; hace falta construirlo y mirar de verdad.

## Qué cambia

- La versión pasa a 0.1.0a17 en los metadatos del paquete, en la CLI, en el README, en las notas de versión, en la guía y en la web, y se regenera y versiona el `uv.lock`.
- Las notas dejan de decir que la 0.1.0a16 es la última: está publicada, con su tag y su release. La 0.1.0a17 queda declarada como preparada, no como publicada, hasta que Brian la suba.
- Un probador corto, `tools/probar_entrega_a17.py`, construye el wheel y el sdist, los instala en un entorno nuevo y comprueba desde fuera del checkout: la versión y el origen de la importación, que el wheel trae `oracle_factory/data/skill/SKILL.md`, y que instalados funcionan `skill`, `skill --instalar`, `puerta`, `agentes` y la ayuda de los subcomandos nuevos.
- El probador deja un registro con los hashes del wheel y del sdist, las versiones de las herramientas y los límites, y la evidencia del cambio la produce `tools/verificar_cambio.py`.
- Las pruebas que sólo afirmaban hechos de la 0.1.0a16 (qué versión es la última, qué está publicado) pasan a decir lo de la 0.1.0a17.

## Fuera de alcance

- Publicar en PyPI, crear el tag o la release de GitHub: la subida a PyPI la hace Brian, y el tag y la release los hago yo sólo por su pedido explícito, después de la revisión y el cierre.
- Cambiar las versiones de Oracle, Oracle Task u Oracle Clue.
- Empaquetar una versión nueva de la extensión de VS Code: sigue en 0.5.0.
- Repetir las comprobaciones de las entregas anteriores con servidores de prueba (elaboración con un modelo simulado, avisos de OSV): esas funciones no cambiaron y las cubre la suite.
- Un probador parametrizado por versión para las próximas entregas: queda como idea aparte.

## Decisiones humanas

- Que la 0.1.0a17 salga con todo lo ya integrado en `main` (la lista de arriba).
- Que la entrega sea mínima: sin copiar las cuatro herramientas de la a16.
- Cuándo se publica: eso se decide después del cierre.
