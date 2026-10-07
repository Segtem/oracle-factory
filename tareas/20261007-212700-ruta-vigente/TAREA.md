# oracle-factory ruta apunta al candidato vigente, no a HEAD

- ESTADO: ABIERTA
- PRIORIDAD: 10
- ETIQUETAS: estructura, autoproduccion


## Objetivo

`oracle-factory ruta ID evidencia` imprime la carpeta del candidato de HEAD (así lo dice la spec consolidada, `openspec/specs/estructura/spec.md`). Pero un commit que sólo guarda informes o evidencia no cambia el producto: el candidato sigue siendo el vigente. Si se produce evidencia en la ruta de HEAD, se crea una carpeta de candidato nueva que pasa a ser la vigente y deja huérfanos los informes del candidato real.

Pasó en el cambio 20261007-192608-revisores: tras commitear el informe de agy, `ruta` dio `11b2048` en vez de `962ede7`, el verificador escribió allí y no encontró la revisión. `pedir-revision` y `juzgar` ya usan el candidato vigente; `ruta` debería hacer lo mismo (MODIFIED en la spec de estructura).

## Notas

- Mientras tanto: producir la evidencia antes de commitear los informes, o escribirla en `ruta_canonica(..., candidato_vigente(ID))`.
- Las carpetas creadas por error en ese cambio están fuera del repo, en el scratchpad (no se borraron).
