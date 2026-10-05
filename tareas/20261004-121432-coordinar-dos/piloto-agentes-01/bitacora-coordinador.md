# Bitácora del coordinador — piloto con agentes 01 (2026-10-05)

Encargo: Brian pidió «haz el piloto para saber si funciona». Sólo hay una persona disponible, así que el piloto es **con agentes**: sesiones independientes (A1, B1 y después A2) que sólo conocen la guía y las instrucciones comunes. El coordinador (agente principal) representa a las personas A y B en los pasos humanos y es el integrador. Esas decisiones quedan rotuladas como tomadas por el coordinador; no son decisiones humanas.

## Preparación
- Producto: proyecto Factory con el ejemplo `notas`, cambio de ejemplo `20261005-101618-comprobar-el` aceptado, medido, revisado, juzgado y cerrado por el coordinador. Base `d704844560fe22eedde97ac0411193d144c02a35`.
- Remoto: `origen.git` (bare). Checkouts: `a/` (A1, después A2), `b/` (B1), `integracion/` (coordinador).
- Entorno: venv con oracle-factory 0.1.0a3 (rama de colaboración, 7709b83), oracle-task 0.2.0, oracle-clue 0.1.0a1 y oracle-metalenguaje 0.38.1.
- Fricción del coordinador al preparar: `revision` falla con «necesita un repositorio Git con al menos un commit» si el proyecto todavía no tiene commits. Además, `cerrar` modifica `factory.json`/`TAREA.md` y genera `review.md`/`oracle-veredicto.txt`, que hay que commitear aparte.

## Fase 1 — propuesta, spec y reparto (A1 y B1 en paralelo)

### A1 (terminó a las 10:19 aprox.)
- Cambio `20261005-101725-crear-notas-con`, capacidad `creacion`. Commit `e16a9f0aca9e3972f51a8edf097baee639809c56` en `trabajo/persona-a`, subido a origen.
- Propone el contrato «nota v1»: `crear_nota(titulo, cuerpo="") -> {"titulo", "cuerpo"}`, `ValueError` si el título es inválido, sin recortar, en `examples/notas/notas.py`. A es la dueña.
- Detecta de antemano los archivos compartidos (`sensor.py`, `test_notas.py`, `catalogos/`, `requisitos/`) y los deja fuera de su alcance hasta que se acuerde un orden.
- Observaciones:
  1. La spec generada por `nuevo` no trae `## ADDED Requirements` y la del ejemplo sí.
  2. No está claro si los TODO de `tasks.md`/`design.md` bloquean `aprobar-spec`.
  3. `factory.json` registra «workstation» como actor.
  4. La guía no orienta sobre qué capacidad elegir.
  5. El `tasks note` que sugiere la guía da por hecho un acuerdo que todavía no existe.
  6. La guía no tiene un patrón para archivos compartidos por diseño.

### B1
- Cambio `20261005-101733-listar-notas`, capacidad `listado`. Commits `5558e8c…` y `7dba0c2049183d605c145fabe2e423e8f94c2104` en `trabajo/persona-b`.
- Propone `listar_notas(notas) -> str` en el módulo nuevo `examples/notas/listado.py`: `- <titulo>` por línea, sin salto final, `""` si la lista está vacía.
- Leyó la rama de A por iniciativa propia y encontró dos huecos del contrato: títulos con salto de línea (`puede_guardar("a\nb")` es verdadero) y espacios sin recortar.
- Observaciones:
  1. Los IDs truncados se leen raro.
  2. Actor «workstation».
  3. La plantilla de proposal tiene «Brian» fijo.
  4. Spec sin `## ADDED Requirements`.
  5. No hay forma de validar la spec antes de la aceptación humana.
  6. La guía no dice dónde vive el código.
  7. La «versión» de la interfaz no la fija nada.
  8. No está claro si se puede leer la rama del otro antes del acuerdo.
  9. El reparto pide el commit de la dependencia antes de que exista.

## Decisiones del coordinador (en representación de A y B, no son humanas) — 10:25
- **Solapamiento de archivos compartidos.** Se elige separar frentes con contratos en vez de serializar: cada frente agrega su propio sensor (`examples/notas/sensor_<capacidad>.py`), sus pruebas y sus catálogos con prefijo propio. `sensor.py`, `test_notas.py`, `oracle.json` y los catálogos `notas.*` no los toca nadie. Los `requisitos/` son por cambio y no se pisan.
- **Contrato «nota v1» (A es la dueña):** `crear_nota(titulo, cuerpo="") -> {"titulo": str, "cuerpo": str}`. Si el título no cumple `puede_guardar` o contiene un salto de línea (`\n` o `\r`), lanza `ValueError`. El título se guarda recortado con `strip()` y el cuerpo, tal cual. A debe reflejarlo en su spec antes de la aceptación.
- **B:** formato `- <titulo>`, sólo el título. Acepta «nota v1». Sus pruebas construyen dicts sin depender del código de A; la integración prueba `listar_notas([crear_nota(...)])`.
- B queda aceptada ya. A, después de su ajuste.

