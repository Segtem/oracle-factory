# Declarar publicada la 0.1.0a18

## Por qué

La 0.1.0a18 ya está en PyPI (los hashes del wheel y del sdist coinciden con los que salieron de `main`), tiene su tag `v0.1.0a18` y su pre-release en GitHub. Pero las notas, el README, la guía y la portada de `main` todavía la presentan como «en preparación» y dicen que sus comandos «se podrán usar cuando se publique». Quien instala o lee la web recibe una información que contradice la release.

## Qué cambia

- Las notas de la 0.1.0a18 dejan de decir «(en preparación)» y suman la línea «Publicada» con su tag y su release, como la a17.
- El README dice «Versión publicada en PyPI: `oracle-factory==0.1.0a18`».
- `docs/colaboracion.md`, la guía `site/desde-cero.html` y la portada `site/index.html` hablan de la a18 como publicada, no como candidata; `tests/datos/guias-texto.json` se regenera.
- Pruebas nuevas (`tests/test_publicada_a18.py`) fijan ese estado y comprueban que la regla de `docs_al_dia` detecta lo que siga llamando candidata a la versión publicada.
- Las pruebas de `tests/test_entrega_a18.py` y `tests/test_docs.py` que afirmaban el estado «en preparación» pasan a afirmar el estado publicado.

## Fuera de alcance

- No se publica nada ni se cambia el tag o la release: ya están hechos.
- No se cambia código del producto ni la versión.
- La reorganización grande de la web (capturas, simulación, ejemplos) es de los cambios que siguen.

## Decisiones humanas

- Aprobar esta spec. Brian ya subió la a18 a PyPI y pidió el tag y la release.
