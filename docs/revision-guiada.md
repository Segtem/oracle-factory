# Revisar con un informe y decisiones separados

Este recorrido está disponible desde Factory 0.1.0a4. Identifique el checkout con `git rev-parse HEAD`; el número de versión por sí solo no identifica estas modificaciones de desarrollo.

Factory comprueba consistencia, contexto y conservación de documentos. Una persona competente analiza el código, los tests, el sensor y las medidas y decide qué hacer con sus hallazgos. Un agente puede ayudar a preparar el análisis; los nombres y motivos registrados no autentican a una persona ni demuestran que sus conclusiones sean correctas.

## Preparar el entorno y el candidato

Desde este checkout, prepare un entorno con las dependencias fijadas del proyecto:

```bash
uv venv .venv
uv pip install --python .venv/bin/python -e .
```

Los comandos siguientes se ejecutan desde ese checkout. `--proyecto` selecciona el producto que se revisa y va antes del subcomando. Sustituya `/ruta/producto`, `ID_COMPLETO` y las rutas de documentos por los valores reales.

El cambio debe estar abierto y tener propuesta/spec aceptadas y vigentes. Termine y confirme el producto antes de preparar la revisión. Factory captura HEAD y una huella de los archivos actuales: si hay cambios sin commit, la huella los incluye, pero no significa que estén guardados en HEAD.

```bash
.venv/bin/python fabrica.py --proyecto /ruta/producto estado ID_COMPLETO
.venv/bin/python fabrica.py --proyecto /ruta/producto revision-preparar ID_COMPLETO
```

