# Tres defectos de Factory a la vista: una spec de otra capacidad, requisitos huérfanos al reimportar y un requisito que quedó sin medir

## Why

Los tres aparecieron trabajando con Factory el 2026-10-19 y 2026-10-20, y en los tres Factory se callaba hasta muy tarde:

- Un cambio de la capacidad `colaboracion` traía también `specs/trazabilidad/spec.md`; Factory importa sólo la spec de
  la capacidad del cambio y la otra se perdió sin aviso (hubo que mover el requisito y aprobar de nuevo).
- Al aprobar de nuevo una spec y reimportar, los requisitos de la importación anterior quedaron en `requisitos/` con el
  ID viejo (dos veces; hubo que sacarlos a mano).
- Un requisito quedó con medidas confirmadas pero con su marca «sin medir»; recién `juzgar`, después de toda la
  revisión, lo bloqueó con «no tiene cobertura completa», sin decir cuál.

## What changes

- `aprobar-spec` se niega si el cambio tiene specs de otra capacidad, y dice cuáles.
- `importar` quita de `requisitos/` los requisitos que una importación anterior de ese mismo cambio había escrito y la
  nueva ya no trae.
- `estado` avisa, apenas se deciden las medidas, el requisito que todavía dice «sin medir», con qué hacer; y el error de
  `juzgar` nombra esos requisitos.

## Out of scope

- Importar varias capacidades en un mismo cambio.

## Human decisions

- Brian lo eligió el 2026-10-20 como cambio chico, antes del RAG.
