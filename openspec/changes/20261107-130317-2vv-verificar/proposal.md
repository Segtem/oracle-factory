# Verificar para CI: comprobar de solo lectura que los cambios están consistentes

## Por qué

Hoy la consistencia de los cambios sólo la comprueba quien corre `estado` a mano, en una máquina, con una persona al lado. Un clon en otra máquina, o un CI en GitHub, no tiene cómo saber si alguien empujó una revisión que ya no corresponde al producto, un informe tocado después de aprobarse, o un cierre que no decidió una persona. La puerta local mira secretos y guías; no mira los cambios. Es la tarea `ci-remoto` (2026-10-05), la parte de «chequeo apto para CI».

## Qué cambia

- Un comando nuevo, `oracle-factory verificar [--json]`, de sólo lectura, sin terminal ni agente. Recorre los cambios del proyecto y, de cada uno, comprueba lo que ya sabe comprobar `estado`:
  - en un cambio abierto, que la spec, las medidas, la revisión y el juicio sigan vigentes sobre el producto actual y que las huellas de los informes coincidan;
  - en un cambio cerrado, que sus informes y decisiones conserven su huella y que el cierre lo haya decidido una persona (una propuesta de agente sin confirmar no cuenta; en modo autónomo, el cierre de un agente sí vale).
- Sale con 0 si todo está consistente y con 1 si algo no lo está, nombrando el cambio y qué falta. Con `--json` imprime lo mismo en un objeto con esquema versionado.
- Los hechos de la evidencia que no están en esta máquina (carpeta ignorada o clon limpio) se avisan, no fallan: otra máquina no los tiene.
- Una plantilla de workflow de GitHub Actions y una guía `docs/ci.md` que explica cómo usarlo en CI y en un hook `pre-push`.

## Fuera de alcance

- Correr la suite de pruebas o los analizadores estáticos en CI (tareas aparte).
- Sumarlo a la puerta local (`oracle-factory puerta`); queda para después, con su visto bueno.
- Activar el workflow en este repositorio: aquí sólo se entrega la plantilla.
- Medir el trabajo entre dos máquinas (la otra parte de `ci-remoto`).
- Confirmar, cerrar o corregir nada: `verificar` informa; corregir sigue siendo de una persona.

## Decisiones humanas

- ¿Se activa el workflow en este repositorio (`.github/workflows/`) o queda sólo como plantilla en `docs/`? Propongo sólo plantilla.
- ¿`verificar` se suma a la puerta local una vez que ande en CI? Propongo decidirlo aparte.
- Que los cambios cerrados no se comparen con el producto actual (se vuelven «desactualizados» apenas se integran, por diseño) es una decisión de diseño que tomé yo; si preferís otra, decilo antes de aprobar.
