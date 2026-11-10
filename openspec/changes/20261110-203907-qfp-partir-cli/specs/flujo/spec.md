# Capability: flujo

## ADDED Requirements

### Requirement: cli_py_queda_con_margen_bajo_su_tope
Tipo: no funcional
El sistema DEBE tener `oracle_factory/cli.py` de 145.000 bytes o menos, y ningún archivo del paquete por encima de sus topes.

#### Scenario: el tamaño
- DADO el paquete
- CUANDO se mide `oracle_factory/cli.py`
- ENTONCES mide 145.000 bytes o menos y `tools/tamanos.py` no informa problemas

### Requirement: lo_mudado_a_proyecto_sigue_igual
Tipo: no funcional
El sistema DEBE ofrecer en `cli` las funciones mudadas a `oracle_factory/proyecto.py` (`inicializar`, `plan_ejemplo`, `comando_migrar`, `comando_procedencia`, `comando_autonomia`, `comando_desplegar` y `comando_autopilot`) como el mismo objeto, con la misma firma, sin que `cli.py` las defina; las funciones de `proyecto.py` DEBEN leer de `cli` lo que necesitan en el momento de usarlo, y `proyecto` DEBE estar entre los módulos que vigila la prueba de módulos de la CLI.

#### Scenario: los nombres
- DADO `cli` y `proyecto`
- CUANDO se busca cada función mudada
- ENTONCES `cli.NOMBRE` es `proyecto.NOMBRE`, con la misma firma de antes, y `cli.py` no la define

#### Scenario: la vigilancia
- DADO la prueba de módulos de la CLI
- CUANDO se mira su lista de módulos
- ENTONCES incluye `proyecto`
