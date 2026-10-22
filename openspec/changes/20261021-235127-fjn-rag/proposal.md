# RAG del conocimiento: preguntar al vault con búsqueda híbrida, sólo lo vigente, con citas y calidad medida

## Why

El vault de `kb/` ya no se desactualiza: se genera del registro y las notas de personas vencen solas. Pero para
encontrar algo hay que saber dónde está. `buscar` encuentra texto literal; una pregunta como «¿por qué los IDs llevan
caracteres al azar?» no aparece así en ningún archivo. Una persona o un agente que retoma un cambio necesita recuperar
el porqué de una decisión sin leer 58 cambios, y saber que lo que lee sigue valiendo.

## What changes

- `oracle-factory preguntar "TEXTO"` (y `--json`) devuelve los pasajes que mejor responden, cada uno con su cita
  (archivo y sección) y de qué cambio es. Busca en el vault (`kb/`), en las propuestas, diseños y specs de los cambios,
  en las specs vigentes (`openspec/specs/`) y en `docs/`.
- Sólo lo vigente: no devuelve una nota de personas por revisar (la nombra aparte) ni lo de un cambio abandonado.
- Búsqueda híbrida: léxica (BM25, sin tildes ni mayúsculas), semántica (embeddings) y por el grafo del vault (un cambio
  trae sus requisitos y al revés), fusionadas por rango.
- Embeddings configurables en `.factory/config.json`: por defecto Ollama local con `qwen3-embedding:0.6b`; un proveedor
  externo (compatible con la API de OpenAI) sólo si el proyecto lo configura con su URL y la variable de su clave. Sin
  proveedor disponible, la búsqueda sigue léxica y por el grafo y lo dice.
- El índice vive en `.factory/local/rag/` (no versionado), se arma solo cuando el contenido cambió y reusa el embedding
  de cada pasaje que no cambió. No hay que mantenerlo.
- Preguntas de oro en `kb/preguntas-de-oro.json`: cada pregunta con los archivos que tienen que aparecer entre los
  primeros resultados. `oracle-factory preguntar --evaluar --salida CARPETA` corre todas y deja hechos para Oracle; las
  medidas de Factory juzgan la calidad con eso.
- Sin dependencias nuevas: SQLite y HTTP de la biblioteca estándar.

## Out of scope

- Generar respuestas con un LLM: `preguntar` recupera pasajes con sus citas; redactar la respuesta es del agente o de la
  persona que los lee.
- El tablero de VS Code y el MCP: usarán `preguntar --json` en otro cambio.
- Indexar el código fuente: para eso está `por-que ARCHIVO:LÍNEA`.

## Human decisions

- Decidido por Brian (2026-10-21): embeddings locales con Ollama y `qwen3-embedding:0.6b` por defecto; las preguntas de
  oro las propone el agente y las aprueba Brian con esta spec. Las preguntas iniciales están en `design.md`.
- A aprobar con la spec: el umbral de calidad (al menos 18 de las 22 preguntas con un archivo esperado entre los cinco
  primeros, con embeddings; la búsqueda sólo léxica se informa sin juicio).
