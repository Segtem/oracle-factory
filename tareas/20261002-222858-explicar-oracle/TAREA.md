# Explicar Oracle Factory como flujo humano de producción de software

- ESTADO: ABIERTA
- PRIORIDAD: 50
- ETIQUETAS: 

### Nota (2026-10-02 22:28:58 UTC)

OpenSpec: openspec/changes/20261002-222858-explicar-oracle. Estado de factory: espera aprobación humana de proposal.md y spec.md.

### Nota (2026-10-02 22:30:25 UTC)

Borrador completo de propuesta, requisitos OpenSpec, diseño y tareas para la web pixel art. Falta revisión/aprobación humana explícita antes de implementar.

### Nota (2026-10-02 22:31:42 UTC)

Propuesta/spec terminadas para revisión humana; rama local feat/20261002-oracle-factory-landing-page. No se inició implementación.

### Nota (2026-10-02 23:11:37 UTC)

Revisión del borrador: Oracle 0.38.1 reconoce 5 requisitos en dry-run. La escena web queda explícitamente como simulación visual sin modificar aprobaciones ni tareas reales. Estado continúa espera_aprobacion_spec; web aún no implementada.


### Nota (2026-10-02 23:19:26 UTC)

El usuario indicó «Bien, vamos a trabajar con factory» tras la revisión del alcance presentado. Se continúa la implementación autorizada de la web. Se registra el origen conversacional; no se simula una confirmación escrita en terminal.

### Nota (2026-10-02 23:19:26 UTC)

Requisitos importados: landing_page_c9060e010b9653288.distinguir_responsabilidades_y_madurez_de_herramientas, landing_page_c9060e010b9653288.explicar_la_produccion_de_software_con_oracle_factory, landing_page_c9060e010b9653288.funcionar_como_sitio_estatico_autonomo, landing_page_c9060e010b9653288.mostrar_puntos_de_control_humanos, landing_page_c9060e010b9653288.ofrecer_una_animacion_accesible_y_controlable. Los nuevos nacen SIN MEDIR; verificá cobertura antes del juicio.

### Nota (2026-10-03 12:11:16 UTC)

Integrada web pixel art, comparación de cuatro enfoques y guía desde cero. Alcance ampliado según instrucciones del usuario: portada en main, explicación para principiantes y guía con PyPI/uv. Se conserva el origen conversacional de la autorización. Importación previa sin medidas archivada como texto; no se simula revisión ni cierre humano.

### Nota (2026-10-03 12:11:16 UTC)

Requisitos importados: landing_page_c27184b22c91734e3.comparar_enfoques_para_visitantes_sin_experiencia, landing_page_c27184b22c91734e3.distinguir_responsabilidades_y_madurez_de_herramientas, landing_page_c27184b22c91734e3.explicar_la_produccion_de_software_con_oracle_factory, landing_page_c27184b22c91734e3.funcionar_como_sitio_estatico_autonomo, landing_page_c27184b22c91734e3.guiar_desde_cero_con_herramientas_disponibles, landing_page_c27184b22c91734e3.mostrar_puntos_de_control_humanos, landing_page_c27184b22c91734e3.ofrecer_una_animacion_accesible_y_controlable. Los nuevos nacen SIN MEDIR; verificá cobertura antes del juicio.

### Nota (2026-10-03 12:13:54 UTC)

Verificación integrada: 21 tests Python OK (incluye integración real del ejemplo con Oracle/Trackertast de PyPI); 11 comprobaciones Chromium OK, sin errores JS ni peticiones externas. Evidencia y límites en verificacion-web.json. GitHub Pages habilitado con build_type workflow; queda integrar/push main y verificar el despliegue. Los 7 requisitos de la web siguen SIN MEDIR; no se simula verde ni aprobación humana final.


### Nota (2026-10-03 12:20:52 UTC)

Web integrada y empujada a main: fdde6d1. GitHub Pages publicado: https://segtem.github.io/oracle-factory/ y desde-cero.html. Workflow 37122464122 success. Se verificaron HTTP 200 y coincidencia byte a byte de las dos páginas y los cuatro recursos locales. Tarea permanece abierta para evaluación humana de claridad y acuerdo de medidas; no se registra cierre ni revisión humana ficticia.

## Próximo paso

Recoger la evaluación humana de la web publicada y hacer que una persona sin experiencia siga la guía; registrar sus trabas y acordar medidas defendibles para los 7 requisitos antes del cierre formal de Factory. La distribución instalable y el selector de proyecto se siguen en 20261002-234439-dist-uv.
