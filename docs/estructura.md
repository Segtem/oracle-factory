# Dónde está cada cosa

Un proyecto Factory reparte lo que guarda entre cuatro lugares. Saber cuál es cuál evita inventar nombres: para el último caso hay comandos que lo dicen (`oracle-factory donde`, `ruta` y `buscar`, más abajo).

```text
proyecto/
  .factory/                           # lo que Factory produce; versionada, salvo local/
    cambios/<ID>/                     # un cambio
      candidatos/<sha7>/              # todo lo que se produjo sobre ese commit
        evidencia/                    #   salida del sensor, pruebas, cobertura de Oracle
        clue/                         #   paquete de contexto de Clue
        revision/                     #   informes, decisiones y triage de la revisión
    local/                            # de esta máquina; Git la ignora
      revisiones/<sha7>/              #   checkouts estables para que Clue revise
  openspec/changes/<ID>/              # el acuerdo humano, visible: propuesta, spec, diseño y plan
  tareas/                             # de Oracle Task: la tarea de cada cambio (TAREA.md)
  requisitos/  catalogos/  oracle.json    # de Oracle: requisitos, medidas y configuración
```

## Quién es dueño de qué

| Carpeta | Dueño | Qué contiene |
|---|---|---|
| `.factory/` | Factory | Lo que se produce sobre un candidato y lo propio de cada máquina |
| `openspec/changes/<ID>/` | OpenSpec y Factory | El acuerdo (`proposal.md`, `spec.md`, `design.md`, `tasks.md`) y el registro del cambio (`factory.json`) |
| `tareas/` | Oracle Task | La tarea de cada cambio, con sus notas |
| `requisitos/`, `catalogos/`, `oracle.json` | Oracle | Los requisitos importados, las medidas y la configuración |

El acuerdo humano queda a la vista en `openspec/changes/`, no escondido: es lo que se lee para saber qué se construye, y si cambia, invalida la revisión.

## Lo versionado y lo local

- **`.factory/` se versiona**: es lo que comparten las personas. Lo que Factory escribe ahí lleva rutas relativas al proyecto, nunca la ruta de una máquina, para que un clon en otro lugar lo encuentre.
- **`.factory/local/` no se versiona**: `init` agrega `.factory/local/` al `.gitignore`. Ahí van los checkouts de revisión, que son de cada máquina. Si esa carpeta no estuviera ignorada, Git la vería como un directorio sin seguimiento y la huella del producto la rechazaría.
- La huella de archivos del producto excluye `.factory/` entera, como ya excluye `tareas/`: agregar evidencia o un paquete de Clue no invalida una revisión. Cambiar el acuerdo, el código o las medidas sí.

## Una carpeta por candidato

Un candidato es un commit sobre el que se produjo algo. Su carpeta es `.factory/cambios/<ID>/candidatos/<sha7>/`, se llama como el SHA de 7 caracteres del commit, y agrupa lo que se produjo en él:

```fish
oracle-factory ruta ID evidencia      # .../.factory/cambios/ID/candidatos/<sha7>/evidencia
oracle-factory ruta ID clue           # .../candidatos/<sha7>/clue
oracle-factory ruta ID revision       # .../candidatos/<sha7>/revision
oracle-factory ruta ID checkout       # .../.factory/local/revisiones/<sha7>
```

`ruta` imprime la ruta sobre el HEAD actual y **no crea nada**. Se usa así:

```fish
python examples/notas/sensor.py --salida (oracle-factory ruta ID evidencia)/hechos.json
git worktree add --detach (oracle-factory ruta ID checkout) HEAD
```

## Encontrar las cosas

| Comando | Para qué |
|---|---|
| `oracle-factory donde ID` | Lista cada artefacto del cambio con su ruta, si existe y qué gate respalda |
| `oracle-factory donde ID --candidato SHA` | Lo mismo, limitado a ese candidato |
| `oracle-factory buscar TEXTO` | Busca en propuestas, specs, requisitos, tareas y registros; muestra ruta, línea y cambio |
| `oracle-factory listar --abiertos` | Los cambios abiertos (también `--cerrados` y `--fase FASE`) |

Todos son de sólo lectura. Un artefacto que el registro menciona pero ya no existe aparece como **AUSENTE**, no se oculta.

## Desde cualquier carpeta

Como Git, los comandos buscan `.factory/` subiendo desde la carpeta actual, y usan el proyecto que encuentren. Si lo encontraron arriba, lo dicen por la salida de error. `--proyecto` manda siempre; sin `.factory/` en ningún ancestro, se usa la carpeta actual como hasta ahora. `init` crea `.factory/` en la carpeta donde se ejecuta.

## Los cambios anteriores

Los cambios creados antes de esta estructura tienen su evidencia en carpetas con otros nombres (`evidencia-mapeo`, `revision-pendiente`, `contexto-clue-<sha>.json`…). **No se mueven.** `donde` las lista como *históricas*: son evidencia atada a hashes y, en el caso de los paquetes de Clue, a la ruta del checkout que revisaron.

## Lo que viene

Esta es la primera fase. El estado de cada cambio (`factory.json`, `review.md`, `oracle-veredicto.txt`) y la configuración del proyecto todavía viven en `openspec/changes/<ID>/` y en la raíz; pasarlos a `.factory/` es un cambio aparte.
