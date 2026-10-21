# Design

## Corpus y pasajes

Lo que se indexa, con su cambio cuando lo tiene: las notas de `kb/` (generadas y de personas), `proposal.md`,
`design.md` y la spec de cada cambio en `openspec/changes/`, las specs vigentes de `openspec/specs/` y `docs/*.md`. Cada
archivo se parte por secciones (`#`, `##`, `###`); un pasaje es una sección, con el título de su archivo adelante para
que no quede sin contexto. La cita es `ruta#sección`.

Fuera: las notas de personas por revisar (`kb --verificar` las nombra; `preguntar` las lista aparte como «por revisar»)
y todo lo de un cambio abandonado. Las notas generadas siempre están al día porque Factory las regenera en cada decisión.

## Ranking

- Léxico: BM25 (k1 1,2, b 0,75) sobre palabras sin tildes ni mayúsculas, sin una lista corta de palabras vacías.
- Semántico: coseno entre el embedding de la pregunta y el de cada pasaje.
- Fusión: Reciprocal Rank Fusion (k = 60) de los dos rankings.
- Grafo: los pasajes de una nota enlazada (`[[...]]`) con una de las primeras cinco suman la mitad de su puntaje; así un
  cambio trae a sus requisitos y un requisito a su cambio.

Cada resultado dice cuánto aportó cada vía. Sin embeddings, la fusión es léxico + grafo.

## Embeddings

`.factory/config.json`, opcional:

```json
"rag": {"embeddings": {"proveedor": "ollama", "url": "http://localhost:11434", "modelo": "qwen3-embedding:0.6b"}}
```

Sin `rag`, es eso mismo. `"proveedor": "openai"` usa `POST {url}/embeddings` con la clave de la variable que nombra
`"clave_env"`; `"proveedor": "ninguno"` apaga lo semántico. Nada sale de la máquina si el proyecto no configuró una URL
que no es local. HTTP con `urllib`; sin dependencias nuevas.

## Índice

`.factory/local/rag/indice.sqlite`: por pasaje, su ruta, sección, cambio, texto, huella (sha256 del texto) y su
embedding (float32, con el modelo que lo hizo). Al preguntar se recorre el corpus; si una huella no está, se agrega (y se
pide su embedding); lo que ya no está se borra. Un modelo distinto invalida los embeddings. Nada que mantener a mano.

## Preguntas de oro

`kb/preguntas-de-oro.json`: `[{"id", "pregunta", "esperadas": [rutas]}]`. Acierto: alguna ruta esperada entre los
cinco primeros resultados (por archivo). `preguntar --evaluar --salida CARPETA` deja `hechos.json` con la relación
`rag_pregunta` (id, acierto, puesto, modo) y `rag_corrida` (preguntas, aciertos, mrr, modo, modelo), más el detalle.

Propuestas (las aprueba Brian con la spec):

| id | pregunta | esperadas (cambio) |
| --- | --- | --- |
| ids-al-azar | ¿Por qué los IDs de los cambios llevan tres letras al azar? | clones |
| dos-toman | ¿Qué pasa si dos personas toman el mismo cambio en ramas distintas y después se integran? | unir |
| elegir-version | ¿Cómo elijo cuál vale cuando dos ramas dejaron fases o cierres distintos? | unir |
| generados-no-chocan | ¿Por qué resumen.md y el vault no dan conflicto al mergear? | unir |
| quien-trabaja | ¿Cómo sé qué persona y qué agente están trabajando en un cambio? | quien |
| compartir-tablero | ¿Cómo comparto el tablero con otra persona para trabajar de a dos? | liveshare, sesion |
| revision-vieja | ¿Cuándo deja de valer una revisión ya registrada? | la-vigencia-de |
| catalogo-cambia | ¿Qué pasa si cambia el catálogo de una medida que ya estaba confirmada? | catalogo-confirmado |
| abandonar | ¿Cómo dejo un cambio sin terminar y quién lo decide? | abandonar |
| pedir-revision | ¿Cómo le pido a codex que revise un candidato? | revisores |
| clon-revisor | ¿Por qué el revisor trabaja en un clon aparte y no en un worktree? | aislar |
| riesgo-aceptado | ¿Qué es un riesgo aceptado y sigue valiendo en la vuelta siguiente? | vueltas-severidad |
| linea-cambio | ¿Cómo encuentro qué cambio escribió una línea de código? | kb, commits |
| nota-vence | ¿Cuándo una nota escrita por una persona en el vault deja de estar al día? | kb |
| modos | ¿Qué modos de trabajo hay y quién decide los requisitos en cada uno? | modos-de-trabajo |
| varios-sensores | ¿Se puede juzgar un candidato con los hechos de más de un sensor? | hechos-varios |
| donde-estado | ¿Dónde se guarda el estado de cada cambio? | fase-2-de-la |
| dos-procesos | ¿Qué pasa si dos procesos escriben el registro de un cambio al mismo tiempo? | bloqueo-registro, clones |
| banco | ¿Cómo se prueba que dos personas con sus agentes no se pisan? | coordinar-dos |
| otra-capacidad | ¿Por qué no me deja aprobar una spec con dos capacidades? | avisos |
| trazabilidad | ¿Cómo voy de un requisito a las líneas que lo prueban? | trazabilidad |
| paquete-producto | ¿Qué archivos no entran en el paquete que se manda a revisar? | paquete-producto |

Para cada cambio, las rutas esperadas son su nota en `kb/cambios/` y los documentos de su carpeta en
`openspec/changes/`.
