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

puede responder de tres maneras: consultar datos del registro, recuperar documentos o elaborar una respuesta con un
modelo generativo que hayas configurado. Busca en el vault, en las propuestas, diseños y specs de los cambios, en las
specs vigentes y en `docs/`. Deja afuera las notas por revisar (las nombra) y todo lo de un cambio abandonado. Es de sólo
lectura: no aprueba, cierra ni modifica cambios. Esta ampliación está en desarrollo en esta rama; no está en el paquete
publicado anterior al cambio.

`oracle-factory preguntar "¿Cuántas tareas cerradas hay?"` calcula el número desde el registro vigente, sin pedirle a un
modelo que cuente documentos. También reconoce consultas simples para listar y contar todos, abiertos, cerrados o
abandonados. Los cerrados archivados siguen contando como cerrados. Un filtro directo no admitido se avisa; no se
reemplaza silenciosamente por otro. Para explicaciones abiertas se puede usar un modelo generativo.

`--json` devuelve `oracle-factory.preguntar/2`: `tipo`, `respuesta`, `fuentes`, `herramientas`, modelos y límites, además
de `resultados` (pasajes candidatos), sus aportes y las notas por revisar. Los tipos distinguen `registro`,
`respuesta_elaborada`, `documentos`, `sin_respaldo`, `requiere_aclaracion` y `consulta_no_admitida`. Un puntaje de ranking
sirve para ordenar candidatos: no es probabilidad de certeza. `--max N` limita los pasajes mostrados.

Sin modelo generativo se conservan consultas directas y recuperación, avisando que los pasajes no son una explicación
elaborada. Si la recuperación no reúne al menos dos términos de la consulta (uno si la consulta sólo tiene uno), ni una
similitud semántica de al menos 0,65, avisa que no encontró respaldo suficiente. Es un criterio de selección, no una
garantía de comprensión semántica; los candidatos siguen visibles para inspección. Con un modelo, éste puede consultar
más fuentes y tiene que responder con citas verificables, abstenerse o pedir aclaración.

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

**Modelo que elabora respuestas.** Es distinto del modelo de embeddings y no se elige ni descarga automáticamente.
Se configura en `rag.generacion`, con `proveedor` (`ollama`, `openai` o `ninguno`) y un `modelo` explícito. Ollama usa por
defecto la URL local; `openai` designa una API compatible con Chat Completions, requiere `url` explícita (incluido su
prefijo `/v1`, si corresponde) y `clave_env` con el nombre de una variable de entorno, nunca la clave en Git.
El modelo debe admitir llamadas a herramientas. No se usa otro proveedor si falla el elegido.

Las herramientas disponibles son `recuperar` y `registro` (contar, listar, agrupar por fase y consultar un cambio).
Sus argumentos se validan; no pueden ejecutar SQL, shell, código arbitrario o acciones de escritura. Por defecto el
ciclo admite 4 llamadas a herramientas y 120 segundos; `max_llamadas` permite entre 1 y 8 y `segundos` entre 1 y 300. El contexto se
limita a 64 KB, la respuesta del proveedor a 256 KiB y cada fuente enviada a 6000 caracteres. Si se alcanza un límite o
el modelo falla, se informa y se conserva la recuperación disponible.

Las citas de una respuesta elaborada tienen que identificar una fuente consultada y copiar un fragmento que exista en
ella; los números deben aparecer en las citas. Esto verifica pertenencia textual, no demuestra que la interpretación
del modelo sea correcta. Las inferencias se rotulan y la evaluación real revisa la calidad de las respuestas.

**La calidad se mide.** `kb/preguntas-de-oro.json` tiene preguntas con los archivos que tienen que aparecer entre los
cinco primeros pasajes. `oracle-factory preguntar --evaluar --salida CARPETA` las corre y deja hechos para Oracle.
`--casos ARCHIVO` agrega casos sin reemplazar las preguntas originales: grupo `registro` (valor esperado), `abstencion`
(tipo esperado) o `generativa` (conceptos mínimos en `contiene` y rutas esperadas en `fuentes`). El archivo debe estar
dentro del proyecto. Los resultados separan cada grupo, sus aciertos, errores y abstenciones incorrectas; para las
documentales conservan el puesto y MRR. Los controles de conceptos y citas no son un juez semántico universal.
La evidencia distingue modelos simulados de mediciones con el modelo real: una prueba del transporte no acredita
calidad de las explicaciones. Se conserva el umbral humano documental de al menos 18 de las 22 preguntas originales.

Desde un agente, lo mismo por MCP: ver [agentes](agentes.md).
