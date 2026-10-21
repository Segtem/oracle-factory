# Design

- `inicializar`: después de crear sus carpetas, escribe `.gitkeep` en las vacías que no están ignoradas (no en
  `.factory/local/`). `nuevo` crea `tareas/` (y lo que `oracle-task` necesita) si falta, antes de llamar a `tasks new`.
- `nuevo`: el sufijo efectivo es `<sufijo>-<3 caracteres de [a-z0-9]>`; el ID sigue cumpliendo `ID_RE`.
- `con_reintento(identificador, aplicar)`: lee el registro, aplica la mutación (que vuelve a comprobar sus reglas sobre lo
  leído) y guarda con la huella leída; si el registro cambió entre medio, vuelve a empezar (hasta 20 veces, con una espera
  corta al azar). Lo usan `mensaje`, `tomar` y `soltar`.
