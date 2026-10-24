# El conocimiento del proyecto

Un vault que se escribe a mano se desactualiza. En Factory el conocimiento sale del registro de cada cambio y se rehace
solo; lo que escriben las personas vence cuando cambian sus fuentes; y para encontrarlo hay una búsqueda que sólo
devuelve lo vigente, con su cita.

## El vault: `kb/`

`oracle-factory kb` escribe `kb/` desde el registro, con enlaces de Obsidian:

- una nota por cambio (fase, responsable, requisitos con su veredicto, decisiones con quién, cuándo y por qué, riesgos
  aceptados, commits y mensajes),
- una por requisito (texto, medidas, el cambio que lo trajo y si sigue vigente),
- y un índice (`kb/README.md`).

Nadie las edita a mano: se rehacen con cada decisión de Factory, y `oracle-factory kb --verificar` falla, sin escribir, si
no coinciden con el registro. El texto no depende de cuándo se genera, así que dos clones generan lo mismo.

## Notas de personas que vencen

Lo que el registro no sabe (una guía, una decisión de diseño explicada) va en `kb/notas/`, con sus fuentes en el
frontmatter: archivos, requisitos o IDs de cambio.

```markdown
---
fuentes: [oracle_factory/rag.py, 20261021-235127-fjn-rag]
---
# Cómo ajustar el RAG
…
```

Cuando cambia una fuente, la nota queda **por revisar**: `kb --verificar` falla nombrándola y `estado` la avisa en el
cambio que tocó esa fuente. Una persona la relee y la marca con `oracle-factory kb revisada kb/notas/NOMBRE.md`.

## ¿Por qué existe esta línea?

`oracle-factory por-que ARCHIVO:LÍNEA` (o `--json`) va del commit que escribió esa línea a su cambio (por el trailer
`Cambio: ID`, o deducido de sus commits) y muestra sus requisitos con su veredicto, las decisiones, los riesgos y
hallazgos sobre ese archivo, y las notas que lo tienen como fuente. En VS Code, «Factory: ¿Por qué existe esta línea?»
lo hace para la línea del cursor. `oracle-factory trazabilidad ID` hace el camino inverso: de cada requisito a las líneas
que lo prueban ([trazabilidad](trazabilidad.md)).

## Preguntar

```bash
oracle-factory preguntar "¿Por qué los IDs de los cambios llevan letras al azar?"
```

devuelve los pasajes que mejor responden, cada uno con su cita (`archivo#sección`) y su cambio. Busca en el vault, en las
propuestas, diseños y specs de los cambios, en las specs vigentes y en `docs/`. Deja afuera las notas por revisar (las
nombra) y todo lo de un cambio abandonado, y es sólo lectura. `--json` lo da con esquema versionado
(`oracle-factory.preguntar/1`), `--max N` cuántos pasajes.

Busca de tres maneras a la vez y dice cuánto aportó cada una: por palabras (sin tildes ni mayúsculas), por significado
(embeddings) y por el grafo del vault (un cambio trae a sus requisitos y al revés).

**Embeddings.** Por defecto, Ollama en la máquina con `qwen3-embedding:0.6b` (`ollama pull qwen3-embedding:0.6b` una vez).
En `.factory/config.json`:

```json
"rag": {"embeddings": {"proveedor": "ollama", "url": "http://localhost:11434", "modelo": "qwen3-embedding:0.6b"}}
```

`"proveedor": "openai"` usa un servidor compatible con la API de OpenAI (`"url"`, `"modelo"`, y `"clave_env"` con el
nombre de la variable de la clave); `"proveedor": "ninguno"` apaga lo semántico. Ningún texto sale de la máquina a una URL
que el proyecto no escribió, y no se siguen redirecciones. Sin proveedor, la búsqueda sigue por palabras y por el grafo,
y lo avisa.

**El índice** vive en `.factory/local/rag/` (no se versiona) y se pone al día solo al preguntar: sólo pide los embeddings
de lo que cambió.

**La calidad se mide.** `kb/preguntas-de-oro.json` tiene preguntas con los archivos que tienen que aparecer entre los
cinco primeros pasajes. `oracle-factory preguntar --evaluar --salida CARPETA` las corre y deja hechos para Oracle (por
pregunta, si acertó y en qué puesto; en total, los aciertos y el MRR). Factory mide así el suyo.

Desde un agente, lo mismo por MCP: ver [agentes](agentes.md).
