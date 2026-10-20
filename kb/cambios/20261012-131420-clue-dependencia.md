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

- 2026-10-12 13:14 · Cambio creado · sin identificar (sin\_identificar)
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

- `beb83f4` 20261012-131420-clue-dependencia: medidas confirmadas por Brian (deducido)
- `bf752f4` 20261012-131420-clue-dependencia: comentarios y límites de pruebas y verificadores ya no suponen que Clue puede faltar (F-001 de codex-1 sobre beb83f4) (deducido)
- `122ef26` 20261012-131420-clue-dependencia: k1 prueba con el PATH vacío; el verificador registra la versión de Clue; nombres y la guía al día (hallazgos de agy-1 y codex-1 sobre bf752f4) (deducido)
- `e3f2b64` 20261012-131420-clue-dependencia: tipos\_spec ignora la sección REMOVED; sin la distribución de Clue, error en vez de PATH; pedir-revision probado sin Clue en el PATH; guía al día (hallazgos de agy-1 y codex-1 sobre 122ef26) (deducido)
- `e62557b` 20261012-131420-clue-dependencia: medidas confirmadas por Brian (deducido)
- `e200bab` 20261012-131420-clue-dependencia: el más nuevo de cada revisor reemplaza a los anteriores aunque no se pueda usar (hallazgo de codex-1 sobre e62557b) (deducido)
- `010f58a` 20261012-131420-clue-dependencia: un JSON que no es objeto en revision/ se avisa (hallazgo de codex-1 y agy-1 sobre e200bab) (deducido)
- Todos, también los que se deducen al integrarlo: `oracle-factory log 20261012-131420-clue-dependencia`.

## Mensajes

- Ninguno.
