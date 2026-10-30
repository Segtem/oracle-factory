# Preparar la distribución 0.1.0a16

## Why

La versión 0.1.0a15 ya está publicada en PyPI, pero Factory siguió mejorando después de prepararla: registra la procedencia de las dependencias de cada candidato (inventario CycloneDX, quién usó una dependencia, auditoría contra avisos OSV y consulta a OSV.dev con autorización explícita de red); su `uv.lock` viaja con el repositorio y una prueba exige que coincida con `pyproject.toml`; el código de la CLI se repartió en módulos para no pasar el límite de tamaño de la revisión; y las notas y los textos declaran publicada la 0.1.0a15. Brian necesita una versión instalable desde PyPI que tenga todo eso, para usar Factory fuera de su máquina.

## What changes

- La versión pasa a 0.1.0a16 en los metadatos del paquete, en la CLI, en el README, en las notas de versión, en la guía y en la web.
- Las notas dejan de decir que la 0.1.0a15 es la última: está publicada, con su tag y su release. La 0.1.0a16 queda declarada como preparada, no como publicada, hasta que Brian la suba.
- Se regenera y se versiona el `uv.lock` con la versión nueva.
- Se construye el wheel y el sdist, se instalan en un entorno nuevo y se comprueban desde fuera del checkout: versión, origen de importación, las consultas de siempre y lo nuevo de esta versión.
- Se corre la suite y se registra la evidencia, con sus hashes y sus límites.

## Out of scope

- Publicar en PyPI, crear el tag o la release de GitHub de la 0.1.0a16: lo hace Brian, o yo por su pedido explícito y después de la revisión y el cierre.
- Cambiar versiones de Oracle, Oracle Task u Oracle Clue.
- Empaquetar la extensión de VS Code en una versión nueva.
- Probar `--consultar-osv` contra api.osv.dev real: la entrega lo comprueba contra un servidor local, y el límite queda declarado.

## Human decisions

- Que la 0.1.0a16 salga con `procedencia`, `uv-lock` y `avisos-osv`, que ya están integrados en `main`.
