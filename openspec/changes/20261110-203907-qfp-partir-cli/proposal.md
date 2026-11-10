# cli.py: mudar los comandos del proyecto a su módulo para volver a tener margen bajo el tope

## Por qué

`oracle_factory/cli.py` mide 159.984 bytes y su tope es 160.000 (una prueba lo exige porque Oracle Clue no acepta archivos de más de 256.000 y queremos margen). La etapa 3 de los registros fuera del repo lo dejó a 16 bytes del tope, y la etapa 4 lo va a tocar. Hay que partirlo antes, sin cambiar nada de lo que hace.

## Qué cambia

- Un módulo nuevo, `oracle_factory/proyecto.py`, con los comandos del proyecto: `inicializar`, `plan_ejemplo`, `comando_migrar`, `comando_procedencia`, `comando_autonomia`, `comando_desplegar` y `comando_autopilot`.
- Siguen disponibles en `cli` con el mismo nombre y la misma firma (el mismo objeto), y leen lo de `cli` en el momento de usarlo (`cli.NOMBRE`), como los módulos que ya se separaron (`lecturas`, `flujo_revision`, `flujo_medidas`).
- `cli.py` queda con margen: como máximo 145.000 bytes.
- La prueba de módulos de la CLI (`tests/test_cli_modulos.py`) suma `proyecto` a la lista de módulos que vigila, para que le apliquen las mismas reglas que a los otros.

## Fuera de alcance

- Cualquier cambio de comportamiento: la ayuda de la CLI, las salidas y la suite entera quedan idénticas.

## Decisiones humanas

Ninguna nueva.
