# Modos de trabajo: quién decide qué

Un cambio de Factory pasa por cuatro decisiones: aceptar la propuesta y la spec, elegir las medidas de cada requisito, registrar la revisión y cerrar. El **modo de trabajo** del cambio dice cuáles toma una persona y cuáles puede tomar un agente. Lo que no cambia en ningún modo: una persona, desde su terminal, siempre puede decidir, y todo queda registrado a nombre de quien lo hizo, como persona o como agente.

## Los tres modos

- **`confirmacion`** (el modo por defecto): el agente trabaja y propone la spec, las medidas y la revisión, y una persona las confirma; el cierre no se propone: lo toma una persona directamente. Conviene cuando se empieza, cuando el producto importa o cuando todavía no se conoce bien al agente. Es el modo en que Factory se construye a sí misma.
- **`funcional`**: la persona decide lo que el producto promete a quien lo usa (los requisitos funcionales); el agente decide solo lo no funcional (rendimiento, mantenimiento, cómo se mide por dentro). Conviene cuando la persona quiere estar en el qué, no en cada detalle del cómo.
- **`autonomo`**: el agente decide todo, cierre incluido, y queda registrado como agente. Conviene para tareas acotadas y reversibles, o para probar el flujo. Una persona puede intervenir igual en cualquier momento.

Un cambio toma el modo del proyecto (`modo_por_defecto` en `.factory/config.json`) o el que se elige al crearlo:

```bash
oracle-factory nuevo --capacidad notas --modo funcional "Guardar notas"
```

## Quién decide qué

Lo que pasa cuando un agente toma cada decisión (con `--agente`), según el modo. Una persona en su terminal decide siempre, en cualquier modo.

| Decisión | `confirmacion` | `funcional` | `autonomo` |
|---|---|---|---|
| Aceptar la propuesta y la spec (el cambio tiene algún requisito funcional) | el agente propone; una persona confirma | sólo una persona | decide el agente |
| Aceptar la propuesta y la spec (todos sus requisitos son no funcionales) | el agente propone; una persona confirma | decide el agente | decide el agente |
| Elegir las medidas de un requisito funcional | el agente propone; una persona confirma | sólo una persona | decide el agente |
| Elegir las medidas de un requisito no funcional | el agente propone; una persona confirma | decide el agente | decide el agente |
| Registrar la revisión (el cambio tiene algún requisito funcional) | el agente propone; una persona confirma | sólo una persona | decide el agente |
| Registrar la revisión (todos sus requisitos son no funcionales) | el agente propone; una persona confirma | decide el agente | decide el agente |
| Cerrar el cambio | sólo una persona | sólo una persona | decide el agente |

- **«el agente propone; una persona confirma»**: lo que hizo el agente queda como propuesta y no cuenta hasta que una persona lo confirma desde una terminal, con el mismo comando sin `--agente` (o `medir ID --confirmar` para las medidas).
- **«sólo una persona»**: el comando con `--agente` falla y dice que esa decisión es de una persona.
- **«decide el agente»**: la decisión cuenta, registrada a nombre del agente.

Abandonar un cambio (`oracle-factory abandonar ID`) lo decide siempre una persona; un agente sólo puede proponer el motivo.

## Requisitos funcionales y no funcionales

Cada requisito de la spec declara su tipo en la línea que sigue al título:

```markdown
### Requirement: guardar una nota
Tipo: funcional
```

Los tipos son `funcional` y `no funcional`. Un requisito sin línea `Tipo:` cuenta como funcional, que es el lado seguro: en modo `funcional` lo decide una persona. Si el proyecto pone `"tipos_obligatorios": true` en `.factory/config.json`, `importar` rechaza la spec mientras algún requisito no declare su tipo.

## Cómo leer estado

`oracle-factory estado ID` muestra, junto a cada decisión tomada, quién la tomó y cómo, y entre lo pendiente, lo que un agente propuso y todavía no cuenta (un fragmento, en el orden en que sale):

```text
Pendiente: medidas de cli_c28628c0586fe682a.medir_dice_que_medidas_reemplaza propuestas por claude-code, sin confirmar por una persona
Aprobación spec: sí, Ana Pérez (persona, decidio, modo confirmacion)
Revisión registrada por: Ana Pérez (persona, confirmo, modo confirmacion; motivo: …)
Medidas de cli_c28628c0586fe682a.la_plantilla_de_un_cambio_nuevo_trae_la_forma_de_openspec: Ana Pérez (persona, confirmo, modo confirmacion)
```

Entre paréntesis van tres datos:

- **Quién**: `persona` (alguien en una terminal interactiva, con el nombre de su configuración de Git, o su usuario del sistema si Git no tiene nombre) o `agente` (el nombre que se pasó a `--agente`).
- **Cómo**: `decidio` (tomó la decisión directamente) o `confirmo` (una persona confirmó, tal cual, lo que había propuesto un agente).
- **En qué modo** estaba el cambio cuando se decidió, y el motivo si lo hubo.

Una propuesta de un agente no figura como decisión: aparece en «Pendiente», con quién la propuso, y entre los eventos del registro del cambio, con forma `propuso`. Cuando una persona la confirma, pasa a ser una decisión «persona, confirmo».

`estado ID --json` da lo mismo para un programa: en `decisiones`, cada decisión tomada con su actor, tipo de actor, forma, modo, fecha y motivo; en `requisitos`, la `propuesta` de medidas que espera confirmación.

## Cambiar de modo

```bash
oracle-factory modo ID funcional
```

Subir la intervención humana (por ejemplo, de `autonomo` a `confirmacion`) lo puede hacer cualquiera. Bajarla lo decide una persona desde su terminal, con confirmación, nunca un agente. Al cambiar de modo, las decisiones que un agente tomó y que en el modo nuevo ya no le corresponden dejan de contar: vuelven a ser propuestas, o se descartan para que las tome una persona.

## Un ejemplo real

Factory se construye con Factory, en modo `confirmacion`. En cada cambio, el agente de código escribe la propuesta, implementa, propone las medidas con `--agente claude-code medir …`, pide las revisiones a otros modelos y propone aprobar la revisión con un motivo. Una persona hace lo que la tabla le reserva: aprueba la spec, confirma las medidas (`medir ID --confirmar`), registra la revisión eligiendo el motivo y cierra. En `estado` queda, para cada gate, «persona, confirmo» o «persona, decidio», y en los eventos del cambio, cada propuesta del agente con forma `propuso`.

El piloto con agentes de `tareas/20261004-121432-coordinar-dos/` es anterior a los modos (Factory 0.1.0a3): ahí un agente coordinador representó a las personas, y por eso no sirve como ejemplo de esto.

## Límites

- Factory no autentica a nadie. «Persona» quiere decir que el comando corrió en una terminal interactiva sin `--agente`; el nombre es el de la configuración de Git de esa terminal, o el usuario del sistema si Git no tiene nombre. Un agente que tiene una terminal interactiva y omite `--agente` quedaría registrado como persona: los modos son un protocolo entre quienes trabajan juntos, no un control de acceso.
- Una entrada por tubería (sin terminal) no cuenta como persona: queda «sin identificar» y no puede decidir.
- El modo dice quién decide, no si la decisión es buena: eso sigue siendo de la revisión y de las medidas.
