# Pedir una revisión independiente desde Factory

## Why

Para revisar un candidato, hoy el agente arma a mano el checkout y el paquete de Oracle Clue, escribe un pedido para el revisor, lo lanza con un script propio (`ask-codex`, `ask-agy`), espera, valida el informe y lo copia a la carpeta del candidato. En el último cambio fueron cinco vueltas así. Factory no sabe que pasó nada de eso hasta que el informe aparece en `revision/`, y el pedido —qué se le preguntó al revisor— no queda registrado. Además, `revision-preparar` sólo muestra la vuelta vigente: las anteriores, con sus hallazgos ya corregidos, no aparecen.

Es la segunda pieza del objetivo «Factory se construye a sí misma» (tarea `lanzar-revisores`).

## What changes

1. **`oracle-factory pedir-revision ID --a NOMBRE`** pide una revisión del candidato actual al revisor configurado: prepara el checkout y el paquete de Clue en las rutas del candidato, arma el pedido, lanza el comando del revisor, espera (con un tope), valida el informe con Clue y lo guarda en `revision/`. `--pedir TEXTO` agrega indicaciones; `--base REF` elige la base del paquete.
2. **Revisores configurables** en `.factory/config.json` (`revisores`): para cada nombre, el comando con marcadores, el proveedor, el modelo y el tope en minutos. Factory no depende de ninguna herramienta; la guía trae ejemplos para Codex y Agy.
3. **El pedido se genera desde el cambio** con una plantilla versionada (propuesta, spec, paquete, checkout, formato del informe esperado y vueltas anteriores), que un proyecto puede reemplazar con `.factory/pedido-revision.md`. El pedido usado queda guardado junto al informe.
4. **Lo que sale mal no se guarda como informe:** si el revisor no deja informe, si Clue lo rechaza o si se pasa del tope, se avisa y su salida queda para inspeccionar. Con cambios de producto sin commit, no se lanza.
5. **El revisor no decide:** `pedir-revision` no registra revisiones ni decisiones; deja un evento con el revisor, el proveedor, el modelo, el candidato y el resultado.
6. **`revision-preparar` muestra las vueltas anteriores** del mismo cambio como comprobaciones (candidato, revisor y hallazgos), sin pedir que se decidan otra vez.
7. Este cambio se revisa con `pedir-revision`.

## Out of scope

- Revisores en segundo plano con un comando para recoger el informe después (decidido: `pedir-revision` espera).
- Elegir automáticamente qué revisor usar o cuántas vueltas dar.
- Que el revisor corrija el código.

## Human decisions

Respondidas por Brian el 2026-10-07:

1. **Cómo se lanza cada revisor:** *configurable en `.factory/config.json`*, con ejemplos para Codex y Agy.
2. **Mientras el revisor trabaja:** *espera y termina con el informe*, con un tope configurable.
3. **Vueltas anteriores:** *se muestran sin volver a decidirlas*.
4. **El pedido:** *generado desde el cambio*, con plantilla versionada y reemplazable; `--pedir` agrega indicaciones.

Riesgo a la vista: `pedir-revision` ejecuta el comando que dice la configuración del proyecto. Un proyecto clonado puede traer un comando cualquiera, igual que un `Makefile`; se ejecuta sólo cuando alguien corre `pedir-revision`, y el comando se muestra antes de ejecutarlo.
