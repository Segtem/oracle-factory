# Activar el workflow verificar en este repositorio

## Por qué

`oracle-factory verificar` y su plantilla de GitHub Actions ya existen, pero este repositorio no corre `verificar` en su propio CI: un cambio con la revisión vieja o con una huella que no coincide puede llegar a `main` sin que nada lo marque. Factory se desarrolla con Factory, así que tiene que usar su propia verificación.

## Qué cambia

- Un workflow `.github/workflows/verificar.yml` corre `oracle-factory verificar` en cada push y pull request, con permisos de sólo lectura y sin secretos. Instala Factory desde el checkout (`uv tool install .`), no desde PyPI, para probar el código que se está integrando.
- La política: si `verificar` encuentra un cambio inconsistente, el workflow **falla en `main`** y **avisa sin fallar en las demás ramas y pull requests** (una revisión desactualizada es normal en una rama de trabajo mientras se edita). El aviso sale como anotación `::warning::` con el detalle.
- La plantilla `docs/plantillas/verificar.yml` y la guía `docs/ci.md` cuentan la misma política, para que otros proyectos la copien.

## Fuera de alcance

- Cambiar qué comprueba `verificar` o su código de salida.
- Proteger la rama `main` en GitHub (reglas de ramas, checks obligatorios): es configuración del repositorio en GitHub, de Brian.
- Correr la suite de pruebas en CI: es una tarea aparte.

## Decisiones humanas

- Que falle en `main` y avise en las demás: Brian lo decidió.
- Aprobar esta spec.
