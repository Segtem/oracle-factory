# Desplegar a varios destinos

Un producto rara vez es un solo lugar: un VPS, una app, un ESP32, un contenedor. Factory los llama **destinos** y no sabe nada de
ninguno: el proyecto declara los comandos y Factory los ordena, los ejecuta cuando una persona lo autoriza, prueba cada destino y
el conjunto, y deja un registro. Nada se despliega solo ni por CI, y un agente despliega sólo si una persona le dio autonomía en producción
(`oracle-factory autonomia produccion autonomo`).

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

Son obligatorios `desplegar` y `version` de cada destino, y el `conjunto` del proyecto (sin saber qué versión corre, no se puede comprobar que el destino quedó como el plan). Cada comando corre desde la raíz del proyecto con `FACTORY_COMMIT` (el commit del plan),
`FACTORY_DESTINO` y `FACTORY_RAMA` en el entorno. `secretos` lleva **nombres** de variables de entorno, nunca el valor: Factory
comprueba que existan y tapa su valor en lo que registra.

| Campo | Para qué |
| --- | --- |
| `alcanzable` | antes de tocar nada: si falla, el destino queda «inalcanzable» (nunca verde) |
| `construir`, `desplegar` | lo que hace el despliegue |
| `version` (obligatorio) | imprime el commit que corre; si no es el del plan, el destino queda «fallido» |
| `probar` | prueba de humo; sin ella el destino queda «desplegado», no «probado» |
| `volver` | cómo volver atrás si otro destino falla |
| `depende_de` | destinos que tienen que estar probados antes |
| `alcance` | (opcional) rutas de Git de las que depende el destino; las usa `desplegar --cambios` |
| `conjunto.probar` (obligatorio) | prueba de que todo anda junto; corre al final, sólo si cada destino quedó probado |

## El flujo

```bash
oracle-factory destinos                  # estado de cada destino y de la última corrida (--json para el tablero)
oracle-factory desplegar                 # arma el plan y lo muestra; no ejecuta nada (también --simular, y lo puede hacer un agente)
oracle-factory desplegar --autorizar     # una persona, desde su terminal: ejecuta el plan (--destino NOMBRE elige uno y arrastra lo que necesita)
```

## Desplegar sólo lo que cambió

Con `alcance` en un destino —una lista de rutas de Git, carpetas o patrones— `oracle-factory desplegar --cambios` elige los destinos con archivos cambiados dentro de su alcance, entre la última versión que Factory desplegó en ese destino y el commit del plan:

```json
"nodo": {"tipo": "esp32", "alcance": ["firmware/", "lib/comun/"], "desplegar": "pio run -t upload", "version": "curl -fsS http://nodo.local/version"}
```

- Entran siempre los destinos **sin `alcance`**, los que **nunca se desplegaron** y aquellos cuya **versión anterior no se puede comparar** (el repositorio no la conoce): ante la duda, se despliega.
- Lo que un destino elegido necesita (`depende_de`) entra también, antes que él. Sus consumidores no: `depende_de` arrastra lo que se necesita, no a quien lo usa.
- El plan dice por qué entra cada destino y cuáles se omiten. Si ninguno resulta afectado, dice que no hay nada que desplegar y no ejecuta nada, ni siquiera con `--autorizar`.
- `--cambios` no se combina con `--destino`. Sin `--cambios`, `desplegar` actúa sobre todos los destinos, como siempre.

**Límite:** sólo se miran las rutas declaradas. Si un destino depende de algo que no está en su `alcance` (una dependencia de compilación, una variable de entorno), un cambio ahí no lo detecta: declará esas rutas o desplegá sin `--cambios`.

El plan se niega si la puerta local no está en verde o si el commit no está en la rama de despliegue. Con `cortar` (por defecto) el
primer fallo detiene la corrida y vuelve atrás, del último al primero, lo que ya se desplegó; con `seguir` se continúa con los
destinos que no dependen del caído, para ver todo lo que falla, y al final se vuelve atrás igual lo que se desplegó. Lo que no tiene `volver` queda «desplegado» con un aviso.

Estados: `sin_desplegar`, `desplegado`, `probado`, `fallido`, `revertido`, `inalcanzable`. «Desactualizado» se calcula comparando
la versión que el destino dice que corre con la punta de la rama; si no responde, es «desconocido».

Cada corrida deja `.factory/despliegues/<ID>/registro.json` con el commit, quién planeó y quién autorizó, y por destino las
versiones antes y después, los comandos, su salida (con los secretos tapados) y los tiempos.
