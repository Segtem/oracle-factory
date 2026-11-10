# Capability: flujo

## ADDED Requirements

### Requirement: el_agente_lanzado_recibe_un_entorno_minimo
Tipo: funcional
El sistema DEBE lanzar el comando de `--lanzar` con un entorno que contenga únicamente `FACTORY_AGENTE`, las variables `PATH`, `HOME`, `USER`, `LOGNAME`, `SHELL`, `LANG`, `LANGUAGE`, `TERM`, `TZ`, `TMPDIR`, `BASH_DEFAULT_TIMEOUT_MS`, `BASH_MAX_TIMEOUT_MS`, las que empiezan con `LC_` o con `XDG_`, y las que la persona nombró con `--entorno` y existen; ninguna otra variable del entorno de la persona DEBE llegar al agente, tampoco las de nombre inocuo, y los comandos mecánicos que corre Factory no cambian.

#### Scenario: un entorno con secretos y variables comunes
- DADO un entorno con `PATH`, `HOME`, `LANG`, `OPENROUTER_API_KEY`, `MI_TOKEN` y `OTRA_VARIABLE`
- CUANDO el conductor lanza al agente
- ENTONCES el agente ve `PATH`, `HOME`, `LANG` y `FACTORY_AGENTE`, y no ve `OPENROUTER_API_KEY`, `MI_TOKEN` ni `OTRA_VARIABLE`

#### Scenario: los prefijos permitidos
- DADO variables `LC_ALL`, `XDG_CONFIG_HOME` y `LCX_OTRA`
- CUANDO el conductor lanza al agente
- ENTONCES llegan `LC_ALL` y `XDG_CONFIG_HOME`, y no `LCX_OTRA`

#### Scenario: los comandos mecánicos
- DADO el mismo entorno
- CUANDO el conductor corre un comando mecánico de Factory
- ENTONCES se corre como hasta ahora, con el entorno completo

### Requirement: entorno_explicito_por_corrida
Tipo: funcional
El sistema DEBE aceptar `--entorno NOMBRE`, repetible y sólo junto con `--ejecutar --lanzar`, que agrega esa variable al entorno del agente si existe en el entorno de la persona; DEBE rechazar antes de correr nada, con un mensaje claro y código de salida distinto de cero, un nombre que no sea un identificador de variable (letras, dígitos y guion bajo, sin empezar con dígito) o `--entorno` sin `--lanzar`; y NO DEBE guardar nada de esto en la configuración.

#### Scenario: una variable entregada a propósito
- DADO `ANTHROPIC_API_KEY` en el entorno de la persona
- CUANDO se corre `autopilot --ejecutar --lanzar COMANDO --entorno ANTHROPIC_API_KEY`
- ENTONCES el agente la ve, y en la corrida siguiente sin `--entorno` ya no

#### Scenario: nombres que no sirven
- DADO `--entorno "A B"`, `--entorno 1A` o `--entorno` sin `--lanzar`
- CUANDO se corre el comando
- ENTONCES falla con un mensaje claro sin lanzar nada ni escribir nada

### Requirement: la_guia_de_permisos_no_abre_python
Tipo: funcional
El sistema DEBE, en `docs/modos.md`, explicar que Factory filtra el entorno del agente y mostrar un ejemplo de `--lanzar` cuyos permisos de Python se limiten a `-m unittest` y a `tools/verificar_cambio.py`, sin el patrón abierto `.venv/bin/python:*`, diciendo por qué ese patrón abierto no se recomienda (permite red, leer el entorno y ejecutar git).

#### Scenario: la documentación
- DADO `docs/modos.md`
- CUANDO se lee la sección del conductor
- ENTONCES contiene el ejemplo con Python acotado, la explicación del entorno filtrado y la advertencia sobre el patrón abierto, y el ejemplo no contiene `.venv/bin/python:*`
