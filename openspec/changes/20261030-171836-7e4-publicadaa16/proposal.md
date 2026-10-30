# Declarar publicada la 0.1.0a16 en las notas y los textos

## Por qué

La 0.1.0a16 ya está publicada en PyPI (con los mismos SHA-256 que los archivos preparados, e instalada en un entorno limpio), con su tag `v0.1.0a16` y su release de GitHub. Pero las notas de versión, el README, la web y la guía siguen diciendo que está «en preparación» y que los comandos de instalación «se podrán usar cuando se publique». Es el mismo error que se corrigió con la 0.1.0a14 y la 0.1.0a15, y quien lee el repositorio recibe una información falsa sobre cómo instalar.

## Qué cambia

- Las notas de la 0.1.0a16 dejan de decir «en preparación» y declaran la publicación en PyPI, con su tag y su release.
- El README, `docs/colaboracion.md`, la guía «desde cero» y la portada dejan de presentar la 0.1.0a16 como candidata en preparación y dicen que está publicada.
- El texto de la guía que fijan las pruebas se actualiza a lo mismo.
- Las pruebas de la entrega pasan a comprobar el estado publicado, y la regla que detecta lo que siga llamando candidata a una versión publicada conserva su cobertura con pruebas propias.

## Fuera de alcance

- Cambiar nada del producto ni de la versión.
- Publicar o etiquetar otra cosa.
- Reescribir las notas de las versiones anteriores.

## Decisiones humanas

- Ninguna: es el estado real, comprobado contra PyPI, el tag y la release.
