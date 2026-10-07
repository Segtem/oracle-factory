# Design

Notas para implementar después de la aceptación. No son parte del contrato.

- **Página nueva:** `site/colaboracion.html`, estática, con `style.css`; secciones con `id` estables (`reparto`, `checkouts`, `decisiones`, `relevo`, `revision`, `integracion`, `cierre`, `no-probado`). El ejemplo es el de la prueba entre máquinas: Ana y Bruno, cada uno en su máquina, con un remoto Git común.
- **Fuente:** `docs/colaboracion.md` v2 es la referencia; la página resume y enlaza. Las fricciones salen de `tareas/20261004-121432-coordinar-dos/piloto-agentes-01/piloto.md`.
- **Comprobaciones:** `tests/test_web.py` extrae de `site/*.html` y `docs/*.md` cada `oracle-factory <subcomando>` y cada `--opción` que lo acompaña y los contrasta con el parser de la CLI (no con una lista escrita a mano); y resuelve cada `href` relativo y cada ancla. Se corre en la suite, sin navegador.
- **`--sufijo`:** ya implementado en el árbol al crear este cambio (lo estrenó su propio ID): por defecto la capacidad; validación con `SLUG_RE` y hasta 40 caracteres.
- **Verificación visual:** Playwright no está instalado en esta máquina; la página se revisa además con Agy (auditoría de contenido) y se mira en el navegador antes de cerrar.
