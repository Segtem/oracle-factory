# Alcance opcional de los destinos: desplegar sólo lo que cambió

## Por qué

Hoy `desplegar` actúa sobre todos los destinos declarados (o sobre los que se nombran con `--destino`). En un producto con varios destinos —un VPS, una app, un ESP32— casi siempre cambia uno solo, y desplegar los demás cuesta tiempo, riesgo y, en un ESP32, un reflasheo innecesario. Quien despliega tiene que saber a mano qué destino tocó cada cambio.

## Qué cambia

- Un destino puede declarar `alcance`: la lista de rutas de Git (carpetas o patrones) de las que depende. Es opcional; sin él, el destino se considera siempre afectado.
- `oracle-factory desplegar --cambios` elige los destinos afectados: los que tienen archivos cambiados dentro de su `alcance` entre la última versión que Factory desplegó en ese destino y el commit del plan. Siempre entran los destinos sin `alcance`, los que nunca se desplegaron y aquellos cuya versión anterior no se puede comparar. Lo que un destino elegido necesita (`depende_de`) entra también, como ya pasa con `--destino`.
- El plan dice por qué entra cada destino y cuáles se omiten, y si no hay ninguno afectado dice que no hay nada que desplegar y no ejecuta nada ni siquiera con `--autorizar`.
- Sin `--cambios` nada cambia. `--cambios` no se combina con `--destino`.
- La guía `docs/despliegue.md` y la plantilla `docs/plantillas/destinos.json` cuentan el campo y la opción.

## Fuera de alcance

- Detectar cambios en lo que un destino consume fuera de las rutas declaradas (dependencias de compilación, variables): lo que no está en `alcance` no se mira, y la guía lo dice.
- Desplegar los destinos que dependen de uno cambiado: `depende_de` arrastra lo que un destino necesita, no a sus consumidores.
- Ejecutar nada solo: autorizar sigue siendo de una persona.

## Decisiones humanas

- Que el alcance se declare en `.factory/destinos.json` (versionado) y que `--cambios` sea una opción explícita, no el comportamiento por defecto.
- Aprobar esta spec.
