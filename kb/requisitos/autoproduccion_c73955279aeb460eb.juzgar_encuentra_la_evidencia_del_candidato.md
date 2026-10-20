---
generado: oracle-factory kb
id: "autoproduccion_c73955279aeb460eb.juzgar_encuentra_la_evidencia_del_candidato"
vigente: true
---

# juzgar encuentra la evidencia del candidato

> Generado por `oracle-factory kb` desde el registro de Factory: no se edita a mano.

- Id: `autoproduccion_c73955279aeb460eb.juzgar_encuentra_la_evidencia_del_candidato`
- Vigente: sí
- Cambio: [[cambios/20261007-150043-autoproduccion]]
- Veredicto: cumple
- Medidas: `factory_autoproduccion.juzgar_encuentra_la_evidencia_del_candidato`, `factory_autoproduccion.corrida_completa`
- Fuente: openspec/changes/20261007-150043-autoproduccion/specs/autoproduccion/spec.md#juzgar encuentra la evidencia del candidato

Tipo: funcional `juzgar` sin `--con` SHALL usar `hechos.json` de la carpeta de evidencia del candidato actual (`.factory/cambios/<ID>/candidatos/<sha7>/evidencia/`, la que devuelve `ruta ID evidencia`), y si no existe SHALL fallar sin registrar nada, nombrando la ruta esperada.
