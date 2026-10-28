# Declarar publicada la 0.1.0a15 en las notas y los textos

## Why

La 0.1.0a15 ya está publicada en PyPI (con los mismos SHA-256 que los archivos preparados), con su tag `v0.1.0a15` y su release de GitHub. Pero las notas de versión, el README, la web y la guía siguen diciendo que está «en preparación» y que los comandos de instalación «se podrán usar cuando se publique». Es el mismo error que se corrigió con la 0.1.0a14, y quien lee el repositorio recibe una información falsa sobre cómo instalar.

## What changes

- Las notas de la 0.1.0a15 dejan de decir «en preparación» y declaran la publicación en PyPI, con su tag y su release.
- El README, `docs/colaboracion.md`, la guía «desde cero» y la portada dejan de presentar la 0.1.0a15 como candidata en preparación y dicen que está publicada.
- El texto de la guía que fijan las pruebas se actualiza a lo mismo.
- La detección de divergencias de documentación suma el sentido contrario: cuando las notas declaran publicada la versión actual, ningún texto puede describirla como candidata o en preparación.

## Out of scope

- Cambiar nada del producto ni de la versión.
- Publicar o etiquetar otra cosa.
- Reescribir las notas de las versiones anteriores.

## Human decisions

- Ninguna: es el estado real, comprobado contra PyPI.
