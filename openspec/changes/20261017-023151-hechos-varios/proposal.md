# Juzgar un candidato con hechos de varios sensores

## Why

Fricción 1 del piloto con agentes (tarea `20261005-105254-hechos-varios`, `tareas/20261004-121432-coordinar-dos/piloto-agentes-01/piloto.md`): un candidato integrado tiene un sensor por frente, pero `juzgar --con` acepta un solo JSON, y nada detecta que dos sensores emitan la misma relación, que pone rojo el requisito de otro frente sin conflicto en Git. En el piloto se resolvió combinándolos a mano (`combinar_hechos.py`). Oracle 0.39.0 (2026-10-17) ya acepta `--con` repetido en `juzgar` y `cobertura` y rechaza una relación que venga en dos archivos; falta que Factory lo use.

## What changes

- **Factory fija Oracle 0.39.0.**
- **`juzgar --con` se repite**, un archivo por sensor, y le pasa todos a Oracle. Sin `--con` sigue usando los hechos del candidato, como hoy.
- **El registro guarda cada archivo con su huella.** Con uno solo, el formato es el de siempre; con varios, los demás van aparte. Si cualquiera cambia, falta o no es una ruta, el juicio deja de valer: `estado` nombra el archivo, y el próximo paso repite el juicio con los mismos `--con`. `donde` lista todos.
- **Dos sensores con la misma relación** no dejan un veredicto: Oracle lo rechaza nombrando la relación y los dos archivos, y Factory no registra nada.
- **Docs**: `docs/colaboracion.md` cuenta cómo juzgar un candidato integrado con un sensor por frente.

## Out of scope

- Que Factory descubra solo los hechos de varios sensores en la carpeta del candidato: se nombran con `--con`.
- Subir Jam, LyraGASP y commander a Oracle 0.39.0: va después, midiendo cada uno.

## Human decisions

- Brian eligió el 2026-10-16 hacer primero el cambio en Oracle (0.39.0, publicado) y después este.