## Fase 2
### B1 — entrega
- Aceptación con la frase dada (proposal `ae798b0d…`, spec `721c114d…`). Requisitos `listado_c7296af2cde2d7c6e.{una_linea_por_nota,lista_vacia}`.
- Producto en `fcc0abbe04f441218030d2d9666ec360fa6ab0fa` y evidencia en `3a3bab005f9014a800aa6915b95668b90a8a028e`: 6 pruebas OK y sensor con 3 casos en código 0. Medidas `listado.casos_ejecutados` y `listado.resultados`. Comprobó a mano que el sensor detecta una versión rota.
- Hallazgo principal: **solapamiento de interfaz que Git no ve**. Si dos sensores emiten la misma relación (`comprobacion`), `notas.casos_ejecutados == 3` se pone rojo en el candidato integrado sin que nadie toque su archivo. B usó `listado_comprobacion` por su cuenta.
- Otras observaciones:
  1. `aprobar-spec` acepta la frase por pipe, sin comprobar que haya una persona.
  2. El «próximo paso» no avanza después de `medir`.
  3. `medir --listar` mezcla unas 40 medidas `meta`/`proceso`/`simulacion`.
  4. El campo `fuente` de cada `.requisito` guarda una ruta absoluta del checkout, que no existe en otro clone.
  5. El sensor no figura en `oracle.json` (`sensores`), que es un archivo compartido.
  6. Los hechos van a `.factory-demo/` según el README y a `tareas/` según la guía.
  7. No está claro qué commit se le ofrece al revisor (el de producto o el de evidencia).
  8. Actor «workstation».
- Coordinador: el hallazgo de la relación compartida se le pasa a A2 por el canal del piloto.

### A1 — implementación y relevo
- Contrato ajustado y reparto confirmado (`28080dcf…`). Aceptación con la frase dada (proposal `8942767f…`, spec `3156eecf…`). A1 también reescribió «Human decisions» para registrar quién decidió; el coordinador lo da por incluido en el ajuste pedido.
- Requisitos `creacion_cb8a4a12b0ffc6e4e.{crear_nota_valida,rechazar_titulo_invalido}`. Producto en `8b677495cb78c0a6deba6963cc1d2623a4ccdd32`, con 7 pruebas OK.
- Relevo ofrecido en `09363acfe5e225b75df60e1c2cb8118168705592`, con la recepción pendiente. A1 deja de escribir.
- Observaciones:
  1. El texto de `aprobar-spec` mezcla el pedido y el resultado en una línea.
  2. `"Mi nota\n"` se rechaza porque el salto se evalúa antes del `strip()`: es una consecuencia del contrato que nadie pidió explícitamente.
  3. `importar` escribe en `requisitos/` y ni el reparto ni las decisiones lo nombraban.
  4. Un relevo commiteado no puede contener su propio hash, así que «HEAD de entrega» es ambiguo.
  5. El relevo deja desactualizado el «Escritor activo» del reparto, y no está definido quién lo actualiza.
  6. Actor «workstation».

## Fase 3
### A2 — recepción, entrega de A y revisión de B
- **Recepción:** verificó HEAD, padre, base, árbol, índice, locks, procesos y los 5 SHA-256 del relevo, y las 7 pruebas. Todo coincidía. Confirmación registrada en `9f6d40a5…`, con el escritor activo pasado a A2.
- **Entrega de A:** producto en `1d39ca3f3c0b9a70c7d7f148d4c599368b0336ae` y evidencia en `d276e305f20de423356e540e9154c7c0c5ee4f6b`. Usa la relación propia `creacion_comprobacion` con el campo `requisito`, y cuatro medidas, cada requisito con las suyas. Comprobó que una fila fallida pone rojas las medidas.
- **Revisión de B:** checkout propio, paquete con base `d704844`, informe `entrega-b-informe.json` válido. Hallazgos:
  - **A2-B-01:** el orden no está probado. Un mutante que ordena por título pasa todo; lo demostró.
  - **A2-B-02:** los dos requisitos comparten medidas.
  - **A2-B-03:** `fuente` guarda una ruta absoluta.
