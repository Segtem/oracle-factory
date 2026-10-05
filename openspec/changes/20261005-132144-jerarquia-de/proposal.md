# Jerarquía de carpetas: una carpeta `.factory/` y comandos para encontrar las cosas

## Why

Saber dónde está cada cosa es parte del trabajo, no un detalle. Hoy Factory define dónde van el acuerdo (`openspec/changes/<ID>/`) y la tarea (`tareas/<ID>/TAREA.md`), pero no dónde va todo lo que se produce después. En las tres tareas trabajadas el 2026-10-05 se inventaron más de treinta nombres sobre la marcha:

- `evidencia`, `evidencia-mapeo`, `evidencia-mapeo-descartada`, `evidencia-<sha>` (seis variantes);
- `revision-pendiente`, `revision-pendiente.md`, `revision-mapeo-pendiente.md`, `revision-brian`, `revision-r2`, `revisiones/preparacion-*`, `revisiones/registro-*`;
- `contexto-clue-<sha>.json` y `contexto-clue-<sha>-durable.json` (doce paquetes);
- `piloto-agentes-01`, `piloto-pendiente.md`.

Además, Task rechazó `tareas/integracion-<sha>/` como «nombre de carpeta inválido», y los checkouts de revisión empezaron en `/tmp` y se perdían al reiniciar.

Esos registros están repartidos entre `openspec/changes/<ID>/` y `tareas/<ID>/`, y la huella del producto los separa con excepciones sueltas (`tareas/` y tres archivos dentro de `openspec/changes/<ID>/`). Esas excepciones son frágiles: crear un cambio nuevo en la rama principal invalidó la revisión de los modos de trabajo. Y como Factory usa la carpeta actual o `--proyecto`, no funciona desde una subcarpeta como lo hace Git.

Brian propuso, el 2026-10-05, una carpeta propia «al estilo git» donde esté todo lo que Factory necesita. Este cambio la introduce.

## What changes

1. **Una carpeta `.factory/` en la raíz del proyecto**, creada por `init`:

   ```text
   proyecto/
     .factory/                  # versionada: lo que comparten las personas
       cambios/<ID>/            # lo que Factory produce sobre un cambio
         candidatos/<sha7>/{evidencia, clue, revision}/
       local/                   # IGNORADA por Git: de esta máquina
         revisiones/<sha7>/     # checkouts estables para que Clue revise
     openspec/changes/<ID>/     # el acuerdo humano, visible: propuesta, spec, diseño
     tareas/  requisitos/  catalogos/  oracle.json    # de Task y de Oracle
   ```

   Una carpeta por candidato (SHA de 7 caracteres) agrupa todo lo que se produjo sobre ese commit.
2. **Descubrimiento como Git:** los comandos suben desde la carpeta actual hasta encontrar `.factory/`. `--proyecto` sigue mandando; sin `.factory/` en ningún ancestro, el comportamiento es el de hoy.
3. **Lo versionado y lo local:** lo compartido va en Git y sin rutas absolutas; lo de cada máquina (checkouts, bloqueos, cachés) va en `.factory/local/`, ignorada.
4. **La huella del producto excluye `.factory/` entera**, en lugar de las excepciones sueltas. Los registros que Factory produce se verifican por sus propios hashes, como ocurre hoy con `tareas/`.
5. **Comandos para encontrar las cosas:** `oracle-factory donde ID`, `ruta ID TIPO` y `buscar TEXTO`, más filtros en `listar`, todos de sólo lectura.
6. **Estructura documentada** en `docs/estructura.md`, enlazada desde el README.
7. **Lo existente se respeta:** los cambios anteriores no se mueven; `donde` los marca como históricos.

## Out of scope

- **Mover el estado de cada cambio** (`factory.json`, `review.md`, `oracle-veredicto.txt`) y la configuración del proyecto a `.factory/`: es la fase 2, un cambio propio.
- Las carpetas de otras herramientas: `tareas/` es de Oracle Task; `requisitos/`, `catalogos/` y `oracle.json` son de Oracle; `openspec/` es de OpenSpec. Sus nombres son fijos.
- Esconder el acuerdo humano: la propuesta y la spec siguen visibles en `openspec/changes/`.
- Crear o gestionar worktrees de desarrollo. Los checkouts de Clue se crean con `git worktree add` en la ruta que imprime `ruta`.
- Índices o bases de datos: la búsqueda recorre los archivos.
- La herramienta de revisión en el IDE y la web (tareas `revision-ide` y `docs-web-modos`).

## Human decisions

Brian respondió en la conversación del 2026-10-05:

1. **Raíz de los checkouts de revisión:** dentro del proyecto, en `.factory/local/revisiones/`, ignorada por Git (reemplaza la clave `raiz_revisiones` propuesta antes).
2. **Carpeta de candidato:** SHA de 7 caracteres.
3. **Cambios existentes:** quedan como están; `donde` los marca como históricos.
4. **Comandos:** `donde`, `ruta` y `buscar`, en español.
5. **`.factory/` y su contenido** (aceptando las cinco recomendaciones): el acuerdo humano queda visible en `openspec/`; `.factory/` es versionada con `local/` ignorada; los comandos suben carpetas como Git; la spec de estructura se reescribe antes de implementar; Factory no gestiona worktrees de desarrollo.

6. **La revisión independiente (R2) encontró nueve hallazgos** y Brian aceptó (2026-10-05, «Dale») corregirlos todos y reescribir la spec con los escenarios que faltaban: el clon trae `.factory/`, la frontera de un proyecto sin `.factory/`, la carpeta personal, el enlace simbólico, los valores no válidos en `donde`, los archivos omitidos y las formas equivalentes en `buscar`.

Pendiente: aceptación de proposal.md y spec.md. Preparar esta propuesta no la acepta ni autoriza implementarla.
