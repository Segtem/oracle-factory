# Ensayo: migrar Factory mismo a un almacén, con lo preparado (2026-11-12)

`python tools/ensayar_migracion.py ~/Dev/factory-preparar-migracion --pruebas`, sobre un clon temporal del commit `4f9beb71`
(la implementación de este cambio), con un almacén y una configuración de usuario temporales. Tardó 959 s (la suite dos veces).
No tocó el repo de Factory ni la configuración del usuario.

## Qué pasó

- `migrar --almacen` copió **6672 archivos versionados** al almacén en un commit. Sacó las líneas de Factory de `.gitignore` y
  `.gitattributes` del producto. En el índice de la copia quedaron 6674 cambios sin commitear: las 6672 bajas más esos dos
  archivos. No movió nada sin versionar (el clon no trae `.factory/local/`) ni sacó hooks (un clon no trae los hooks de
  `.git/hooks`; los cubre pm2).
- `listar` muestra los mismos cambios antes y después (sin la línea «Acuerdos:», que nombra dónde están los registros).
- Pruebas de la copia: **1478, todas bien antes y después de migrar**, con 15 omitidas en las dos corridas (el clon no trae
  `node_modules/`: las de la web con Playwright). En el ensayo de la etapa 6 fallaban 17 después de migrar: las 15 de
  `test_terminal_lista` (arregladas en la etapa 6) y p6 y vg3 (arregladas en este cambio).

## Lo que queda para la migración real (decisión de Brian, aparte)

- Crear el repo del almacén, correr `oracle-factory migrar --almacen` desde `~/Dev/factory` y revisar la baja con `git status`.
- Mantener la guía versionada con `oracle-factory agentes --en-el-repo`.
- `migrar` saca los hooks del trailer y de rehacer lo generado; la puerta pre-push queda. Los drivers de unión que `hooks`
  escribió en `.git/config` quedan: sacarlos sería cambiar la configuración de Git, y sin las líneas de `.gitattributes` no se usan.
- Mover los 162 MB de `.factory/local/` (lo hace `migrar`).
- Commitear y empujar la baja borra unos 6700 archivos en origin y respaldo; los `tools/verify_*.py` de cambios cerrados, que
  leen registros del repo, no se vuelven a correr.
