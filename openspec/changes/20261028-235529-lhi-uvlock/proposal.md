# Rastrear el uv.lock de Factory y no dar por no confiable un paquete que el entorno no instala

## Why

`oracle-factory procedencia` declara no confiable un inventario cuando el lock no coincide con lo que pide el proyecto. Aplicado a Factory mismo, el resultado fue «no confiable»: el `uv.lock` de Factory está en el `.gitignore` y quedó viejo (dice que `oracle-factory` es la 0.1.0a3, fija Oracle 0.38.1 y no incluye Oracle Clue). Un lock que no viaja con el repositorio ni se mantiene al día no sirve de ancla para saber de dónde viene cada dependencia de Factory.

Al regenerarlo apareció un segundo problema, de la propia procedencia: el lock incluye `typing-extensions`, que sólo se instala en algunas versiones de Python, y como el entorno no lo instala el inventario se declaraba no confiable. Un lock multiplataforma siempre trae paquetes que un entorno concreto no instala (por versión de Python o por sistema operativo); tratarlo como una diferencia da falsas alarmas en cualquier proyecto real y le quita valor a la marca «confiable».

## What changes

- El `uv.lock` de Factory se regenera con `uv lock` para que coincida con `pyproject.toml` (Factory 0.1.0a15, Oracle 0.39.0, Oracle Task 0.2.0, Oracle Clue 0.1.0a2 y sus dependencias, con sus hashes), se saca del `.gitignore` y se versiona.
- Una prueba exige que el lock versionado de Factory sea confiable respecto de su `pyproject.toml`: cambiar la versión o una dependencia sin regenerarlo hace fallar la prueba, con el mensaje de la procedencia.
- Un paquete que está en el lock y no está instalado deja de ser una diferencia: el inventario lo marca (`factory:instalado: false` en ese componente) y sigue siendo confiable. Una versión instalada que no coincide con el lock sigue siendo una diferencia.
- `AGENTS.md` (la parte escrita a mano) y `docs/procedencia.md` dicen cuándo regenerar el lock: en cada cambio de versión o de dependencias.

## Out of scope

- Instalar o actualizar dependencias de Factory.
- Evaluar los marcadores de entorno del lock para decidir qué paquete corresponde instalar.
- Incluir el lock en el paquete publicado en PyPI.

## Human decisions

- Si el lock debe regenerarse en cada versión (se propone que sí, y que una prueba lo exija).
