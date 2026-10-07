# Dónde está cada cosa

Un proyecto Factory reparte lo que guarda entre cuatro lugares. Saber cuál es cuál evita inventar nombres: para el último caso hay comandos que lo dicen (`oracle-factory donde`, `ruta` y `buscar`, más abajo).

```text
proyecto/
  .factory/                           # lo que Factory produce; versionada, salvo local/
    LEEME.md                          # explica la carpeta; existe para que Git la versione aunque esté vacía
    config.json                       # configuración del proyecto: modo por defecto, tipos obligatorios y alias de capacidades
    specs/<capacidad>.json            # índice de la spec consolidada: de qué cambio viene cada requisito y qué reemplazó
    resumen.md                        # el estado actual en una lectura: se genera, no se edita a mano
    cambios/<ID>/                     # un cambio
      factory.json                    #   su estado: fase, decisiones, eventos
      review.md                       #   la revisión libre, si la hubo
      oracle-veredicto.txt            #   el último veredicto de Oracle
      candidatos/<sha7>/              # todo lo que se produjo sobre ese commit
        evidencia/                    #   salida del sensor, pruebas, cobertura de Oracle
        clue/                         #   paquete de contexto de Clue
        revision/                     #   informes, decisiones y triage de la revisión
    local/                            # de esta máquina; Git la ignora
      revisiones/<sha7>/              #   checkouts estables para que Clue revise
  openspec/changes/<ID>/              # el acuerdo humano, visible: propuesta, spec, diseño y plan
  openspec/specs/<capacidad>/spec.md  # lo vigente de cada capacidad: se genera al cerrar cada cambio
  tareas/                             # de Oracle Task: la tarea de cada cambio (TAREA.md)
  requisitos/  catalogos/  oracle.json    # de Oracle: requisitos, medidas y configuración
```

## Quién es dueño de qué

| Carpeta | Dueño | Qué contiene |
|---|---|---|
| `.factory/` | Factory | El estado de cada cambio, la configuración, los índices de las specs consolidadas (`specs/`), lo que se produce sobre un candidato y lo propio de cada máquina |
| `openspec/changes/<ID>/` | OpenSpec | Sólo el acuerdo: `proposal.md`, `design.md`, `tasks.md` y `specs/` |
| `openspec/specs/<capacidad>/` | Factory (formato OpenSpec) | La spec consolidada: los requisitos vigentes de la capacidad. Se genera; no se edita a mano |
| `tareas/` | Oracle Task | La tarea de cada cambio, con sus notas |
| `requisitos/`, `catalogos/`, `oracle.json` | Oracle | Los requisitos importados, las medidas y la configuración |

El acuerdo humano queda a la vista en `openspec/changes/`, no escondido: es lo que se lee para saber qué se construye, y si cambia, invalida la revisión.

## Lo versionado y lo local

- **`.factory/` se versiona**: es lo que comparten las personas. Lo que Factory escribe ahí lleva rutas relativas al proyecto, nunca la ruta de una máquina, para que un clon en otro lugar lo encuentre.
- **`.factory/local/` no se versiona**: `init` agrega `.factory/local/` al `.gitignore`. Ahí van los checkouts de revisión, que son de cada máquina. Si esa carpeta no estuviera ignorada, Git ofrecería esos checkouts como directorios sin seguimiento.
- **Git no versiona carpetas vacías**, así que `init` deja un archivo, `.factory/LEEME.md`, que explica la carpeta y hace que un clon la tenga.
- La huella de archivos del producto excluye `.factory/` entera, como ya excluye `tareas/`, y las specs consolidadas que genera Factory (ver más abajo): agregar evidencia o un paquete de Clue no invalida una revisión. Cambiar el acuerdo, el código o las medidas sí.

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

Todos son de sólo lectura. Un artefacto que el registro menciona pero ya no existe aparece como **AUSENTE**, no se oculta; un valor del registro que no es una ruta de texto aparece como **no válido**. `buscar` compara sin distinguir mayúsculas ni formas equivalentes (`Straße` y `STRASSE`), y avisa cuántos archivos omitió por superar 1 MB.

