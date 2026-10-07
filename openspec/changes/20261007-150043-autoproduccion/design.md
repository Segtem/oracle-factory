# Design

Notas para implementar después de la aceptación. No son parte del contrato.

- **Candidato actual:** `git rev-parse HEAD`[:7], como `ruta`. La evidencia se produce sobre el commit de producto; los commits que sólo guardan evidencia y registros no cambian la huella, pero sí HEAD: `juzgar` sin `--con` busca primero el HEAD actual y, si no hay, el commit más reciente con la misma huella de producto que tenga evidencia (lista las candidatas si hay más de una).
- **Informes de revisores:** `candidatos/<sha7>/revision/*.json` con `schema_version` de Oracle Clue (`oracle-clue.review/v1`); el paquete en `candidatos/<sha7>/clue/*.json`. Se emparejan por `diff_sha256`/`context_sha256` y `head`.
- **Validación:** `oracle-clue validar INFORME --paquete PAQUETE --repo REPO`, con `REPO` el del paquete. Si Clue está disponible pero falta el paquete o su checkout, el informe no se usa y se avisa cómo recrearlo (así lo pide la spec: con Clue disponible, cada informe se valida antes de usarse).
- **Mapeo al informe guiado:** hallazgo `id` → `id`; `title` → `descripcion`; `location` → `ubicacion` (`archivo:línea`); `evidence` + proveedor y modelo → `evidencia`. Comprobación por evidencia: `resultado.json` (`exitoso`, pruebas, casos). Límites: `limitations` de cada informe y `limites` de la evidencia.
- **Módulo puro** `oracle_factory/preparacion.py` (datos leídos → informe y decisiones); la CLI lee los archivos y llama a Clue.
- **Este repositorio:** los verificadores siguen recibiendo `--salida`; se les pasa `$(oracle-factory ruta ID evidencia)`.
