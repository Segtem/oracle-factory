# Design

- El hook es un script corto en la carpeta de hooks de Git (`git rev-parse --git-path hooks`, que respeta
  `core.hooksPath` y es compartida por los worktrees) que llama a `oracle-factory trailer` con el intérprete de Factory
  que lo instaló. Marca propia en una línea para reconocerlo; si no está el intérprete, sale con 0.
- `trailer ARCHIVO [FUENTE]`: si en este checkout hay exactamente un cambio abierto y el mensaje no tiene ya `Cambio:`,
  agrega `Cambio: ID` con `git interpret-trailers --in-place` (respeta los otros trailers, como Co-Authored-By).
- `log` junta: `git log --all --grep '^Cambio: ID$'`; los candidatos del registro (eventos con `candidato` y carpetas
  `candidatos/*`); y el merge más viejo de HEAD que trajo un candidato (`git log --ancestry-path --merges c..HEAD`),
  cuyo rango `M^1..M^2` son los commits de la rama. Sin merge, sólo los candidatos.
- El tablero recibe `commits` por cambio desde `datos_estado`; el panel pide `{tipo: 'commit', sha}` y la extensión,
  con el sha validado como hex, abre `git show` en un documento de sólo lectura con lenguaje diff.