## Desde cualquier carpeta

Como Git, los comandos buscan `.factory/` subiendo desde la carpeta actual, y usan el proyecto que encuentren. Si lo encontraron arriba, lo dicen por la salida de error. `--proyecto` manda siempre; sin `.factory/` en ningún ancestro, se usa la carpeta actual como hasta ahora. `init` crea `.factory/` en la carpeta donde se ejecuta, y avisa si esa carpeta está dentro de otro proyecto.

Tres límites protegen de usar el proyecto equivocado:

- Un **proyecto anterior sin `.factory/`** (el que tiene `oracle.json` y `openspec/changes/`) es una frontera: no hereda el proyecto de afuera.
- **Tu carpeta personal nunca es la raíz.** Otras herramientas usan `~/.factory/` y no debe tomarse por un proyecto.
- Un **enlace simbólico** llamado `.factory` no cuenta como marcador.

## Los cambios anteriores

Los cambios creados antes de esta estructura tienen su evidencia en carpetas con otros nombres (`evidencia-mapeo`, `revision-pendiente`, `contexto-clue-<sha>.json`…). **No se mueven.** `donde` las lista como *históricas*: son evidencia atada a hashes y, en el caso de los paquetes de Clue, a la ruta del checkout que revisaron.

## Lo vigente de cada capacidad

Cada cambio trae una spec *delta*: lo que agrega (`ADDED`), modifica (`MODIFIED`) o quita (`REMOVED`); sin encabezados, todo cuenta como agregado. Al cerrar el cambio, Factory la fusiona en `openspec/specs/<capacidad>/spec.md`, que queda con los requisitos vigentes y, en cada uno, el cambio y el requisito de Oracle de los que viene. Para saber qué hace el sistema hoy se lee esa spec, no todas las propuestas.

- **Un conflicto no se resuelve solo:** agregar un requisito que ya existe, modificar o quitar uno que no existe, repetir un nombre en la spec del cambio o usar `RENAMED` rechaza el cierre antes de preguntar y nombra el requisito. Para resolverlo se corrige la spec del cambio: `MODIFIED` para cambiar un requisito que ya existe, `REMOVED` para darlo de baja, y para renombrarlo se quita y se agrega con el nombre nuevo. Corregir la spec cambia el acuerdo: hay que volver a aceptarla (`aprobar-spec`), reimportar, decidir las medidas y renovar la revisión y el juicio antes de cerrar.
- **Una spec consolidada editada a mano no se pisa:** si `openspec/specs/<capacidad>/spec.md` no es la que generó Factory, cerrar o archivar un cambio de esa capacidad se rechaza antes de preguntar. Se restaura con `git restore openspec/specs/<capacidad>/spec.md` y se vuelve a intentar (moverla no alcanza: una vez que existe su índice, Factory espera encontrarla); lo que se quería cambiar entra por la spec de un cambio.
- **Nada de lo cerrado se mueve:** a diferencia de OpenSpec, la carpeta del cambio queda en `openspec/changes/<ID>/` y sus requisitos de Oracle no se reimportan. `estado` de un cambio archivado dice cuáles de sus requisitos siguen vigentes y cuáles reemplazó otro cambio.
- **Un nombre por capacidad:** `capacidades` en `.factory/config.json` declara alias (`{"estructura2": "estructura"}`); un cambio con un alias se fusiona en la capacidad de destino, y `nuevo` lo avisa.
- **Los cambios cerrados antes de esto** se archivan con `oracle-factory archivar`, en el orden en que se cerraron; correrlo de nuevo no cambia nada.
- La spec consolidada que generó Factory (la que tiene índice en `.factory/specs/<capacidad>.json`) queda fuera de la huella del producto, como `.factory/`: se deriva de specs ya aceptadas, y si contara, archivar los cambios anteriores vencería la revisión del último cambio integrado. Cualquier otro archivo de `openspec/specs/` sí cuenta.
- **Si se corta:** `cerrar` cierra primero y fusiona después. Un corte antes de cerrar no deja nada fusionado y se reintenta; uno después deja el cambio cerrado sin archivar, y `oracle-factory archivar` lo completa.

