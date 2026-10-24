---
generado: oracle-factory kb
id: "web_c2ef84113c2f0ab7f.la_documentacion_se_comprueba_contra_la_cli"
vigente: true
---

# la documentacion se comprueba contra la cli

> Generado por `oracle-factory kb` desde el registro de Factory: no se edita a mano.

- Id: `web_c2ef84113c2f0ab7f.la_documentacion_se_comprueba_contra_la_cli`
- Vigente: sí
- Cambio: [[cambios/20261023-005051-ufj-docs]]
- Veredicto: cumple
- Medidas: `factory_docs.la_documentacion_se_comprueba_contra_la_cli`, `factory_docs.documentacion_al_dia`, `factory_docs.corrida_completa`
- Fuente: openspec/changes/20261023-005051-ufj-docs/specs/web/spec.md#la documentación se comprueba contra la CLI

Tipo: funcional Una comprobación automática SHALL fallar si un subcomando de la CLI no aparece en el README ni en `docs/`, si el README, `docs/` o la web nombran un `oracle-factory X` que no es un subcomando, o si nombran una versión de Factory distinta de la de `pyproject.toml` (salvo en las notas de versión y en el historial de versiones del README).
