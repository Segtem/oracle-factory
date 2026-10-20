---
generado: oracle-factory kb
id: "20261012-131420-clue-dependencia"
fase: "cerrada"
capacidad: "autoproduccion"
---

# Oracle Clue como dependencia fija de Factory

> Generado por `oracle-factory kb` desde el registro de Factory: no se edita a mano.

- Fase: cerrada
- Capacidad: autoproduccion
- Responsable: nadie
- Spec: [openspec/changes/20261012-131420-clue-dependencia/specs/autoproduccion/spec.md](../../openspec/changes/20261012-131420-clue-dependencia/specs/autoproduccion/spec.md)

## Requisitos

- [[requisitos/autoproduccion_c847ea5712990b078.el_informe_mas_nuevo_de_cada_revisor_reemplaza_a_los_anteriores]] — cumple
- [[requisitos/autoproduccion_c847ea5712990b078.el_menu_de_la_decision_no_corre_sus_numeros]] — cumple
- [[requisitos/autoproduccion_c847ea5712990b078.importar_no_trae_lo_que_la_spec_retira]] — cumple
- [[requisitos/autoproduccion_c847ea5712990b078.los_informes_de_revisores_siempre_se_validan]] — cumple
- [[requisitos/autoproduccion_c847ea5712990b078.oracle_clue_viene_con_factory]] — cumple

## Decisiones

- 2026-10-12 13:14 · Cambio creado · sin identificar (sin_identificar)
- 2026-10-12 13:17 · Spec aprobada · Brian Hollweg (persona)
- 2026-10-12 13:17 · Requisitos importados · claude-code (agente)
- 2026-10-12 13:31 · Spec aprobada · Brian Hollweg (persona)
- 2026-10-12 13:31 · Requisitos importados · claude-code (agente)
- 2026-10-12 13:32 · Medidas confirmadas · Brian Hollweg (persona)
- 2026-10-12 13:32 · Medidas confirmadas · Brian Hollweg (persona)
- 2026-10-12 13:32 · Medidas confirmadas · Brian Hollweg (persona)
- 2026-10-12 15:00 · Revisión registrada · Brian Hollweg (persona) — cambios
- 2026-10-12 15:00 · Juicio de Oracle · claude-code (agente)
- 2026-10-12 15:52 · Spec aprobada · Brian Hollweg (persona)
- 2026-10-12 15:52 · Requisitos importados · claude-code (agente)
- 2026-10-12 15:53 · Medidas confirmadas · Brian Hollweg (persona)
- 2026-10-12 15:53 · Medidas confirmadas · Brian Hollweg (persona)
- 2026-10-12 15:53 · Medidas confirmadas · Brian Hollweg (persona)
- 2026-10-12 15:53 · Medidas confirmadas · Brian Hollweg (persona)
- 2026-10-12 15:53 · Medidas confirmadas · Brian Hollweg (persona)
- 2026-10-12 16:48 · Revisión registrada · Brian Hollweg (persona) — aprobar: Candidato 010f58a: codex y agy sin hallazgos y con revisión completa. Los hallazgos de las vueltas anteriores quedaron corregidos, cada uno con una prueba que falla en el código viejo; evidencia en verde (8 casos de contrato). La revisión anterior registrada como «cambios» se debió a informes incompletos por un error en el pedido y al menú que corría sus números; las dos causas se corrigieron en este cambio. Las últimas vueltas fueron incrementales desde e3f2b64 porque el paquete completo supera el límite de Clue.
- 2026-10-12 16:49 · Juicio de Oracle · claude-code (agente)
- 2026-10-12 16:53 · Cerrado · Brian Hollweg (persona)
- 2026-10-12 16:53 · Archivado · Brian Hollweg (persona)

## Riesgos aceptados

- Ninguno.

## Commits

