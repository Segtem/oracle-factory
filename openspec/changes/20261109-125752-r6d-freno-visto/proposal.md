# Frenos: el de pruebas editadas deja de frenar cuando una persona aprobó la revisión

## Por qué

El freno `prueba_existente_editada` pide «decilo en la revisión». Pero sigue frenando al conductor (`autopilot`) durante todo el cambio, aunque el agente ya lo dijo y una persona aprobó la revisión viéndolo. Pasó en `revprop`: el conductor no pudo seguir con `juzgar` y hubo que hacerlo a mano. Un freno que ya cumplió su función es ruido: enseña a ignorarlos.

## Qué cambia

`prueba_existente_editada` se comporta como `hallazgo_alto_abierto`: no se declara cuando hay una revisión aprobada y vigente (la decisión es `aprobar`, es del mismo producto que el candidato actual y no tiene problemas). Si el candidato cambia después, la revisión deja de ser vigente y el freno vuelve. Los avisos de `alarmas` («test existente editado») siguen mostrándose siempre. Los otros frenos no cambian.

## Fuera de alcance

- Que la revisión tenga que mencionar el test editado: no se lee el texto de la decisión.
- Los demás frenos (`juicios_rojos`, `cambio_grande`, `bucle_de_revision`).

## Decisiones humanas

Ninguna nueva: la revisión aprobada por una persona es la forma en que una persona «vio» el freno.
