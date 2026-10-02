# Factory POC

La persona conserva autoridad sobre alcance, aprobación de la spec, decisiones de revisión y cierre.

## Protocolo de trabajo

- Cada cambio tiene una tarea `trackertast` y un paquete OpenSpec bajo `openspec/changes/<id>/`.
- No implementar antes de que una persona acepte `proposal.md` y `spec.md`.
- Importar requisitos con `fabrica.py importar`; cada requisito queda sin medir hasta que alguien elija una medida.
- Implementar en una rama y registrar el commit revisado.
- El informe de CodeRabbit (o de otra persona) se guarda junto al cambio. Un humano resuelve los hallazgos y registra la decisión.
- Correr Oracle con evidencia del producto; un verde sin requisitos medidos no habilita el cierre.
- `fabrica.py cerrar` requiere confirmación escrita de una persona y cierra la tarea tracker.
- No presentar una revisión probabilística como veredicto, ni el veredicto de Oracle como prueba de propiedades no medidas.