El segundo comando imprime las rutas nuevas de `informe.json` y `decisiones.json` bajo `tareas/ID_COMPLETO/revisiones/preparacion-…/`. Si el candidato tiene carpeta propia (`oracle-factory ruta ID revision`) con informes de revisores en formato de Oracle Clue, el informe sale completado con sus hallazgos, comprobaciones, límites y archivos, y las decisiones listan cada hallazgo sin estado (ver [estructura](estructura.md#una-carpeta-por-candidato)). Los campos humanos —revisor, si la revisión está completa y el estado de cada hallazgo— quedan en `null`. Prepararlos no acepta hallazgos, no registra revisión y no invalida una revisión anterior. Repetirlo crea otra carpeta y conserva los archivos existentes.

Se recomienda usar esas rutas dentro de la tarea: están fuera de la huella de archivos del producto, por lo que completar el informe no lo vuelve obsoleto por sí mismo. Un commit nuevo que sólo archiva notas o registros tampoco la invalida: Factory compara la huella de archivos del producto y guarda el commit como dato. Si cambia un archivo del producto antes de registrar, prepare de nuevo.

## Pedir la revisión a un revisor externo

Un revisor puede ser otra persona o un agente; conviene que sea de una familia de modelo distinta a la del que escribió el código. Factory no depende de ninguno: cada proyecto declara los suyos en `.factory/config.json`.

```json
"revisores": {
  "codex": {"comando": ["env", "CODEX_MODEL=gpt-6-luna", "ask-codex", "{pedido}", "{carpeta}", "{carpeta}/codex.md"],
            "proveedor": "codex", "modelo": "gpt-6-luna", "tope_minutos": 90}
}
```

El nombre del revisor (la clave) es minúsculas, dígitos y guiones: va en nombres de archivo. El comando es una lista de argumentos (sin shell) con marcadores: `{pedido}` (el texto del pedido), `{pedido_archivo}`, `{carpeta}` (la carpeta de trabajo del revisor, en `.factory/local/revisores/`), `{informe}` (dónde tiene que dejar su informe), `{registro}`, `{paquete}` y `{checkout}`. Cualquier otra llave, abierta o cerrada, se rechaza al leer la configuración, para que un marcador mal escrito no llegue al revisor. Con eso:

```bash
oracle-factory pedir-revision ID_COMPLETO --a codex
```

prepara el checkout y el paquete de Oracle Clue del candidato actual (en las rutas de `oracle-factory ruta`), arma el pedido desde la propuesta, la spec y las vueltas anteriores, lanza al revisor, espera hasta el tope, valida su informe con Clue y lo guarda —con el pedido usado— en la carpeta `revision/` del candidato. `--pedir "TEXTO"` agrega indicaciones; `--base REF` cambia la base del paquete. El pedido sale de una plantilla de Factory que cada proyecto puede reemplazar con `.factory/pedido-revision.md`.

Si el revisor no se puede iniciar, no deja informe, Clue lo rechaza o se pasa del tope, no se guarda nada en `revision/` y su salida queda en la carpeta de trabajo. Con cambios del producto sin commit, no se lanza. En ningún caso el revisor decide: `pedir-revision` sólo deja un evento con el revisor, el modelo y el resultado. Ejecuta el comando que dice la configuración del proyecto, como haría un `Makefile`: revisala antes de usarla en un repositorio ajeno.

`revision-preparar` toma después los informes del candidato vigente y muestra como comprobaciones las vueltas anteriores, sin pedir que se decidan otra vez.

## Revisar paso a paso

El camino corto para la persona es un solo comando:

```bash
oracle-factory revisar ID_COMPLETO
```

Prepara el informe del candidato vigente y lo muestra en texto: evidencia, revisores, vueltas anteriores y límites. Después pregunta con menús:

1. **Cada hallazgo abierto:** aceptar el riesgo, descartarlo o dejarlo abierto.
2. **La decisión:** aprobar, sólo si no queda nada abierto y todo cumple, o pedir cambios.
3. **El motivo:** el que propuso el agente, uno armado con los datos del cambio u «Otro», para escribirlo.

Se responde con el número de la opción; Enter solo no elige nada. Factory completa el informe y las decisiones (revisor, hash, resoluciones) y registra la revisión. El registro guarda de dónde salió el motivo (`agente`, `armado` o `persona`), también el de cada hallazgo resuelto (`origen_motivo`, opcional en los documentos completados a mano).

El agente puede dejar preparada su recomendación, que la persona ve como primera opción de motivo:

```bash
oracle-factory --agente claude-code revisar ID_COMPLETO --decision aprobar --motivo "Sin hallazgos en el candidato; acepto el límite X."
```

Las secciones que siguen describen los mismos documentos por dentro, para quien prefiera completarlos a mano.

Las medidas que propuso el agente se confirman también con un menú: `oracle-factory medir ID_COMPLETO --confirmar` las lista por requisito, avisa si alguna conserva `sin_medir` y las confirma todas o de a una.

## Completar lo que realmente se revisó

En `informe.json`, conserve `schema_version`, `cambio`, `contexto` y `documentos` generados. Si ya no corresponden al candidato, vuelva a preparar; no edite hashes para aparentar vigencia.

| Campo humano | Qué registrar |
| --- | --- |
| `revisor` | Nombre de quien realizó el análisis; debe coincidir con `--revisor` |
| `completa` | `true` o `false`, explícitamente; declare `false` si quedó revisión pendiente |
| `archivos_revisados` | Lista no vacía de rutas relativas del producto, sin repeticiones; admite referir archivos eliminados |
| `comprobaciones` | Lista no vacía de objetos con `descripcion`, `resultado` y `evidencia` |
| `limites` | Lista explícita de límites; `[]` sólo si no declara otros límites. Es obligatoriamente no vacía si `completa` es `false` |
| `hallazgos` | Lista de objetos con `id`, `descripcion`, `ubicacion` y `evidencia`; IDs únicos |
| `sin_hallazgos_motivo` | Motivo concreto si `hallazgos` es `[]`; `null` si hay hallazgos |

En cada comprobación, `resultado` es `cumple`, `falla` o `no_ejecutada`. Descripción y evidencia son texto no vacío que explica qué se observó y cómo recuperarlo; una referencia textual no hace que Factory ejecute la prueba o verifique ese archivo. Una comprobación fallida o no ejecutada impide registrar `aprobar`, incluso si no hay hallazgos abiertos. Puede registrar `cambios` para dejar esa situación documentada.

Ejemplo de forma de una comprobación, **pendiente de completar**:

```json
{
  "descripcion": "PENDIENTE",
  "resultado": "no_ejecutada",
  "evidencia": "PENDIENTE"
}
```

Factory rechaza campos humanos obligatorios en `null`, vacíos o con el marcador exacto `PENDIENTE`, ignorando mayúsculas y espacios externos. No puede determinar que otro texto sea convincente. No agregue un hallazgo ficticio para completar una plantilla.

## Registrar decisiones humanas

Termine el informe antes de completar `decisiones.json`. Obtenga el SHA-256 de sus bytes finales con:

```bash
.venv/bin/python -c 'import hashlib,pathlib,sys; print(hashlib.sha256(pathlib.Path(sys.argv[1]).read_bytes()).hexdigest())' /ruta/producto/tareas/ID_COMPLETO/revisiones/PREPARACION/informe.json
```

En el documento de decisiones complete:

- `informe_sha256`: el hash recién obtenido. Cualquier edición posterior del informe requiere renovarlo y revisar de nuevo las decisiones que se apoyan en él.
- `actor` y `motivo`: persona que asume la decisión general y su justificación. Puede ser distinta del revisor.
- `decisiones`: lista explícita, posiblemente vacía. Cada resolución contiene `hallazgo_id`, `estado`, `motivo`, `actor` y `fecha`.

La fecha debe ser ISO 8601 con hora, segundos y zona, por ejemplo `2026-10-04T15:00:00-03:00`. Use la fecha real de la decisión. Los estados admitidos son `corregido`, `descartado` y `riesgo_aceptado`, siempre con motivo. Factory verifica referencias, estructura y fecha; no comprueba la corrección ni autentica al actor. Si arreglar el defecto cambió el producto, corresponde una revisión del nuevo contexto.

Un hallazgo sin resolución válida queda abierto. No agregue una resolución `pendiente`: deje ese ID sin decisión hasta que la persona resuelva. Un ID inexistente, una decisión duplicada o un hash diferente hacen que el documento se rechace. Si no hubo hallazgos, escriba `decisiones: []`, conserve el motivo de ausencia en el informe y complete actor/motivo generales.

## Registrar el resultado con confirmación

Para dejar documentados problemas o revisión incompleta:

```bash
.venv/bin/python fabrica.py --proyecto /ruta/producto revision ID_COMPLETO --formato guiado --informe tareas/ID_COMPLETO/revisiones/PREPARACION/informe.json --decisiones tareas/ID_COMPLETO/revisiones/PREPARACION/decisiones.json --revisor "NOMBRE_REAL" --decision cambios
```

Si la persona acepta el informe completo, todas las comprobaciones declaran `cumple` y no quedan hallazgos abiertos, puede solicitar `--decision aprobar` en ese comando. En modo guiado no se pasa `--hallazgos-abiertos`: se calcula a partir de IDs y resoluciones.

La terminal muestra commit y huella, responsable, alcance, límites, comprobaciones, hallazgos, resoluciones y pendientes. La persona confirma eligiendo «Registrar» en el menú que se le muestra. La lista vacía de hallazgos y la validación de JSON nunca sustituyen esa decisión.

Después de confirmar, Factory vuelve a comprobar informe, decisiones, spec, contexto y registro de estado. Si alguno cambió, rechaza la operación para volver a revisar. Si todo corresponde, archiva copias nuevas bajo `tareas/ID_COMPLETO/revisiones/registro-…/`, guarda sus hashes y la decisión e invalida el juicio Oracle previo. No modifica las copias históricas. Esto no es un bloqueo general de otros editores o máquinas: use un escritor activo por cambio, según la [guía de colaboración](colaboracion.md).

Una revisión aprobada todavía requiere evidencia y juicio Oracle con cobertura suficiente antes del cierre. La ejecución del sensor y el cierre siguen siendo pasos separados; esta funcionalidad no los ejecuta por usted.

## Recuperación y revisión libre

| Situación | Próximo paso |
| --- | --- |
| Campos pendientes o JSON inválido | Complete los campos indicados; revise claves desconocidas/duplicadas y la versión del documento |
| Hay abiertos, revisión parcial o comprobaciones no satisfactorias | Registre `cambios` o complete la revisión; no declare cero manualmente |
| Cambió el informe antes de registrar | Actualice su hash en decisiones después de revisar la edición |
| Cambió el producto o la spec | Prepare un informe del contexto nuevo; si cambió proposal/spec, renueve antes su aceptación e importación. Si sólo cambió el HEAD (un commit que no toca el producto), el informe sigue valiendo |
| Se canceló o cambiaron entradas durante la confirmación | El registro anterior no fue sustituido; revise el diagnóstico y repita cuando el contexto esté estable |
| Falló preparar/archivar | Revise la carpeta residual indicada; conserve antecedentes y no dé el nuevo gate por publicado |
| Falló guardar el estado | La revisión anterior o edición concurrente se conserva; las copias nuevas pueden quedar como residuo |
| La revisión quedó registrada pero falló la nota del tracker | Consulte `estado` y recupere sólo la nota; no suponga que se revirtió la revisión |
| Cambió o falta una copia archivada | `estado` y `cerrar` la señalan como no vigente; restituya la evidencia original o registre una nueva revisión |

La inmutabilidad es una política de escritura de Factory, no un permiso de filesystem: alguien puede editar las copias y entonces sus hashes dejan de coincidir. Editar los originales bajo la tarea después de archivar no cambia las copias registradas.

El formato libre sigue disponible y es el predeterminado. Los comandos anteriores que pasan `--hallazgos-abiertos N` explícitamente conservan su flujo; omitir ese argumento ahora se rechaza. Los registros antiguos aparecen como `libre histórico`. La terminal los distingue como declaraciones humanas sin validación estructural de su contenido. Un error del modo guiado nunca se convierte silenciosamente a libre.

Clue y CodeRabbit pueden aportar antecedentes para el análisis. Los schemas de Clue son distintos: Factory no los importa, convierte ni valida automáticamente con este comando. Si usa Clue, conserve su paquete/informe/triage por el [recorrido de colaboración](colaboracion.md) y complete el registro de Factory sobre el mismo candidato con criterio humano.

## Comprobación del corte

El sensor de este checkout ejecuta pruebas G1–G8 con Git, Task y Oracle reales en repositorios temporales:

```bash
.venv/bin/python tools/verify_review_guided.py --salida /tmp/evidencia-revision-guiada-01
```

La carpeta debe ser nueva. Conserva resultados por caso, trazas de comandos, fuentes y hashes; una omisión, falla o caso duplicado no se presenta como éxito. Las confirmaciones de pruebas son fixtures y no aprueban tareas reales. La prueba funcional de CLI no mide claridad para principiantes ni calidad de revisión humana.
