# Design

- `revisar_paso_a_paso` envuelve lo que viene después de mostrar la revisión: un `FactoryError`, `EOFError` o `KeyboardInterrupt` guarda `evento(estado, "revision_cancelada", forma="intento", causa=…, candidato=sha)` en el registro recién leído y vuelve a lanzar el error, con el mismo mensaje de siempre.
- `aviso_revision(estado)`: busca el último evento entre `revision_registrada` y `revision_cancelada`; si es el cancelado, arma el aviso. Lo suman `estado` en texto y `datos_estado` en `avisos`.
