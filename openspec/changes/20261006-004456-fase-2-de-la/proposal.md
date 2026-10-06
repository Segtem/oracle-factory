# Fase 2 de la estructura: el estado de cada cambio y la configuración van a .factory/

## Why

La fase 1 (`20261005-132144-jerarquia-de`) creó `.factory/` para lo que Factory produce sobre un candidato (evidencia, paquetes de Clue, informes). El **estado** de cada cambio sigue repartido: el registro `factory.json`, la revisión libre `review.md` y el veredicto `oracle-veredicto.txt` viven mezclados con el acuerdo humano en `openspec/changes/<ID>/`, y la configuración del proyecto en un `factory.json` de la raíz. Quien abre `openspec/changes/<ID>/` para leer qué se construye se encuentra con archivos que escribe una máquina, y la regla «lo humano a la vista, lo que Factory produce en `.factory/`» se cumple a medias.

Medido hoy: 13 cambios con registro, 6 con `oracle-veredicto.txt` y 3 con `review.md`; 12 registros citan la ruta `openspec/changes/<ID>/oracle-veredicto.txt`. La configuración de la raíz es opcional y este repositorio no la usa.

## What changes

1. **Un lugar para el estado.** Un cambio nuevo guarda `factory.json`, `review.md` y `oracle-veredicto.txt` en `.factory/cambios/<ID>/`. En `openspec/changes/<ID>/` quedan sólo el acuerdo: `proposal.md`, `design.md`, `tasks.md` y `specs/`.
2. **La configuración** del proyecto se escribe en `.factory/config.json`. Si sólo existe el `factory.json` de la raíz, se sigue leyendo y se avisa.
3. **Un proyecto no migrado sigue funcionando**: si el estado de un cambio está en el lugar viejo, se lee de ahí y se avisa cómo migrar. Nada se mueve solo.
4. **Un comando `oracle-factory migrar`** mueve el estado de todos los cambios al lugar nuevo. Reescribe en el registro las rutas que citan los archivos movidos, no toca ningún otro contenido, y es repetible. `--verificar` dice qué movería sin escribir nada.
5. **La migración conserva el significado**: el `estado` de cada cambio dice lo mismo antes y después, y las revisiones y veredictos siguen vigentes (la huella del producto ya excluye estos archivos y `.factory/`, así que no cambia).
6. Se migran en este repositorio los 13 cambios existentes, con revisión independiente (R2) porque toca registros de cambios cerrados.
7. Los comandos `donde`, `ruta`, `buscar` y `listar` entienden los dos lugares; la guía `docs/estructura.md` describe el layout nuevo.

## Out of scope

- **`tareas/` no se mueve** (es de Oracle Task) ni se reescribe su evidencia; tampoco se mueve la evidencia anterior de `tareas/<ID>/evidencia-*` a `.factory/cambios/<ID>/candidatos/`.
- **El acuerdo (`proposal`, `spec`, `design`, `tasks`) queda en `openspec/changes/<ID>/`**, a la vista, como se decidió en la fase 1.
- Cambiar el contenido o el formato de `factory.json` y de la configuración.
- Reescribir el historial de Git.

## Human decisions

Respondidas por Brian el 2026-10-06:

1. **Cambios que ya existen:** *migrarlos* (no leerlos como histórico). Por eso `migrar` es parte del cambio, con su verificación y una revisión de R2.
2. **Configuración del proyecto:** *a `.factory/config.json`*, con la raíz como respaldo con aviso.
3. **Qué va a la carpeta de cada cambio:** *sólo el estado*; el acuerdo se queda en `openspec/changes/<ID>/`.
