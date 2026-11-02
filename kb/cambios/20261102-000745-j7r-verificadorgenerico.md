---
generado: oracle-factory kb
id: "20261102-000745-j7r-verificadorgenerico"
fase: "oracle_verde"
capacidad: "practicas"
---

# Un verificador reutilizable para la evidencia de cada cambio

> Generado por `oracle-factory kb` desde el registro de Factory: no se edita a mano.

- Fase: oracle_verde
- Capacidad: practicas
- Responsable: nadie
- Spec: [openspec/changes/20261102-000745-j7r-verificadorgenerico/specs/practicas/spec.md](../../openspec/changes/20261102-000745-j7r-verificadorgenerico/specs/practicas/spec.md)

## Requisitos

- [[requisitos/practicas_ca947e8cba4f605c1.el_verificador_atribuye_cada_caso_al_requisito_que_su_nombre_indica]] — cumple
- [[requisitos/practicas_ca947e8cba4f605c1.el_verificador_escribe_los_catalogos_del_cambio]] — cumple
- [[requisitos/practicas_ca947e8cba4f605c1.el_verificador_produce_la_evidencia_completa_del_cambio]] — cumple

## Decisiones

- 2026-11-02 00:07 · Cambio creado · claude-code (agente)
- 2026-11-02 00:11 · Spec aprobada · Brian Hollweg (persona)
- 2026-11-02 00:13 · Spec aprobada · Brian Hollweg (persona)
- 2026-11-02 00:13 · Requisitos importados · claude-code (agente)
- 2026-11-02 00:35 · Medidas confirmadas · Brian Hollweg (persona)
- 2026-11-02 00:35 · Medidas confirmadas · Brian Hollweg (persona)
- 2026-11-02 00:35 · Medidas confirmadas · Brian Hollweg (persona)
- 2026-11-02 01:14 · Medidas confirmadas · Brian Hollweg (persona)
- 2026-11-02 01:14 · Medidas confirmadas · Brian Hollweg (persona)
- 2026-11-02 01:14 · Medidas confirmadas · Brian Hollweg (persona)
- 2026-11-02 01:41 · Medidas confirmadas · Brian Hollweg (persona)
- 2026-11-02 01:41 · Medidas confirmadas · Brian Hollweg (persona)
- 2026-11-02 01:41 · Medidas confirmadas · Brian Hollweg (persona)
- 2026-11-02 10:01 · Medidas confirmadas · Brian Hollweg (persona)
- 2026-11-02 10:01 · Medidas confirmadas · Brian Hollweg (persona)
- 2026-11-02 10:01 · Medidas confirmadas · Brian Hollweg (persona)
- 2026-11-02 15:18 · Medidas confirmadas · Brian Hollweg (persona)
- 2026-11-02 15:18 · Medidas confirmadas · Brian Hollweg (persona)
- 2026-11-02 15:18 · Medidas confirmadas · Brian Hollweg (persona)
- 2026-11-02 15:41 · Juicio de Oracle · agy (agente)
- 2026-11-02 16:01 · Medidas confirmadas · Brian Hollweg (persona)
- 2026-11-02 16:01 · Medidas confirmadas · Brian Hollweg (persona)
- 2026-11-02 16:01 · Medidas confirmadas · Brian Hollweg (persona)
- 2026-11-02 20:11 · Medidas confirmadas · Brian Hollweg (persona)
- 2026-11-02 20:11 · Medidas confirmadas · Brian Hollweg (persona)
- 2026-11-02 20:11 · Medidas confirmadas · Brian Hollweg (persona)
- 2026-11-02 20:27 · Juicio de Oracle · agy (agente)
- 2026-11-02 20:39 · Revisión registrada · Brian Hollweg (persona) — aprobar: Siete rondas con revisores independientes (agy2-flash y codex), la última con 0 y 0 sobre el candidato c41e9ce. Hallazgos por ronda, sumando los dos revisores: 9, 6, 5, 2, 1, 2 y 0. Todos los de las rondas 1 a 6 eran reales y se corrigieron con prueba y mutación: alcance con comillas y caracteres no imprimibles, nombres de requisitos pasados a slug, requisitos repetidos, secciones REMOVED y bloques de código con cercas como CommonMark, salida relativa, lecturas ilegibles, herencia y mixins, cláusulas del éxito aisladas, hora de modificación de las fuentes, retiro de catálogos obsoletos y rechazo de enlaces simbólicos. Evidencia con éxito, producida por la propia herramienta: 1041 pruebas y 46 casos de contrato. En cada ronda se corrió una tanda de mutaciones sobre los arreglos; los mutantes que sobrevivían se cerraron con pruebas nuevas y los equivalentes se eliminaron simplificando el código. Límite declarado en docs/tests.md: un requisito con Pruebas: no aplica sigue necesitando un caso con esta herramienta, porque soportarlo cambiaría la spec aprobada.
- 2026-11-02 20:39 · Juicio de Oracle · claude-code (agente)

