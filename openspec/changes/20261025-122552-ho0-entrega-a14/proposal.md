# Preparar la distribución 0.1.0a14 con documentación y RAG actualizados

## Why

Las mejoras de documentación y preguntar están aceptadas, cerradas e integradas en main, pero la
última distribución publicada sigue siendo 0.1.0a13. Quien instala desde PyPI todavía no recibe
los conteos del registro ni las respuestas elaboradas del checkout actual. Además, una consulta
hecha desde el checkout puede importar ese código aunque el ejecutable instalado sea anterior:
es lo que ocurrió con la instalación global 0.1.0a12 durante la comprobación de uso diario.

El siguiente paso propuesto es preparar 0.1.0a14 como una entrega verificable fuera del checkout.

## What changes

- Actualizar a 0.1.0a14 los metadatos del paquete, notas de versión, instalación y textos de la web
  que correspondan a la entrega, distinguiendo la preparación de una publicación ya verificada.
- Construir wheel y sdist; instalar el wheel en un entorno nuevo y probarlo desde otra carpeta,
  sin importar módulos del checkout ni depender del ejecutable global de Brian.
- Comprobar en esa instalación las consultas del registro, las respuestas con un proveedor fixture
  explícito, los límites y el modo sin modelo generativo. La calidad real de Qwen2.5:14B conserva
  la evidencia del cambio preguntar, que se referencia sin convertir fixtures en medición real.
- Ejecutar los arneses de instalación y guía existentes, la suite y la comprobación de documentación;
  registrar configuración, versiones, hashes y límites en evidencia de este cambio.

## Out of scope

Nuevas funciones del RAG, nuevos modelos, cambios de criterios de calidad y actualización de las
dependencias de Jam o LyraGASP. La aprobación de esta spec no autoriza integrar, empujar, crear el
tag ni publicar en GitHub o PyPI. Esas decisiones se piden después; uv publish lo ejecuta Brian.

## Human decisions

Brian acepta o pide cambios a esta preparación y confirma sus medidas después de la propuesta.
Cuando el candidato esté revisado y cerrado, decide integración y push; luego, por separado,
autoriza tag y release de GitHub y ejecuta la publicación de PyPI.
