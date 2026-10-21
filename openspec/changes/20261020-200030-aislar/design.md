# Design

- En `pedir_revision`, en lugar de `git worktree add --detach CHECKOUT HEAD`: `git clone --quiet --local --no-checkout
  ROOT CHECKOUT` y `git -C CHECKOUT checkout --quiet --detach HEAD`. `--local` enlaza los objetos en el mismo disco
  (no copia nada) y el clon no depende del repositorio: un gc no lo deja sin el candidato. La base del paquete de Clue es un SHA, que el clon tiene.
- Prueba: un revisor de prueba que, en su checkout, cambia `user.name`, crea una rama y hace un commit; después el
  repositorio sigue con su `user.name`, sin esa rama, y el informe se valida igual.
