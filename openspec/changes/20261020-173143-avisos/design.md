# Design

- `specs_de_otra_capacidad`: las `specs/*/spec.md` del cambio que no son `estado["spec"]`; `aprobar-spec` falla antes de
  mostrar el menú.
- `importar`: los ids de los eventos `requisitos_importados` anteriores menos los de esta importación; el dominio de
  esos requisitos es propio del cambio (`capacidad_c<sha de id y spec>`), así que se borran sus `.requisito` sin tocar
  los de otros cambios.
- `sin_medir_con_medidas`: requisitos con medidas decididas cuyo `.requisito` tiene `sin_medir`; lo usan el aviso de
  `estado` y el error de `juzgar`.
