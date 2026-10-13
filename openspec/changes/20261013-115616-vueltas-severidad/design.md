# Design

- La severidad sale de `findings[].severity` de cada informe de Clue, que la exige y admite `critica`, `alta`, `media`, `baja` e `informativa`. Bajos son `baja` e `informativa`; cualquier otro valor, o ninguno (un informe guardado que la perdió), pide otra vuelta.
- Una sola función decide si hace falta otra vuelta para un candidato: lee los informes de `revision/` del candidato y descuenta los hallazgos que coinciden con un riesgo aceptado. La usan `pedir-revision` (al terminar) y `proximo_paso`, así no divergen.
- Los riesgos aceptados viven en `estado["aceptados"]` del registro del cambio: `{archivo, titulo, firma, motivo, actor, fecha, candidato}`. La firma es `archivo` (sin línea) + título normalizado. Se agrega al aceptar en `revisar`, aunque la decisión final sea pedir cambios; se saca al revocar.
- El pedido al revisor los suma al bloque de vueltas anteriores (`$vueltas`), que ya existe en la plantilla; una plantilla propia del proyecto no necesita cambiar.
- No se toca el esquema del informe guiado: la severidad ya va en la evidencia de cada hallazgo, y `revisar` la muestra.
