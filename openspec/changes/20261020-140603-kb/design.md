# Design

- `oracle_factory/kb.py` arma el vault puro desde lo que la CLI ya sabe (`leer`, `datos_estado` para abiertos, el
  registro para cerrados, `commits_del_cambio`, los requisitos con su veredicto del informe de Oracle). Notas:
  `kb/cambios/<ID>.md`, `kb/requisitos/<id>.md`, `kb/README.md` (índice). Cada nota generada lleva
  `generado: oracle-factory kb` en el frontmatter y una línea que dice que no se edita a mano. Texto determinista
  (orden fijo, sin la hora de generación) para que `--verificar` compare byte a byte.
- Se regenera donde hoy se llama `actualizar_resumen()`.
- Notas humanas: `kb/notas/*.md` con frontmatter `fuentes: [ruta, requisito o ID]`. La huella vive en
  `.factory/kb.json` (`{nota: {fuente: sha256, revisada_por, cuando}}`); una fuente archivo es su contenido, una de
  requisito es su `.requisito`, una de cambio es su registro. `kb revisada NOTA` exige terminal (persona).
- `por-que`: `git blame --porcelain -L N,N`, después `cambio_del_commit`-like: el trailer del commit, o el cambio cuyo
  `commits_del_cambio` lo contiene (se busca sólo si no hay trailer). Las decisiones salen de los eventos con forma
  `decidio`/`confirmo` y su motivo; los hallazgos y riesgos, de los informes y `aceptados` filtrados por ese archivo.
- VS Code: comando `factory.porQue` que corre `oracle-factory por-que --json` con el archivo y la línea del editor activo
  y lo muestra en un panel de sólo lectura.
