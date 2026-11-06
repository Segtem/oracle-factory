# Desplegar a varios destinos

Un producto rara vez es un solo lugar: un VPS, una app, un ESP32, un contenedor. Factory los llama **destinos** y no sabe nada de
ninguno: el proyecto declara los comandos y Factory los ordena, los ejecuta cuando una persona lo autoriza, prueba cada destino y
el conjunto, y deja un registro. Nada se despliega solo: ni por CI, ni por un agente.

## Declarar los destinos

`.factory/destinos.json` (hay un ejemplo completo en `docs/plantillas/destinos.json`):

```json
{
  "rama": "main",
  "politica_ante_fallo": "cortar",
  "destinos": {
    "api": {"tipo": "vps", "desplegar": "tools/desplegar_vps.sh", "version": "ssh vps cat /srv/api/VERSION",
            "probar": "tools/humo_api.sh", "volver": "tools/volver_vps.sh", "secretos": ["VPS_SSH_KEY"]},
    "nodo": {"tipo": "esp32", "depende_de": ["api"], "alcanzable": "ping -c1 nodo.local", "desplegar": "pio run -t upload",
             "version": "curl -fsS http://nodo.local/version", "probar": "tools/humo_nodo.sh"}
  },
  "conjunto": {"probar": "tools/prueba_de_conjunto.sh"}
}
```

Sólo `desplegar` es obligatorio. Cada comando corre desde la raíz del proyecto con `FACTORY_COMMIT` (el commit del plan),
`FACTORY_DESTINO` y `FACTORY_RAMA` en el entorno. `secretos` lleva **nombres** de variables de entorno, nunca el valor: Factory
comprueba que existan y tapa su valor en lo que registra.

| Campo | Para qué |
| --- | --- |
| `alcanzable` | antes de tocar nada: si falla, el destino queda «inalcanzable» (nunca verde) |
| `construir`, `desplegar` | lo que hace el despliegue |
| `version` | imprime el commit que corre; si no es el del plan, el destino queda «fallido» |
| `probar` | prueba de humo; sin ella el destino queda «desplegado», no «probado» |
| `volver` | cómo volver atrás si otro destino falla |
| `depende_de` | destinos que tienen que estar probados antes |
| `conjunto.probar` | prueba de que todo anda junto; corre al final, sólo si cada destino quedó probado |

## El flujo

```bash
oracle-factory destinos                  # estado de cada destino y de la última corrida (--json para el tablero)
oracle-factory desplegar                 # arma el plan y lo muestra; no ejecuta nada (también --simular, y lo puede hacer un agente)
oracle-factory desplegar --autorizar     # una persona, desde su terminal: ejecuta el plan
```

El plan se niega si la puerta local no está en verde o si el commit no está en la rama de despliegue. Con `cortar` (por defecto) el
primer fallo detiene la corrida y vuelve atrás, del último al primero, lo que ya se desplegó; con `seguir` se continúa con los
destinos que no dependen del caído. Lo que no tiene `volver` queda «desplegado» con un aviso.

Estados: `sin_desplegar`, `desplegado`, `probado`, `fallido`, `revertido`, `inalcanzable`. «Desactualizado» se calcula comparando
la versión que el destino dice que corre con la punta de la rama; si no responde, es «desconocido».

Cada corrida deja `.factory/despliegues/<ID>/registro.json` con el commit, quién planeó y quién autorizó, y por destino las
versiones antes y después, los comandos, su salida (con los secretos tapados) y los tiempos.
