# Design

- Un global `ORACLE` (como `ROOT`) se calcula al empezar cada comando a partir de la configuración; todo lo que hoy usa `ROOT / "requisitos"`, `ROOT / "catalogos"`, `ROOT / "oracle.json"` o `--proyecto ROOT` para Oracle pasa a `ORACLE`. Las tareas, `openspec/` y `.factory/` siguen en la raíz.
- La fuente de un requisito importado sigue siendo relativa a la raíz del proyecto (`openspec/changes/…`), donde está la spec.
- `estructura.donde` y `estructura.buscar` reciben la carpeta de Oracle para nombrar y recorrer los requisitos.
- La raíz del proyecto se sigue encontrando por `.factory/`, así que no necesita `oracle.json` en la raíz.
- `confiar_escalares` se agrega a los comandos de Oracle que evalúan medidas (`cobertura`, y la cobertura con hechos de `juzgar`); `importar` no ejecuta escalares.
