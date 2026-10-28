# Registrar la procedencia de las dependencias de cada candidato

## Why

Hoy Factory registra qué se decidió y con qué evidencia, pero no de dónde viene el software de terceros sobre el que corre cada candidato. Si mañana se descubre una vulnerabilidad en una dependencia, no hay forma de saber qué cambios y qué entregas la usaron, ni de decidir qué corregir. El propio `uv.lock` de Factory ilustra el problema: dice que `oracle-factory` es la 0.1.0a3, fija Oracle 0.38.1 y no incluye Oracle Clue, mientras que `pyproject.toml` pide Oracle 0.39.0 y Clue 0.1.0a2; el archivo que debería probar el origen de cada dependencia no refleja lo que Factory publica.

Brian propuso adoptar las mejores prácticas de Lightwell (el servicio de IBM y Red Hat para corregir vulnerabilidades de dependencias libres sin forzar actualizaciones) sin depender de él: inventario de componentes, versiones fijadas, hashes de los archivos, origen declarado, reconocimiento de las versiones corregidas y trazabilidad de cada corrección.

## What changes

- Un comando nuevo, `oracle-factory procedencia`, arma un inventario de las dependencias de Python del proyecto, en el formato abierto CycloneDX (JSON). De cada componente dice nombre, versión, enlace `pkg:pypi`, índice de origen, hashes de sus archivos tal como los registra el lock, si la versión está fijada, y de dónde sale cada dato (el lock o el entorno instalado).
- Si el lock no coincide con lo que pide `pyproject.toml` o con lo que está instalado, el inventario lo declara «no confiable» y lista las diferencias, en vez de presentarlo como verdad.
- Con el identificador de un cambio, el inventario se guarda en la carpeta de su candidato y queda un evento en el registro con su huella.
- `procedencia --buscar paquete[==versión]` dice qué candidatos y qué cambios usaron esa dependencia.
- `procedencia --auditar --avisos ARCHIVO` cruza los inventarios guardados con un archivo de avisos de seguridad en formato OSV, sin red, y lista los componentes afectados, las versiones corregidas y los candidatos afectados.
- Una versión con el sufijo de una corrección de Lightwell (`+rhlw…` o `.rhlw-…`) se reconoce y se marca como corregida.
- El `uv.lock` de Factory se regenera para que coincida con `pyproject.toml`.

## Out of scope

- Corregir o actualizar dependencias automáticamente, o decidir por la persona qué corrección aplicar.
- Firmar artefactos o verificar firmas (por ejemplo con Sigstore).
- Consultar servicios de avisos por la red (OSV, GitHub): queda para otro cambio.
- Otros ecosistemas además de Python (npm, Go, Maven).
- Usar Lightwell o su índice de paquetes.

## Human decisions

- Si el formato es CycloneDX, como se propone, o uno propio más simple.
- Si el inventario debe ser obligatorio para cerrar un cambio (se propone que no, en esta primera versión).
- Si los avisos se consultan por la red en un cambio posterior.
