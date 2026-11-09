# Capability: flujo

## ADDED Requirements

### Requirement: el_segundo_revisor_no_es_uno_que_no_dejo_resultado
Tipo: funcional
El sistema DEBE, al calcular `segundo_revisor` en `estado --json`, descartar a un revisor que tenga un lanzamiento sin resultado sobre el candidato vigente, y ofrecer en su lugar el primero (por orden de nombre) de otro proveedor que no tenga ese problema; si no queda ninguno, `segundo_revisor` DEBE ser `null`. Un lanzamiento sin resultado sobre otro candidato, o ya cerrado por un resultado, no descarta a nadie, y el resto de las reglas del `segundo_revisor` no cambia.

#### Scenario: el revisor falló sobre el candidato vigente
- DADO un cambio de camino completo, un informe de `agy`, y un lanzamiento de `codex` sobre el candidato vigente sin resultado
- CUANDO se pide `estado --json`
- ENTONCES `segundo_revisor` es `null` si no hay otro revisor de otro proveedor, y el nombre de otro revisor de otro proveedor si lo hay

#### Scenario: el lanzamiento es de otro candidato o ya terminó
- DADO un lanzamiento sin resultado de `codex` sobre un candidato anterior, o un lanzamiento cerrado por su resultado
- CUANDO se pide `estado --json`
- ENTONCES `segundo_revisor` sigue siendo `codex`

#### Scenario: el conductor no repite el pedido
- DADO el escenario del primer caso con `segundo_revisor` en `null`
- CUANDO el conductor decide sobre el paso `revisar`
- ENTONCES no corre `pedir-revision` y sigue como sin segundo revisor