## El estado actual en una lectura

`oracle-factory resumen` escribe `.factory/resumen.md`: los requisitos vigentes de cada capacidad (con su tipo, sus medidas, el cambio del que vienen y el veredicto con que se cerró ese cambio), los cambios abiertos con lo que les falta, los riesgos que aceptó una persona y los límites declarados en las revisiones, separando los de cambios que todavía tienen requisitos vigentes de los históricos. No copia los escenarios: enlaza la spec consolidada de cada capacidad.

- **Se lee con formato** con `glow -p .factory/resumen.md`.
- **El veredicto es el del cierre**, con su fecha; no es una corrida nueva de Oracle.
- **Se regenera solo** al cerrar y al archivar. `oracle-factory resumen --verificar` dice, sin escribir, si falta o quedó viejo (por ejemplo, porque un cambio abierto avanzó o un commit venció una revisión): las mismas entradas dan siempre los mismos bytes, así que verificar es regenerar y comparar.
- **No vence ninguna revisión:** vive en `.factory/`, fuera de la huella. `--salida RUTA` lo escribe en otro lugar del proyecto (por ejemplo `RESUMEN.md`); fuera de `.factory/`, ese archivo sí cuenta en la huella.

## Migrar un proyecto anterior (fase 2)

Hasta la fase 2, el estado de cada cambio (`factory.json`, `review.md`, `oracle-veredicto.txt`) vivía en `openspec/changes/<ID>/` y la configuración en un `factory.json` de la raíz. Un proyecto así **sigue funcionando**: Factory lee y escribe el estado donde está y avisa por la salida de error que existe `migrar`. Nada se mueve solo.

```text
oracle-factory migrar --verificar    # lista lo que movería, no escribe; falla mientras haya algo por migrar
oracle-factory migrar                # lo mueve; no hace commits
```

`migrar` escribe lo nuevo antes de borrar lo viejo y el registro al final, y en el registro sólo reescribe las rutas que citan `review.md` y `oracle-veredicto.txt`; el resto queda byte a byte. Si lo cortan, se vuelve a correr. Si un cambio tiene el estado en los dos lugares con contenido distinto, o si algo del camino es un enlace simbólico, avisa, no toca ese cambio y termina con código distinto de cero. Lo que no sabe mover (una carpeta de cambio sin registro, un `factory.json` de la raíz que no es la configuración de Factory) lo deja donde está y lo avisa, pero no es un fallo: la segunda ejecución da 0. Después de migrar, `estado` dice lo mismo y las revisiones siguen vigentes, porque la huella del producto no incluye `.factory/`. La excepción es la configuración de la raíz: es parte del producto, y moverla cambia la huella (`--verificar` lo avisa antes).

## Límites declarados

- **`tareas/` y su evidencia no se mueven**: la evidencia anterior a la estructura sigue en `tareas/<ID>/evidencia-*` y `donde` la lista como histórica.
- **`migrar` no juzga el contenido de la configuración**: mueve el `factory.json` de la raíz si sus claves son las de Factory, aunque un valor sea inválido; `config_proyecto` lo rechaza igual en el lugar nuevo, como antes en la raíz.
- **`migrar` no se defiende de otro proceso que cree enlaces mientras corre**: borra el nombre del temporal y lo abre sin seguir enlaces, pero no se prueba con concurrencia.
- **Sólo Linux, probado.** No se probó en Windows ni con otras versiones de Python que la del entorno de desarrollo.
- **`.factory/` entera queda fuera de la huella del producto**, por decisión de la spec: lo que Factory produce (evidencia, paquetes, informes) no invalida una revisión. Otra herramienta que use una carpeta `.factory` en el mismo proyecto se tomaría como propia; la carpeta personal y los enlaces simbólicos nunca cuentan como raíz.
- **`buscar` y `donde` no rechazan un enlace simbólico en otro lugar** (por ejemplo `openspec/` o `tareas/` enlazados): son de sólo lectura y el enlace lo puso quien trabaja en el proyecto. Sí rechazan que `.factory` sea un enlace.
