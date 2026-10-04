# Agy Task — 2026-10-03 21:52:58

**Tarea:** Revisión final de guía, en español. Tu primera auditoría está en tareas/20261003-235610-web-rigurosa/agy2.md. Lee site/desde-cero.html actual como principiante y verificá rutas, comandos de copia Mac/Linux y PowerShell, creación de archivos, .gitignore, confirmaciones y orden de recuperación contra oracle_factory/cli.py. No edites nada ni hagas aprobaciones/commits. No instalar ni ejecutar ejemplos nuevamente: root los está reproduciendo desde comandos extraídos de la guía. Reporta únicamente omisiones/error concretos restantes con cita y corrección, o ninguno encontrado y los límites. No es piloto humano. No aconsejes informes aprobados ficticios ni interpretar 3 filas como casos únicos. Tiempo acotado.
**Directorio:** /home/workstation/Dev/factory
**Cuenta:** prof
**Modelo:** gemini-3.8-flash-high (esfuerzo high, timeout 6m)

---

# Revisión final de la guía ([site/desde-cero.html](file:///home/workstation/Dev/factory/site/desde-cero.html))

Tras contrastar detalladamente el texto actual de [site/desde-cero.html](file:///home/workstation/Dev/factory/site/desde-cero.html) contra la lógica de [oracle_factory/cli.py](file:///home/workstation/Dev/factory/oracle_factory/cli.py), los archivos del ejemplo en [oracle_factory/data/notas/](file:///home/workstation/Dev/factory/oracle_factory/data/notas/) y las observaciones de la primera auditoría ([tareas/20261003-235610-web-rigurosa/agy2.md](file:///home/workstation/Dev/factory/tareas/20261003-235610-web-rigurosa/agy2.md)):

### Veredicto: **Ninguno encontrado** (no quedan errores u omisiones bloqueantes).

---

## 1. Verificaciones realizadas contra la CLI

1. **Rutas relativas completas:**
   - Destinos de propuesta y especificación: `openspec/changes/ID_DEL_CAMBIO/proposal.md` y `openspec/changes/ID_DEL_CAMBIO/specs/notas/spec.md`. Coinciden exactamente con la estructura creada por `nuevo()` en [oracle_factory/cli.py#L98-L100](file:///home/workstation/Dev/factory/oracle_factory/cli.py#L98-L100).
   - Catálogos y reglas: `catalogos/` y los nombres exactos `notas.casos_ejecutados.oracle` y `notas.resultados.oracle` (sin comodines ambiguos en la explicación de lectura).
   - Requisitos: Se aclara que el nombre de archivo es `requisitos/<id_de_importacion>.requisito` evitando adivinar hashes.
   - Evidencias: `.factory-demo/hechos.json` y `.factory-demo/review.md` coinciden con lo esperado por `juzgar` y `revision`.

2. **Comandos de copia (macOS/Linux y PowerShell):**
   - **macOS / Linux:** Sintaxis estándar con `cp` a rutas completas de destino.
   - **PowerShell (Windows):** Sintaxis precisa con `Copy-Item`, separando claramente cada archivo de origen y destino con barras `/` (compatibles nativamente en PowerShell).

3. **Creación de archivos:**
   - La guía diferencia explícitamente entre bloques ejecutables de terminal y bloques de **contenido para archivos** (`.gitignore`, `.requisito`, `.factory-demo/review.md`).
   - Se advierte la indentación estricta de cuatro espacios sin tabuladores para la línea `medido_por` requerida por Oracle Metalenguaje.

4. **Configuración de `.gitignore`:**
   - Se instruye incluir `.factory-demo/`, `__pycache__/` y `*.pyc`. Esto es crítico para que `contexto_producto()` en [oracle_factory/cli.py#L184-L204](file:///home/workstation/Dev/factory/oracle_factory/cli.py#L184-L204) no detecte archivos no rastreados generados por Python ni huellas temporales al ejecutar pruebas o el sensor.

5. **Frases de confirmación:**
   - Las tres frases exigidas interactivamente por la CLI coinciden carácter por carácter:
     - `APROBAR ESPECIFICACION ID_DEL_CAMBIO` ([cli.py#L231](file:///home/workstation/Dev/factory/oracle_factory/cli.py#L231))
     - `REGISTRAR REVISION ID_DEL_CAMBIO` ([cli.py#L284](file:///home/workstation/Dev/factory/oracle_factory/cli.py#L284))
     - `CERRAR ID_DEL_CAMBIO` ([cli.py#L398](file:///home/workstation/Dev/factory/oracle_factory/cli.py#L398))
   - Se advierte explícitamente que son respuestas a preguntas interactivas de la terminal y no comandos de shell.

6. **Orden de recuperación («Si algo no funciona»):**
   - **Cambio de propuesta o spec:** Explica que `aprobar-spec` reinicia `requisitos=[]`, `revision=None` y `oracle=None` ([cli.py#L237](file:///home/workstation/Dev/factory/oracle_factory/cli.py#L237)), detallando el reencadenamiento exacto: `importar` → vincular medidas en `.requisito` → `oracle cobertura` → pruebas y sensor → commit → `revision` → `juzgar` → `estado` → `cerrar`.
   - **Cambio de código o commit:** Explica que no se reaprueba la spec vigente; se ejecutan pruebas y sensor, se genera commit y se registra una nueva `revision` (lo que invalida el juicio anterior, [cli.py#L295](file:///home/workstation/Dev/factory/oracle_factory/cli.py#L295)), requiriendo repetir `juzgar`.
   - **Cambio de informe o hechos:** Detalla que cambiar el informe exige repetir `revision` y luego `juzgar`, mientras que renovar solo hechos con producto idéntico solo requiere repetir `juzgar`.
   - **Pérdida del ID:** Señala el uso de `tasks list`.
   - **Otro proyecto:** Recuerda ubicar `--proyecto` antes del subcomando ([cli.py#L462](file:///home/workstation/Dev/factory/oracle_factory/cli.py#L462)).

7. **Rigor conceptual:**
   - La plantilla de revisión no asume un informe preaprobado ni resultados ficticios; provee campos `PENDIENTE` y aclara que Factory solo verifica existencia y no vacío, requiriendo evaluación humana.
   - El significado del veredicto verde de Oracle aclara que certifica la observación de tres casos sin fallos, sin garantizar que sean casos únicos, semánticamente exhaustivos ni ausencia de errores fuera de lo medido.

---

## 2. Límites de esta auditoría

- **No es un piloto con un humano principiante:** Se trata de una auditoría técnica analítica de consistencia y usabilidad asistida por agente. La prueba con una persona principiante real sigue pendiente como validación de campo.
- **Sin ejecuciones locales en este turno:** No se instalaron paquetes ni se ejecutaron ejemplos en el entorno de trabajo, respetando la reproducción externa en curso por root.
- **Verificación cruzada de plataformas:** Linux fue validado empíricamente en la auditoría inicial; la compatibilidad de macOS y Windows se verificó analíticamente sobre la sintaxis de PowerShell, terminales POSIX y convenciones de rutas de archivos.
