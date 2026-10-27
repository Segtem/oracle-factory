# Design

`oracle_factory/cli.py` (`nuevo`, `config_proyecto`) elige el texto de cuatro plantillas guardadas en un diccionario por idioma; `config_proyecto` suma la clave `idioma` con su validación y `nuevo` el argumento `--idioma`. Las plantillas viven en un módulo chico (`oracle_factory/plantillas.py`) para que se puedan comparar entre sí. No cambia el esquema del registro: el idioma sólo decide el texto de los archivos al crearlos.
