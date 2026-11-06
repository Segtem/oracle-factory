# Diseño

## El modelo: destinos, no tecnologías

Un **destino** es cualquier lugar donde corre una parte del producto. Factory no sabe qué es un VPS ni un ESP32: sabe de
destinos que declaran comandos. `.factory/destinos.json`:

```json
{
  "rama": "main",
  "politica_ante_fallo": "cortar",
  "destinos": {
    "api":  {"tipo": "vps",   "construir": "make imagen", "desplegar": "tools/desplegar_vps.sh", "probar": "tools/humo_api.sh",
             "version": "ssh vps cat /srv/api/VERSION", "volver": "tools/volver_vps.sh", "secretos": ["VPS_SSH_KEY"]},
    "app":  {"tipo": "app",   "desplegar": "tools/publicar_app.sh", "probar": "tools/humo_app.sh", "depende_de": ["api"]},
    "nodo": {"tipo": "esp32", "construir": "pio run", "desplegar": "tools/ota.sh", "probar": "tools/humo_nodo.sh",
             "version": "tools/version_nodo.sh", "depende_de": ["api"], "alcanzable": "ping -c1 nodo.local"}
  },
  "conjunto": {"probar": "tools/prueba_de_conjunto.sh"}
}
```

Cada campo de comando es una línea que se ejecuta desde la raíz del proyecto, con el entorno del usuario. Los `secretos` son
**nombres** de variables de entorno que el comando necesita: Factory comprueba que existan, nunca los lee para guardarlos y
tapa su valor en cualquier salida registrada.

## El ciclo

1. **Plan** (`oracle-factory desplegar`): resuelve el commit de la rama de despliegue, exige la puerta local en verde, ordena los
   destinos por `depende_de` (un ciclo es un error) y decide cuáles tocar: todos, o los que `alcance` (rutas) dicen que cambiaron.
   Imprime el plan; con `--simular` termina ahí. Es lo único que un agente puede hacer solo.
2. **Autorización**: una persona repite el comando con `--autorizar`. Un agente (`--agente`) no puede. Queda en el registro quién y cuándo.
3. **Ejecución por destino, en orden**: `alcanzable` → `construir` → `desplegar` → `version` (debe devolver el commit del plan)
   → `probar` (humo). Un destino cuyo `alcanzable` falla queda **inalcanzable**, no verde.
4. **Prueba de conjunto**, sólo si todos los destinos del plan quedaron probados.
5. **Fallo**: según `politica_ante_fallo` (`cortar` por defecto, o `seguir`) se detiene o sigue con los destinos que no dependen
   del caído; los desplegados en esta corrida se vuelven atrás con `volver` si existe, y si no quedan «desplegado sin volver»,
   dicho en voz alta.
6. **Resultado**: «todo quedó funcionando» sólo si cada destino del plan está *probado* con la versión del plan y el conjunto pasó.

## Estados de un destino

`sin_desplegar` → `desplegado` → `probado`; o `fallido`, `revertido`, `inalcanzable`. `desactualizado` no se guarda: se calcula
comparando la versión que el destino dice que corre (`version`) con la punta de la rama de despliegue, y por eso depende de
que el destino se alcance en ese momento (si no, se muestra «desconocido»).

## Evidencia

`.factory/despliegues/<ID>/` con un `registro.json` por corrida: commit, quién planeó y quién autorizó, y por destino los
estados, versiones antes y después, comandos, salida con secretos tapados, tiempos y resultado. Es el insumo de las medidas
de Oracle del cambio y de `destinos --json`. Los registros son hechos observados: no se editan a mano.

## Para el tablero (cambio siguiente)

`oracle-factory destinos --json` es el contrato: lista de destinos con `nombre`, `tipo`, `estado`, `version_desplegada`,
`version_esperada`, `ultima_prueba`, `desactualizado`, `depende_de`, y la última corrida (`id`, `resultado`, `autorizo`).
La vista «Destinos» de VS Code mostrará la matriz, qué necesita a una persona (autorizar un plan pendiente, un destino fallido o
inalcanzable) y escribirá el comando para copiar, igual que el resto del tablero: **no ejecuta** el despliegue.

## Qué se descartó

- Integrar Docker, Ansible, esptool o una tienda de apps: ata Factory a tecnologías y caduca. Con comandos declarados sirve para
  cualquier cosa, y las plantillas muestran cómo.
- Desplegar desde un CI remoto: el CD sería automático y sin persona. El CI queda para `verificar` (otro cambio).
- Guardar secretos en `.factory/`: el repositorio puede ser público.
