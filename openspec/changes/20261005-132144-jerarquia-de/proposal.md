# Jerarquía de carpetas y comandos para encontrar las cosas

## Why

Saber dónde está cada cosa es parte del trabajo, no un detalle. Hoy Factory define dónde van el acuerdo (`openspec/changes/<ID>/`) y la tarea (`tareas/<ID>/TAREA.md`), pero no dónde va todo lo que se produce después. En las tres tareas trabajadas el 2026-10-05 se inventaron más de treinta nombres sobre la marcha:

- `evidencia`, `evidencia-mapeo`, `evidencia-mapeo-descartada`, `evidencia-<sha>` (seis variantes);
- `revision-pendiente`, `revision-pendiente.md`, `revision-mapeo-pendiente.md`, `revision-brian`, `revision-r2`, `revisiones/preparacion-*`, `revisiones/registro-*`;
- `contexto-clue-<sha>.json` y `contexto-clue-<sha>-durable.json` (doce paquetes);
- `piloto-agentes-01`, `piloto-pendiente.md`.

Además, Task rechazó `tareas/integracion-<sha>/` como «nombre de carpeta inválido», y los checkouts de revisión empezaron en `/tmp` y se perdían al reiniciar.

Para encontrar la evidencia de un candidato o el informe que respalda una revisión, hoy hay que conocer la historia. Una persona que llega, o un agente nuevo, no puede deducirlo.

## What changes

1. **Estructura documentada** (`docs/estructura.md`): qué va en la raíz del proyecto, en `openspec/changes/<ID>/` (el acuerdo y los registros de Factory) y en `tareas/<ID>/` (el trabajo y su evidencia), con una carpeta por candidato:

   ```text
   tareas/<ID>/
     TAREA.md
     candidatos/<sha>/        # todo lo que se produjo sobre ese commit
       evidencia/             # salida del sensor, pruebas, cobertura Oracle
       clue/                  # paquete de contexto
       revision/              # informes, decisiones y triage, uno por revisor
     piloto/  integracion/    # cuando existen
   ```

   Los checkouts estables de revisión van fuera del repositorio, en una raíz configurable.
2. **`oracle-factory donde ID`**: lista cada artefacto del cambio con su ruta, si existe y a qué gate respalda (spec, medidas, revisión, juicio, cierre). Con `--candidato SHA`, sólo lo de ese candidato.
3. **`oracle-factory ruta ID TIPO`**: imprime la ruta canónica para producir un artefacto sobre el HEAD actual, por ejemplo `--salida $(oracle-factory ruta ID evidencia)`. Así los sensores, Clue y los agentes escriben donde corresponde sin inventar nombres.
4. **`oracle-factory buscar TEXTO`**: busca en propuestas, specs, requisitos, tareas y registros, y muestra la ruta, la línea y el cambio al que pertenece cada resultado. Complementa `tasks search`, que sólo mira las tareas.
5. **`oracle-factory listar` con filtros** por fase y por estado (abiertos, cerrados).
6. **Lo existente se respeta:** los cambios anteriores no se mueven. `donde` reconoce los nombres viejos y los marca como históricos.

## Out of scope

- Mover automáticamente los artefactos de cambios existentes.
- La herramienta de revisión en el IDE (tarea `revision-ide`) y la web (tarea `docs-web-modos`).
- La estructura interna de Oracle, Task o Clue.
- Índices o bases de datos: la búsqueda recorre los archivos.

## Human decisions

Brian respondió en la conversación del 2026-10-05, aceptando las recomendaciones:

1. **Raíz de los checkouts de revisión:** configurable en `factory.json` del proyecto con la clave `raiz_revisiones`; por defecto `~/Dev/_revisiones`. Quien trabaje en otra máquina la cambia en su `factory.json`.
2. **Carpeta de candidato:** SHA de 7 caracteres.
3. **Cambios existentes:** quedan como están; `donde` los marca como históricos.
4. **Comandos:** `donde`, `ruta` y `buscar`, en español.

Pendiente: aceptación de proposal.md y spec.md. Preparar esta propuesta no la acepta ni autoriza implementarla.
