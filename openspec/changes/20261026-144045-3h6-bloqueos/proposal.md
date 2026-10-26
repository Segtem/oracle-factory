# Mostrar cada bloqueo con su solución

## Why

En el piloto de uso (proyecto de notas) Brian Hollweg, sin ayuda del chat, no pudo registrar su revisión. Intentó
`oracle-factory revisar` dos veces y Factory lo bloqueó con mensajes que mandaban a `pedir-revision` sin decir con qué
revisor ni qué faltaba antes. El tablero le ofreció como próximo paso `pedir-revision … --a NOMBRE`, con un hueco sin
completar. Cuando configuramos un revisor, el pedido falló porque el código del ejemplo estaba en el primer commit del
proyecto y no había una base contra la cual armar el paquete. Brian pidió que el tablero deje a la vista cada bloqueo con su
solución.

## What changes

- Cuando el próximo paso es pedir una revisión y el proyecto no tiene ningún revisor configurado, `estado` y el tablero lo
  dicen en palabras (qué falta y dónde declararlo, con un ejemplo) en vez de ofrecer un comando con un hueco.
- Los bloqueos de `revisar` por falta de candidato, de informes o de evidencia nombran la causa y el comando exacto para
  seguir, con el revisor configurado.
- `pedir-revision --base vacio` arma el paquete contra una base sin archivos, para revisar todo el producto de un candidato
  cuyo código está en el primer commit. Factory crea esa base como un objeto de Git sin tocar ramas, historia ni
  configuración. El error por paquete vacío nombra esa opción.

## Out of scope

- El `^C` automático al enviar un comando a una terminal nueva desde el botón de VS Code: se sigue investigando aparte.
- Cambios en la extensión de VS Code: ya muestra como instrucción un próximo paso que no empieza con `oracle-factory`.
- Elegir o instalar revisores por la persona.

## Human decisions

- Brian decidió (2026-10-26) cerrar el piloto como bloqueado y arreglar Factory con este cambio.