## Riesgos aceptados

- Ninguno.

## Commits

- `205dcbb` verificador-generico: propuesta, diseño y spec (trailer)
- `931405c` verificador-generico: aprobación de la spec e importación de requisitos (trailer)
- `e672ef2` verificador-generico: herramienta, pruebas, documento y catálogos (trailer)
- `29c271f` verificador-generico: clases sin base, trazabilidad que falla, casos que nunca corren; catálogos regenerados (trailer)
- `bda8996` verificador-generico: proponer las medidas (trailer)
- `1b54f3f` verificador-generico: registrar la confirmación de medidas por Brian (trailer)
- `a0a7312` verificador-generico: arreglar los hallazgos de la primera ronda (alcance con comillas, slug de requisitos, repetidos, salida relativa, lecturas ilegibles, catálogos exactos, límite de 'Pruebas: no aplica') (trailer)
- `053682b` verificador-generico: proponer de nuevo las medidas (trailer)
- `eca559f` verificador-generico: registrar la confirmación de medidas por Brian (trailer)
- `d88c315` verificador-generico: arreglar los hallazgos de la segunda ronda (casos por nombre del método, alcance sin escapes, cabecera como Factory, fuentes con salida relativa, clases auxiliares, éxito exige la corrida exacta) (trailer)
- `7d1c4f8` verificador-generico: proponer de nuevo las medidas (trailer)
- `bd88492` verificador-generico: registrar la confirmación de medidas por Brian (trailer)
- `4f9bbf9` verificador-generico: arreglar los hallazgos de la tercera ronda (herencia, bloques de código, secciones, separadores Unicode, cláusulas del éxito aisladas) (trailer)
- `6aad62d` verificador-generico: proponer de nuevo las medidas (trailer)
- `a35cbce` verificador-generico: registrar la confirmación de medidas por Brian (trailer)
- `c6c5460` verificador-generico: arreglar los hallazgos de la cuarta ronda (cercas de Markdown como CommonMark, archivo restaurado durante la corrida) (trailer)
- `198f19e` verificador-generico: proponer de nuevo las medidas (trailer)
- `9043270` verificador-generico: proponer las medidas con los catálogos regenerados (trailer)
- `749822a` verificador-generico: registrar la confirmación de medidas por Brian (trailer)
- `32805c6` verificador-generico: arreglar el hallazgo de la quinta ronda (catálogos obsoletos del módulo se retiran) (trailer)
- `7036ab2` verificador-generico: proponer las medidas con los catálogos regenerados (trailer)
- `55ef385` verificador-generico: registrar la confirmación de medidas por Brian (trailer)
- `dd138be` verificador-generico: arreglar el hallazgo de la sexta ronda (no se escribe sobre enlaces simbólicos) (trailer)
- `217081a` verificador-generico: proponer las medidas con los catálogos regenerados (trailer)
- `c41e9ce` verificador-generico: registrar la confirmación de medidas por Brian (trailer)
- `7b795e5` verificador-generico: registrar la séptima ronda de revisiones y la evidencia (trailer)
- `dda725f` verificador-generico: proponer la aprobación de la revisión (trailer)
- `de6ef97` verificador-generico: proponer la aprobación de la revisión (motivo corregido) (trailer)
- `7ce3da2` verificador-generico: registrar la revisión aprobada por Brian (trailer)
- Todos, también los que se deducen al integrarlo o los posteriores a la última decisión: `oracle-factory log 20261102-000745-j7r-verificadorgenerico`.

## Mensajes

- Ninguno.