- Observaciones:
  1. Escribió `__pycache__` en `a/` antes de confirmar la recepción (inocuo, pero es una escritura).
  2. La «próxima acción» del relevo incluía `juzgar` y contradecía al coordinador.
  3. `estado` sugiere `medir --listar` después de medir.
  4. Las CLI de Oracle tienen poca ayuda (`medida probar --con`, la conjunción `y`).
  5. Las medidas del ejemplo violan las meta `ningun_umbral_de_igualdad` y `toda_medida_filtra_o_agrupa`.
  6. No está claro si `oracle cobertura` previa cuenta como juzgar.
  7. Para juzgar el candidato integrado hay que combinar los hechos de los tres sensores.

## Decisiones del coordinador — triage de B y medidas de A
- A2-B-01: corregir (agregar un caso no ordenado).
- A2-B-02: corregir (separar las medidas por requisito, como hizo A).
- A2-B-03: riesgo aceptado. Es comportamiento de Factory `importar`, fuera del alcance de B.
- Medidas `creacion.*`: pertinentes, aceptadas.
- Fricción: el schema de triage de Clue sólo tiene `corregido`, `descartado` y `riesgo_aceptado`. No hay un estado para «pedir corrección» antes de corregir, así que el triage se escribe después de la corrección, sobre el informe viejo.

### B1 — corrección y revisión de A
- Corrección: producto en `ed3476bae1ac2a0c1024d7a059ed706d97d39e12` y evidencia en `619baeaf807049e411b0130a4b48817d060066c4`. Caso no ordenado y medidas separadas por requisito. Con mutantes comprobó que cada uno afecta sólo a su requisito.
- Revisión de A (informe `entrega-a-informe.json`, válido). Hallazgos:
  - **B1-A-01:** otros separadores de línea Unicode pasan el contrato.
  - **B1-A-02:** sin validación de tipos.
  - **B1-A-03:** el reparto de A quedó desactualizado.
- Hizo una sonda del contrato combinado A→B.
- Observaciones:
  1. Escribió una vez fuera de sus rutas y lo corrigió.
  2. `medir` reemplaza sin avisarlo y no señala medidas huérfanas en el catálogo.
  3. `oracle cobertura --con` funciona como un «juzgar sin registro» que la guía no menciona.
  4. Nada detecta relaciones duplicadas entre sensores.
  5. El campo `requisito` no está unificado: A usa el sufijo y B el ID completo.
  6. El paquete de Clue no muestra el diff y `validar` no evalúa el contenido.
  7. No hay esqueleto para escribir el informe.
  8. No está fijado si se revisa el commit de producto o el de evidencia.

## Fase 4 — triage e integración (coordinador)
- Triage de B (`coordinador/entrega-b-decisiones.json`): B-01 y B-02 corregidos, B-03 riesgo aceptado. Triage de A (`coordinador/entrega-a-decisiones.json`): los tres hallazgos como riesgo aceptado (B1-A-01 exigiría cambiar la spec). Los dos pasan `oracle-clue validar --triage`.
- Integración en serie en `trabajo/integracion`:
  - A en `79efe14` (merge de `d276e30`).
  - B en `bfce3ed` (merge de `619baea`). Merge limpio.
  - Prueba del contrato «nota v1» en `examples/notas/test_integracion.py`. **Candidato `f9b4b3866cc0e67b10f4100c2b7c4ae02e4b9216`**, 12 pruebas OK.
- Hechos combinados de los tres sensores con un script del coordinador que falla ante una relación repetida (`comprobacion` 3, `creacion_comprobacion` 7, `listado_comprobacion` 4). `oracle cobertura`: **5 de 5 requisitos cumplen**, incluido el del ejemplo base.
- Hueco de la guía: no dice cómo combinar los hechos de varios sensores para juzgar un candidato integrado.
- Revisión renovada del candidato: revisor neutral R1, una sesión nueva.

## Fase 5 — revisión del integrado y cierre
- R1: hechos y cobertura idénticos byte a byte a los del integrador. 6 hallazgos (R1-01..06); el más relevante, R1-01, es el efecto cruzado del riesgo B1-A-01 sobre `una_linea_por_nota` de B. Triage del coordinador: los seis como riesgo aceptado (`coordinador/candidato-f9b4b38-decisiones.json`, validado).
- Factory en `integracion/`: `revision` (informe de R1, 0 abiertos), `juzgar --con hechos-integrados.json` (código 0) y `cerrar` en los dos cambios. Registrar la revisión de B no invalidó la de A.
- Fricción del coordinador: `tareas/integracion-<sha>/` rompe `tasks review`. Se movió a `tareas/<A>/integracion-<sha>/` con `integracion.md` y `combinar_hechos.py`. Archivo en `719c3bd`, que pasó a `main` del remoto.
- Conclusiones en `piloto.md`.
