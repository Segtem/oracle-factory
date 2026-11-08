# Capability: ci

## ADDED Requirements

### Requirement: el_repositorio_corre_verificar_en_su_ci
Tipo: funcional
El sistema DEBE tener un workflow de GitHub Actions que corra `oracle-factory verificar` en cada push y pull request, con permisos de sólo lectura, sin secretos y con Factory instalado desde el checkout.

#### Scenario: el workflow del repositorio
- DADO el archivo `.github/workflows/verificar.yml`
- CUANDO se lee
- ENTONCES se dispara con push y pull_request, sólo pide `contents: read`, no usa secretos, instala con `uv tool install .` y corre `oracle-factory verificar`

### Requirement: verificar_falla_en_main_y_avisa_en_las_demas
Tipo: funcional
El sistema DEBE hacer fallar el workflow cuando `verificar` encuentra un cambio inconsistente en la rama `main`, y DEBE avisar sin fallar, con una anotación de advertencia, en cualquier otra rama o pull request.

#### Scenario: un cambio inconsistente en main
- DADO `verificar` que sale con 1 y la referencia `refs/heads/main`
- CUANDO se ejecuta el paso de verificación
- ENTONCES sale con 1

#### Scenario: un cambio inconsistente en otra rama
- DADO `verificar` que sale con 1 y la referencia `refs/heads/tarea/x` o `refs/pull/3/merge`
- CUANDO se ejecuta el paso de verificación
- ENTONCES sale con 0 e imprime una anotación `::warning::`

#### Scenario: todo consistente
- DADO `verificar` que sale con 0
- CUANDO se ejecuta el paso en cualquier referencia
- ENTONCES sale con 0 y no imprime advertencia

### Requirement: la_plantilla_y_la_guia_cuentan_la_politica
Tipo: funcional
El sistema DEBE contar la misma política (falla en `main`, avisa en las demás) en la plantilla `docs/plantillas/verificar.yml` y en `docs/ci.md`.

#### Scenario: la plantilla y la guía
- DADOS la plantilla y la guía
- CUANDO se leen
- ENTONCES la plantilla aplica la política en su paso de verificación y la guía la explica y nombra el workflow de este repositorio
