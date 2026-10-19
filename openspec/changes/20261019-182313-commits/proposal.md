# Los commits unidos a su cambio: trailer Cambio, oracle-factory log, estado y tablero

## Why

En la prueba del ajedrez Brian tenía Git, pero no podía ver qué commits eran de qué cambio: la historia y el registro
de Factory iban por separado. Sin esa unión no se puede seguir un cambio en su código, ni responder después (C) «¿qué
decisión creó esta línea?».

## What changes

- Cada commit nuevo lleva el trailer `Cambio: <ID>` cuando el checkout tiene un solo cambio abierto. Lo agrega un hook
  `prepare-commit-msg` que instalan `init` y el comando nuevo `oracle-factory hooks`; si ya hay un hook de otro, no lo
  pisa y dice cómo encadenarlo. El hook nunca bloquea un commit.
- `oracle-factory log ID` (y `--json`) lista los commits del cambio: los que tienen su trailer y, para lo de antes del
  trailer, los que se deducen de los candidatos registrados y del merge que los integró. Cada commit dice cómo se lo unió
  (trailer o deducido) y si fue candidato revisado o con evidencia.
- `estado` muestra cuántos commits tiene el cambio y el último; `estado --json` los trae.
- El tablero suma una sección Commits por cambio; elegir un commit abre su diff en VS Code (sólo lectura).

## Out of scope

- Reescribir commits viejos para agregarles el trailer.
- «¿Por qué existe esta línea?» (blame → commit → cambio → decisiones): es C, que usa esto.
- Otros sistemas de control de versiones.

## Human decisions

- Brian eligió el 2026-10-19: trailer más deducción; verlos en `log`, en `estado` y en el tablero.
- Si un hook ajeno ya existe, Factory no lo encadena solo: la persona decide.
