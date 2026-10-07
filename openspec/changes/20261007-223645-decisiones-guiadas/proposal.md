# Decisiones guiadas: menú y opciones en vez de frases

## Why

Cada decisión de una persona en Factory hoy cuesta fricción que no aporta control. Al cerrar el cambio de revisores, Brian tuvo que:

- tipear `CERRAR 20261007-192608-revisores` y `REGISTRAR REVISION …` para confirmar;
- completar «TU MOTIVO» en un comando largo;
- correr un script del agente para llenar `revisor`, `completa`, el SHA y el motivo en dos JSON;
- confirmar 7 medidas con un bucle de fish y volver a hacerlo porque faltaba `--quitar-sin-medir`.

Pidió que las decisiones sean «sin fricciones, asistidas con IA», como cuando el agente le pregunta con un menú y opciones.

La frase existe para probar que decide una persona en una terminal. Un menú interactivo prueba lo mismo: el agente corre sin terminal y no puede contestarlo.

## What changes

- Toda confirmación de persona (aprobar spec, medidas, revisión, cierre, modo) se toma eligiendo una opción numerada de un menú que dice qué se decide y qué implica cada opción, en vez de tipear una frase.
- Un comando `oracle-factory revisar ID` lleva la revisión de punta a punta:
  - prepara el informe del candidato vigente si hace falta y lo muestra como texto;
  - pide decidir cada hallazgo abierto con opciones;
  - ofrece aprobar o pedir cambios, y registra.
  
  Reemplaza preparar, editar JSON, pegar el SHA y el comando de cinco opciones.
- El motivo se elige, no se escribe desde cero. El menú ofrece:
  - el motivo que propuso el agente (`--agente … --motivo`), si existe;
  - un motivo armado con los datos del cambio;
  - «Otro» con texto libre.
- `medir ID --confirmar` muestra las medidas propuestas por el agente, incluido quitar `sin_medir`, y las confirma de una vez o de a una.

## Out of scope

- Errores con causa y próximo paso, `oracle-factory` como comando instalado y salidas con glow: siguen en la tarea cli-humana.
- Flechas, colores o panel lateral: la primera versión usa la biblioteca estándar (opciones numeradas).
- Decisiones sin terminal: siguen rechazándose como hoy.

## Human decisions

- ¿El menú de confirmación acepta Enter solo como «la opción recomendada»? Propuesta: no; hay que elegir el número, para que una decisión no salga de un Enter apurado.
- ¿El motivo armado con datos es una opción aunque no haya propuesta del agente? Propuesta: sí.
