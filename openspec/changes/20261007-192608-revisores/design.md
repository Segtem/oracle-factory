# Design

Notas para implementar después de la aceptación. No son parte del contrato.

- **Configuración:** `"revisores": {"codex": {"comando": ["ask-codex", "{pedido}", "{carpeta}", "{registro}"], "proveedor": "codex", "modelo": "gpt-6-luna", "tope_minutos": 90}}`. Marcadores: `{pedido}` (texto), `{pedido_archivo}`, `{carpeta}` (carpeta de trabajo del revisor, en `.factory/local/revisores/<sha7>-<nombre>/`), `{informe}` (dónde tiene que dejar el informe), `{registro}` (salida del proceso). `config_proyecto` lo valida.
- **Ejecución:** `subprocess.run(argv, timeout=tope)`, sin shell; stdout/stderr a `{registro}`. Al vencer el tope se mata el grupo de procesos.
- **Paquete:** `oracle-clue preparar --repo <checkout> --base <base> --contexto <spec> --salida clue/paquete-<nombre>-<n>.json`; base por defecto, el merge-base con la rama principal (`git symbolic-ref refs/remotes/origin/HEAD` o `main`).
- **Validación:** `oracle-clue validar informe --paquete … --repo <checkout>`; si `oracle-clue` no está, no se puede pedir (es necesario para preparar el paquete).
- **Plantilla:** `oracle_factory/data/pedido_revision.md` con `string.Template`; incluye el esquema del informe (campos de `oracle-clue.review/v1`) y la regla «no edites el checkout ni hagas commits».
- **Historial:** en `material_del_candidato`, las carpetas de candidatos anteriores (ancestros de HEAD) con `revision/*.json` se resumen en comprobaciones `Vuelta anterior en <sha7>: <proveedor>, N hallazgos (ids)`.
- **Evento:** `revision_pedida` con `revisor`, `proveedor`, `modelo`, `candidato`, `resultado` (`ok`, `sin_informe`, `rechazado`, `tope`), `hallazgos`.
