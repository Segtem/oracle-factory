# Producir en la carpeta del candidato y preparar la revisión desde los informes de los revisores

## Why

Factory define dónde va lo que se produce sobre un candidato (`oracle-factory ruta ID TIPO` → `.factory/cambios/<ID>/candidatos/<sha7>/{evidencia,clue,revision}`), pero ni este repositorio lo usa: la evidencia va a `tareas/<ID>/evidencia-<sha>/`, los paquetes de Clue y los informes de los revisores viven en el scratchpad del agente, y el informe de la revisión guiada lo arma un script distinto por cambio que copia a mano hallazgos, comprobaciones y límites. Es trabajo repetitivo que hoy hace el agente sin que Factory lo registre.

Es la primera pieza del objetivo «Factory se construye a sí misma» (tareas `producir-en-ruta` y `preparar-desde-clue`): con esto, los cambios siguientes ya se revisan con la herramienta nueva.

## What changes

1. **`juzgar` sin `--con`** usa `hechos.json` de la carpeta de evidencia del candidato actual (la que da `ruta ID evidencia`); si no existe, falla diciendo la ruta esperada. `--con` sigue igual.
2. **`revision-preparar` lee los informes de los revisores** guardados en la carpeta `revision/` del candidato (formato de Oracle Clue) y la evidencia de `evidencia/`, y completa el informe guiado: cada hallazgo con su descripción, ubicación y lo que dijo el revisor; comprobaciones con el resultado de la evidencia; límites declarados por los revisores y por la evidencia; y los archivos que tocó el candidato según el paquete de Clue.
3. **El borrador de decisiones no decide:** lista cada hallazgo con estado vacío; la persona elige corregido, descartado o riesgo aceptado, como hasta ahora.
4. **Si `oracle-clue` está instalado**, cada informe se valida contra su paquete; si no, se marca «sin validar» y se avisa. Un informe ilegible o de otro candidato se avisa y no se usa.
5. **Este repositorio produce en la carpeta del candidato:** la evidencia, los paquetes de Clue y los informes de los revisores de este cambio van a `.factory/cambios/<ID>/candidatos/<sha7>/`.

## Out of scope

- Lanzar a los revisores desde Factory (tarea `lanzar-revisores`).
- Mover la evidencia de los cambios anteriores desde `tareas/`.
- Auditorías en Markdown (como las de Agy): se guardan en la carpeta pero no entran al informe estructurado.

## Human decisions

Respondidas por Brian el 2026-10-07:

1. **El borrador de decisiones:** *sin estado*; decide la persona.
2. **Validar con Clue:** *sí, si está instalado*; si no, «sin validar» con aviso.
3. **`juzgar` sin `--con`:** *usa los hechos del candidato actual*.