- `3ab326d` 20261012-131420-clue-dependencia: propuesta, spec y diseño (deducido)
- `fdf155f` 20261012-131420-clue-dependencia: decisión de Brian sobre exponer el comando oracle-clue (deducido)
- `25ee7e1` 20261012-131420-clue-dependencia: spec aprobada por Brian; requisitos importados (deducido)
- `97b4982` 20261012-131420-clue-dependencia: oracle-clue como dependencia fija usada desde el entorno de Factory, sin informes «sin validar», e importar deja afuera los requisitos REMOVED; spec ampliada, pruebas, verificador, catálogos y docs (deducido)
- `79fe821` 20261012-131420-clue-dependencia: spec reaprobada por Brian y requisitos reimportados (sin el retirado); fuera los de la importación anterior (deducido)
- `ff43a4e` 20261012-131420-clue-dependencia: medidas propuestas por claude-code (deducido)
- `beb83f4` 20261012-131420-clue-dependencia: medidas confirmadas por Brian (deducido)
- `bf752f4` 20261012-131420-clue-dependencia: comentarios y límites de pruebas y verificadores ya no suponen que Clue puede faltar (F-001 de codex-1 sobre beb83f4) (deducido)
- `54d56b5` 20261012-131420-clue-dependencia: informe de codex (deducido)
- `122ef26` 20261012-131420-clue-dependencia: k1 prueba con el PATH vacío; el verificador registra la versión de Clue; nombres y la guía al día (hallazgos de agy-1 y codex-1 sobre bf752f4) (deducido)
- `23dba6e` 20261012-131420-clue-dependencia: informe de codex (deducido)
- `e3f2b64` 20261012-131420-clue-dependencia: tipos_spec ignora la sección REMOVED; sin la distribución de Clue, error en vez de PATH; pedir-revision probado sin Clue en el PATH; guía al día (hallazgos de agy-1 y codex-1 sobre 122ef26) (deducido)
- `6afba16` 20261012-131420-clue-dependencia: informe de codex (deducido)
- `e1c0c36` 20261012-131420-clue-dependencia: informe de agy sobre e3f2b64 (sin hallazgos) (deducido)
- `b50b92e` 20261012-131420-clue-dependencia: evidencia del candidato e3f2b64 (deducido)
- `bc60a63` 20261012-131420-clue-dependencia: claude-code propone aprobar con su motivo (deducido)
- `7d24176` 20261012-131420-clue-dependencia: veredicto Oracle (deducido)
- `8f9c401` 20261012-131420-clue-dependencia: revisión registrada por Brian (deducido)
- `9000121` 20261012-131420-clue-dependencia: el informe más nuevo de cada revisor reemplaza a los anteriores y el menú de la decisión no corre sus números (lo que trabó la revisión de este cambio); spec ampliada, pruebas, verificador y docs (deducido)
- `5b0b2ce` 20261012-131420-clue-dependencia: spec reaprobada por Brian; requisitos reimportados; medidas propuestas por claude-code (deducido)
- `e62557b` 20261012-131420-clue-dependencia: medidas confirmadas por Brian (deducido)
- `06a3842` 20261012-131420-clue-dependencia: informe de codex (deducido)
- `e200bab` 20261012-131420-clue-dependencia: el más nuevo de cada revisor reemplaza a los anteriores aunque no se pueda usar (hallazgo de codex-1 sobre e62557b) (deducido)
- `4a53003` 20261012-131420-clue-dependencia: informe de codex (deducido)
- `010f58a` 20261012-131420-clue-dependencia: un JSON que no es objeto en revision/ se avisa (hallazgo de codex-1 y agy-1 sobre e200bab) (deducido)
- `94911c1` 20261012-131420-clue-dependencia: informe de codex (deducido)
- `e0dcec2` 20261012-131420-clue-dependencia: informe de agy sobre 010f58a (sin hallazgos) (deducido)
- `0abfe83` 20261012-131420-clue-dependencia: evidencia del candidato 010f58a (deducido)
- `3cd4e05` 20261012-131420-clue-dependencia: claude-code propone aprobar con su motivo (deducido)
- `2394acd` 20261012-131420-clue-dependencia: revisión registrada por Brian (deducido)
- `5a44767` 20261012-131420-clue-dependencia: veredicto Oracle (deducido)

## Mensajes

- Ninguno.
