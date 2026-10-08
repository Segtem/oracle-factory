# Revisar los comandos de Factory para que una persona trabaje cómoda

- ESTADO: CERRADA
- PRIORIDAD: 40
- ETIQUETAS: cli, modos, ux


## Objetivo

Revisar el recorrido completo de la CLI pensando en la persona, no en el agente: nombres, mensajes, próximos pasos, cómo se muestran los requisitos para decidir y la instalación (hoy hace falta `uv run python fabrica.py`, y `oracle-factory` no está como comando). Incluye `20261005-105254-cli-piloto` (fricciones del piloto) y debe hacerse junto con los modos, que agregan las decisiones de persona.

### Nota (2026-10-07 00:40:23 UTC)

2026-10-07, pedido de Brian: el Markdown en la consola se ve como texto plano. Mientras tanto se abre con glow -p (instalado). Decidir acá cómo se ven las salidas de estado, donde y resumen (p. ej. resumen --ver con glow si está).

### Nota (2026-10-07 19:09:01 UTC)

2026-10-07: completar la revisión guiada (revisor, completa, informe_sha256, actor, motivo) obliga a editar JSON a mano o pegar un script; hace falta un comando del estilo revision-completar --revisor.

- 2026-10-07: sin `oracle-metalenguaje` en el intérprete (Brian corrió `python fabrica.py medir` con el python del sistema) la CLI cae con un traceback de `ModuleNotFoundError` en `inventario_medidas`. Debería decir qué falta y cómo seguir (activar `.venv` o instalar `oracle-factory`).

- 2026-10-07, cierre del cambio revisores — fricciones medidas en una sola sesión de Brian:
  - confirmar 7 medidas obligó a un bucle de fish con ids largos (`revisores_c466…`) pegados a mano;
  - la compuerta de aprobación dijo «revisión incompleta, hallazgos abiertos o comprobaciones falla/no_ejecutada» sin decir cuál; tuvo que diagnosticarlo el agente;
  - `revision-preparar` dejó un informe vacío en silencio cuando no había candidato vigente;
  - registrar la revisión pidió definir `$S`, `$P`, correr un script del agente y un comando de cinco opciones;
  - leer el informe era leer JSON (`informe.json`), no un texto para personas.
  Pedido de Brian: «Tenemos que mejorar y facilitar la parte cli-humana».

- 2026-10-07, pedido de Brian: «las decisiones que tome el humano desde la cli deberían ser como cuando me hacés preguntas desde acá, un menú y opciones; debería ser guiado». Cada decisión humana (aprobar la spec, confirmar medidas y quitar sin_medir, registrar la revisión, cerrar) como un recorrido interactivo: muestra lo que hay que decidir en texto legible, ofrece opciones numeradas con una recomendada y una descripción de qué implica cada una, permite «otra» con texto libre para el motivo, y al final muestra el comando equivalente (para que quede registrado y se pueda repetir sin menú). Sin tty no hay menú: el comando dice qué opciones existen.
- Confirmar medidas sin quitar `sin_medir` deja el requisito a medio cubrir y `juzgar` bloquea recién al final; el menú de medidas tiene que incluir ese paso.

- 2026-10-07, Brian, sobre el menú con que se eligió el motivo de la revisión de revisores: «Esa interfaz que acabás de crear es la que debería tener cli-humana». La referencia:
  - una pregunta por decisión, con una etiqueta corta («Motivo», «Decisión»);
  - 2 a 4 opciones, la recomendada primero y marcada «(Recomendado)», cada una con una línea que dice qué implica;
  - una vista previa del texto que se va a registrar (el motivo armado con los datos del cambio: candidato, vueltas, evidencia, límites aceptados), para no escribirlo desde cero;
  - siempre una opción «Otro» con texto libre;
  - al elegir, Factory ejecuta el registro y muestra el comando equivalente.
  Primera versión con la biblioteca estándar (opciones numeradas y la vista previa debajo); flechas y panel lateral sólo si hace falta.

- 2026-10-07, Brian: «Debería ser sin fricciones las decisiones, asistidas con IA … en vez de tener que pegar "REGISTRAR REVISION 20261007-192608-revisores", me parece poco práctico». Propuesta:
  - la frase de confirmación prueba que decide una persona en una terminal; un menú interactivo prueba lo mismo (el agente corre sin tty y no puede contestarlo), así que la frase se reemplaza por elegir una opción y Enter;
  - «asistidas con IA»: el agente prepara la decisión con `--agente` (ya existe como propuesta), incluido el motivo redactado con los datos del cambio; el menú de la persona la muestra como opción recomendada con su vista previa, y la persona elige, edita («Otro») o rechaza. La IA redacta; decide la persona.
