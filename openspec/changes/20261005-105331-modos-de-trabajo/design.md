# Design

Notas para implementar después de la aceptación. No son parte del contrato.

- **Vía de agente:** `--agente NOMBRE` (o `FACTORY_AGENTE`) en los comandos de decisión. Sin esa opción, la decisión es de persona y exige `sys.stdin.isatty()`. Un agente puede simular una terminal (por ejemplo con `script`): esto evita confusiones accidentales, no suplanta una autenticación.
- **Propuestas:** se guardan en `factory.json` bajo `propuestas`, con el hash de lo propuesto. Confirmar compara ese hash y rechaza si cambió.
- **Tipo de requisito:** se lee la línea `Tipo:` dentro del bloque del requisito en `spec.md` y se guarda en el registro del cambio, sin depender de Oracle.
- **Compatibilidad:** los cambios existentes sin `modo` se leen como el modo por defecto del proyecto (pregunta 1 de la propuesta) y sus eventos viejos se muestran como «actor no registrado».
- **Dependencias:** se implementa sobre colaboración y revisión guiada ya integradas, porque modifica `aprobar-spec`, `medir`, `revision`/`revision-preparar` y `cerrar`.
